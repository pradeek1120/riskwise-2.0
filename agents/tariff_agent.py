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
    temperature=0.1
)

prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a global trade and tariff analyst.
Analyse tariff changes and calculate financial impact on supply chain contracts.

ALWAYS respond ONLY in this exact JSON format, no extra text:
{{
  "country": "name",
  "product_category": "category",
  "current_tariff_rate": "X%",
  "new_tariff_rate": "X%",
  "tariff_change": "+X%",
  "annual_contract_value": "$X",
  "financial_impact": {{
    "additional_annual_cost": "$X",
    "additional_monthly_cost": "$X",
    "cost_increase_percentage": "X%"
  }},
  "risk_level": "Low/Medium/High/Critical",
  "affected_products": ["product1", "product2"],
  "alternative_countries": [
    {{
      "country": "name",
      "tariff_rate": "X%",
      "estimated_savings": "$X/year",
      "feasibility": "High/Medium/Low"
    }}
  ],
  "recommendation": "action here",
  "urgent_action_required": false
}}"""),
    ("human", """Analyse this tariff situation:
Country: {country}
Product Category: {product_category}
Current Tariff Rate: {current_tariff}
New Tariff Rate: {new_tariff}
Annual Contract Value: {contract_value}
Current Suppliers: {current_suppliers}
Context: {context}
""")
])

tariff_chain = prompt | llm | StrOutputParser()


def analyse_tariff_impact(
    country: str,
    product_category: str,
    current_tariff: str,
    new_tariff: str,
    contract_value: str,
    current_suppliers: str = "Not specified",
    context: str = "General trade update"
) -> dict:
    """Analyse tariff change and calculate full financial impact."""

    print(f"\n📊 Analysing tariff impact: {product_category} from {country}...")

    result = tariff_chain.invoke({
        "country": country,
        "product_category": product_category,
        "current_tariff": current_tariff,
        "new_tariff": new_tariff,
        "contract_value": contract_value,
        "current_suppliers": current_suppliers,
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
    result = analyse_tariff_impact(
        country="China",
        product_category="Electronics & Semiconductors",
        current_tariff="7.5%",
        new_tariff="25%",
        contract_value="$5,000,000",
        current_suppliers="TechParts China Co., ChipMakers Shanghai",
        context="New US-China trade restrictions announced March 2026"
    )

    print("\n💰 TARIFF IMPACT ANALYSIS:")
    print(json.dumps(result, indent=2))

    if "error" not in result:
        impact = result.get("financial_impact", {})
        alts = result.get("alternative_countries", [])
        urgent = result.get("urgent_action_required", False)

        print(f"\n{'='*45}")
        print(f"Country       : {result.get('country')}")
        print(f"Tariff Change : {result.get('tariff_change')}")
        print(f"Extra Cost    : {impact.get('additional_annual_cost')}/year")
        print(f"Risk Level    : {result.get('risk_level')}")
        print(f"Urgent Action : {'🚨 YES' if urgent else '✅ No'}")
        if alts:
            top = alts[0]
            print(f"\n🌍 Best Alternate: {top['country']} at {top['tariff_rate']}")
            print(f"   Saves: {top['estimated_savings']}")
        print(f"{'='*45}")
