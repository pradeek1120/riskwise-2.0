import os
import json
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser

load_dotenv()

# ── Azure OpenAI Connection
llm = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-08-01-preview"),
    temperature=0.1
)

# ── Prompt Template
prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an expert supply chain risk analyst.
Score suppliers on risk from 0 to 100 across 12 dimensions.

Scoring:
- 0-30   = Low Risk
- 31-60  = Medium Risk
- 61-80  = High Risk
- 81-100 = Critical Risk

ALWAYS respond ONLY in this exact JSON format, no extra text:
{{
  "supplier_name": "name",
  "overall_risk_score": 0,
  "risk_level": "Low/Medium/High/Critical",
  "dimension_scores": {{
    "financial_health": 0,
    "delivery_reliability": 0,
    "geopolitical_exposure": 0,
    "quality_consistency": 0,
    "capacity_utilization": 0,
    "dependency_risk": 0,
    "compliance_record": 0,
    "natural_disaster_exposure": 0,
    "cybersecurity_posture": 0,
    "esg_rating": 0,
    "lead_time_stability": 0,
    "communication_responsiveness": 0
  }},
  "top_3_risks": ["risk1", "risk2", "risk3"],
  "recommendation": "action here",
  "alert_required": false
}}"""),
    ("human", """Analyse this supplier:
Supplier Name: {supplier_name}
Country: {country}
Industry: {industry}
Annual Contract Value: {contract_value}
Years as Supplier: {years_as_supplier}
Recent Issues: {recent_issues}
Additional Info: {additional_info}
""")
])

supplier_risk_chain = prompt | llm | StrOutputParser()


def analyse_supplier_risk(
    supplier_name: str,
    country: str,
    industry: str,
    contract_value: str,
    years_as_supplier: str,
    recent_issues: str = "None reported",
    additional_info: str = "None"
) -> dict:
    """Analyse a supplier and return a full risk score."""

    print(f"\n🏭 Analysing supplier: {supplier_name}...")

    result = supplier_risk_chain.invoke({
        "supplier_name": supplier_name,
        "country": country,
        "industry": industry,
        "contract_value": contract_value,
        "years_as_supplier": years_as_supplier,
        "recent_issues": recent_issues,
        "additional_info": additional_info
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
    result = analyse_supplier_risk(
        supplier_name="TechParts China Co.",
        country="China",
        industry="Electronics Manufacturing",
        contract_value="$2.5 Million/year",
        years_as_supplier="3 years",
        recent_issues="2 delayed shipments in Q4 2025, quality complaints on batch #447",
        additional_info="Single source supplier for critical components"
    )

    print("\n📊 SUPPLIER RISK ANALYSIS RESULT:")
    print(json.dumps(result, indent=2))

    if "error" not in result:
        score = result.get("overall_risk_score", 0)
        level = result.get("risk_level", "Unknown")
        alert = result.get("alert_required", False)
        print(f"\n{'='*45}")
        print(f"Supplier   : {result.get('supplier_name')}")
        print(f"Risk Score : {score}/100")
        print(f"Risk Level : {level}")
        print(f"Alert      : {'🚨 YES' if alert else '✅ No'}")
        print(f"Action     : {result.get('recommendation')}")
        print(f"{'='*45}")
