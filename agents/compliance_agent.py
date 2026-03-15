import os
import json
from datetime import datetime
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser

load_dotenv()

llm = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-08-01-preview"),
    temperature=0.1
)

prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a trade compliance and supply chain reporting specialist.
Generate professional, detailed supply chain risk compliance reports.

ALWAYS respond ONLY in this exact JSON format, no extra text:
{{
  "report_title": "Supply Chain Risk Report - Q1 2026",
  "report_date": "date",
  "company": "company name",
  "period": "period",
  "executive_summary": "2-3 sentence summary of overall risk status",
  "overall_risk_status": "Low/Medium/High/Critical",
  "risk_score_summary": {{
    "total_suppliers_analysed": 0,
    "low_risk_count": 0,
    "medium_risk_count": 0,
    "high_risk_count": 0,
    "critical_risk_count": 0
  }},
  "key_risk_events": [
    "Event 1",
    "Event 2",
    "Event 3"
  ],
  "compliance_issues": [
    "Issue 1",
    "Issue 2"
  ],
  "regulatory_changes": [
    "Change 1",
    "Change 2"
  ],
  "esg_score": 0,
  "esg_breakdown": {{
    "environmental": 0,
    "social": 0,
    "governance": 0
  }},
  "financial_risk_exposure": "$X",
  "top_recommendations": [
    "Recommendation 1",
    "Recommendation 2",
    "Recommendation 3"
  ],
  "next_review_date": "date",
  "report_status": "Final/Draft"
}}"""),
    ("human", """Generate compliance report:
Company: {company}
Reporting Period: {period}
Total Suppliers: {total_suppliers}
High Risk Suppliers: {high_risk_suppliers}
Risk Events This Period: {risk_events}
Mitigation Actions Taken: {mitigation_actions}
Financial Exposure: {financial_exposure}
Additional Context: {context}
""")
])

compliance_chain = prompt | llm | StrOutputParser()


def generate_compliance_report(
    company: str,
    period: str,
    total_suppliers: int = 8,
    high_risk_suppliers: int = 3,
    risk_events: str = "None",
    mitigation_actions: str = "None",
    financial_exposure: str = "Unknown",
    context: str = "Standard quarterly review"
) -> dict:
    """Generate a full compliance and risk report."""

    print(f"\n📋 Generating compliance report for {company}...")

    result = compliance_chain.invoke({
        "company": company,
        "period": period,
        "total_suppliers": total_suppliers,
        "high_risk_suppliers": high_risk_suppliers,
        "risk_events": risk_events,
        "mitigation_actions": mitigation_actions,
        "financial_exposure": financial_exposure,
        "context": context
    })

    try:
        clean = result.strip()
        if "```json" in clean:
            clean = clean.split("```json")[1].split("```")[0].strip()
        elif "```" in clean:
            clean = clean.split("```")[1].split("```")[0].strip()
        return json.loads(clean)
    except json.JSONDecodeError:
        return {"error": "Failed to parse response", "raw": result}


if __name__ == "__main__":
    result = generate_compliance_report(
        company="RiskWise Demo Corp",
        period="Q1 2026 (January - March)",
        total_suppliers=8,
        high_risk_suppliers=3,
        risk_events="China tariff hike to 25%, Taiwan geopolitical tensions, Russia sanctions update",
        mitigation_actions="Identified 3 alternate suppliers in Vietnam and India, raised draft POs",
        financial_exposure="$2.3M additional annual cost from tariff changes",
        context="Microsoft AI Dev Days Hackathon Demo - Q1 2026"
    )

    print("\n📋 COMPLIANCE REPORT:")
    print(json.dumps(result, indent=2))

    if "error" not in result:
        print(f"\n{'='*50}")
        print(f"Report    : {result.get('report_title')}")
        print(f"Status    : {result.get('overall_risk_status')}")
        print(f"ESG Score : {result.get('esg_score')}/100")
        print(f"Exposure  : {result.get('financial_risk_exposure')}")
        recs = result.get('top_recommendations', [])
        print(f"\n🎯 Top Recommendation:")
        if recs:
            print(f"   → {recs[0]}")
        print(f"{'='*50}")
