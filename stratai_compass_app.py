import os
import io
from datetime import datetime
from itertools import product

import pandas as pd
import plotly.express as px
import streamlit as st

# Optional PDF export
try:
    from fpdf import FPDF
    FPDF_AVAILABLE = True
except ImportError:
    FPDF_AVAILABLE = False

# ===========================
# CONFIG
# ===========================
st.set_page_config(
    page_title="StratAI Compass",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ===========================
# REFERENCE LISTS
# ===========================

OBJECTIVES = [
    "Maximize revenue growth",
    "Increase customer adoption",
    "Optimize pricing",
    "Expand into new therapeutic areas",
    "Strengthen internal AI capabilities",
]

SEGMENTS = [
    "Large hospitals",
    "Small/medium clinics",
    "Specialty research labs",
    "Biotech startups",
    "Enterprise healthcare networks",
]

THERAPEUTIC_AREAS = [
    "Oncology",
    "Rare diseases",
    "Infectious disease",
    "Neurological disease",
    "Cardiovascular",
]

BENCHMARKS = [
    "McKinsey AI maturity",
    "Gartner life sciences model",
    "Bain pricing maturity",
    "Revanta internal benchmark",
]

# ===========================
# BASELINE SCORES
# ===========================


def base_segment_scores():
    return {
        "Large hospitals": 85,
        "Small/medium clinics": 65,
        "Specialty research labs": 70,
        "Biotech startups": 60,
        "Enterprise healthcare networks": 80,
    }


def base_therapeutic_scores():
    return {
        "Oncology": 90,
        "Rare diseases": 80,
        "Infectious disease": 75,
        "Neurological disease": 70,
        "Cardiovascular": 85,
    }


# ===========================
# OBJECTIVE WEIGHTS
# ===========================


def objective_weights(objective: str):
    if objective == "Maximize revenue growth":
        return dict(segment=0.35, therapeutic=0.35, pricing=0.2, capability=0.1)
    if objective == "Increase customer adoption":
        return dict(segment=0.4, therapeutic=0.25, pricing=0.25, capability=0.1)
    if objective == "Optimize pricing":
        return dict(segment=0.25, therapeutic=0.25, pricing=0.4, capability=0.1)
    if objective == "Expand into new therapeutic areas":
        return dict(segment=0.2, therapeutic=0.5, pricing=0.15, capability=0.15)
    if objective == "Strengthen internal AI capabilities":
        return dict(segment=0.2, therapeutic=0.2, pricing=0.1, capability=0.5)
    # default equal weights
    return dict(segment=0.25, therapeutic=0.25, pricing=0.25, capability=0.25)


# ===========================
# PRICING ENGINE
# ===========================


def base_price_matrix():
    """Base annual contract prices in USD and therapeutic premiums."""
    base_segment = {
        "Large hospitals": 220_000,
        "Small/medium clinics": 90_000,
        "Specialty research labs": 130_000,
        "Biotech startups": 110_000,
        "Enterprise healthcare networks": 280_000,
    }
    therapeutic_premium = {
        "Oncology": 1.25,
        "Rare diseases": 1.30,
        "Infectious disease": 1.10,
        "Neurological disease": 1.05,
        "Cardiovascular": 1.15,
    }
    return base_segment, therapeutic_premium


def objective_price_multiplier(objective: str):
    """Multipliers based on objective (low, high)."""
    if objective == "Maximize revenue growth":
        return 1.15, 1.30
    if objective == "Increase customer adoption":
        return 0.70, 0.90
    if objective == "Optimize pricing":
        return 0.90, 1.10
    if objective == "Expand into new therapeutic areas":
        return 0.85, 1.05
    if objective == "Strengthen internal AI capabilities":
        return 0.80, 1.00
    return 0.90, 1.10


def indicative_price_range(objective, segment, therapeutic):
    """Compute indicative low/high annual contract price in USD."""
    base_segment, therapeutic_premium = base_price_matrix()
    base = base_segment.get(segment, 150_000)
    premium = therapeutic_premium.get(therapeutic, 1.10)
    low_mult, high_mult = objective_price_multiplier(objective)

    base_with_premium = base * premium
    price_low = round(base_with_premium * low_mult, -3)
    price_high = round(base_with_premium * high_mult, -3)
    return int(price_low), int(price_high)


# ===========================
# PRICING STRATEGY & CAPABILITY
# ===========================


def pricing_strategy_recommendation(objective, segment, therapeutic, benchmark):
    """Rule-based pricing strategy recommender."""
    if objective in ["Maximize revenue growth", "Expand into new therapeutic areas"]:
        model = "Value-based pricing with enterprise tiers"
    elif objective == "Increase customer adoption":
        model = "Usage-based pricing with freemium or pilot tiers"
    elif objective == "Optimize pricing":
        model = "Hybrid model (tiered subscription plus usage-based add-ons)"
    else:
        model = "Standard subscription with optional usage-based add-ons"

    if ("Large" in segment) or ("Enterprise" in segment):
        budget_level = "higher"
    else:
        budget_level = "moderate"

    rationale = [
        f"Objective '{objective}' favours a model that balances scalability and perceived value.",
        f"Segment '{segment}' typically has {budget_level} budget and multiple stakeholders.",
        f"Therapeutic focus on '{therapeutic}' usually requires clear ROI and outcome evidence.",
        f"Benchmark '{benchmark}' encourages aligning pricing tiers with AI maturity stages.",
    ]

    pricing_score = 80 if ("Hybrid" in model or "Value-based" in model) else 70
    return model, pricing_score, rationale


def capability_score_from_objective(objective):
    mapping = {
        "Maximize revenue growth": 75,
        "Increase customer adoption": 70,
        "Optimize pricing": 65,
        "Expand into new therapeutic areas": 60,
        "Strengthen internal AI capabilities": 55,
    }
    return mapping.get(objective, 70)


def internal_capability_recommendations(objective, segment, therapeutic):
    """Return a list of internal roadmap actions."""
    common = [
        "Set up a cross-functional steering group (product, data science, commercial, clinical).",
        "Standardise data pipelines and quality checks for clinical and operational data.",
        "Define KPIs that link AI outputs to revenue, adoption, and clinical impact.",
    ]

    if objective == "Strengthen internal AI capabilities":
        extra = [
            "Build an internal MLOps platform for experiment tracking, deployment, and monitoring.",
            "Hire or upskill an AI product owner focused on clinical use cases.",
            "Introduce model risk and governance processes aligned with healthcare regulation.",
        ]
    elif "hospitals" in segment:
        extra = [
            "Develop EHR integration capabilities (for example HL7 or FHIR).",
            "Create a hospital success playbook for workflow redesign and change management.",
        ]
    else:
        extra = [
            "Develop lightweight APIs and connectors for clinics, labs, and smaller customers.",
            "Create a scalable customer success playbook for pilot to scale transitions.",
        ]

    if therapeutic == "Oncology":
        extra.append("Partner with oncology key opinion leaders to validate use cases.")
    elif therapeutic == "Rare diseases":
        extra.append("Form data partnerships to address small sample sizes.")
    elif therapeutic == "Infectious disease":
        extra.append("Enable near real time data ingestion and basic public health reporting.")

    # deduplicate while preserving order
    seen = set()
    result = []
    for item in common + extra:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


# ===========================
# MAIN ANALYSIS ENGINE
# ===========================


def analyze_choice(objective, segment, therapeutic, benchmark):
    seg_scores = base_segment_scores()
    ther_scores = base_therapeutic_scores()

    seg_score = seg_scores.get(segment, 70)
    ther_score = ther_scores.get(therapeutic, 70)

    pricing_model, pricing_score, pricing_rationale = pricing_strategy_recommendation(
        objective, segment, therapeutic, benchmark
    )
    capability_score = capability_score_from_objective(objective)
    weights = objective_weights(objective)

    overall = (
        seg_score * weights["segment"]
        + ther_score * weights["therapeutic"]
        + pricing_score * weights["pricing"]
        + capability_score * weights["capability"]
    )
    overall = round(overall, 1)

    capability_actions = internal_capability_recommendations(
        objective, segment, therapeutic
    )

    best_segment = max(seg_scores, key=seg_scores.get)
    best_therapeutic = max(ther_scores, key=ther_scores.get)

    price_low, price_high = indicative_price_range(objective, segment, therapeutic)
    price_mid = (price_low + price_high) // 2

    return {
        "segment_score": seg_score,
        "therapeutic_score": ther_score,
        "pricing_score": pricing_score,
        "capability_score": capability_score,
        "overall_score": overall,
        "best_segment": best_segment,
        "best_therapeutic": best_therapeutic,
        "pricing_model": pricing_model,
        "pricing_rationale": pricing_rationale,
        "capability_actions": capability_actions,
        "segment_scores_all": seg_scores,
        "therapeutic_scores_all": ther_scores,
        "price_low": price_low,
        "price_high": price_high,
        "price_mid": price_mid,
    }


# ===========================
# LOGGING
# ===========================

LOG_FILE = "stratai_compass_logs.csv"


def init_logs():
    if "logs" not in st.session_state:
        if os.path.exists(LOG_FILE):
            st.session_state["logs"] = pd.read_csv(LOG_FILE)
        else:
            st.session_state["logs"] = pd.DataFrame(
                columns=[
                    "timestamp",
                    "objective",
                    "segment",
                    "therapeutic",
                    "benchmark",
                    "segment_score",
                    "therapeutic_score",
                    "pricing_score",
                    "capability_score",
                    "overall_score",
                    "price_low",
                    "price_high",
                    "price_mid",
                ]
            )


def append_log(row):
    df = st.session_state["logs"]
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    st.session_state["logs"] = df
    df.to_csv(LOG_FILE, index=False)


# ===========================
# EXPORT HELPERS
# ===========================


def make_excel_bytes(summary):
    buffer = io.BytesIO()

    summary_rows = [
        ["Objective", summary["objective"]],
        ["Segment", summary["segment"]],
        ["Therapeutic area", summary["therapeutic"]],
        ["Benchmark", summary["benchmark"]],
        ["Pricing model", summary["pricing_model"]],
        ["Overall score", summary["overall_score"]],
        ["Indicative price low (USD)", summary["price_low"]],
        ["Indicative price high (USD)", summary["price_high"]],
    ]
    df_summary = pd.DataFrame(summary_rows, columns=["Metric", "Value"])

    df_scores = pd.DataFrame(
        {
            "Dimension": [
                "Segment fit",
                "Therapeutic fit",
                "Pricing fit",
                "Internal capability",
            ],
            "Score": [
                summary["segment_score"],
                summary["therapeutic_score"],
                summary["pricing_score"],
                summary["capability_score"],
            ],
        }
    )

    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df_summary.to_excel(writer, sheet_name="Summary", index=False)
        df_scores.to_excel(writer, sheet_name="Scores", index=False)

    buffer.seek(0)
    return buffer


def make_pdf_bytes(summary):
    if not FPDF_AVAILABLE:
        return None

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Fixed width for text blocks (avoid width=0 issues in fpdf2)
    W = 180

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "StratAI Compass Report", ln=True)

    pdf.set_font("Arial", size=12)
    pdf.ln(5)
    pdf.multi_cell(
        W,
        8,
        f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}",
    )
    pdf.ln(3)

    pdf.multi_cell(W, 8, f"Objective: {summary['objective']}")
    pdf.multi_cell(W, 8, f"Segment: {summary['segment']}")
    pdf.multi_cell(W, 8, f"Therapeutic area: {summary['therapeutic']}")
    pdf.multi_cell(W, 8, f"Benchmark: {summary['benchmark']}")
    pdf.multi_cell(
        W,
        8,
        f"Indicative annual price range: "
        f"${summary['price_low']:,} to ${summary['price_high']:,} per account",
    )
    pdf.ln(3)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "Scores", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(
        W,
        8,
        (
            f"Segment fit: {summary['segment_score']}\n"
            f"Therapeutic fit: {summary['therapeutic_score']}\n"
            f"Pricing fit: {summary['pricing_score']}\n"
            f"Internal capability: {summary['capability_score']}\n"
            f"Overall score: {summary['overall_score']}"
        ),
    )
    pdf.ln(3)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "Recommended pricing strategy", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(W, 8, summary["pricing_model"])
    pdf.ln(3)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "Pricing rationale", ln=True)
    pdf.set_font("Arial", size=12)
    for line in summary["pricing_rationale"]:
        pdf.multi_cell(W, 8, f"- {line}")
    pdf.ln(3)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "Internal tools and process roadmap", ln=True)
    pdf.set_font("Arial", size=12)
    for action in summary["capability_actions"]:
        pdf.multi_cell(W, 8, f"- {action}")

    # Get PDF output; fpdf2 may return bytes (newer) or str (older)
    pdf_out = pdf.output(dest="S")

    if isinstance(pdf_out, bytes):
        # Already bytes (fpdf2 on Streamlit Cloud)
        pdf_bytes = pdf_out
    else:
        # Old behavior: returned a string that needs encoding
        pdf_bytes = pdf_out.encode("latin-1", "replace")

    return io.BytesIO(pdf_bytes)




# ===========================
# INITIALISE
# ===========================

init_logs()

mode = st.sidebar.radio("Mode", ["Client dashboard", "Admin panel", "Guide"])
st.sidebar.markdown("---")
st.sidebar.caption("StratAI Compass · Revanta strategy support")

# ===========================
# GUIDE MODE
# ===========================

if mode == "Guide":
    st.title("StratAI Compass – Guide")

    st.markdown(
        """
### What this app does

StratAI Compass is a strategy co-pilot for Revanta.

You choose business objectives, customer segments, therapeutic areas, and benchmark models.
The app then:

- Scores how attractive and aligned each scenario is.
- Recommends a pricing strategy and indicative price range.
- Outlines internal tools and processes Revanta should build.
- Logs all scenarios in the Admin panel.

### Score interpretation

Scores are on a 0 to 100 scale:

- 80 – 100: very strong fit.
- 65 – 79: good fit, but may need refinement.
- 50 – 64: weak fit; consider alternatives.
- Below 50: poor fit for the stated objective.

The overall score is a weighted mix of:

- Segment fit
- Therapeutic fit
- Pricing fit
- Internal capability

Weights depend on the chosen objective.
"""
    )

# ===========================
# CLIENT DASHBOARD
# ===========================

elif mode == "Client dashboard":
    st.title("StratAI Compass – Revanta Strategy Navigator")

    st.markdown(
        "Use this dashboard to explore segments, therapeutic areas, and objectives. "
        "The tool will score each scenario, recommend a pricing strategy with an "
        "indicative price range, and outline internal tools and processes needed for growth."
    )

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        selected_objectives = st.multiselect(
            "Business objective(s)", OBJECTIVES, default=[OBJECTIVES[0]]
        )
    with col2:
        selected_segments = st.multiselect(
            "Customer segment(s)", SEGMENTS, default=[SEGMENTS[0]]
        )
    with col3:
        selected_therapeutics = st.multiselect(
            "Therapeutic area(s)", THERAPEUTIC_AREAS, default=[THERAPEUTIC_AREAS[0]]
        )
    with col4:
        selected_benchmarks = st.multiselect(
            "Benchmark model(s)", BENCHMARKS, default=[BENCHMARKS[0]]
        )

    run = st.button("Run analysis", type="primary")

    if run:
        if not (
            selected_objectives
            and selected_segments
            and selected_therapeutics
            and selected_benchmarks
        ):
            st.warning("Please select at least one option in each category.")
        else:
            scenarios = list(
                product(
                    selected_objectives,
                    selected_segments,
                    selected_therapeutics,
                    selected_benchmarks,
                )
            )

            if len(scenarios) > 40:
                st.warning(
                    f"You selected {len(scenarios)} scenario combinations. "
                    "Please narrow down selections to fewer than 40."
                )
            else:
                rows = []
                for obj, seg, ther, bench in scenarios:
                    res = analyze_choice(obj, seg, ther, bench)
                    row = {
                        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                        "objective": obj,
                        "segment": seg,
                        "therapeutic": ther,
                        "benchmark": bench,
                        "segment_score": res["segment_score"],
                        "therapeutic_score": res["therapeutic_score"],
                        "pricing_score": res["pricing_score"],
                        "capability_score": res["capability_score"],
                        "overall_score": res["overall_score"],
                        "price_low": res["price_low"],
                        "price_high": res["price_high"],
                        "price_mid": res["price_mid"],
                    }
                    rows.append(row)
                    append_log(row)

                st.session_state["multi_results"] = pd.DataFrame(rows)

                first = rows[0]
                detailed = analyze_choice(
                    first["objective"],
                    first["segment"],
                    first["therapeutic"],
                    first["benchmark"],
                )
                st.session_state["last_result"] = {
                    **detailed,
                    "objective": first["objective"],
                    "segment": first["segment"],
                    "therapeutic": first["therapeutic"],
                    "benchmark": first["benchmark"],
                }

    if "last_result" in st.session_state:
        res = st.session_state["last_result"]

        st.markdown("## Summary scores (first scenario)")
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Overall score", res["overall_score"])
        c2.metric("Segment fit", res["segment_score"])
        c3.metric("Therapeutic fit", res["therapeutic_score"])
        c4.metric("Pricing fit", res["pricing_score"])
        c5.metric("Internal capability", res["capability_score"])

        radar_df = pd.DataFrame(
            {
                "Dimension": [
                    "Segment fit",
                    "Therapeutic fit",
                    "Pricing fit",
                    "Internal capability",
                ],
                "Score": [
                    res["segment_score"],
                    res["therapeutic_score"],
                    res["pricing_score"],
                    res["capability_score"],
                ],
            }
        )
        radar_fig = px.line_polar(
            radar_df, r="Score", theta="Dimension", line_close=True, range_r=[0, 100]
        )
        radar_fig.update_traces(fill="toself")
        st.plotly_chart(radar_fig, use_container_width=True)

        st.markdown("## Recommendations")
        left, right = st.columns(2)
        with left:
            st.subheader("Pricing strategy")
            st.write(f"**Recommended model:** {res['pricing_model']}")
            st.write(
                f"**Indicative annual price range:** "
                f"${res['price_low']:,} – ${res['price_high']:,} per account"
            )
            st.write("**Rationale:**")
            for line in res["pricing_rationale"]:
                st.markdown(f"- {line}")
        with right:
            st.subheader("Internal tools and processes")
            for action in res["capability_actions"]:
                st.markdown(f"- {action}")

        st.markdown("## How does this choice compare?")
        seg_df = pd.DataFrame(
            {
                "Segment": list(res["segment_scores_all"].keys()),
                "Score": list(res["segment_scores_all"].values()),
            }
        )
        st.plotly_chart(
            px.bar(seg_df, x="Segment", y="Score", title="Segment attractiveness"),
            use_container_width=True,
        )

        ther_df = pd.DataFrame(
            {
                "Therapeutic area": list(res["therapeutic_scores_all"].keys()),
                "Score": list(res["therapeutic_scores_all"].values()),
            }
        )
        st.plotly_chart(
            px.bar(
                ther_df,
                x="Therapeutic area",
                y="Score",
                title="Therapeutic area attractiveness",
            ),
            use_container_width=True,
        )

        st.info(
            f"Global best segment (baseline): {res['best_segment']} | "
            f"Best therapeutic area: {res['best_therapeutic']}"
        )

        if "multi_results" in st.session_state:
            st.markdown("## Scenario comparison table")
            st.dataframe(st.session_state["multi_results"], use_container_width=True)

        st.markdown("## Export")
        excel_buf = make_excel_bytes(res)
        st.download_button(
            "Download Excel summary",
            data=excel_buf,
            file_name="stratai_compass_summary.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

        if FPDF_AVAILABLE:
            pdf_buf = make_pdf_bytes(res)
            st.download_button(
                "Download PDF report",
                data=pdf_buf,
                file_name="stratai_compass_report.pdf",
                mime="application/pdf",
            )
        else:
            st.warning(
                "PDF export is disabled because the 'fpdf' package is not installed. "
                "Run 'pip install fpdf' to enable it."
            )

# ===========================
# ADMIN PANEL
# ===========================

else:
    st.title("StratAI Compass – Admin panel")

    st.markdown(
        "Review every scenario explored in the tool. "
        "Use filters to understand which objectives and segments are most commonly tested."
    )

    logs = st.session_state["logs"]
    if logs.empty:
        st.info("No scenarios logged yet.")
    else:
        st.subheader("Summary")
        total = len(logs)
        first_ts = logs["timestamp"].min()
        last_ts = logs["timestamp"].max()
        c1, c2, c3 = st.columns(3)
        c1.metric("Total scenarios run", total)
        c2.metric("First run (UTC)", first_ts)
        c3.metric("Most recent run (UTC)", last_ts)

        st.subheader("Full history")
        st.dataframe(logs, use_container_width=True)

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
            "Download filtered logs as CSV",
            data=csv_bytes,
            file_name="stratai_compass_logs_filtered.csv",
            mime="text/csv",
        )

