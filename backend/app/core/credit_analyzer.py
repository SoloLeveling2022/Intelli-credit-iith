"""Credit analysis engine - transforms reconciler logic to credit risk analysis"""

import uuid
from app.core.graph_db import get_driver
from app.models.credit import RiskAssessmentResult, RiskIndicator, Severity


def analyze_company(application_id: str, company_id: str) -> list[dict]:
    """Main credit analysis function - analyzes all aspects of a company"""
    indicators = []
    indicators.extend(analyze_revenue_consistency(company_id))
    indicators.extend(calculate_debt_servicing_capacity(company_id))
    indicators.extend(detect_shell_companies(company_id))
    indicators.extend(detect_revenue_inflation(company_id))
    indicators.extend(analyze_cashflow(company_id))
    return indicators


def analyze_revenue_consistency(company_id: str) -> list[dict]:
    """Compare ITR revenue against bank statement deposits"""
    driver = get_driver()
    indicators = []
    
    with driver.session() as session:
        # Find discrepancies between ITR and bank deposits
        result = session.run(
            """
            MATCH (c:Company {company_id: $company_id})-[:FILED]->(itr:ITR)
            OPTIONAL MATCH (c)-[:HOLDS]->(bank:BankStatement)
            WHERE itr.assessment_year = bank.period_end
            WITH c, itr, SUM(bank.total_credits) AS total_deposits
            WHERE itr.revenue > 0 AND total_deposits > 0
              AND abs(itr.revenue - total_deposits) / itr.revenue > 0.15
            RETURN itr.itr_id AS itr_id, 
                   itr.revenue AS reported_revenue,
                   total_deposits,
                   abs(itr.revenue - total_deposits) AS difference
            """,
            company_id=company_id,
        )
        
        for record in result:
            diff = record["difference"]
            indicators.append({
                "id": str(uuid.uuid4()),
                "indicator_type": RiskIndicator.REVENUE_INFLATION.value,
                "severity": _severity_for_amount(diff),
                "company_id": company_id,
                "document_id": record["itr_id"],
                "field_name": "revenue",
                "expected_value": str(record["total_deposits"]),
                "actual_value": str(record["reported_revenue"]),
                "amount_impact": diff,
                "description": f"Revenue mismatch: ITR shows INR {record['reported_revenue']:,.2f} but bank deposits total INR {record['total_deposits']:,.2f}. Difference: INR {diff:,.2f} (>15% threshold).",
                "detected_date": None,
            })
    
    return indicators


def calculate_debt_servicing_capacity(company_id: str) -> list[dict]:
    """Calculate DSCR (Debt Service Coverage Ratio)"""
    driver = get_driver()
    indicators = []
    
    with driver.session() as session:
        result = session.run(
            """
            MATCH (c:Company {company_id: $company_id})-[:HAS]->(fs:FinancialStatement)
            WHERE fs.statement_type = 'profit_loss'
            WITH c, fs
            ORDER BY fs.financial_year DESC
            LIMIT 1
            RETURN fs.ebitda AS ebitda,
                   fs.revenue AS revenue,
                   c.total_debt AS total_debt
            """,
            company_id=company_id,
        )
        
        for record in result:
            ebitda = record.get("ebitda", 0)
            total_debt = record.get("total_debt", 0)
            
            if total_debt > 0:
                # Simplified DSCR = EBITDA / Annual Debt Service (assuming 20% annual payment)
                annual_debt_service = total_debt * 0.20
                dscr = ebitda / annual_debt_service if annual_debt_service > 0 else 0
                
                if dscr < 1.25:  # DSCR should be > 1.25 for safe lending
                    indicators.append({
                        "id": str(uuid.uuid4()),
                        "indicator_type": RiskIndicator.DEBT_COVENANT_BREACH.value,
                        "severity": Severity.HIGH.value if dscr < 1.0 else Severity.MEDIUM.value,
                        "company_id": company_id,
                        "field_name": "dscr",
                        "expected_value": ">= 1.25",
                        "actual_value": f"{dscr:.2f}",
                        "amount_impact": 0,
                        "description": f"Weak debt servicing capacity. DSCR = {dscr:.2f}. EBITDA INR {ebitda:,.2f} cannot adequately cover debt obligations.",
                        "detected_date": None,
                    })
    
    return indicators


def detect_shell_companies(company_id: str) -> list[dict]:
    """Detect circular trading patterns (shell company indicators)"""
    driver = get_driver()
    indicators = []
    
    with driver.session() as session:
        result = session.run(
            """
            MATCH path = (a:Company {company_id: $company_id})-[:RELATED_TO*2..4]->(a)
            WHERE ALL(r IN relationships(path) WHERE r.transaction_value > 100000)
            RETURN [n IN nodes(path) | n.company_id] AS cycle,
                   [n IN nodes(path) | n.legal_name] AS names,
                   length(path) AS cycle_length,
                   reduce(total = 0, r IN relationships(path) | total + r.transaction_value) AS total_volume
            ORDER BY total_volume DESC
            LIMIT 5
            """,
            company_id=company_id,
        )
        
        for record in result:
            indicators.append({
                "id": str(uuid.uuid4()),
                "indicator_type": RiskIndicator.SHELL_COMPANY_INDICATOR.value,
                "severity": Severity.CRITICAL.value,
                "company_id": company_id,
                "field_name": "related_party_cycle",
                "expected_value": "No circular transactions",
                "actual_value": f"Cycle of {record['cycle_length']} companies",
                "amount_impact": record["total_volume"],
                "description": f"Circular trading detected involving {' → '.join(record['names'])}. Total volume: INR {record['total_volume']:,.2f}. Possible shell company network.",
                "detected_date": None,
            })
    
    return indicators


def detect_revenue_inflation(company_id: str) -> list[dict]:
    """Detect suspicious transaction patterns"""
    driver = get_driver()
    indicators = []
    
    with driver.session() as session:
        # Check for round-amount transactions (potential fake invoices)
        result = session.run(
            """
            MATCH (c:Company {company_id: $company_id})-[:ISSUED|RECEIVED]->(doc:FinancialDocument)
            WHERE doc.amount % 50000 = 0 AND doc.amount > 100000
            WITH c,COUNT(doc) AS round_amount_count, SUM(doc.amount) AS total_round
            WHERE round_amount_count > 5
            RETURN round_amount_count, total_round
            """,
            company_id=company_id,
        )
        
        for record in result:
            indicators.append({
                "id": str(uuid.uuid4()),
                "indicator_type": RiskIndicator.REVENUE_INFLATION.value,
                "severity": Severity.MEDIUM.value,
                "company_id": company_id,
                "field_name": "transaction_pattern",
                "expected_value": "Varied transaction amounts",
                "actual_value": f"{record['round_amount_count']} round-amount transactions",
                "amount_impact": record["total_round"],
                "description": f"Suspicious pattern: {record['round_amount_count']} transactions with exact round amounts (multiples of 50,000). Total: INR {record['total_round']:,.2f}",
                "detected_date": None,
            })
    
    return indicators


def analyze_cashflow(company_id: str) -> list[dict]:
    """Analyze working capital and cash flow health"""
    driver = get_driver()
    indicators = []
    
    with driver.session() as session:
        result = session.run(
            """
            MATCH (c:Company {company_id: $company_id})-[:HAS]->(fs:FinancialStatement)
            WHERE fs.statement_type = 'balance_sheet'
            WITH c, fs
            ORDER BY fs.financial_year DESC
            LIMIT 1
            RETURN fs.current_assets AS current_assets,
                   fs.current_liabilities AS current_liabilities,
                   fs.equity AS equity
            """,
            company_id=company_id,
        )
        
        for record in result:
            current_assets = record.get("current_assets", 0)
            current_liabilities = record.get("current_liabilities", 1)
            equity = record.get("equity", 0)
            
            # Current ratio check
            current_ratio = current_assets / current_liabilities if current_liabilities > 0 else 0
            if current_ratio < 1.0:
                indicators.append({
                    "id": str(uuid.uuid4()),
                    "indicator_type": RiskIndicator.WORKING_CAPITAL_SHORTAGE.value,
                    "severity": Severity.HIGH.value,
                    "company_id": company_id,
                    "field_name": "current_ratio",
                    "expected_value": ">= 1.0",
                    "actual_value": f"{current_ratio:.2f}",
                    "amount_impact": current_liabilities - current_assets,
                    "description": f"Working capital shortage. Current Ratio = {current_ratio:.2f}. Current liabilities (INR {current_liabilities:,.2f}) exceed current assets (INR {current_assets:,.2f}).",
                    "detected_date": None,
                })
            
            # Negative equity check
            if equity < 0:
                indicators.append({
                    "id": str(uuid.uuid4()),
                    "indicator_type": RiskIndicator.CASHFLOW_NEGATIVE.value,
                    "severity": Severity.CRITICAL.value,
                    "company_id": company_id,
                    "field_name": "equity",
                    "expected_value": "> 0",
                    "actual_value": str(equity),
                    "amount_impact": abs(equity),
                    "description": f"Negative net worth of INR {abs(equity):,.2f}. Company is technically insolvent.",
                    "detected_date": None,
                })
    
    return indicators


def _severity_for_amount(amount: float) -> str:
    """Determine severity based on monetary impact"""
    if amount >= 5000000:  # 50 Lakhs
        return Severity.CRITICAL.value
    elif amount >= 1000000:  # 10 Lakhs
        return Severity.HIGH.value
    elif amount >= 100000:  # 1 Lakh
        return Severity.MEDIUM.value
    return Severity.LOW.value
