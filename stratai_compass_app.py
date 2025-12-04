import os
import io
from datetime import datetime

import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st

# Optional PDF export
try:
    from fpdf import FPDF
    FPDF_AVAILABLE = True
except ImportError:
    FPDF_AVAILABLE = False


# ---------------------------
# CONFIG
# ---------------------------
st.set_page_config(
    page_title="StratAI Compass",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ---------------------------
# HELPER: SCORING LOGIC
# ---------------------------

OBJECTIVES = [
    "Maximize revenue growth",
    "Increase customer adoption",
    "Optimize pricing",
    "Expand into new therapeutic areas",
    "Strengthen internal AI capabilities"
]

SEGMENTS = [
    "Large hospitals",
    "Small/medium clinics",
    "Specialty research labs",
    "Biotech startups",
    "Enterprise healthcare networks"
]

THERAPEUTIC_AREAS = [
    "Oncology",
    "Rare diseases",
    "Infectious disease",
    "Neurological disease",
    "Cardiovascular"
]

BENCHMARKS = [
    "McKinsey AI maturity",
    "Gartner life sciences model",
    "Bain pricing maturity",
    "Revanta internal benchmark"
]


def base_segment_scores():
    """
    Baseline attractiveness scores for each segment.
    Values are just placeholders; replace with real data later.
    """
    return {
        "Large hospitals": 85,
        "Small/medium clinics": 65,
        "Specialty research labs": 70,
        "Biotech startups": 60,
        "Enterprise healthcare networks": 80
    }


def base_therapeutic_scores():
    """
    Baseline attractiveness for each therapeutic area.
    """
    return {
        "Oncology": 90,
        "Rare diseases": 80,
        "Infectious disease": 75,
        "Neurological disease": 70,
        "Cardiovascular": 85
    }


def objective_weights(objective: str):
    """
    How much each dimension matters for the chosen objective.
    Returns weights that sum roughly to 1.
    """
    if objective == "Maximize revenue growth":
        return dict(segment=0.35, therapeutic=0.35, pricing=0.2, capability=0.1)
    elif objective == "Increase customer adoption":
        return dict(segment=0.4, therapeutic=0.25, pricing=0.25, capability=0.1)
    elif objective == "Optimize pricing":
        return dict(segment=0.25, therapeutic=0.25, pricing=0.4, capability=0.1)
    elif objective == "Expand into new therapeutic areas":
        return dict(segment=0.2, therapeutic=0.5, pricing=0.15, capability=0.15)
    elif objective == "Strengthen internal AI capabilities":
        return dict(segment=0.2, therapeutic=0.2, pricing=0.1, capability=0.5)
    return dict(segment=0.25, therapeutic=0.25, pricing=0.25, capability=0.25)


def pricing_strategy_recommendation(objective, segment, therapeutic, benchmark):
    """
    Very simple rule-based recommender.
    Replace with advanced logic later.
    """
    if objective in ["Maximize revenue growth", "Expand into new therapeutic areas"]:
        model = "Value-based pricing with enterprise tiers"
    elif objective == "Increase customer adoption":
        model = "Usage-based pricing with freemium / pilot tiers"
    elif objective == "Optimize pricing":
        model = "Hybrid model (tiered + usage-based add-ons)"
    else:
        model = "Standard subscription with optional usage add-ons"

    rationale = [
        f"Objective '{objective}' favours a model that balances scalability and perceived value.",
        f"Segment '{segment}' typically has { 'higher' if 'Large' in segment or 'Enterprise' in segment else 'moderate' } budget and purchasing committees.",
        f"Therapeutic focus on '{therapeutic}' often demands clear ROI due to clinical risk and regulatory scrutiny.",
        f"Benchmark reference: '{benchmark}' suggests aligning pricing tiers with AI maturity and adoption stage."
    ]

    pricing_score = 80 if "Hybrid" in model or "Value-based" in model else 70
    return model, pricing_score, rationale


def capability_score_from_objective(objective):
    """
    Rough capability pressure: how much Revanta must stretch internally.
    Higher score = better current capability fit.
    """
    mapping = {
        "Maximize revenue growth": 75,
        "Increase customer adoption": 70,
        "Optimize pricing": 65,
        "Expand into new therapeutic areas": 60,
        "Strengthen internal AI capabilities": 55  # implies more work to do
    }
    return mapping.get(objective, 70)


def internal_capability_recommendations(objective, segment, therapeutic):
    """
    Text bullets for internal tools / processes.
    """
    common = [
        "Establish cross-functional steering group (product, data science, commercial, clinical).",
        "Implement standardized data pipelines and quality checks for clinical and operational data.",
        "Create clear KPIs linking AI outcomes to revenue, adoption, and clinical impact."
    ]

    if objective == "Strengthen internal AI capabilities":
        extra = [
            "Build an internal MLOps platform for experiment tracking, deployment, and monitoring.",
            "Hire or upskill an AI product owner dedicated to clinical use cases.",
            "Institute model risk management and governance aligned with healthcare regulations."
        ]
    elif "hospitals" in segment:
        extra = [
            "Develop integration capabilities with major EHR platforms.",
            "Create a hospital-success team focused on onboarding and workflow redesign."
        ]
    else:
        extra = [
            "Develop lightweight API integrations for smaller sites and research labs.",
            "Set up a scalable customer success playbook for pilot-to-scale transitions."
        ]

    if therapeutic == "Oncology":
        extra.append("Partner with oncology key opinion leaders to validate AI models and build trust.")
    elif therapeutic == "Rare diseases":
        extra.append("Invest in specialized data partnerships to overcome small-sample challenges.")
    elif therapeutic == "Infectious disease":
        extra.append("Ensure real-time data processing and strong public-health reporting interfaces.")

    # Deduplicate while preserving order
    seen = set()
    out = []
    for item in common + extra:
        if item not in seen:
            out.append(item)
            seen.add(item)
    return out


def analyze_choice(objective, segment, therapeutic, benchmark):
    """
    Main engine: compute scores + recommendations.
    """
    seg_scores = base_segment_scores()
    ther_scores = base_therapeutic_scores()

    chosen_segment_score = seg_scores.get(segment, 70)
    chosen_ther_score = ther_scores.get(therapeutic, 70)

    pricing_model, pricing_score, pricing_rationale = pricing_strategy_recommendation(
        objective, segment, therapeutic, benchmark
    )

    capability_score = capability_score_from_objective(objective)
    weights = objective_weights(objective)

    overall_score = (
        chosen_segment_score * weights["segment"] +
        chosen_ther_score * weights["therapeutic"] +
        pricing_score * weights["pricing"] +
        capability_score * weights["capability"]
    )

    capability_actions = internal_capability_recommendations(
        objective, segment, therapeutic
    )

    # Recommendation: if another segment/therapy would be better
    # For now, pick global best in each category
    best_segment = max(seg_scores, key=seg_scores.get)
    best_therapeutic = max(ther_scores, key=ther_scores.get)

    return {
        "segment_score": chosen_segment_score,
        "therapeutic_score": chosen_ther_score,
        "pricing_score": pricing_score,
        "capability_score": capability_score,
        "overall_score": round(overall_score, 1),
        "best_segment": best_segment,
        "best_therapeutic": best_therapeutic,
        "pricing_model": pricing_model,
        "pricing_rationale": pricing_rationale,
        "capability_actions": capability_actions,
        "segment_scores_all": seg_scores,
        "therapeutic_scores_all": ther_scores
    }


# ---------------------------
# LOGGING UTILITIES
# ---------------------------

LOG_FILE = "stratai_compass_logs.csv"


def init_logs():
    if "logs" not in st.session_state:
        if os.path.exists(LOG_FILE):
            st.session_state["logs"] = pd.read_csv(LOG_FILE)
        else:
            st.session_state["logs"] = pd.DataFrame(
                columns=[
                    "timestamp", "objective", "segment", "therapeutic", "benchmark",
                    "segment_score", "therapeutic_score", "pricing_score",
                    "capability_score", "overall_score"
                ]
            )


def append_log(row_dict):
    df = st.session_state["logs"]
    df = pd.concat([df, pd.DataFrame([row_dict])], ignore_index=True)
    st.session_state["logs"] = df
    df.to_csv(LOG_FILE, index=False)


# ---------------------------
# EXPORT UTILITIES
# ---------------------------

def make_excel_bytes(summary_dict):
    """
    Build an in-memory Excel file with summary data and scores.
    """
    buffer = io.BytesIO()

    # Summary sheet
    summary_rows = [
        ["Objective", summary_dict["objective"]],
        ["Segment", summary_dict["segment"]],
        ["Therapeutic area", summary_dict["therapeutic"]],
        ["Benchmark", summary_dict["benchmark"]],
        ["Pricing model", summary_dict["pricing_model"]],
        ["Overall score", summary_dict["overall_score"]]
    ]
    df_summary = pd.DataFrame(summary_rows, columns=["Metric", "Value"])

    # Scores sheet
    df_scores = pd.DataFrame({
        "Dimension": ["Segment fit", "Therapeutic fit", "Pricing fit", "Internal capability"],
        "Score": [
            summary_dict["segment_score"],
            summary_dict["therapeutic_score"],
            summary_dict["pricing_score"],
            summary_dict["capability_score"]
        ]
    })

    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df_summary.to_excel(writer, sheet_name="Summary", index=False)
        df_scores.to_excel(writer, sheet_name="Scores", index=False)

    buffer.seek(0)
    return buffer


def make_pdf_bytes(summary_dict):
    """
    Very simple text-based PDF using FPDF.
    """
    if not FPDF_AVAILABLE:
        return None

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "StratAI Compass Report", ln=True)

    pdf.set_font("Arial", size=12)
    pdf.ln(5)
    pdf.multi_cell(0, 8, f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    pdf.ln(3)

    pdf.multi_cell(0, 8, f"Objective: {summary_dict['objective']}")
    pdf.multi_cell(0, 8, f"Segment: {summary_dict['segment']}")
    pdf.multi_cell(0, 8, f"Therapeutic area: {summary_dict['therapeutic']}")
    pdf.multi_cell(0, 8, f"Benchmark: {summary_dict['benchmark']}")
    pdf.ln(3)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "Scores", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(
        0, 8,
        f"Segment fit: {summary_dict['segment_score']}\n"
        f"Therapeutic fit: {summary_dict['therapeutic_score']}\n"
        f"Pricing fit: {summary_dict['pricing_score']}\n"
        f"Internal capability: {summary_dict['capability_score']}\n"
        f"Overall score: {summary_dict['overall_score']}"
    )
    pdf.ln(3)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "Recommended pricing strategy", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 8, summary_dict["pricing_model"])
    pdf.ln(3)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "Pricing rationale", ln=True)
    pdf.set_font("Arial", size=12)
    for line in summary_dict["pricing_rationale"]:
        pdf.multi_cell(0, 8, f"- {line}")
    pdf.ln(3)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "Internal tools & process roadmap", ln=True)
    pdf.set_font("Arial", size=12)
    for action in summary_dict["capability_actions"]:
        pdf.multi_cell(0, 8, f"- {action}")

    pdf_bytes = pdf.output(dest="S").encode("latin-1")
    return io.BytesIO(pdf_bytes)


# ---------------------------
# UI: SIDEBAR
# ---------------------------

init_logs()

mode = st.sidebar.radio("Mode", ["Client dashboard", "Admin panel"])

st.sidebar.markdown("---")
st.sidebar.caption("StratAI Compass · Revanta strategy support")


# ---------------------------
# CLIENT DASHBOARD
# ---------------------------
if mode == "Client dashboard":
    st.title("StratAI Compass – Revanta Strategy Navigator")

    st.markdown(
        "Use this dashboard to explore **segments, therapeutic areas, and objectives**. "
        "StratAI Compass will score the choice, recommend a pricing strategy, and outline "
        "internal tools and processes needed for growth."
    )

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        objective = st.selectbox("Business objective", OBJECTIVES)
    with col2:
        segment = st.selectbox("Customer segment", SEGMENTS)
    with col3:
        therapeutic = st.selectbox("Therapeutic area", THERAPEUTIC_AREAS)
    with col4:
        benchmark = st.selectbox("Benchmark model", BENCHMARKS)

    run = st.button("Run analysis", type="primary")

    if run:
        result = analyze_choice(objective, segment, therapeutic, benchmark)
        st.session_state["last_result"] = {
            **result,
            "objective": objective,
            "segment": segment,
            "therapeutic": therapeutic,
            "benchmark": benchmark
        }

        # Log the query
        log_row = {
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "objective": objective,
            "segment": segment,
            "therapeutic": therapeutic,
            "benchmark": benchmark,
            "segment_score": result["segment_score"],
            "therapeutic_score": result["therapeutic_score"],
            "pricing_score": result["pricing_score"],
            "capability_score": result["capability_score"],
            "overall_score": result["overall_score"]
        }
        append_log(log_row)

    if "last_result" in st.session_state:
        res = st.session_state["last_result"]

        st.markdown("## Summary scores")

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Overall score", res["overall_score"])
        c2.metric("Segment fit", res["segment_score"])
        c3.metric("Therapeutic fit", res["therapeutic_score"])
        c4.metric("Pricing fit", res["pricing_score"])
        c5.metric("Internal capability", res["capability_score"])

        # Radar chart
        radar_df = pd.DataFrame({
            "Dimension": ["Segment fit", "Therapeutic fit", "Pricing fit", "Internal capability"],
            "Score": [
                res["segment_score"],
                res["therapeutic_score"],
                res["pricing_score"],
                res["capability_score"]
            ]
        })
        radar_fig = px.line_polar(
            radar_df,
            r="Score",
            theta="Dimension",
            line_close=True,
            range_r=[0, 100]
        )
        radar_fig.update_traces(fill="toself")
        st.plotly_chart(radar_fig, use_container_width=True)

        st.markdown("## Recommendations")

        col_l, col_r = st.columns(2)
        with col_l:
            st.subheader("Pricing strategy")
            st.write(f"**Recommended model:** {res['pricing_model']}")
            st.write("**Rationale:**")
            for line in res["pricing_rationale"]:
                st.markdown(f"- {line}")

        with col_r:
            st.subheader("Internal tools & processes")
            st.write("Suggested roadmap:")
            for action in res["capability_actions"]:
                st.markdown(f"- {action}")

        st.markdown("## How does this choice compare?")

        seg_df = pd.DataFrame({
            "Segment": list(res["segment_scores_all"].keys()),
            "Score": list(res["segment_scores_all"].values())
        })
        seg_fig = px.bar(seg_df, x="Segment", y="Score", title="Segment attractiveness")
        st.plotly_chart(seg_fig, use_container_width=True)

        ther_df = pd.DataFrame({
            "Therapeutic area": list(res["therapeutic_scores_all"].keys()),
            "Score": list(res["therapeutic_scores_all"].values())
        })
        ther_fig = px.bar(ther_df, x="Therapeutic area", y="Score",
                          title="Therapeutic area attractiveness")
        st.plotly_chart(ther_fig, use_container_width=True)

        st.info(
            f"Global best segment (by baseline data): **{res['best_segment']}** · "
            f"Best therapeutic area: **{res['best_therapeutic']}**"
        )

        st.markdown("## Export")

        excel_buffer = make_excel_bytes(res)
        st.download_button(
            label="Download Excel summary",
            data=excel_buffer,
            file_name="stratai_compass_summary.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        if FPDF_AVAILABLE:
            pdf_buffer = make_pdf_bytes(res)
            st.download_button(
                label="Download PDF report",
                data=pdf_buffer,
                file_name="stratai_compass_report.pdf",
                mime="application/pdf"
            )
        else:
            st.warning(
                "PDF export is unavailable because the 'fpdf' package is not installed. "
                "Run `pip install fpdf` to enable this feature."
            )


# ---------------------------
# ADMIN PANEL
# ---------------------------
else:
    st.title("StratAI Compass – Admin panel")

    st.markdown(
        "View and export all scenarios explored by clients. "
        "Use this log to understand common objectives, segments, and focus areas."
    )

    logs = st.session_state["logs"]
    if logs.empty:
        st.info("No queries logged yet.")
    else:
        st.subheader("Query history")
        st.dataframe(logs, use_container_width=True)

        # Simple filters
        col_a, col_b = st.columns(2)
        with col_a:
            seg_filter = st.multiselect("Filter by segment", SEGMENTS)
        with col_b:
            obj_filter = st.multiselect("Filter by objective", OBJECTIVES)

        filtered = logs.copy()
        if seg_filter:
            filtered = filtered[filtered["segment"].isin(seg_filter)]
        if obj_filter:
            filtered = filtered[filtered["objective"].isin(obj_filter)]

        st.subheader("Filtered view")
        st.dataframe(filtered, use_container_width=True)

        csv_bytes = filtered.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download filtered logs as CSV",
            data=csv_bytes,
            file_name="stratai_compass_logs_filtered.csv",
            mime="text/csv"
        )

        st.caption("Full log file is also stored on the server as 'stratai_compass_logs.csv'.")
