"""
CAM (Credit Appraisal Memo) API - Generate comprehensive credit appraisal memos and reports.
"""
import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response, HTMLResponse
from app.core.llm_chain import generate_cam_explanation, generate_credit_risk_summary
from app.core.cam_generator import generate_cam_document, generate_cam_section
from app.models.credit import CAMSection, RiskIndicator

router = APIRouter()

_cam_store: list[dict] = []


class CAMRequest(BaseModel):
    cin: str
    application_id: Optional[str] = None
    risk_indicators: Optional[list[dict]] = None


@router.post("/generate")
async def generate_cam(body: CAMRequest):
    """Generate a Credit Appraisal Memo for a loan application."""
    
    # Auto-generate application_id if not provided
    if not body.application_id:
        body.application_id = f"CAM-{body.cin}-{uuid.uuid4().hex[:8]}"
    
    # Use empty list if no risk indicators provided
    if body.risk_indicators is None:
        body.risk_indicators = []
    
    try:
        # Convert risk indicator dicts to RiskIndicator objects
        indicators = [RiskIndicator(**ri) for ri in body.risk_indicators]
        
        # Generate LLM-powered credit risk explanation
        explanation = await generate_cam_explanation(indicators)
        
        # Generate comprehensive risk summary
        risk_summary = await generate_credit_risk_summary(
            cin=body.cin,
            risk_indicators=indicators
        )
        
    except Exception as e:
        explanation = f"Unable to generate AI explanation: {str(e)}"
        risk_summary = "Risk summary generation failed."

    # Build CAM document
    cam = {
        "id": str(uuid.uuid4()),
        "application_id": body.application_id,
        "cin": body.cin,
        "sections": [
            {
                "title": "Executive Summary",
                "content": explanation,
                "order": 1,
            },
            {
                "title": "Company Profile",
                "content": f"[Company profile for CIN: {body.cin}]",
                "order": 2,
            },
            {
                "title": "Financial Analysis",
                "content": risk_summary,
                "order": 3,
            },
            {
                "title": "Five C's Assessment",
                "content": "[Character, Capacity, Capital, Collateral, Conditions scoring]",
                "order": 4,
            },
            {
                "title": "Risk Assessment",
                "content": f"Identified {len(indicators)} risk indicators",
                "order": 5,
            },
            {
                "title": "Credit Recommendation",
                "content": _get_recommendation(indicators),
                "order": 6,
            },
        ],
        "risk_indicators": [ri.model_dump() for ri in indicators],
        "generated_at": datetime.now().isoformat(),
    }

    _cam_store.append(cam)
    return cam


@router.get("/list")
async def list_cams(cin: str = None):
    """List all generated CAMs with optional CIN filter."""
    cams = _cam_store
    if cin:
        cams = [c for c in cams if c["cin"] == cin]
    
    return {
        "total": len(cams),
        "cams": [{
            "id": c["id"],
            "application_id": c["application_id"],
            "cin": c["cin"],
            "generated_at": c["generated_at"],
        } for c in cams]
    }


@router.get("/{cam_id}")
async def get_cam(cam_id: str):
    """Get detailed CAM by ID."""
    for cam in _cam_store:
        if cam["id"] == cam_id:
            return cam
    raise HTTPException(status_code=404, detail=f"CAM {cam_id} not found")


@router.get("/export/{cam_id}/pdf")
async def export_cam_pdf(cam_id: str):
    """Export CAM as PDF document."""
    cam = None
    for c in _cam_store:
        if c["id"] == cam_id:
            cam = c
            break
    
    if not cam:
        raise HTTPException(status_code=404, detail=f"CAM {cam_id} not found")
    
    try:
        pdf_bytes = generate_cam_document(
            application_id=cam["application_id"],
            cin=cam["cin"],
            sections=[CAMSection(**s) for s in cam["sections"]],
            risk_indicators=[RiskIndicator(**ri) for ri in cam["risk_indicators"]],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {e}")

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=CAM_{cam['application_id']}.pdf"},
    )


@router.get("/export/{cam_id}/html")
async def export_cam_html(cam_id: str):
    """Export CAM as HTML document."""
    cam = None
    for c in _cam_store:
        if c["id"] == cam_id:
            cam = c
            break
    
    if not cam:
        raise HTTPException(status_code=404, detail=f"CAM {cam_id} not found")
    
    # Generate HTML from sections
    html_parts = [
        f"<html><head><title>CAM - {cam['application_id']}</title>",
        "<style>body{font-family:Arial,sans-serif;margin:40px;} h1{color:#2c3e50;} h2{color:#34495e;border-bottom:2px solid #3498db;padding-bottom:10px;} .section{margin:30px 0;}</style>",
        "</head><body>",
        f"<h1>Credit Appraisal Memo</h1>",
        f"<p><strong>Application ID:</strong> {cam['application_id']}</p>",
        f"<p><strong>CIN:</strong> {cam['cin']}</p>",
        f"<p><strong>Generated:</strong> {cam['generated_at']}</p>",
        "<hr>",
    ]
    
    for section in sorted(cam["sections"], key=lambda s: s["order"]):
        html_parts.append(f"<div class='section'>")
        html_parts.append(f"<h2>{section['title']}</h2>")
        html_parts.append(f"<p>{section['content']}</p>")
        html_parts.append("</div>")
    
    html_parts.append("</body></html>")
    
    return HTMLResponse(content="".join(html_parts))


@router.post("/explain-indicator")
async def explain_risk_indicator(risk_indicator: dict):
    """Generate detailed explanation for a specific risk indicator using LLM."""
    try:
        indicator = RiskIndicator(**risk_indicator)
        explanation = await generate_cam_explanation([indicator])
        return {
            "indicator_type": indicator.indicator_type,
            "severity": indicator.severity,
            "explanation": explanation,
            "recommendation": _get_recommendation([indicator]),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Explanation generation failed: {str(e)}")


def _get_recommendation(indicators: list[RiskIndicator]) -> str:
    """Generate recommendation based on risk indicators."""
    critical_count = sum(1 for i in indicators if i.severity == "CRITICAL")
    high_count = sum(1 for i in indicators if i.severity == "HIGH")
    
    if critical_count > 2:
        return "REJECT: Multiple critical risk indicators detected. Loan application should be declined."
    elif critical_count == 1 or high_count > 3:
        return "CONDITIONAL APPROVAL: Significant risks identified. Approve only with enhanced monitoring, reduced loan amount, or additional collateral."
    elif high_count <= 1:
        return "APPROVE: Risk profile is acceptable. Proceed with standard loan terms."
    else:
        return "CONDITIONAL APPROVAL: Moderate risks detected. Consider reduced loan amount or enhanced documentation."
