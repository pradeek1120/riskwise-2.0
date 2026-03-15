import os
import json
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv

from agents.geopolitical_agent import analyse_geopolitical_risk
from agents.tariff_agent import analyse_tariff_impact
from agents.supplier_risk_agent import analyse_supplier_risk
from agents.mitigation_agent import generate_mitigation_plan
from agents.compliance_agent import generate_compliance_report

load_dotenv()


# ── Shared State passed between all agents
class RiskWiseState(TypedDict):
    # Input fields
    country: str
    supplier_name: str
    product_category: str
    contract_value: str
    current_tariff: str
    new_tariff: str
    # Output fields filled by each agent
    geo_risk: Optional[dict]
    tariff_risk: Optional[dict]
    supplier_risk: Optional[dict]
    mitigation_plan: Optional[dict]
    compliance_report: Optional[dict]
    # Calculated fields
    overall_risk_score: Optional[int]
    alert_required: bool
    pipeline_log: list


# ── Agent Node 1: Geopolitical Risk
def run_geo_agent(state: RiskWiseState) -> RiskWiseState:
    print("\n" + "─"*50)
    print("[1/5] 🌍 Geopolitical Risk Agent Running...")
    print("─"*50)

    result = analyse_geopolitical_risk(
        country=state["country"],
        industry=state["product_category"],
        context="Supply chain risk assessment 2026",
        dependency="High"
    )
    state["geo_risk"] = result
    state["alert_required"] = result.get("alert_required", False)

    score = result.get("risk_score", 0)
    level = result.get("risk_level", "Unknown")
    state["pipeline_log"].append(f"Geo Agent: {state['country']} scored {score}/100 ({level})")
    print(f"   ✅ Geo Risk Score: {score}/100 — {level}")
    return state


# ── Agent Node 2: Tariff Impact
def run_tariff_agent(state: RiskWiseState) -> RiskWiseState:
    print("\n" + "─"*50)
    print("[2/5] 📊 Tariff Impact Agent Running...")
    print("─"*50)

    result = analyse_tariff_impact(
        country=state["country"],
        product_category=state["product_category"],
        current_tariff=state.get("current_tariff", "7.5%"),
        new_tariff=state.get("new_tariff", "25%"),
        contract_value=state["contract_value"],
        current_suppliers=state["supplier_name"],
        context="Trade policy update 2026"
    )
    state["tariff_risk"] = result

    extra_cost = result.get("financial_impact", {}).get("additional_annual_cost", "Unknown")
    state["pipeline_log"].append(f"Tariff Agent: Extra cost = {extra_cost}/year")
    print(f"   ✅ Additional Cost: {extra_cost}/year")
    return state


# ── Agent Node 3: Supplier Risk Scoring
def run_supplier_agent(state: RiskWiseState) -> RiskWiseState:
    print("\n" + "─"*50)
    print("[3/5] 🏭 Supplier Risk Scoring Agent Running...")
    print("─"*50)

    result = analyse_supplier_risk(
        supplier_name=state["supplier_name"],
        country=state["country"],
        industry=state["product_category"],
        contract_value=state["contract_value"],
        years_as_supplier="3 years",
        recent_issues="Flagged by geopolitical and tariff agents",
        additional_info=f"Geo Risk: {state['geo_risk'].get('risk_level', 'Unknown')}"
    )
    state["supplier_risk"] = result
    state["overall_risk_score"] = result.get("overall_risk_score", 0)

    score = result.get("overall_risk_score", 0)
    level = result.get("risk_level", "Unknown")
    state["pipeline_log"].append(f"Supplier Agent: {state['supplier_name']} scored {score}/100 ({level})")
    print(f"   ✅ Supplier Risk Score: {score}/100 — {level}")
    return state


# ── Agent Node 4: Auto-Mitigation
def run_mitigation_agent(state: RiskWiseState) -> RiskWiseState:
    print("\n" + "─"*50)
    print("[4/5] 🔄 Auto-Mitigation Agent Running...")
    print("─"*50)

    extra_cost = state.get("tariff_risk", {}).get("financial_impact", {}).get("additional_annual_cost", "Unknown")
    geo_level = state.get("geo_risk", {}).get("risk_level", "Unknown")

    result = generate_mitigation_plan(
        risk_type="Combined Geopolitical + Tariff Risk",
        supplier=state["supplier_name"],
        risk_score=state.get("overall_risk_score", 0),
        country=state["country"],
        contract_value=state["contract_value"],
        details=f"Supplier scored {state.get('overall_risk_score')}/100. Geo: {geo_level}. Tariff extra cost: {extra_cost}",
        geo_risk_level=geo_level,
        tariff_impact=extra_cost
    )
    state["mitigation_plan"] = result

    actions = result.get("immediate_actions", [])
    state["pipeline_log"].append(f"Mitigation Agent: {len(actions)} immediate actions generated")
    print(f"   ✅ Generated {len(actions)} immediate actions")
    if actions:
        print(f"   🎯 Top Action: {actions[0][:80]}...")
    return state


# ── Agent Node 5: Compliance Report
def run_compliance_agent(state: RiskWiseState) -> RiskWiseState:
    print("\n" + "─"*50)
    print("[5/5] 📋 Compliance & Reporting Agent Running...")
    print("─"*50)

    extra_cost = state.get("tariff_risk", {}).get("financial_impact", {}).get("additional_annual_cost", "Unknown")
    mitigation_actions = ", ".join(
        state.get("mitigation_plan", {}).get("immediate_actions", ["None"])[:2]
    )

    result = generate_compliance_report(
        company="RiskWise Demo Corp",
        period="Q1 2026",
        total_suppliers=8,
        high_risk_suppliers=3,
        risk_events=f"Tariff hike in {state['country']}, Geo risk: {state.get('geo_risk', {}).get('risk_level', 'Unknown')}",
        mitigation_actions=mitigation_actions,
        financial_exposure=extra_cost,
        context=f"Automated report for {state['supplier_name']}"
    )
    state["compliance_report"] = result

    status = result.get("overall_risk_status", "Unknown")
    esg = result.get("esg_score", 0)
    state["pipeline_log"].append(f"Compliance Agent: Report generated — Status: {status}, ESG: {esg}/100")
    print(f"   ✅ Report Generated — Risk Status: {status}, ESG Score: {esg}/100")
    return state


# ── Conditional Routing: Should we run mitigation?
def should_mitigate(state: RiskWiseState) -> str:
    score = state.get("overall_risk_score", 0)
    print(f"\n   🔀 Routing Decision: Risk Score = {score}/100")
    if score >= 60:
        print(f"   ⚠️  Score >= 60 → Triggering Mitigation Agent")
        return "mitigate"
    else:
        print(f"   ✅ Score < 60 → Skipping to Compliance Report")
        return "report"


# ── Build the LangGraph
def build_riskwise_graph():
    graph = StateGraph(RiskWiseState)

    # Add all agent nodes
    graph.add_node("geo_agent", run_geo_agent)
    graph.add_node("tariff_agent", run_tariff_agent)
    graph.add_node("supplier_agent", run_supplier_agent)
    graph.add_node("mitigation_agent", run_mitigation_agent)
    graph.add_node("compliance_agent", run_compliance_agent)

    # Define the flow
    graph.set_entry_point("geo_agent")
    graph.add_edge("geo_agent", "tariff_agent")
    graph.add_edge("tariff_agent", "supplier_agent")

    # Conditional: if risk >= 60 → mitigate, else → report directly
    graph.add_conditional_edges(
        "supplier_agent",
        should_mitigate,
        {
            "mitigate": "mitigation_agent",
            "report": "compliance_agent"
        }
    )
    graph.add_edge("mitigation_agent", "compliance_agent")
    graph.add_edge("compliance_agent", END)

    return graph.compile()


# ── Run the full pipeline
if __name__ == "__main__":
    print("\n" + "="*50)
    print("🛡️  RISKWISE 2.0 — FULL PIPELINE STARTING")
    print("="*50)

    app = build_riskwise_graph()

    # Run the pipeline
    final_state = app.invoke({
        "country": "China",
        "supplier_name": "TechParts China Co.",
        "product_category": "Electronics & Semiconductors",
        "contract_value": "$5,000,000",
        "current_tariff": "7.5%",
        "new_tariff": "25%",
        "alert_required": False,
        "pipeline_log": [],
        "geo_risk": None,
        "tariff_risk": None,
        "supplier_risk": None,
        "mitigation_plan": None,
        "compliance_report": None,
        "overall_risk_score": None
    })

    # Final Summary
    print("\n\n" + "="*55)
    print("🛡️  RISKWISE 2.0 — COMPLETE PIPELINE RESULTS")
    print("="*55)
    print(f"Supplier         : {final_state['supplier_name']}")
    print(f"Country          : {final_state['country']}")
    print(f"Overall Risk     : {final_state.get('overall_risk_score')}/100")

    geo = final_state.get("geo_risk", {})
    print(f"Geo Risk Level   : {geo.get('risk_level', 'N/A')} ({geo.get('risk_score', 0)}/100)")

    tariff = final_state.get("tariff_risk", {})
    extra = tariff.get("financial_impact", {}).get("additional_annual_cost", "N/A")
    print(f"Tariff Impact    : {extra}/year extra cost")

    supplier = final_state.get("supplier_risk", {})
    print(f"Supplier Level   : {supplier.get('risk_level', 'N/A')}")

    mitigation = final_state.get("mitigation_plan", {})
    if mitigation:
        actions = mitigation.get("immediate_actions", [])
        print(f"Mitigation       : {len(actions)} actions generated")
        if actions:
            print(f"Top Action       : {actions[0][:70]}...")

    report = final_state.get("compliance_report", {})
    print(f"Final Status     : {report.get('overall_risk_status', 'N/A')}")
    print(f"ESG Score        : {report.get('esg_score', 'N/A')}/100")

    print("\n📋 Pipeline Log:")
    for i, log in enumerate(final_state.get("pipeline_log", []), 1):
        print(f"   {i}. {log}")
    print("="*55)
