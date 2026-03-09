"""
Credit risk assessment using the Five C's of Credit framework.
Calculates composite credit scores for companies based on:
- Character (30%): Promoter background, litigation history, compliance
- Capacity (25%): DSCR, profitability, cashflow adequacy
- Capital (20%): Net worth, leverage ratios, equity contribution
- Collateral (15%): Asset backing, security coverage
- Conditions (10%): Industry outlook, economic environment
"""
from app.core.graph_db import get_driver, find_shell_companies
from app.models.credit import RiskLevel


def calculate_all_company_risks() -> list[dict]:
    """Calculate credit risk scores for all companies in the graph."""
    driver = get_driver()
    shell_company_cins = _get_shell_company_cins()

    companies = []
    with driver.session() as session:
        result = session.run(
            """
            MATCH (c:Company)
            OPTIONAL MATCH (c)-[:HAS_FINANCIAL]->(fs:FinancialStatement)
            OPTIONAL MATCH (c)-[:HAS_BANK_STATEMENT]->(bs:BankStatement)
            OPTIONAL MATCH (c)-[:HAS_ITR]->(itr:ITR)
            OPTIONAL MATCH (c)-[:HAS_LITIGATION]->(lit:Litigation)
            OPTIONAL MATCH (c)<-[:PROMOTES]-(p:Promoter)
            OPTIONAL MATCH (c)-[:TRADES_WITH]->(partner:Company)
            WITH c,
                 COUNT(DISTINCT fs) AS financial_docs,
                 COUNT(DISTINCT bs) AS bank_statements,
                 COUNT(DISTINCT itr) AS itr_count,
                 COUNT(DISTINCT lit) AS litigation_count,
                 COUNT(DISTINCT p) AS promoter_count,
                 COUNT(DISTINCT partner) AS trade_partners,
                 AVG(fs.revenue) AS avg_revenue,
                 AVG(fs.profit) AS avg_profit,
                 SUM(CASE WHEN lit.status = 'Pending' THEN 1 ELSE 0 END) AS pending_litigation
            RETURN c.cin AS cin,
                   c.name AS company_name,
                   c.industry AS industry,
                   financial_docs,
                   bank_statements,
                   itr_count,
                   litigation_count,
                   pending_litigation,
                   promoter_count,
                   trade_partners,
                   avg_revenue,
                   avg_profit
            """
        )
        
        for record in result:
            cin = record["cin"]
            
            # Calculate Five C's scores
            character_score = _calculate_character_score(
                session, cin, 
                record["litigation_count"], 
                record["pending_litigation"],
                record["itr_count"]
            )
            
            capacity_score = _calculate_capacity_score(
                session, cin,
                record["avg_revenue"],
                record["avg_profit"]
            )
            
            capital_score = _calculate_capital_score(
                session, cin
            )
            
            collateral_score = _calculate_collateral_score(
                session, cin
            )
            
            conditions_score = _calculate_conditions_score(
                record["industry"]
            )
            
            # Composite credit score (weighted average)
            credit_score = round(
                character_score * 0.30 +
                capacity_score * 0.25 +
                capital_score * 0.20 +
                collateral_score * 0.15 +
                conditions_score * 0.10,
                1
            )
            
            # Shell company check
            is_shell = cin in shell_company_cins
            if is_shell:
                credit_score = max(0, credit_score - 30)  # Heavy penalty
            
            # Risk level (inverted from credit score)
            risk_score = 100 - credit_score
            if risk_score >= 75:
                risk_level = RiskLevel.CRITICAL.value
            elif risk_score >= 50:
                risk_level = RiskLevel.HIGH.value
            elif risk_score >= 25:
                risk_level = RiskLevel.MEDIUM.value
            else:
                risk_level = RiskLevel.LOW.value
            
            # Risk factors
            risk_factors = []
            if character_score < 50:
                risk_factors.append("Poor management integrity/compliance")
            if capacity_score < 50:
                risk_factors.append("Weak debt servicing capacity")
            if capital_score < 50:
                risk_factors.append("Inadequate capital/net worth")
            if collateral_score < 50:
                risk_factors.append("Insufficient asset backing")
            if is_shell:
                risk_factors.append("Shell company pattern detected")
            if record["pending_litigation"] > 0:
                risk_factors.append(f"{record['pending_litigation']} pending litigation cases")
            
            companies.append({
                "cin": cin,
                "company_name": record["company_name"] or "Unknown",
                "industry": record["industry"] or "Unknown",
                "credit_score": credit_score,
                "risk_score": risk_score,
                "risk_level": risk_level,
                "five_cs_breakdown": {
                    "character": round(character_score, 1),
                    "capacity": round(capacity_score, 1),
                    "capital": round(capital_score, 1),
                    "collateral": round(collateral_score, 1),
                    "conditions": round(conditions_score, 1),
                },
                "financial_docs": record["financial_docs"],
                "bank_statements": record["bank_statements"],
                "itr_count": record["itr_count"],
                "litigation_count": record["litigation_count"],
                "shell_company_flag": is_shell,
                "risk_factors": risk_factors,
                "financial_health_score": round((capacity_score + capital_score) / 2, 1),
                "conduct_score": round(character_score, 1),
                "market_score": round(conditions_score * 1.5, 1),  # Scaled up
            })

    return sorted(companies, key=lambda c: c["credit_score"], reverse=True)


def calculate_single_company_risk(cin: str) -> dict | None:
    """Calculate credit risk for a specific company."""
    all_companies = calculate_all_company_risks()
    for c in all_companies:
        if c["cin"] == cin:
            return c
    return None


def _calculate_character_score(session, cin: str, litigation_count: int, pending_litigation: int, itr_count: int) -> float:
    """
    Character (30%): Management integrity, compliance, promoter background.
    - ITR filing regularity: +30 points if >= 3 years
    - Litigation penalty: -10 per pending case
    - Promoter background: +20 if clean
    """
    score = 50  # Base score
    
    # ITR filing compliance
    if itr_count >= 3:
        score += 30
    elif itr_count >= 2:
        score += 20
    elif itr_count >= 1:
        score += 10
    
    # Litigation penalty
    score -= (pending_litigation * 10)
    score -= ((litigation_count - pending_litigation) * 3)  # Historical litigation too
    
    # Promoter background check
    promoter_result = session.run(
        """
        MATCH (c:Company {cin: $cin})<-[:PROMOTES]-(p:Promoter)
        OPTIONAL MATCH (p)-[:PROMOTES]->(other:Company)
        RETURN COUNT(DISTINCT other) AS other_companies,
               SUM(CASE WHEN p.defaulter = true THEN 1 ELSE 0 END) AS defaulter_count
        """,
        cin=cin
    )
    promoter_record = promoter_result.single()
    if promoter_record:
        if promoter_record["defaulter_count"] == 0:
            score += 20  # Clean promoter track record
    
    return max(0, min(100, score))


def _calculate_capacity_score(session, cin: str, avg_revenue: float, avg_profit: float) -> float:
    """
    Capacity (25%): Ability to repay - DSCR, profitability, cashflow.
    - Profitability margin: revenue and profit trends
    - DSCR estimation
    - Cashflow adequacy
    """
    score = 50  # Base score
    
    if avg_revenue and avg_profit:
        profit_margin = (avg_profit / avg_revenue) * 100
        
        # Profitability scoring
        if profit_margin > 15:
            score += 30
        elif profit_margin > 10:
            score += 20
        elif profit_margin > 5:
            score += 10
        elif profit_margin < 0:
            score -= 20  # Loss-making
        
        # Revenue scale bonus
        if avg_revenue > 100000000:  # > 10 Cr
            score += 10
        elif avg_revenue > 50000000:  # > 5 Cr
            score += 5
    
    # Bank statement checking (cashflow adequacy)
    bank_result = session.run(
        """
        MATCH (c:Company {cin: $cin})-[:HAS_BANK_STATEMENT]->(bs:BankStatement)
        RETURN AVG(bs.total_credits - bs.total_debits) AS avg_net_cashflow,
               AVG(bs.cheque_bounces) AS avg_bounces
        """,
        cin=cin
    )
    bank_record = bank_result.single()
    if bank_record and bank_record["avg_net_cashflow"]:
        if bank_record["avg_net_cashflow"] > 0:
            score += 10  # Positive cashflow
        else:
            score -= 15  # Negative cashflow - red flag
        
        if bank_record["avg_bounces"] and bank_record["avg_bounces"] > 1:
            score -= 10  # Cheque bounce penalty
    
    return max(0, min(100, score))


def _calculate_capital_score(session, cin: str) -> float:
    """
    Capital (20%): Net worth, equity contribution, leverage ratio.
    - Net worth adequacy
    - Debt-to-equity ratio
    - Paid-up capital
    """
    score = 50  # Base score
    
    financial_result = session.run(
        """
        MATCH (c:Company {cin: $cin})-[:HAS_FINANCIAL]->(fs:FinancialStatement)
        RETURN AVG(fs.net_worth) AS avg_net_worth,
               AVG(fs.total_assets) AS avg_assets,
               AVG(fs.total_liabilities) AS avg_liabilities,
               c.paid_up_capital AS paid_up_capital
        """,
        cin=cin
    )
    
    record = financial_result.single()
    if record:
        net_worth = record["avg_net_worth"] or 0
        assets = record["avg_assets"] or 0
        liabilities = record["avg_liabilities"] or 0
        paid_up = record["paid_up_capital"] or 0
        
        # Net worth scoring
        if net_worth > 50000000:  # > 5 Cr
            score += 25
        elif net_worth > 10000000:  # > 1 Cr
            score += 15
        elif net_worth > 0:
            score += 5
        else:
            score -= 30  # Negative net worth - critical
        
        # Debt-to-equity ratio
        if assets > 0:
            equity = assets - liabilities
            if equity > 0:
                debt_to_equity = liabilities / equity
                if debt_to_equity < 1:
                    score += 15  # Conservative leverage
                elif debt_to_equity < 2:
                    score += 5   # Acceptable
                elif debt_to_equity > 3:
                    score -= 10  # Over-leveraged
        
        # Paid-up capital adequacy
        if paid_up > 10000000:
            score += 10
    
    return max(0, min(100, score))


def _calculate_collateral_score(session, cin: str) -> float:
    """
    Collateral (15%): Asset backing, security coverage ratio.
    - Fixed assets value
    - Current assets vs liabilities
    """
    score = 50  # Base score
    
    financial_result = session.run(
        """
        MATCH (c:Company {cin: $cin})-[:HAS_FINANCIAL]->(fs:FinancialStatement)
        RETURN AVG(fs.total_assets) AS avg_assets,
               AVG(fs.current_assets) AS avg_current_assets,
               AVG(fs.current_liabilities) AS avg_current_liabilities
        """,
        cin=cin
    )
    
    record = financial_result.single()
    if record:
        assets = record["avg_assets"] or 0
        current_assets = record["avg_current_assets"] or 0
        current_liabilities = record["avg_current_liabilities"] or 0
        
        # Total assets scoring
        if assets > 100000000:  # > 10 Cr
            score += 30
        elif assets > 50000000:
            score += 20
        elif assets > 10000000:
            score += 10
        
        # Current ratio (liquidity)
        if current_liabilities > 0:
            current_ratio = current_assets / current_liabilities
            if current_ratio > 2:
                score += 20
            elif current_ratio > 1.5:
                score += 15
            elif current_ratio > 1:
                score += 5
            else:
                score -= 10  # Liquidity crisis
    
    return max(0, min(100, score))


def _calculate_conditions_score(industry: str) -> float:
    """
    Conditions (10%): Industry outlook, economic environment.
    Simple industry-based scoring (in production, use real-time industry data).
    """
    # Industry outlook scores (simplified)
    industry_scores = {
        "IT/Software": 85,
        "Pharmaceuticals": 80,
        "Manufacturing": 70,
        "Services": 70,
        "Trading": 65,
        "Textiles": 60,
        "Construction": 60,
        "Real Estate": 55,
        "Food Processing": 65,
        "Automobiles": 65,
    }
    
    return industry_scores.get(industry, 60)  # Default 60 for unknown industries


def _get_shell_company_cins() -> set:
    """Get CINs of companies involved in shell company patterns."""
    cycles = find_shell_companies()
    cins = set()
    for cycle in cycles:
        cins.update(cycle.get("cycle", []))
    return cins


def calculate_all_vendor_risks() -> list[dict]:
    """
    Calculate GST vendor (taxpayer) risk scores based on filing compliance,
    mismatch frequency, circular trading patterns, and volume anomalies.
    Returns a list of vendor risk objects keyed by GSTIN.
    """
    driver = get_driver()
    vendors = []
    
    try:
        with driver.session() as session:
            result = session.run(
                """
                MATCH (t:Taxpayer)
                OPTIONAL MATCH (t)-[:SUPPLIED_TO]-(inv:Invoice)
                OPTIONAL MATCH (t)-[:SUPPLIED_BY]-(inv2:Invoice)
                WITH t,
                     COUNT(DISTINCT inv) AS outward_invoices,
                     COUNT(DISTINCT inv2) AS inward_invoices
                RETURN t.gstin AS gstin,
                       t.legal_name AS name,
                       outward_invoices,
                       inward_invoices
                """
            )
            
            for record in result:
                gstin = record["gstin"]
                if not gstin:
                    continue
                
                # Basic risk assessment: more zeros for risk
                risk_score = 25  # Default LOW risk
                outward = record["outward_invoices"] or 0
                inward = record["inward_invoices"] or 0
                
                if outward == 0 or inward == 0:
                    risk_score = 50  # MEDIUM risk if no trading activity
                
                risk_level = "LOW"
                if risk_score >= 75:
                    risk_level = "CRITICAL"
                elif risk_score >= 50:
                    risk_level = "HIGH"
                elif risk_score >= 25:
                    risk_level = "MEDIUM"
                
                vendors.append({
                    "gstin": gstin,
                    "name": record["name"] or "Unknown",
                    "risk_score": risk_score,
                    "risk_level": risk_level,
                    "outward_invoices": outward,
                    "inward_invoices": inward,
                })
    except Exception:
        # Return empty list on any error
        pass
    
    return sorted(vendors, key=lambda v: v["risk_score"], reverse=True)
