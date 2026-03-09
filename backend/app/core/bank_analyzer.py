"""Bank Statement Analyzer - Parse and analyze bank transactions"""

from datetime import datetime
from typing import Dict, List


def parse_bank_statement(pdf_bytes: bytes, bank_name: str = "auto") -> Dict:
    """Parse bank statement PDF (stub implementation)"""
    # TODO: Implement bank-specific parsers
    # Different banks have different formats (HDFC, ICICI, SBI, Axis, etc.)
    
    return {
        "bank_name": "HDFC Bank",
        "account_number": "XXXX5678",
        "period_start": "2024-01-01",
        "period_end": "2024-12-31",
        "opening_balance": 2500000,
        "closing_balance": 3200000,
        "average_balance": 2850000,
        "total_credits": 45000000,
        "total_debits": 44300000,
        "bounce_count": 0,
        "transactions": [],
        "note": "[STUB] Bank statement parsing not yet implemented"
    }


def calculate_cashflow_metrics(transactions: List[Dict]) -> Dict:
    """Calculate cash flow metrics from transactions"""
    # TODO: Categorize and aggregate transactions
    
    operating_inflows = 0
    operating_outflows = 0
    financing_inflows = 0
    financing_outflows = 0
    investing_inflows = 0
    investing_outflows = 0
    
    for txn in transactions:
        # Categorize based on description (requires ML/rules)
        category = categorize_transaction(txn.get("description", ""))
        amount = txn.get("credit", 0) - txn.get("debit", 0)
        
        if category == "operating":
            if amount > 0:
                operating_inflows += amount
            else:
                operating_outflows += abs(amount)
        elif category == "financing":
            if amount > 0:
                financing_inflows += amount
            else:
                financing_outflows += abs(amount)
        elif category == "investing":
            if amount > 0:
                investing_inflows += amount
            else:
                investing_outflows += abs(amount)
    
    return {
        "operating_cashflow": operinflows - operating_outflows,
        "financing_cashflow": financing_inflows - financing_outflows,
        "investing_cashflow": investing_inflows - investing_outflows,
        "free_cashflow": (operating_inflows - operating_outflows) - (investing_outflows - investing_inflows),
        "note": "[STUB] Actual categorization requires transaction analysis"
    }


def categorize_transaction(description: str) -> str:
    """Categorize transaction (stub implementation)"""
    # TODO: Implement ML-based categorization or rule-based system
    
    description_lower = description.lower()
    
    if any(word in description_lower for word in ["salary", "revenue", "sales", "payment received"]):
        return "operating"
    elif any(word in description_lower for word in ["loan", "interest", "emi", "repayment"]):
        return "financing"
    elif any(word in description_lower for word in ["investment", "fd", "purchase of asset"]):
        return "investing"
    
    return "other"


def detect_suspicious_patterns(transactions: List[Dict]) -> List[Dict]:
    """Detect suspicious banking patterns (stub implementation)"""
    flags = []
    
    # TODO: Implement pattern detection:
    # 1. Round-tripping (money moving out and back in)
    # 2. Circular transactions
    # 3. Cash deposits exceeding limits
    # 4. Unusual large transactions
    # 5. Frequent bounced cheques
    # 6. Salary credit pattern breaks
    
    # Sample pattern detection
    large_cash_deposits = [
        txn for txn in transactions 
        if txn.get("credit", 0) > 1000000 and "cash" in txn.get("description", "").lower()
    ]
    
    if len(large_cash_deposits) > 3:
        flags.append({
            "pattern": "Frequent large cash deposits",
            "severity": "MEDIUM",
            "description": f"{len(large_cash_deposits)} cash deposits > INR 10 lakhs found. May indicate unaccounted income.",
            "transaction_count": len(large_cash_deposits),
        })
    
    # Check for bounced transactions
    bounced_txns = [
        txn for txn in transactions
        if "bounce" in txn.get("description", "").lower() or "return" in txn.get("description", "").lower()
    ]
    
    if len(bounced_txns) > 2:
        flags.append({
            "pattern": "Bounced transactions",
            "severity": "HIGH",
            "description": f"{len(bounced_txns)} bounced transactions indicate payment issues.",
            "transaction_count": len(bounced_txns),
        })
    
    if not flags:
        flags.append({
            "pattern": "No suspicious patterns",
            "severity": "LOW",
            "description": "Bank statement analysis complete. No red flags detected.",
            "transaction_count": 0,
        })
    
    return flags


def analyze_working_capital(bank_data: Dict, financial_data: Dict) -> Dict:
    """Analyze working capital cycle (stub implementation)"""
    avg_balance = bank_data.get("average_balance", 0)
    revenue = financial_data.get("revenue", 0)
    
    # Working capital as % of revenue
    wc_percentage = (avg_balance / revenue * 100) if revenue > 0 else 0
    
    return {
        "average_bank_balance": avg_balance,
        "as_percentage_of_revenue": wc_percentage,
        "assessment": "Adequate" if wc_percentage > 5 else "Insufficient",
        "note": "[STUB] Full working capital cycle analysis not yet implemented"
    }


def calculate_banking_conduct_score(bank_data: Dict, suspicious_patterns: List[Dict]) -> int:
    """Calculate banking conduct score (0-100)"""
    score = 100
    
    # Deduct for bounces
    bounce_count = bank_data.get("bounce_count", 0)
    score -= bounce_count * 10
    
    # Deduct for suspicious patterns
    high_severity_patterns = [p for p in suspicious_patterns if p.get("severity") == "HIGH"]
    score -= len(high_severity_patterns) * 15
    
    medium_severity_patterns = [p for p in suspicious_patterns if p.get("severity") == "MEDIUM"]
    score -= len(medium_severity_patterns) * 5
    
    # Ensure score is between 0-100
    return max(0, min(100, score))
