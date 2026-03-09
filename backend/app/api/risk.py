"""
Credit Risk API - company credit risk scoring, Five C's analysis, risk indicators.
"""
from fastapi import APIRouter, HTTPException, Query
from app.core.risk_model import calculate_all_company_risks, calculate_single_company_risk, calculate_all_vendor_risks
from app.core.credit_engine import generate_five_cs_analysis
from app.core.llm_chain import generate_credit_risk_summary, generate_risk_summary
from app.core.credit_analyzer import analyze_company

router = APIRouter()


@router.get("/companies")
async def get_company_risks(
    risk_level: str = Query(None),  # LOW, MEDIUM, HIGH, CRITICAL
    min_score: float = Query(None, ge=0, le=100),
    max_score: float = Query(None, ge=0, le=100),
):
    """Get credit risk scores for all companies with optional filtering."""
    try:
        companies = calculate_all_company_risks()
        
        # Apply filters
        if risk_level:
            companies = [c for c in companies if c["risk_level"] == risk_level]
        if min_score is not None:
            companies = [c for c in companies if c["credit_score"] >= min_score]
        if max_score is not None:
            companies = [c for c in companies if c["credit_score"] <= max_score]
        
        return {
            "total": len(companies),
            "companies": companies,
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Risk calculation failed: {str(e)}")


@router.get("/companies/{cin}")
async def get_company_risk_detail(cin: str):
    """Get detailed credit risk analysis for a specific company."""
    try:
        company = calculate_single_company_risk(cin)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Risk calculation failed: {str(e)}")
    
    if not company:
        raise HTTPException(status_code=404, detail=f"Company {cin} not found")
    
    return company


@router.get("/companies/{cin}/summary")
async def get_company_risk_ai_summary(cin: str):
    """Generate AI-powered credit risk summary for a company."""
    try:
        # Get risk analysis
        company = calculate_single_company_risk(cin)
        if not company:
            raise HTTPException(status_code=404, detail=f"Company {cin} not found")
        
        # Get risk indicators
        risk_indicators = analyze_company(cin)
        
        # Generate AI summary
        summary = await generate_credit_risk_summary(cin, risk_indicators)
        
        return {
            "company": company,
            "risk_indicators": [r.model_dump() for r in risk_indicators],
            "ai_summary": summary,
        }
        
    except Exception as e:
        error_msg = f"Unable to generate AI summary: {str(e)}"
        return {"company": company if 'company' in locals() else None, "ai_summary": error_msg}


@router.get("/companies/{cin}/five-cs")
async def get_five_cs_analysis(cin: str):
    """Get Five C's of Credit analysis for a company."""
    try:
        # Analyze company and get risk indicators
        risk_indicators = analyze_company(cin)
        
        # Generate Five C's analysis
        five_cs = generate_five_cs_analysis(cin=cin, risk_indicators=risk_indicators)
        
        return {
            "cin": cin,
            "overall_score": five_cs.overall_score,
            "breakdown": {
                "character": {
                    "score": five_cs.character,
                    "description": "Management integrity, business ethics, payment history",
                },
                "capacity": {
                    "score": five_cs.capacity,
                    "description": "Ability to repay - DSCR, cashflows, profitability",
                },
                "capital": {
                    "score": five_cs.capital,
                    "description": "Net worth, equity contribution, financial strength",
                },
                "collateral": {
                    "score": five_cs.collateral,
                    "description": "Asset backing, security coverage ratio",
                },
                "conditions": {
                    "score": five_cs.conditions,
                    "description": "Industry outlook, economic environment, business cycle",
                },
            },
            "risk_level": "LOW" if five_cs.overall_score >= 75 else 
                         "MEDIUM" if five_cs.overall_score >= 50 else 
                         "HIGH" if five_cs.overall_score >= 25 else "CRITICAL",
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Five C's analysis failed: {str(e)}")


@router.get("/companies/{cin}/scorecard")
async def get_company_scorecard(cin: str):
    """Get comprehensive risk scorecard with detailed metrics."""
    from app.core.graph_db import get_driver

    company = calculate_single_company_risk(cin)
    if not company:
        raise HTTPException(status_code=404, detail=f"Company {cin} not found")

    driver = get_driver()
    with driver.session() as session:
        # Financial statements history
        financial_history = []
        result = session.run(
            """
            MATCH (c:Company {cin: $cin})-[:HAS_FINANCIAL]->(fs:FinancialStatement)
            RETURN fs.year AS year, fs.revenue AS revenue, fs.profit AS profit,
                   fs.total_assets AS assets, fs.total_liabilities as liabilities
            ORDER BY fs.year DESC
            """,
            cin=cin,
        )
        for r in result:
            financial_history.append({
                "year": r["year"],
                "revenue": r["revenue"],
                "profit": r["profit"],
                "assets": r["assets"],
                "liabilities": r["liabilities"],
            })

        # Related companies (suppliers, customers, group entities)
        related_companies = []
        related_result = session.run(
            """
            MATCH (c:Company {cin: $cin})-[rel:TRADES_WITH|RELATED_TO]-(other:Company)
            RETURN other.cin AS cin, other.name AS name,
                   type(rel) AS relationship_type,
                   rel.volume AS volume
            ORDER BY rel.volume DESC LIMIT 10
            """,
            cin=cin,
        )
        for r in related_result:
            related_companies.append({
                "cin": r["cin"],
                "name": r["name"],
                "relationship": r["relationship_type"],
                "volume": r["volume"],
            })

        # Promoters
        promoters = []
        promoter_result = session.run(
            """
            MATCH (c:Company {cin: $cin})<-[:PROMOTES]-(p:Promoter)
            RETURN p.name AS name, p.pan AS pan, p.shareholding AS shareholding
            """,
            cin=cin,
        )
        for r in promoter_result:
            promoters.append({
                "name": r["name"],
                "pan": r["pan"],
                "shareholding": r["shareholding"],
            })

        # Litigation cases
        litigation = []
        litigation_result = session.run(
            """
            MATCH (c:Company {cin: $cin})-[:HAS_LITIGATION]->(lit:Litigation)
            RETURN lit.case_number AS case_number, lit.court AS court,
                   lit.case_type AS case_type, lit.status AS status,
                   lit.amount AS amount
            """,
            cin=cin,
        )
        for r in litigation_result:
            litigation.append({
                "case_number": r["case_number"],
                "court": r["court"],
                "case_type": r["case_type"],
                "status": r["status"],
                "amount": r["amount"],
            })

    # Risk factor breakdown
    risk_breakdown = {
        "financial_health": {
            "weight": 0.30,
            "score": company.get("financial_health_score", 70),
            "factors": ["Profitability", "Leverage Ratio", "Liquidity"],
        },
        "business_conduct": {
            "weight": 0.25,
            "score": company.get("conduct_score", 75),
            "factors": ["Payment History", "Banking Conduct", "Compliance"],
        },
        "market_position": {
            "weight": 0.20,
            "score": company.get("market_score", 65),
            "factors": ["Revenue Growth", "Market Share", "Industry Standing"],
        },
        "management_quality": {
            "weight": 0.15,
            "score": company.get("management_score", 70),
            "factors": ["Promoter Background", "Corporate Governance", "Track Record"],
        },
        "external_factors": {
            "weight": 0.10,
            "score": company.get("external_score", 60),
            "factors": ["Industry Outlook", "Litigation Risk", "Regulatory Environment"],
        },
    }

    return {
        "company": company,
        "financial_history": financial_history,
        "related_companies": related_companies,
        "promoters": promoters,
        "litigation": litigation,
        "risk_breakdown": risk_breakdown,
    }


# Vendor Risk Endpoints (GST Module)

@router.get("/vendors")
async def get_vendor_risks(
    risk_level: str = Query(None),  # LOW, MEDIUM, HIGH, CRITICAL
    min_score: float = Query(None, ge=0, le=100),
    max_score: float = Query(None, ge=0, le=100),
):
    """Get GST vendor risk scores for all taxpayers with optional filtering."""
    try:
        vendors = calculate_all_vendor_risks()
        
        # Apply filters
        if risk_level:
            vendors = [v for v in vendors if v["risk_level"] == risk_level]
        if min_score is not None:
            vendors = [v for v in vendors if v["risk_score"] >= min_score]
        if max_score is not None:
            vendors = [v for v in vendors if v["risk_score"] <= max_score]
        
        return {
            "total": len(vendors),
            "vendors": vendors,
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Vendor risk calculation failed: {str(e)}")


@router.get("/vendors/{gstin}")
async def get_vendor_risk_detail(gstin: str):
    """Get detailed GST risk analysis for a specific vendor/taxpayer."""
    from app.core.graph_db import get_driver
    
    try:
        driver = get_driver()
        with driver.session() as session:
            # Get taxpayer basic info
            result = session.run(
                """
                MATCH (t:Taxpayer {gstin: $gstin})
                OPTIONAL MATCH (t)-[rel_out:SUPPLIED_BY]-(inv_out:Invoice)
                OPTIONAL MATCH (t)-[rel_in:SUPPLIED_TO]-(inv_in:Invoice)
                WITH t, 
                     COUNT(DISTINCT inv_out) AS total_outward,
                     COUNT(DISTINCT inv_in) AS total_inward,
                     SUM(DISTINCT inv_out.taxable_value) AS outward_value,
                     SUM(DISTINCT inv_in.taxable_value) AS inward_value
                OPTIONAL MATCH (t)-[:FILED]->(ret:GSTR1Return)
                WITH t, total_outward, total_inward, outward_value, inward_value,
                     COUNT(DISTINCT ret) AS filing_count
                OPTIONAL MATCH (t)-[:TRADES_WITH]-(partner:Taxpayer)
                RETURN t.gstin AS gstin,
                       t.legal_name AS legal_name,
                       t.trade_name AS trade_name,
                       t.registration_date AS registration_date,
                       t.state AS state,
                       total_outward,
                       total_inward,
                       outward_value,
                       inward_value,
                       filing_count,
                       COUNT(DISTINCT partner) AS trade_partners
                """,
                gstin=gstin,
            )
            record = result.single()
            
            if not record:
                raise HTTPException(status_code=404, detail=f"Vendor {gstin} not found")
            
            # Calculate basic risk score
            risk_score = 25  # Default LOW
            outward = record["total_outward"] or 0
            inward = record["total_inward"] or 0
            filing_count = record["filing_count"] or 0
            
            if outward == 0 or inward == 0:
                risk_score = 50  # MEDIUM
            if filing_count < 3:
                risk_score += 25  # Increase risk for low filing count
            
            risk_level = "LOW"
            if risk_score >= 75:
                risk_level = "CRITICAL"
            elif risk_score >= 50:
                risk_level = "HIGH"
            elif risk_score >= 25:
                risk_level = "MEDIUM"
            
            # Get mismatches
            mismatch_result = session.run(
                """
                MATCH (inv:Invoice)
                WHERE inv.supplierGSTIN = $gstin OR inv.buyerGSTIN = $gstin
                AND inv.has_mismatch = true
                RETURN COUNT(inv) AS mismatch_count
                """,
                gstin=gstin,
            )
            mismatch_record = mismatch_result.single()
            mismatch_count = mismatch_record["mismatch_count"] if mismatch_record else 0
            
            # Calculate filing rate (simplified)
            filing_rate = min(100, (filing_count / 12) * 100) if filing_count else 0
            
            return {
                "gstin": record["gstin"],
                "legal_name": record["legal_name"] or "Unknown",
                "trade_name": record["trade_name"],
                "registration_date": record["registration_date"],
                "state": record["state"],
                "risk_score": risk_score,
                "risk_level": risk_level,
                "total_invoices": outward + inward,
                "total_outward": outward,
                "total_inward": inward,
                "outward_value": record["outward_value"] or 0,
                "inward_value": record["inward_value"] or 0,
                "mismatch_count": mismatch_count,
                "filing_count": filing_count,
                "filing_rate": round(filing_rate, 2),
                "trade_partners": record["trade_partners"] or 0,
            }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Vendor risk calculation failed: {str(e)}")


@router.get("/vendors/{gstin}/summary")
async def get_vendor_risk_ai_summary(gstin: str):
    """Generate AI-powered risk summary for a vendor/taxpayer."""
    try:
        # Get vendor detail
        vendor = await get_vendor_risk_detail(gstin)
        if not vendor:
            raise HTTPException(status_code=404, detail=f"Vendor {gstin} not found")
        
        # Generate AI summary (using existing risk summary function)
        try:
            summary = await generate_risk_summary(gstin, vendor)
        except Exception as e:
            summary = f"Unable to generate AI summary: {str(e)}"
        
        return {
            "vendor": vendor,
            "ai_summary": summary,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Unable to generate AI summary: {str(e)}"
        return {
            "vendor": vendor if 'vendor' in locals() else None,
            "ai_summary": error_msg
        }


@router.get("/vendors/{gstin}/scorecard")
async def get_vendor_scorecard(gstin: str):
    """Get comprehensive risk scorecard for a vendor/taxpayer."""
    from app.core.graph_db import get_driver
    
    try:
        # Get basic vendor info
        vendor = await get_vendor_risk_detail(gstin)
        if not vendor:
            raise HTTPException(status_code=404, detail=f"Vendor {gstin} not found")
        
        driver = get_driver()
        with driver.session() as session:
            # Get trade partners
            trade_partners = []
            partner_result = session.run(
                """
                MATCH (t:Taxpayer {gstin: $gstin})-[rel:TRADES_WITH]-(partner:Taxpayer)
                RETURN partner.gstin AS gstin,
                       partner.legal_name AS name,
                       rel.volume AS volume,
                       rel.frequency AS frequency
                ORDER BY rel.volume DESC LIMIT 10
                """,
                gstin=gstin,
            )
            for r in partner_result:
                trade_partners.append({
                    "gstin": r["gstin"],
                    "name": r["name"] or "Unknown",
                    "volume": r["volume"] or 0,
                    "frequency": r["frequency"] or 0,
                })
            
            # Get monthly filing pattern
            monthly_filings = []
            filing_result = session.run(
                """
                MATCH (t:Taxpayer {gstin: $gstin})-[:FILED]->(ret:GSTR1Return)
                RETURN ret.period AS period, ret.filing_date AS filing_date
                ORDER BY ret.period DESC LIMIT 12
                """,
                gstin=gstin,
            )
            for r in filing_result:
                monthly_filings.append({
                    "period": r["period"],
                    "filed": True,
                    "filing_date": r["filing_date"],
                })
            
            # Get ITC claimed vs eligible (simplified)
            itc_data = session.run(
                """
                MATCH (t:Taxpayer {gstin: $gstin})-[:FILED]->(ret:GSTR3BReturn)
                RETURN SUM(ret.itc_claimed) AS total_claimed,
                       SUM(ret.itc_eligible) AS total_eligible
                """,
                gstin=gstin,
            ).single()
            
            itc_claimed = itc_data["total_claimed"] if itc_data else 0
            itc_eligible = itc_data["total_eligible"] if itc_data else 0
            
        # Risk factor breakdown
        risk_breakdown = {
            "filing_compliance": {
                "weight": 0.25,
                "score": vendor["filing_rate"] * 0.75,  # Scale to 0-75
                "factors": ["Filing Frequency", "On-time Filing", "Return Completeness"],
            },
            "mismatch_frequency": {
                "weight": 0.30,                "score": max(0, 100 - (vendor["mismatch_count"] * 5)),  # Decrease score with mismatches
                "factors": ["Invoice Mismatches", "Value Discrepancies", "Rate Errors"],
            },
            "circular_trading": {
                "weight": 0.25,
                "score": 75,  # Default good score
                "factors": ["Trading Pattern Analysis", "Related Party Transactions", "Suspicious Flows"],
            },
            "volume_anomaly": {
                "weight": 0.20,
                "score": 70,  # Default score
                "factors": ["Revenue Volatility", "Transaction Pattern", "Growth Trend"],
            },
        }
        
        return {
            "vendor": vendor,
            "trade_partners": trade_partners,
            "monthly_filings": monthly_filings,
            "itc_claimed": itc_claimed or 0,
            "itc_eligible": itc_eligible or 0,
            "risk_breakdown": risk_breakdown,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Vendor scorecard generation failed: {str(e)}")
