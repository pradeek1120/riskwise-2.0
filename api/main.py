import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv

from agents.supplier_risk_agent import analyse_supplier_risk
from agents.tariff_agent import analyse_tariff_impact
from agents.geopolitical_agent import analyse_geopolitical_risk
from agents.mitigation_agent import generate_mitigation_plan
from agents.compliance_agent import generate_compliance_report
from orchestration.langgraph_flow import build_riskwise_graph

load_dotenv()

# ── FastAPI App
app = FastAPI(
    title="RiskWise 2.0 API",
    description="Supply Chain Risk & Tariff Intelligence Platform — Microsoft AI Dev Days 2026",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# ── CORS (allows Streamlit to call this API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request Models
class SupplierRequest(BaseModel):
    supplier_name: str
    country: str
    industry: str
    contract_value: str
    years_as_supplier: str
    recent_issues: Optional[str] = "None reported"
    additional_info: Optional[str] = "None"


class TariffRequest(BaseModel):
    country: str
    product_category: str
    current_tariff: str
    new_tariff: str
    contract_value: str
    current_suppliers: Optional[str] = "Not specified"
    context: Optional[str] = "Trade policy update 2026"


class GeoRequest(BaseModel):
    country: str
    industry: Optional[str] = "General Manufacturing"
    context: Optional[str] = "Current global situation 2026"
    dependency: Optional[str] = "Medium"


class MitigationRequest(BaseModel):
    risk_type: str
    supplier: str
    risk_score: int
    country: Optional[str] = "Unknown"
    contract_value: Optional[str] = "Unknown"
    details: Optional[str] = "Risk detected by AI agents"
    geo_risk_level: Optional[str] = "Unknown"
    tariff_impact: Optional[str] = "Unknown"


class ComplianceRequest(BaseModel):
    company: str
    period: str
    total_suppliers: Optional[int] = 8
    high_risk_suppliers: Optional[int] = 3
    risk_events: Optional[str] = "None"
    mitigation_actions: Optional[str] = "None"
    financial_exposure: Optional[str] = "Unknown"
    context: Optional[str] = "Standard quarterly review"


class FullAnalysisRequest(BaseModel):
    country: str
    supplier_name: str
    product_category: str
    contract_value: str
    current_tariff: Optional[str] = "7.5%"
    new_tariff: Optional[str] = "25%"


# ── Routes

@app.get("/")
def root():
    return {
        "message": "🛡️ RiskWise 2.0 API is running!",
        "version": "2.0.0",
        "docs": "/docs",
        "endpoints": [
            "/analyse/supplier",
            "/analyse/tariff",
            "/analyse/geopolitical",
            "/analyse/mitigation",
            "/analyse/compliance",
            "/analyse/full"
        ]
    }


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "RiskWise 2.0"}


@app.post("/analyse/supplier")
async def analyse_supplier(req: SupplierRequest):
    """Analyse a supplier's risk score across 12 dimensions."""
    try:
        result = analyse_supplier_risk(
            supplier_name=req.supplier_name,
            country=req.country,
            industry=req.industry,
            contract_value=req.contract_value,
            years_as_supplier=req.years_as_supplier,
            recent_issues=req.recent_issues,
            additional_info=req.additional_info
        )
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyse/tariff")
async def analyse_tariff(req: TariffRequest):
    """Analyse tariff change and calculate financial impact."""
    try:
        result = analyse_tariff_impact(
            country=req.country,
            product_category=req.product_category,
            current_tariff=req.current_tariff,
            new_tariff=req.new_tariff,
            contract_value=req.contract_value,
            current_suppliers=req.current_suppliers,
            context=req.context
        )
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyse/geopolitical")
async def analyse_geo(req: GeoRequest):
    """Analyse geopolitical risk for a country."""
    try:
        result = analyse_geopolitical_risk(
            country=req.country,
            industry=req.industry,
            context=req.context,
            dependency=req.dependency
        )
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyse/mitigation")
async def analyse_mitigation(req: MitigationRequest):
    """Generate mitigation plan for detected risk."""
    try:
        result = generate_mitigation_plan(
            risk_type=req.risk_type,
            supplier=req.supplier,
            risk_score=req.risk_score,
            country=req.country,
            contract_value=req.contract_value,
            details=req.details,
            geo_risk_level=req.geo_risk_level,
            tariff_impact=req.tariff_impact
        )
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyse/compliance")
async def analyse_compliance(req: ComplianceRequest):
    """Generate compliance and risk report."""
    try:
        result = generate_compliance_report(
            company=req.company,
            period=req.period,
            total_suppliers=req.total_suppliers,
            high_risk_suppliers=req.high_risk_suppliers,
            risk_events=req.risk_events,
            mitigation_actions=req.mitigation_actions,
            financial_exposure=req.financial_exposure,
            context=req.context
        )
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyse/full")
async def full_pipeline_analysis(req: FullAnalysisRequest):
    """Run the complete 5-agent LangGraph pipeline."""
    try:
        graph = build_riskwise_graph()
        result = graph.invoke({
            "country": req.country,
            "supplier_name": req.supplier_name,
            "product_category": req.product_category,
            "contract_value": req.contract_value,
            "current_tariff": req.current_tariff,
            "new_tariff": req.new_tariff,
            "alert_required": False,
            "pipeline_log": [],
            "geo_risk": None,
            "tariff_risk": None,
            "supplier_risk": None,
            "mitigation_plan": None,
            "compliance_report": None,
            "overall_risk_score": None
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
