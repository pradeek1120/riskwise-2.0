import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.supplier_risk_agent import analyse_supplier_risk
from agents.tariff_agent import analyse_tariff_impact
from agents.geopolitical_agent import analyse_geopolitical_risk, scan_all_countries
from agents.mitigation_agent import generate_mitigation_plan
from agents.compliance_agent import generate_compliance_report
from orchestration.langgraph_flow import build_riskwise_graph

# ── Page Config
st.set_page_config(
    page_title="RiskWise 2.0",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #0D2B6B, #1565C0);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 20px;
    }
    .risk-card {
        background: #F0F7FF;
        border-left: 5px solid #1565C0;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .alert-card {
        background: #FFEBEE;
        border-left: 5px solid #C62828;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)


# ── Header
st.markdown("""
<div class="main-header">
    <h1>🛡️ RiskWise 2.0</h1>
    <p>Supply Chain Risk & Tariff Intelligence Platform</p>
    <p><small>Microsoft AI Dev Days Hackathon 2026 | Powered by Azure OpenAI + LangGraph</small></p>
</div>
""", unsafe_allow_html=True)


# ── Sidebar
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/4/44/Microsoft_logo.svg", width=120)
st.sidebar.title("⚙️ RiskWise Controls")
st.sidebar.markdown("---")

page = st.sidebar.selectbox(
    "📊 Select Analysis",
    [
        "🏠 Dashboard Overview",
        "🏭 Supplier Risk Analysis",
        "📊 Tariff Impact Analysis",
        "🌍 Geopolitical Risk Monitor",
        "🔄 Auto-Mitigation Planner",
        "📋 Compliance Report",
        "🤖 Full Pipeline (All 5 Agents)"
    ]
)
st.sidebar.markdown("---")
st.sidebar.info("💡 **Tip:** Use 'Full Pipeline' to run all 5 agents together!")


# ══════════════════════════════════════
# PAGE 1: DASHBOARD OVERVIEW
# ══════════════════════════════════════
if page == "🏠 Dashboard Overview":
    st.header("🏠 Supply Chain Risk Dashboard")

    # KPI Metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Suppliers", "8", "0")
    col2.metric("High Risk", "3", "+1", delta_color="inverse")
    col3.metric("Critical Alerts", "2", "+2", delta_color="inverse")
    col4.metric("Tariff Exposure", "$2.3M", "+$875K", delta_color="inverse")
    col5.metric("ESG Score", "72/100", "-3", delta_color="inverse")

    st.divider()

    # Sample risk data for demo
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🏭 Supplier Risk Heatmap")
        supplier_data = {
            "Supplier": ["TechParts China", "AutoComp India", "SteelWorks Germany",
                         "ChipMakers Taiwan", "LogiSupply Vietnam", "PharmaChem Singapore"],
            "Risk Score": [82, 35, 28, 74, 45, 30],
            "Country": ["China", "India", "Germany", "Taiwan", "Vietnam", "Singapore"],
            "Risk Level": ["Critical", "Low", "Low", "High", "Medium", "Low"]
        }
        df = pd.DataFrame(supplier_data)
        fig = px.bar(
            df, x="Supplier", y="Risk Score",
            color="Risk Score",
            color_continuous_scale="RdYlGn_r",
            title="Supplier Risk Scores",
            range_color=[0, 100]
        )
        fig.add_hline(y=60, line_dash="dash", line_color="orange", annotation_text="Risk Threshold")
        fig.add_hline(y=80, line_dash="dash", line_color="red", annotation_text="Critical Threshold")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("🌍 Global Risk Map")
        country_risk = {
            "Country": ["China", "Russia", "Taiwan", "India", "Vietnam", "Germany", "USA"],
            "Risk Score": [78, 85, 72, 42, 38, 22, 18],
            "ISO": ["CHN", "RUS", "TWN", "IND", "VNM", "DEU", "USA"]
        }
        df_map = pd.DataFrame(country_risk)
        fig_map = px.choropleth(
            df_map,
            locations="ISO",
            color="Risk Score",
            hover_name="Country",
            color_continuous_scale="RdYlGn_r",
            title="Geopolitical Risk by Country",
            range_color=[0, 100]
        )
        st.plotly_chart(fig_map, use_container_width=True)

    st.divider()
    st.subheader("🚨 Active Risk Alerts")
    col1, col2 = st.columns(2)
    with col1:
        st.error("🚨 **CRITICAL**: TechParts China Co. — Risk Score 82/100")
        st.error("🚨 **CRITICAL**: New 25% tariff on electronics from China — $875K extra cost")
    with col2:
        st.warning("⚠️ **HIGH**: ChipMakers Taiwan — Geopolitical tensions (Score: 74/100)")
        st.warning("⚠️ **HIGH**: Russia sanctions update — Affects 2 suppliers")


# ══════════════════════════════════════
# PAGE 2: SUPPLIER RISK
# ══════════════════════════════════════
elif page == "🏭 Supplier Risk Analysis":
    st.header("🏭 Supplier Risk Analysis")
    st.info("Enter supplier details and click Analyse to get an AI-powered risk score across 12 dimensions.")

    col1, col2 = st.columns(2)
    with col1:
        supplier = st.text_input("Supplier Name", "TechParts China Co.")
        country = st.text_input("Country", "China")
        industry = st.text_input("Industry", "Electronics Manufacturing")
    with col2:
        contract = st.text_input("Annual Contract Value", "$2.5M/year")
        years = st.text_input("Years as Supplier", "3 years")
        issues = st.text_area("Recent Issues", "2 delayed shipments in Q4 2025, quality complaints on batch #447")

    if st.button("🔍 Analyse Supplier Risk", type="primary", use_container_width=True):
        with st.spinner(f"🤖 AI Agent analysing {supplier}..."):
            result = analyse_supplier_risk(
                supplier, country, industry, contract, years, issues
            )

        if "error" not in result:
            score = result.get("overall_risk_score", 0)
            level = result.get("risk_level", "Unknown")
            alert = result.get("alert_required", False)

            # KPI Row
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Overall Risk Score", f"{score}/100")
            col2.metric("Risk Level", level)
            col3.metric("Alert Required", "🚨 YES" if alert else "✅ No")
            col4.metric("Top Risk", result.get("top_3_risks", ["N/A"])[0][:20] + "...")

            st.divider()

            # Dimension scores chart
            dims = result.get("dimension_scores", {})
            if dims:
                st.subheader("📊 Risk Score by Dimension")
                dim_df = pd.DataFrame({
                    "Dimension": [k.replace("_", " ").title() for k in dims.keys()],
                    "Score": list(dims.values())
                })
                fig = px.bar(
                    dim_df, x="Score", y="Dimension",
                    orientation="h",
                    color="Score",
                    color_continuous_scale="RdYlGn_r",
                    title=f"Risk Dimensions — {supplier}",
                    range_color=[0, 100]
                )
                st.plotly_chart(fig, use_container_width=True)

            col1, col2 = st.columns(2)
            with col1:
                st.subheader("⚠️ Top 3 Risks")
                for risk in result.get("top_3_risks", []):
                    st.error(f"🔴 {risk}")
            with col2:
                st.subheader("🎯 Recommendation")
                st.info(result.get("recommendation", "N/A"))

            with st.expander("📋 Full JSON Response"):
                st.json(result)
        else:
            st.error(f"Error: {result.get('error')}")


# ══════════════════════════════════════
# PAGE 3: TARIFF IMPACT
# ══════════════════════════════════════
elif page == "📊 Tariff Impact Analysis":
    st.header("📊 Tariff Impact Analysis")
    st.info("Enter tariff change details to calculate the full financial impact on your supply chain.")

    col1, col2 = st.columns(2)
    with col1:
        country = st.text_input("Country", "China")
        product = st.text_input("Product Category", "Electronics & Semiconductors")
        contract = st.text_input("Annual Contract Value ($)", "$5,000,000")
    with col2:
        old_tariff = st.text_input("Current Tariff Rate", "7.5%")
        new_tariff = st.text_input("New Tariff Rate", "25%")
        context = st.text_area("Context", "New US-China trade restrictions March 2026")

    if st.button("💰 Calculate Tariff Impact", type="primary", use_container_width=True):
        with st.spinner("🤖 Tariff Agent calculating financial impact..."):
            result = analyse_tariff_impact(
                country, product, old_tariff, new_tariff, contract,
                context=context
            )

        if "error" not in result:
            impact = result.get("financial_impact", {})

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Tariff Change", result.get("tariff_change", "N/A"))
            col2.metric("Extra Annual Cost", impact.get("additional_annual_cost", "N/A"))
            col3.metric("Extra Monthly Cost", impact.get("additional_monthly_cost", "N/A"))
            col4.metric("Risk Level", result.get("risk_level", "N/A"))

            st.divider()

            alts = result.get("alternative_countries", [])
            if alts:
                st.subheader("🌍 Alternative Sourcing Countries")
                alt_df = pd.DataFrame(alts)
                fig = px.bar(
                    alt_df, x="country", y="tariff_rate",
                    title="Tariff Rates by Alternate Country",
                    color="feasibility",
                    color_discrete_map={"High": "green", "Medium": "orange", "Low": "red"}
                )
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(alt_df, use_container_width=True)

            st.subheader("🎯 Recommendation")
            urgent = result.get("urgent_action_required", False)
            if urgent:
                st.error(f"🚨 URGENT: {result.get('recommendation')}")
            else:
                st.info(result.get("recommendation"))

            with st.expander("📋 Full JSON Response"):
                st.json(result)


# ══════════════════════════════════════
# PAGE 4: GEOPOLITICAL RISK
# ══════════════════════════════════════
elif page == "🌍 Geopolitical Risk Monitor":
    st.header("🌍 Geopolitical Risk Monitor")
    st.info("Monitor geopolitical risk across supplier countries in real-time.")

    mode = st.radio("Analysis Mode", ["Single Country", "Multi-Country Scan"])

    if mode == "Single Country":
        col1, col2 = st.columns(2)
        with col1:
            country = st.text_input("Country", "China")
            industry = st.text_input("Industry Context", "Electronics Manufacturing")
        with col2:
            dependency = st.selectbox("Supply Chain Dependency", ["Low", "Medium", "High", "Critical"])
            context = st.text_area("Current Context", "US-China trade tensions, 2026 tariff changes")

        if st.button("🌍 Analyse Country Risk", type="primary", use_container_width=True):
            with st.spinner(f"🤖 Geopolitical Agent scanning {country}..."):
                result = analyse_geopolitical_risk(country, industry, context, dependency)

            if "error" not in result:
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Risk Score", f"{result.get('risk_score', 0)}/100")
                col2.metric("Risk Level", result.get("risk_level", "N/A"))
                col3.metric("Stability Index", f"{result.get('stability_index', 0)}/100")
                col4.metric("Disruption Probability", result.get("trade_disruption_probability", "N/A"))

                st.divider()
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("⚠️ Key Risks")
                    for risk in result.get("key_risks", []):
                        st.warning(f"⚠️ {risk}")
                with col2:
                    st.subheader("📊 Country Profile")
                    st.info(f"Political Stability: {result.get('political_stability', 'N/A')}")
                    st.info(f"Sanctions Exposure: {result.get('sanctions_exposure', 'N/A')}")
                    st.info(f"Currency Risk: {result.get('currency_risk', 'N/A')}")
                    st.info(f"Monitor Every: {result.get('monitoring_frequency', 'N/A')}")

                if result.get("alert_required"):
                    st.error(f"🚨 ALERT: {result.get('recommended_action')}")
                else:
                    st.success(f"✅ {result.get('recommended_action')}")

    else:
        countries = st.multiselect(
            "Select Countries to Scan",
            ["China", "Russia", "Taiwan", "India", "Vietnam", "Germany", "USA", "Japan", "South Korea", "Bangladesh"],
            default=["China", "Taiwan", "Russia", "India", "Vietnam"]
        )

        if st.button("🌐 Scan All Countries", type="primary", use_container_width=True):
            results = []
            progress = st.progress(0)
            for i, c in enumerate(countries):
                with st.spinner(f"Scanning {c}..."):
                    r = analyse_geopolitical_risk(c)
                    results.append({
                        "Country": c,
                        "Risk Score": r.get("risk_score", 0),
                        "Risk Level": r.get("risk_level", "Unknown"),
                        "Alert": "🚨 YES" if r.get("alert_required") else "✅ No",
                        "Disruption Prob": r.get("trade_disruption_probability", "N/A")
                    })
                    progress.progress((i + 1) / len(countries))

            df = pd.DataFrame(results)
            fig = px.bar(
                df, x="Country", y="Risk Score",
                color="Risk Score",
                color_continuous_scale="RdYlGn_r",
                title="Geopolitical Risk — Multi-Country Scan",
                range_color=[0, 100]
            )
            fig.add_hline(y=60, line_dash="dash", line_color="orange")
            fig.add_hline(y=80, line_dash="dash", line_color="red")
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df, use_container_width=True)


# ══════════════════════════════════════
# PAGE 5: MITIGATION PLANNER
# ══════════════════════════════════════
elif page == "🔄 Auto-Mitigation Planner":
    st.header("🔄 Auto-Mitigation Planner")
    st.info("Enter risk details and get an AI-generated mitigation action plan instantly.")

    col1, col2 = st.columns(2)
    with col1:
        risk_type = st.text_input("Risk Type", "Combined Geopolitical + Tariff Risk")
        supplier = st.text_input("Affected Supplier", "TechParts China Co.")
        risk_score = st.slider("Current Risk Score", 0, 100, 82)
        country = st.text_input("Country", "China")
    with col2:
        contract = st.text_input("Contract Value", "$2.5M/year")
        geo_level = st.selectbox("Geo Risk Level", ["Low", "Medium", "High", "Critical"])
        tariff_impact = st.text_input("Tariff Financial Impact", "$437,500 extra/year")
        details = st.text_area("Additional Details", "Critical single-source supplier. New 25% tariff announced.")

    if st.button("🔄 Generate Mitigation Plan", type="primary", use_container_width=True):
        with st.spinner("🤖 Mitigation Agent generating action plan..."):
            result = generate_mitigation_plan(
                risk_type, supplier, risk_score, country,
                contract, details, geo_level, tariff_impact
            )

        if "error" not in result:
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Severity", result.get("severity", "N/A"))
            col2.metric("Mitigation Cost", result.get("estimated_cost_to_mitigate", "N/A"))
            col3.metric("Time to Resolve", result.get("estimated_time_to_resolve", "N/A"))
            col4.metric("Risk Reduction", result.get("risk_reduction_after_mitigation", "N/A"))

            st.divider()
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("⚡ Immediate Actions")
                for action in result.get("immediate_actions", []):
                    st.error(f"🔴 {action}")
                st.subheader("📅 Short-Term Actions")
                for action in result.get("short_term_actions", []):
                    st.warning(f"🟡 {action}")

            with col2:
                st.subheader("🏭 Alternate Suppliers")
                alts = result.get("alternate_suppliers", [])
                if alts:
                    alt_df = pd.DataFrame(alts)
                    st.dataframe(alt_df, use_container_width=True)
                st.subheader("📈 Long-Term Strategy")
                for action in result.get("long_term_actions", []):
                    st.success(f"🟢 {action}")

            if result.get("escalate_to_management"):
                st.error("🚨 ESCALATE TO MANAGEMENT IMMEDIATELY")
            if result.get("draft_po_required"):
                st.warning("📄 Draft Purchase Order Required")


# ══════════════════════════════════════
# PAGE 6: COMPLIANCE REPORT
# ══════════════════════════════════════
elif page == "📋 Compliance Report":
    st.header("📋 Compliance & Risk Report Generator")
    st.info("Auto-generate a professional supply chain compliance report.")

    col1, col2 = st.columns(2)
    with col1:
        company = st.text_input("Company Name", "RiskWise Demo Corp")
        period = st.text_input("Reporting Period", "Q1 2026 (January - March)")
        total_suppliers = st.number_input("Total Suppliers", value=8)
        high_risk = st.number_input("High Risk Suppliers", value=3)
    with col2:
        risk_events = st.text_area("Key Risk Events", "China tariff hike to 25%, Taiwan geopolitical tensions")
        mitigation = st.text_area("Mitigation Actions Taken", "3 alternate suppliers identified in Vietnam and India")
        exposure = st.text_input("Financial Exposure", "$2.3M additional annual cost")

    if st.button("📋 Generate Report", type="primary", use_container_width=True):
        with st.spinner("🤖 Compliance Agent generating report..."):
            result = generate_compliance_report(
                company, period, int(total_suppliers), int(high_risk),
                risk_events, mitigation, exposure
            )

        if "error" not in result:
            st.success(f"✅ Report Generated: {result.get('report_title')}")

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Overall Status", result.get("overall_risk_status", "N/A"))
            col2.metric("ESG Score", f"{result.get('esg_score', 0)}/100")
            col3.metric("Financial Exposure", result.get("financial_risk_exposure", "N/A"))
            col4.metric("Report Status", result.get("report_status", "N/A"))

            st.divider()
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("📊 Risk Summary")
                summary = result.get("risk_score_summary", {})
                risk_counts = {
                    "Low Risk": summary.get("low_risk_count", 0),
                    "Medium Risk": summary.get("medium_risk_count", 0),
                    "High Risk": summary.get("high_risk_count", 0),
                    "Critical Risk": summary.get("critical_risk_count", 0)
                }
                fig = px.pie(
                    values=list(risk_counts.values()),
                    names=list(risk_counts.keys()),
                    color_discrete_sequence=["green", "yellow", "orange", "red"],
                    title="Supplier Risk Distribution"
                )
                st.plotly_chart(fig, use_container_width=True)

                st.subheader("📋 Executive Summary")
                st.info(result.get("executive_summary", "N/A"))

            with col2:
                st.subheader("🎯 Top Recommendations")
                for rec in result.get("top_recommendations", []):
                    st.success(f"✅ {rec}")

                st.subheader("⚠️ Compliance Issues")
                for issue in result.get("compliance_issues", []):
                    st.warning(f"⚠️ {issue}")

                st.subheader("📅 Next Review")
                st.info(f"Next Review Date: {result.get('next_review_date', 'N/A')}")

            with st.expander("📋 Full Report JSON"):
                st.json(result)


# ══════════════════════════════════════
# PAGE 7: FULL PIPELINE
# ══════════════════════════════════════
elif page == "🤖 Full Pipeline (All 5 Agents)":
    st.header("🤖 Full 5-Agent Pipeline")
    st.info("Run all 5 AI agents together via LangGraph orchestration. Watch them work in sequence!")

    col1, col2 = st.columns(2)
    with col1:
        country = st.text_input("Country", "China")
        supplier = st.text_input("Supplier Name", "TechParts China Co.")
        product = st.text_input("Product Category", "Electronics & Semiconductors")
    with col2:
        contract = st.text_input("Contract Value", "$5,000,000")
        current_tariff = st.text_input("Current Tariff Rate", "7.5%")
        new_tariff = st.text_input("New Tariff Rate", "25%")

    st.info("""
    **Pipeline Flow:**
    🌍 Geo Agent → 📊 Tariff Agent → 🏭 Supplier Agent → 🔄 Mitigation Agent (if risk ≥ 60) → 📋 Compliance Agent
    """)

    if st.button("🚀 Run Full Pipeline", type="primary", use_container_width=True):
        with st.spinner("🤖 Running all 5 agents via LangGraph... This may take 30-60 seconds..."):
            graph = build_riskwise_graph()
            result = graph.invoke({
                "country": country,
                "supplier_name": supplier,
                "product_category": product,
                "contract_value": contract,
                "current_tariff": current_tariff,
                "new_tariff": new_tariff,
                "alert_required": False,
                "pipeline_log": [],
                "geo_risk": None,
                "tariff_risk": None,
                "supplier_risk": None,
                "mitigation_plan": None,
                "compliance_report": None,
                "overall_risk_score": None
            })

        st.success("✅ All 5 agents completed successfully!")
        st.balloons()

        # Pipeline Log
        st.subheader("📋 Pipeline Execution Log")
        for i, log in enumerate(result.get("pipeline_log", []), 1):
            st.text(f"  {i}. {log}")

        st.divider()

        # Results from all agents
        col1, col2, col3 = st.columns(3)
        geo = result.get("geo_risk", {})
        tariff = result.get("tariff_risk", {})
        supplier_r = result.get("supplier_risk", {})
        report = result.get("compliance_report", {})

        col1.metric("Geo Risk Score", f"{geo.get('risk_score', 0)}/100")
        col2.metric("Supplier Risk", f"{result.get('overall_risk_score', 0)}/100")
        col3.metric("Final Status", report.get("overall_risk_status", "N/A"))

        extra = tariff.get("financial_impact", {}).get("additional_annual_cost", "N/A")
        st.error(f"💰 Tariff Financial Impact: {extra} additional annual cost")

        mitigation = result.get("mitigation_plan", {})
        if mitigation:
            st.subheader("🔄 Auto-Mitigation Actions")
            for action in mitigation.get("immediate_actions", []):
                st.warning(f"⚡ {action}")

        st.subheader("🎯 Final Recommendations")
        for rec in report.get("top_recommendations", []):
            st.success(f"✅ {rec}")

        with st.expander("🔍 Full Pipeline JSON Output"):
            st.json(result)
