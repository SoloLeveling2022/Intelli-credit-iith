from datetime import datetime
from fastapi import APIRouter, Query, HTTPException, Body
from app.core.credit_analyzer import analyze_company
from app.core.credit_engine import recommend_decision, generate_five_cs_analysis, calculate_loan_amount, determine_interest_rate
from app.core.graph_db import get_graph_data, search_graph, find_shell_companies, get_company_network
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

# In-memory store for appraisal results (for demo; use DB in production)
# Structure: { application_id: { "result": {...}, "timestamp": str, "decision": str } }
_appraisal_store: dict[str, dict] = {}


class AppraisalRequest(BaseModel):
    cin: str
    application_id: Optional[str] = None
    loan_amount_requested: Optional[float] = None
    loan_purpose: str = "Working Capital"
    force: bool = False


@router.post("")
async def trigger_appraisal(body: AppraisalRequest):
    """Trigger credit appraisal for a loan application."""
    # Auto-generate application_id if not provided
    if not body.application_id:
        import uuid
        body.application_id = f"APP-{body.cin}-{uuid.uuid4().hex[:8]}"
    
    # Use default loan amount if not provided (1 crore)
    if not body.loan_amount_requested:
        body.loan_amount_requested = 10000000.0
    
    application_id = body.application_id
    force = body.force

    # Return cached results if available and not forced
    if not force and application_id in _appraisal_store:
        cached = _appraisal_store[application_id]
        return {
            "status": "cached",
            "application_id": application_id,
            "decision": cached["decision"],
            "last_run": cached["timestamp"],
            "result": cached["result"],
        }

    try:
        # Run credit analysis
        risk_indicators = analyze_company(body.cin)
        
        # Generate Five C's analysis
        five_cs = generate_five_cs_analysis(
            cin=body.cin,
            risk_indicators=risk_indicators
        )
        
        # Calculate loan parameters
        loan_amount = calculate_loan_amount(
            cin=body.cin,
            requested_amount=body.loan_amount_requested
        )
        
        interest_rate = determine_interest_rate(five_cs.overall_score)
        
        # Make credit decision
        decision = recommend_decision(
            five_cs_score=five_cs.overall_score,
            risk_indicators=risk_indicators,
            loan_amount=loan_amount,
            requested_amount=body.loan_amount_requested
        )
        
        result = {
            "application_id": application_id,
            "cin": body.cin,
            "requested_amount": body.loan_amount_requested,
            "approved_amount": loan_amount,
            "interest_rate": interest_rate,
            "five_cs_score": five_cs.overall_score,
            "five_cs_breakdown": {
                "character": five_cs.character,
                "capacity": five_cs.capacity,
                "capital": five_cs.capital,
                "collateral": five_cs.collateral,
                "conditions": five_cs.conditions,
            },
            "risk_indicators": [r.model_dump() for r in risk_indicators],
            "decision": decision["decision"],
            "decision_reason": decision["reason"],
            "conditions": decision.get("conditions", []),
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Credit appraisal failed: {str(e)}")

    timestamp = datetime.now().isoformat()
    _appraisal_store[application_id] = {
        "result": result,
        "timestamp": timestamp,
        "decision": result["decision"],
    }
    
    return {
        "status": "completed",
        "application_id": application_id,
        "decision": result["decision"],
        "last_run": timestamp,
        "result": result,
    }


@router.get("/status")
async def get_appraisal_status(application_id: str):
    """Check if appraisal results exist for an application."""
    if application_id in _appraisal_store:
        cached = _appraisal_store[application_id]
        return {
            "has_results": True,
            "application_id": application_id,
            "decision": cached["decision"],
            "last_run": cached["timestamp"],
        }
    return {"has_results": False, "application_id": application_id}


@router.get("/results")
async def get_results(
    application_id: str = Query(None),
    cin: str = Query(None),
    decision: str = Query(None),  # APPROVED, REJECTED, CONDITIONAL
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
):
    """Get appraisal results with filtering."""
    results = list(_appraisal_store.values())
    
    if application_id:
        results = [r for r in results if r["result"]["application_id"] == application_id]
    if cin:
        results = [r for r in results if r["result"]["cin"] == cin]
    if decision:
        results = [r for r in results if r["decision"] == decision]

    total = len(results)
    start = (page - 1) * page_size
    end = start + page_size

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "results": [r["result"] for r in results[start:end]],
    }


@router.get("/results/{application_id}")
async def get_single_result(application_id: str):
    """Get detailed results for a specific application."""
    if application_id not in _appraisal_store:
        raise HTTPException(status_code=404, detail=f"Application {application_id} not found")
    return _appraisal_store[application_id]["result"]


@router.get("/graph/nodes")
async def get_graph_nodes(limit: int = Query(200, ge=1, le=1000)):
    """Get company network graph nodes."""
    try:
        return get_graph_data(limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch graph data: {str(e)}")


@router.get("/graph/search")
async def search_graph_nodes(q: str):
    """Search companies and promoters in the graph."""
    if not q or len(q) < 2:
        raise HTTPException(status_code=400, detail="Search query must be at least 2 characters")
    try:
        return search_graph(q)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/graph/shell-companies")
async def get_shell_companies():
    """Detect potential shell companies via circular trading patterns."""
    try:
        return find_shell_companies()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Shell company detection failed: {str(e)}")


@router.get("/graph/company-network")
async def get_company_network_endpoint(cin: str):
    """Get the subgraph centered on a specific company — shows related companies, promoters, suppliers."""
    if not cin or len(cin) < 2:
        raise HTTPException(status_code=400, detail="CIN is required")
    try:
        return get_company_network(cin)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Company network fetch failed: {str(e)}")


@router.post("/quick-score")
async def quick_credit_score(cin: str, requested_amount: float):
    """Quick credit scoring without full appraisal — for lead qualification."""
    try:
        risk_indicators = analyze_company(cin)
        five_cs = generate_five_cs_analysis(cin=cin, risk_indicators=risk_indicators)
        
        return {
            "cin": cin,
            "overall_score": five_cs.overall_score,
            "risk_level": "LOW" if five_cs.overall_score >= 75 else 
                         "MEDIUM" if five_cs.overall_score >= 50 else 
                         "HIGH" if five_cs.overall_score >= 25 else "CRITICAL",
            "estimated_approval_amount": calculate_loan_amount(cin=cin, requested_amount=requested_amount),
            "estimated_interest_rate": determine_interest_rate(five_cs.overall_score),
            "red_flags": len([r for r in risk_indicators if r.severity in ["CRITICAL", "HIGH"]]),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quick score failed: {str(e)}")
