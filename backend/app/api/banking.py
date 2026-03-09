"""
Banking analysis API - bank statement analysis, cashflow metrics, suspicious patterns.
"""
from fastapi import APIRouter, HTTPException, Query, Body
from app.core.bank_analyzer import (
    parse_bank_statement,
    calculate_cashflow_metrics,
    detect_suspicious_patterns,
    calculate_banking_conduct_score,
)

router = APIRouter()


@router.post("/analyze")
async def analyze_bank_statement(
    cin: str = Query(...),
    year: str = Query(...),
    transactions: list[dict] = Body(...),
):
    """Analyze bank statement transactions for credit assessment."""
    try:
        # Calculate cashflow metrics
        cashflow = calculate_cashflow_metrics(transactions)
        
        # Detect suspicious patterns
        suspicious = detect_suspicious_patterns(transactions)
        
        # Calculate banking conduct score
        conduct_score = calculate_banking_conduct_score(transactions, suspicious)
        
        return {
            "cin": cin,
            "year": year,
            "total_transactions": len(transactions),
            "cashflow_metrics": cashflow,
            "suspicious_patterns": suspicious,
            "banking_conduct_score": conduct_score,
            "risk_level": "LOW" if conduct_score >= 75 else 
                         "MEDIUM" if conduct_score >= 50 else 
                         "HIGH" if conduct_score >= 25 else "CRITICAL",
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bank statement analysis failed: {str(e)}")


@router.post("/cashflow")
async def get_cashflow_analysis(
    cin: str = Query(...),
    transactions: list[dict] = Body(...),
):
    """Calculate detailed cashflow metrics from bank transactions."""
    try:
        metrics = calculate_cashflow_metrics(transactions)
        return {
            "cin": cin,
            "metrics": metrics,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cashflow calculation failed: {str(e)}")


@router.post("/suspicious-patterns")
async def detect_patterns(
    cin: str = Query(...),
    transactions: list[dict] = Body(...),
):
    """Detect suspicious patterns in bank transactions (round-tripping, circular transactions, etc.)."""
    try:
        patterns = detect_suspicious_patterns(transactions)
        return {
            "cin": cin,
            "patterns_found": len(patterns),
            "patterns": patterns,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pattern detection failed: {str(e)}")


@router.get("/conduct-score")
async def get_conduct_score(cin: str):
    """Get banking conduct score for a company (from Neo4j stored data)."""
    # [STUB] This should query Neo4j for stored bank statement data
    try:
        # In production, fetch transactions from Neo4j
        # For now, return a stub response
        return {
            "cin": cin,
            "conduct_score": 75,
            "score_breakdown": {
                "cheque_bounce_penalty": 0,
                "od_limit_utilization": -5,
                "average_balance_bonus": 10,
                "transaction_regularity": 20,
            },
            "red_flags": [],
            "green_flags": [
                "Regular transaction patterns",
                "Consistent monthly revenue deposits",
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conduct score fetch failed: {str(e)}")


@router.post("/working-capital")
async def calculate_working_capital(
    cin: str = Query(...),
    transactions: list[dict] = Body(...),
):
    """Calculate working capital cycle metrics from bank transactions."""
    try:
        metrics = calculate_cashflow_metrics(transactions)
        
        # Derived working capital metrics
        avg_monthly_revenue = metrics.get("average_monthly_inflow", 0)
        avg_monthly_expenses = metrics.get("average_monthly_outflow", 0)
        
        working_capital_requirement = avg_monthly_expenses * 0.25  # 3 months runway
        operating_cycle_days = 90  # [STUB] Should calculate from receivables + inventory
        
        return {
            "cin": cin,
            "average_monthly_revenue": avg_monthly_revenue,
            "average_monthly_expenses": avg_monthly_expenses,
            "net_monthly_cashflow": avg_monthly_revenue - avg_monthly_expenses,
            "working_capital_requirement": working_capital_requirement,
            "operating_cycle_days": operating_cycle_days,
            "cashflow_adequacy": "ADEQUATE" if avg_monthly_revenue > avg_monthly_expenses else "INADEQUATE",
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Working capital calculation failed: {str(e)}")


@router.post("/revenue-verification")
async def verify_revenue(
    cin: str = Query(...),
    itr_revenue: float = Query(...),
    bank_deposits: float = Query(...),
):
    """Cross-verify revenue declared in ITR vs actual bank deposits."""
    try:
        variance_pct = abs(itr_revenue - bank_deposits) / itr_revenue * 100 if itr_revenue > 0 else 100
        
        status = "MATCHED" if variance_pct < 10 else "MINOR_VARIANCE" if variance_pct < 25 else "MAJOR_DISCREPANCY"
        
        return {
            "cin": cin,
            "itr_revenue": itr_revenue,
            "bank_deposits": bank_deposits,
            "variance_amount": abs(itr_revenue - bank_deposits),
            "variance_percentage": round(variance_pct, 2),
            "verification_status": status,
            "risk_level": "LOW" if status == "MATCHED" else "MEDIUM" if status == "MINOR_VARIANCE" else "HIGH",
            "recommendation": (
                "Revenue figures are consistent." if status == "MATCHED" else
                "Minor variance detected. Request clarification." if status == "MINOR_VARIANCE" else
                "Major discrepancy detected. Investigate for revenue inflation or tax evasion."
            ),
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Revenue verification failed: {str(e)}")
