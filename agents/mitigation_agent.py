import os
import json
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
    temperature=0.2
)

prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a supply chain mitigation specialist.
When risk is detected, provide immediate, actionable mitigation strategies.

ALWAYS respond ONLY in this exact JSON format, no extra text:
{{
  "risk_type": "type of risk",
  "severity": "Low/Medium/High/Critical",
  "immediate_actions": [
    "Immediate action 1",
    "Immediate action 2",
    "Immediate action 3"
  ],
  "short_term_actions": [
    "Action within 1 week",
    "Action within 2 weeks"
  ],
  "long_term_actions": [
    "Strategic action 1",
    "Strategic action 2"
  ],
  "alternate_suppliers": [
    {{
      "name": "Supplier Name",
      "country": "Country",
      "lead_time": "X days",
      "estimated_cost_difference": "+/-X%",
      "qualification_status": "Qualified/Needs Evaluation"
    }}
  ],
  "estimated_cost_to_mitigate": "$X",
  "estimated_time_to_resolve": "X days/weeks",
  "draft_po_required": false,
  "escalate_to_management": false,
  "risk_reduction_after_mitigation": "X%"
}}"""),
    ("human", """Risk Detected - Generate Mitigation Plan:
Risk Type: {risk_type}
Affected Supplier: {supplier}
Current Risk Score: {risk_score}/100
Country: {country}
Contract Value: {contract_value}
Risk Details: {details}
Current Geo Risk Level: {geo_risk_level}
Current Tariff Impact: {tariff_impact}
""")
])

mitigation_chain = prompt | llm | StrOutputParser()


def generate_mitigation_plan(
    risk_type: str,
    supplier: str,
    risk_score: int,
    country: str = "Unknown",
    contract_value: str = "Unknown",
    details: str = "Risk detected by AI agents",
    geo_risk_level: str = "Unknown",
    tariff_impact: str = "Unknown"
) -> dict:
    """Generate a complete mitigation plan when risk is detected."""

    print(f"\n🔄 Generating mitigation plan for {supplier} (Score: {risk_score}/100)...")

    result = mitigation_chain.invoke({
        "risk_type": risk_type,
        "supplier": supplier,
        "risk_score": risk_score,
        "country": country,
        "contract_value": contract_value,
        "details": details,
        "geo_risk_level": geo_risk_level,
        "tariff_impact": tariff_impact
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
    result = generate_mitigation_plan(
        risk_type="Combined Geopolitical + Tariff Risk",
        supplier="TechParts China Co.",
        risk_score=82,
        country="China",
        contract_value="$2.5M/year",
        details="New 25% tariff announced + political tensions. Critical single-source supplier for electronics.",
        geo_risk_level="High (Score: 75/100)",
        tariff_impact="$437,500 additional annual cost"
    )

    print("\n🔄 MITIGATION PLAN:")
    print(json.dumps(result, indent=2))

    if "error" not in result:
        actions = result.get("immediate_actions", [])
        alts = result.get("alternate_suppliers", [])
        escalate = result.get("escalate_to_management", False)

        print(f"\n{'='*45}")
        print(f"Severity     : {result.get('severity')}")
        print(f"Resolve In   : {result.get('estimated_time_to_resolve')}")
        print(f"Mitigation $ : {result.get('estimated_cost_to_mitigate')}")
        print(f"Risk Reduction: {result.get('risk_reduction_after_mitigation')}")
        print(f"Escalate     : {'🚨 YES' if escalate else '✅ No'}")
        print(f"\n🎯 Top Immediate Action:")
        if actions:
            print(f"   → {actions[0]}")
        if alts:
            print(f"\n🏭 Best Alternate Supplier: {alts[0]['name']} ({alts[0]['country']})")
        print(f"{'='*45}")
