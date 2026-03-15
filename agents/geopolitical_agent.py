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
    ("system", """You are a geopolitical risk analyst specialising in supply chain risk.
Score country-level risk for supply chains from 0 to 100.

Scoring:
- 0-30   = Stable (Low Risk)
- 31-60  = Moderate Risk
- 61-80  = High Risk
- 81-100 = Critical Risk

ALWAYS respond ONLY in this exact JSON format, no extra text:
{{
  "country": "name",
  "risk_score": 0,
  "risk_level": "Low/Medium/High/Critical",
  "stability_index": 0,
  "key_risks": ["risk1", "risk2", "risk3"],
  "sanctions_exposure": "None/Low/Medium/High",
  "trade_disruption_probability": "X%",
  "political_stability": "Stable/Unstable/Volatile",
  "infrastructure_reliability": "High/Medium/Low",
  "currency_risk": "Low/Medium/High",
  "recommended_action": "action here",
  "alert_required": false,
  "monitoring_frequency": "Daily/Weekly/Monthly"
}}"""),
    ("human", """Analyse geopolitical supply chain risk for:
Country: {country}
Industry Context: {industry}
Current Events: {context}
Supply Chain Dependency Level: {dependency}
""")
])

geo_chain = prompt | llm | StrOutputParser()


def analyse_geopolitical_risk(
    country: str,
    industry: str = "General Manufacturing",
    context: str = "Current global situation 2026",
    dependency: str = "Medium"
) -> dict:
    """Analyse geopolitical risk for a country."""

    print(f"\n🌍 Analysing geopolitical risk: {country}...")

    result = geo_chain.invoke({
        "country": country,
        "industry": industry,
        "context": context,
        "dependency": dependency
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


def scan_all_countries(countries: list) -> list:
    """Scan multiple countries and return risk scores."""
    results = []
    print(f"\n🌐 Scanning {len(countries)} countries...\n")
    for country in countries:
        result = analyse_geopolitical_risk(country)
        results.append(result)
        if "error" not in result:
            score = result.get("risk_score", 0)
            level = result.get("risk_level", "Unknown")
            alert = "🚨" if result.get("alert_required") else "✅"
            print(f"{alert} {country:20} Score: {score}/100  Level: {level}")
    return results


if __name__ == "__main__":
    # Test single country
    result = analyse_geopolitical_risk(
        country="China",
        industry="Electronics Manufacturing",
        context="US-China trade tensions, tariff increases in 2026",
        dependency="High - Single source for critical components"
    )

    print("\n🌍 GEOPOLITICAL RISK ANALYSIS:")
    print(json.dumps(result, indent=2))

    # Test multiple countries
    print("\n" + "="*50)
    print("MULTI-COUNTRY RISK SCAN")
    print("="*50)
    countries = ["China", "Taiwan", "Russia", "India", "Vietnam", "Germany"]
    scan_all_countries(countries)
