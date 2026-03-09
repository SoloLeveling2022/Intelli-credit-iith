"""Credit decisioning engine - Determines loan amount, interest rate, and approval decision"""

from app.core.graph_db import get_driver
from app.models.credit import CreditGrade, FiveCsScore
from datetime import datetime


def calculate_loan_amount(company_id: str, requested_amount: float) -> float:
    """Calculate recommended loan amount based on company financials"""
    driver = get_driver()
    
    with driver.session() as session:
        result = session.run(
            """
            MATCH (c:Company {company_id: $company_id})-[:HAS]->(fs:FinancialStatement)
            WHERE fs.statement_type IN ['balance_sheet', 'profit_loss']
            WITH c, fs
            ORDER BY fs.financial_year DESC
            LIMIT 1
            RETURN fs.revenue AS revenue,
                   fs.ebitda AS ebitda,
                   fs.equity AS equity,
                   fs.current_assets AS current_assets
            """,
            company_id=company_id,
        ).single()
        
        if not result:
            return requested_amount * 0.5  # Conservative fallback
        
        revenue = result.get("revenue", 0)
        ebitda = result.get("ebitda", 0)
        equity = result.get("equity", 0)
        
        # Maximum loan = min of:
        # 1. 20% of annual revenue
        # 2. 3x EBITDA
        # 3. 2x equity
        # 4. Requested amount
        max_by_revenue = revenue * 0.20 if revenue > 0 else 0
        max_by_ebitda = ebitda * 3 if ebitda > 0 else 0
        max_by_equity = equity * 2 if equity > 0 else 0
        
        recommended = min(
            max_by_revenue,
            max_by_ebitda,
            max_by_equity,
            requested_amount
        )
        
        return max(recommended, 0)


def determine_interest_rate(company_id: str, risk_score: float, credit_grade: str) -> float:
    """Determine interest rate based on risk-based pricing"""
    
    # Base rate (assume RBI repo rate + bank markup)
    base_rate = 8.5
    
    # Risk premium based on credit grade
    risk_premiums = {
        "AAA": 0.5,
        "AA": 1.0,
        "A": 1.5,
        "BBB": 2.5,
        "BB": 4.0,
        "B": 6.0,
        "C": 8.0,
        "D": 12.0,
    }
    
    risk_premium = risk_premiums.get(credit_grade, 5.0)
    
    # Additional premium for risk score (0-100, higher is riskier)
    score_adjustment = (risk_score / 100) * 2.0
    
    final_rate = base_rate + risk_premium + score_adjustment
    
    # Cap between 9% and 24%
    return max(9.0, min(24.0, final_rate))


def generate_five_cs_analysis(company_id: str) -> FiveCsScore:
    """Generate Five C's of Credit analysis"""
    driver = get_driver()
    
    # Initialize scores
    character_score = 50.0
    capacity_score = 50.0
    capital_score = 50.0
    collateral_score = 50.0
    conditions_score = 50.0
    
    character_factors = []
    capacity_factors = []
    capital_factors = []
    collateral_factors = []
    conditions_factors = []
    
    with driver.session() as session:
       
        # CHARACTER: Promoter background, litigation, defaults
        promoter_result = session.run(
            """
            MATCH (c:Company {company_id: $company_id})<-[:DIRECTOR_OF]-(p:Promoter)
            OPTIONAL MATCH (p)-[:DEFENDANT_IN]->(l:Litigation)
            RETURN p.name AS name,
                   p.cibil_score AS cibil,
                   p.default_history AS defaults,
                   COUNT(l) AS litigation_count
            """,
            company_id=company_id,
        )
        
        for p in promoter_result:
            cibil = p.get("cibil", 700)
            defaults = p.get("defaults", False)
            litigation_count = p.get("litigation_count", 0)
            
            if cibil >= 750:
                character_score += 15
                character_factors.append(f"Excellent CIBIL score: {cibil}")
            elif cibil < 650:
                character_score -= 20
                character_factors.append(f"Poor CIBIL score: {cibil}")
            
            if defaults:
                character_score -= 30
                character_factors.append("Promoter has default history")
            
            if litigation_count > 0:
                character_score -= 10 * litigation_count
                character_factors.append(f"{litigation_count} litigation cases found")
        
        # CAPACITY: Cash flow, profitability, DSCR
        financial_result = session.run(
            """
            MATCH (c:Company {company_id: $company_id})-[:HAS]->(fs:FinancialStatement)
            WHERE fs.statement_type = 'profit_loss'
            WITH c, fs
            ORDER BY fs.financial_year DESC
            LIMIT 1
            RETURN fs.revenue AS revenue,
                   fs.profit_after_tax AS profit,
                   fs.ebitda AS ebitda
            """,
            company_id=company_id,
        ).single()
        
        if financial_result:
            revenue = financial_result.get("revenue", 0)
            profit = financial_result.get("profit", 0)
            ebitda = financial_result.get("ebitda", 0)
            
            if profit > 0 and revenue > 0:
                profit_margin = (profit / revenue) * 100
                if profit_margin > 15:
                    capacity_score += 20
                    capacity_factors.append(f"Strong profit margin: {profit_margin:.1f}%")
                elif profit_margin < 5:
                    capacity_score -= 15
                    capacity_factors.append(f"Weak profit margin: {profit_margin:.1f}%")
            
            if ebitda < 0:
                capacity_score -= 25
                capacity_factors.append("Negative EBITDA")
        
        # CAPITAL: Equity, debt-equity ratio
        balance_result = session.run(
            """
            MATCH (c:Company {company_id: $company_id})-[:HAS]->(fs:FinancialStatement)
            WHERE fs.statement_type = 'balance_sheet'
            WITH c, fs
            ORDER BY fs.financial_year DESC
            LIMIT 1
            RETURN fs.equity AS equity,
                   fs.long_term_debt AS debt,
                   fs.totalassets AS total_assets
            """,
            company_id=company_id,
        ).single()
        
        if balance_result:
            equity = balance_result.get("equity", 0)
            debt = balance_result.get("debt", 0)
            
            if equity > 0:
                capital_score += 15
                capital_factors.append(f"Positive net worth: INR {equity:,.0f}")
                
                if debt > 0:
                    debt_equity_ratio = debt / equity
                    if debt_equity_ratio < 1.0:
                        capital_score += 10
                        capital_factors.append(f"Healthy D/E ratio: {debt_equity_ratio:.2f}")
                    elif debt_equity_ratio > 3.0:
                        capital_score -= 20
                        capital_factors.append(f"High D/E ratio: {debt_equity_ratio:.2f}")
            else:
                capital_score -= 30
                capital_factors.append("Negative net worth - technically insolvent")
        
        # COLLATERAL: Asset coverage (simplified)
        if balance_result:
            total_assets = balance_result.get("total_assets", 0)
            if total_assets > 10000000:  # 1 Crore
                collateral_score += 20
                collateral_factors.append(f"Substantial asset base: INR {total_assets:,.0f}")
            else:
                collateral_factors.append("Limited collateral available")
        
        # CONDITIONS: Industry trends (placeholder - would integrate external data)
        conditions_score = 60.0  # Neutral by default
        conditions_factors.append("Industry conditions: Stable (requires sector analysis)")
    
    # Normalize scores to 0-100
    character_score = max(0, min(100, character_score))
    capacity_score = max(0, min(100, capacity_score))
    capital_score = max(0, min(100, capital_score))
    collateral_score = max(0, min(100, collateral_score))
    conditions_score = max(0, min(100, conditions_score))
    
    return FiveCsScore(
        character_score=character_score,
        capacity_score=capacity_score,
        capital_score=capital_score,
        collateral_score=collateral_score,
        conditions_score=conditions_score,
        character_factors=character_factors,
        capacity_factors=capacity_factors,
        capital_factors=capital_factors,
        collateral_factors=collateral_factors,
        conditions_factors=conditions_factors,
    )


def recommend_decision(
    company_id: str,
    risk_score: float,
    credit_grade: str,
    indicators: list,
    five_cs: FiveCsScore
) -> tuple[str, str]:
    """Make final decision: APPROVED, REJECTED, or CONDITIONAL"""
    
    # Decision logic based on multiple factors
    critical_indicators = [i for i in indicators if i.get("severity") == "CRITICAL"]
    high_indicators = [i for i in indicators if i.get("severity") == "HIGH"]
    
    # Weighted composite score from Five C's
    composite_score = (
        five_cs.character_score * 0.30 +
        five_cs.capacity_score * 0.25 +
        five_cs.capital_score * 0.20 +
        five_cs.collateral_score * 0.15 +
        five_cs.conditions_score * 0.10
    )
    
    # Decision rules
    if len(critical_indicators) > 2:
        decision = "REJECTED"
        justification = f"Application rejected due to {len(critical_indicators)} critical risk indicators: {', '.join([i['indicator_type'] for i in critical_indicators[:3]])}. Unacceptable creditrisk profile."
    
    elif credit_grade in ["D", "C"]:
        decision = "REJECTED"
        justification = f"Application rejected due to poor credit grade ({credit_grade}). Borrower does not meet minimum creditworthiness standards."
    
    elif composite_score < 40:
        decision = "REJECTED"
        justification = f"Application rejected. Five C's composite score ({composite_score:.1f}/100) below acceptable threshold (40). Insufficient creditworthiness."
    
    elif len(critical_indicators) == 1 or len(high_indicators) > 3 or composite_score < 60:
        decision = "CONDITIONAL"
        conditions = []
        if len(critical_indicators) > 0:
            conditions.append(f"Address critical risk: {critical_indicators[0]['indicator_type']}")
        if five_cs.character_score < 50:
            conditions.append("Provide additional promoter guarantees")
        if five_cs.capital_score < 50:
            conditions.append("Infuse additional equity capital")
        if five_cs.collateral_score < 50:
            conditions.append("Provide additional collateral security")
        
        justification = f"Conditional approval subject to: " + "; ".join(conditions) + f". Composite score: {composite_score:.1f}/100. Credit grade: {credit_grade}."
    
    else:
        decision = "APPROVED"
        justification = f"Application approved. Strong credit profile with composite score {composite_score:.1f}/100, credit grade {credit_grade}, and {len([i for i in indicators if i.get('severity') in ['LOW', 'MEDIUM']])} manageable risk indicators."
    
    return decision, justification
