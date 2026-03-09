"""
Dashboard statistics API - credit appraisal metrics and KPIs.
"""
from fastapi import APIRouter, Query
from app.core.graph_db import get_driver
from app.api.appraisal import _appraisal_store
from app.core.risk_model import calculate_all_company_risks

router = APIRouter()


@router.get("/dashboard")
async def get_dashboard_stats():
    """Main dashboard KPIs for credit appraisal system."""
    driver = get_driver()
    with driver.session() as session:
        companies = session.run("MATCH (c:Company) RETURN count(c) AS c").single()["c"]
        promoters = session.run("MATCH (p:Promoter) RETURN count(p) AS c").single()["c"]
        
        # Loan applications
        applications = session.run("MATCH (la:LoanApplication) RETURN count(la) AS c").single()["c"]
        
        # Total loan amount
        total_loan_amount = session.run(
            "MATCH (la:LoanApplication) RETURN coalesce(sum(la.approved_amount), 0) AS v"
        ).single()["v"]
        
        # Average ticket size
        avg_loan_amount = session.run(
            "MATCH (la:LoanApplication) WHERE la.approved_amount > 0 RETURN coalesce(avg(la.approved_amount), 0) AS v"
        ).single()["v"]
        
        # Financial documents count
        financial_docs = session.run(
            "MATCH (fd:FinancialDocument) RETURN count(fd) AS c"
        ).single()["c"]
        
        # Bank statements count
        bank_statements = session.run(
            "MATCH (bs:BankStatement) RETURN count(bs) AS c"
        ).single()["c"]
        
        # ITR count
        itr_count = session.run(
            "MATCH (itr:ITR) RETURN count(itr) AS c"
        ).single()["c"]
        
        # Litigation cases
        litigation_count = session.run(
            "MATCH (lit:Litigation) RETURN count(lit) AS c"
        ).single()["c"]

    # Aggregate appraisal results from in-memory store
    all_appraisals = list(_appraisal_store.values())
    total_appraisals = len(all_appraisals)

    # Decision breakdown
    decision_breakdown = {
        "APPROVED": 0,
        "REJECTED": 0,
        "CONDITIONAL": 0,
    }
    for appraisal in all_appraisals:
        decision = appraisal.get("decision", "UNKNOWN")
        if decision in decision_breakdown:
            decision_breakdown[decision] += 1

    # Average credit score
    credit_scores = [a["result"].get("five_cs_score", 0) for a in all_appraisals if "result" in a]
    avg_credit_score = sum(credit_scores) / len(credit_scores) if credit_scores else 0

    # High risk companies count
    try:
        companies_risk = calculate_all_company_risks()
        high_risk_companies = sum(1 for c in companies_risk if c["risk_level"] in ("HIGH", "CRITICAL"))
    except Exception:
        high_risk_companies = 0

    # Approval rate
    approval_rate = (decision_breakdown["APPROVED"] / total_appraisals * 100) if total_appraisals > 0 else 0

    return {
        "total_companies": companies,
        "total_promoters": promoters,
        "total_applications": applications,
        "total_appraisals_completed": total_appraisals,
        "total_loan_amount_approved": round(total_loan_amount, 2),
        "average_loan_amount": round(avg_loan_amount, 2),
        "average_credit_score": round(avg_credit_score, 2),
        "approval_rate": round(approval_rate, 2),
        "high_risk_companies": high_risk_companies,
        "financial_documents": financial_docs,
        "bank_statements": bank_statements,
        "itr_filed": itr_count,
        "litigation_cases": litigation_count,
        "decision_breakdown": decision_breakdown,
    }


@router.get("/appraisal-summary")
async def get_appraisal_summary():
    """Appraisal decision summary and trends."""
    all_appraisals = list(_appraisal_store.values())
    
    breakdown = {
        "APPROVED": {"count": 0, "total_amount": 0.0, "avg_score": 0.0},
        "REJECTED": {"count": 0, "total_amount": 0.0, "avg_score": 0.0},
        "CONDITIONAL": {"count": 0, "total_amount": 0.0, "avg_score": 0.0},
    }
    
    for appraisal in all_appraisals:
        decision = appraisal.get("decision", "UNKNOWN")
        if decision in breakdown:
            result = appraisal.get("result", {})
            breakdown[decision]["count"] += 1
            breakdown[decision]["total_amount"] += result.get("approved_amount", 0)
    
    # Calculate averages
    for key in breakdown:
        if breakdown[key]["count"] > 0:
            breakdown[key]["avg_amount"] = round(breakdown[key]["total_amount"] / breakdown[key]["count"], 2)
        breakdown[key]["total_amount"] = round(breakdown[key]["total_amount"], 2)
    
    return {"breakdown": breakdown}


@router.get("/top-risky-companies")
async def get_top_risky_companies(limit: int = Query(10, ge=1, le=50)):
    """Get top risky companies by credit score."""
    try:
        companies = calculate_all_company_risks()
        # Sort by risk score (higher = riskier)
        top = sorted([c for c in companies if c.get("risk_score", 0) > 0], 
                    key=lambda x: x["risk_score"], reverse=True)[:limit]
    except Exception:
        top = []
    return {"top_risky_companies": top}


@router.get("/portfolio-analysis")
async def get_portfolio_analysis():
    """Analyze loan portfolio by industry, size, risk level."""
    driver = get_driver()
    with driver.session() as session:
        # Industry breakdown
        industry_result = session.run(
            """
            MATCH (c:Company)-[:HAS_APPLICATION]->(la:LoanApplication)
            RETURN c.industry AS industry, count(la) AS count, sum(la.approved_amount) AS total
            ORDER BY total DESC
            """
        )
        industry_breakdown = [
            {"industry": r["industry"], "count": r["count"], "total_amount": round(r["total"] or 0, 2)}
            for r in industry_result
        ]
        
        # Loan size segmentation
        size_result = session.run(
            """
            MATCH (la:LoanApplication)
            WITH la,
                 CASE
                   WHEN la.approved_amount < 1000000 THEN 'Small (<10L)'
                   WHEN la.approved_amount < 5000000 THEN 'Medium (10L-50L)'
                   WHEN la.approved_amount < 10000000 THEN 'Large (50L-1Cr)'
                   ELSE 'Very Large (>1Cr)'
                 END AS size_category
            RETURN size_category, count(*) AS count, sum(la.approved_amount) AS total
            ORDER BY total DESC
            """
        )
        size_breakdown = [
            {"size_category": r["size_category"], "count": r["count"], "total_amount": round(r["total"] or 0, 2)}
            for r in size_result
        ]
    
    return {
        "industry_breakdown": industry_breakdown,
        "size_breakdown": size_breakdown,
    }


@router.get("/recent-activity")
async def get_recent_activity(limit: int = Query(10, ge=1, le=50)):
    """Get recent appraisal activity."""
    recent = sorted(
        _appraisal_store.values(),
        key=lambda x: x.get("timestamp", ""),
        reverse=True
    )[:limit]
    
    return {
        "recent_appraisals": [
            {
                "application_id": r["result"]["application_id"],
                "cin": r["result"]["cin"],
                "decision": r["decision"],
                "approved_amount": r["result"].get("approved_amount", 0),
                "credit_score": r["result"].get("five_cs_score", 0),
                "timestamp": r["timestamp"],
            }
            for r in recent
        ]
    }


@router.get("/itc-flow")
async def get_itc_flow():
    driver = get_driver()
    with driver.session() as session:
        # ITC claimed from GSTR3B
        claimed = session.run(
            "MATCH (r:GSTR3BReturn) RETURN coalesce(sum(r.itc_claimed), 0) AS total"
        ).single()["total"]

        # ITC eligible from GSTR2B invoices
        eligible = session.run(
            "MATCH (r:GSTR2BReturn)-[:CONTAINS_INWARD]->(inv:Invoice) "
            "RETURN coalesce(sum(inv.cgst + inv.sgst + inv.igst), 0) AS total"
        ).single()["total"]

        at_risk = max(0, round(claimed - eligible, 2))
        matched = round(min(claimed, eligible), 2)

    return {
        "nodes": [
            {"id": "claimed", "label": "ITC Claimed (GSTR-3B)"},
            {"id": "eligible", "label": "ITC Eligible (GSTR-2B)"},
            {"id": "matched", "label": "ITC Matched"},
            {"id": "at_risk", "label": "ITC At Risk"},
        ],
        "links": [
            {"source": "claimed", "target": "matched", "value": round(matched, 2)},
            {"source": "claimed", "target": "at_risk", "value": round(at_risk, 2)},
            {"source": "eligible", "target": "matched", "value": round(matched, 2)},
        ],
        "summary": {
            "total_claimed": round(claimed, 2),
            "total_eligible": round(eligible, 2),
            "total_at_risk": round(at_risk, 2),
            "total_matched": round(matched, 2),
        }
    }


@router.get("/trends")
async def get_trends():
    driver = get_driver()
    with driver.session() as session:
        result = session.run(
            """
            MATCH (inv:Invoice)
            WITH inv.return_period AS period, COUNT(inv) AS invoice_count
            OPTIONAL MATCH (t:Taxpayer)
            WITH period, invoice_count, COUNT(DISTINCT t) AS taxpayer_count
            RETURN period, invoice_count, taxpayer_count
            ORDER BY period
            """
        )
        period_data = {}
        for r in result:
            p = r["period"]
            if p:
                period_data[p] = {
                    "period": p,
                    "invoices": r["invoice_count"],
                    "taxpayers": r["taxpayer_count"],
                    "mismatches": 0,
                    "itc_at_risk": 0.0,
                }

    # Add mismatch data from in-memory store
    for period, stored in _results_store.items():
        results = stored.get("results", [])
        if period in period_data:
            period_data[period]["mismatches"] = len(results)
            period_data[period]["itc_at_risk"] = round(
                sum(m.get("amount_difference", 0) for m in results), 2
            )
        else:
            period_data[period] = {
                "period": period,
                "invoices": 0,
                "taxpayers": 0,
                "mismatches": len(results),
                "itc_at_risk": round(sum(m.get("amount_difference", 0) for m in results), 2),
            }

    return {"periods": sorted(period_data.values(), key=lambda x: x["period"])}
