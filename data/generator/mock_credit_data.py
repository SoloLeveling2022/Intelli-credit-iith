"""
Generate mock credit appraisal data for testing.
Creates companies, promoters, financial statements, bank statements, ITRs, and loan applications.
"""
import json
import random
from datetime import datetime, timedelta
from pathlib import Path

# Sample data
INDUSTRIES = ["Manufacturing", "Services", "Trading", "IT/Software", "Textiles", "Pharmaceuticals", 
              "Construction", "Real Estate", "Food Processing", "Automobiles"]

COMPANY_NAMES = [
    "TechCorp Solutions", "Global Trading Ltd", "Apex Manufacturing", "Prime Textiles", 
    "Urban Realty Group", "Pharma Innovations", "AutoParts International", "FoodTech Industries",
    "BuildRight Construction", "DataSoft Technologies", "Fashion Hub Pvt Ltd", "AgriPro Exports",
    "Metro Infrastructure", "HealthCare Systems", "Green Energy Solutions"
]

PROMOTER_NAMES = [
    "Rajesh Kumar", "Priya Sharma", "Amit Patel", "Sunita Reddy", "Vikram Singh",
    "Anjali Mehta", "Suresh Rao", "Kavita Joshi", "Arun Verma", "Deepa Gupta",
    "Manoj Agarwal", "Sneha Desai", "Ramesh Nair", "Pooja Iyer", "Karthik Pillai"
]

OUTPUT_DIR = Path(__file__).parent.parent / "sample"
OUTPUT_DIR.mkdir(exist_ok=True)


def generate_cin(index):
    """Generate a fake CIN (Corporate Identification Number)."""
    # Format: U12345MH2020PTC123456
    state_code = random.choice(["MH", "DL", "KA", "TN", "GJ"])
    year = random.randint(2015, 2023)
    number = str(100000 + index).zfill(6)
    return f"U{random.randint(10000, 99999)}{state_code}{year}PTC{number}"


def generate_pan(index):
    """Generate a fake PAN (Permanent Account Number)."""
    # Format: ABCDE1234F
    letters = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=5))
    digits = str(1000 + index).zfill(4)
    last_letter = random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    return f"{letters}{digits}{last_letter}"


def generate_companies(count=15):
    """Generate mock companies."""
    companies = []
    for i in range(count):
        cin = generate_cin(i)
        companies.append({
            "cin": cin,
            "name": COMPANY_NAMES[i % len(COMPANY_NAMES)],
            "industry": INDUSTRIES[i % len(INDUSTRIES)],
            "incorporation_date": f"{random.randint(2010, 2023)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
            "registered_address": f"{random.randint(1, 999)}, {random.choice(['MG Road', 'Park Street', 'Brigade Road'])}, {random.choice(['Mumbai', 'Delhi', 'Bangalore', 'Chennai'])}",
            "status": "Active",
            "paid_up_capital": round(random.uniform(1000000, 50000000), 2),
        })
    return companies


def generate_promoters(companies):
    """Generate mock promoters for companies."""
    promoters = []
    for i, company in enumerate(companies):
        # 1-3 promoters per company
        num_promoters = random.randint(1, 3)
        for j in range(num_promoters):
            promoters.append({
                "pan": generate_pan(i * 10 + j),
                "name": PROMOTER_NAMES[(i * 3 + j) % len(PROMOTER_NAMES)],
                "cin": company["cin"],
                "shareholding": round(random.uniform(20, 60), 2) if j == 0 else round(random.uniform(5, 30), 2),
                "designation": "Managing Director" if j == 0 else "Director",
            })
    return promoters


def generate_financial_statements(companies):
    """Generate mock financial statements for companies."""
    statements = []
    for company in companies:
        for year in ["FY2022", "FY2023", "FY2024"]:
            base_revenue = random.uniform(10000000, 500000000)
            growth = random.uniform(-0.1, 0.3)  # -10% to +30% growth
            
            revenue = base_revenue * (1 + growth * (int(year[2:]) - 2022))
            profit_margin = random.uniform(0.05, 0.20)
            
            statements.append({
                "cin": company["cin"],
                "year": year,
                "document_type": "BALANCE_SHEET",
                "revenue": round(revenue, 2),
                "profit": round(revenue * profit_margin, 2),
                "total_assets": round(revenue * random.uniform(0.8, 1.5), 2),
                "total_liabilities": round(revenue * random.uniform(0.3, 0.9), 2),
                "net_worth": round(revenue * random.uniform(0.2, 0.8), 2),
                "current_assets": round(revenue * random.uniform(0.3, 0.6), 2),
                "current_liabilities": round(revenue * random.uniform(0.2, 0.5), 2),
            })
    return statements


def generate_bank_statements(companies):
    """Generate mock bank statement summaries."""
    statements = []
    for company in companies:
        for year in ["FY2023", "FY2024"]:
            avg_monthly_revenue = random.uniform(1000000, 40000000)
            
            statements.append({
                "cin": company["cin"],
                "year": year,
                "bank_name": random.choice(["HDFC Bank", "ICICI Bank", "SBI", "Axis Bank"]),
                "account_number": f"*****{random.randint(1000, 9999)}",
                "opening_balance": round(random.uniform(100000, 5000000), 2),
                "closing_balance": round(random.uniform(100000, 5000000), 2),
                "total_credits": round(avg_monthly_revenue * 12, 2),
                "total_debits": round(avg_monthly_revenue * 12 * random.uniform(0.85, 0.95), 2),
                "average_monthly_balance": round(random.uniform(500000, 10000000), 2),
                "cheque_bounces": random.randint(0, 3),
                "od_limit": round(random.uniform(0, 5000000), 2),
            })
    return statements


def generate_itrs(companies):
    """Generate mock ITR (Income Tax Return) filings."""
    itrs = []
    for company in companies:
        for year in ["FY2022", "FY2023", "FY2024"]:
            revenue = random.uniform(10000000, 500000000)
            
            itrs.append({
                "cin": company["cin"],
                "year": year,
                "total_income": round(revenue, 2),
                "total_deductions": round(revenue * random.uniform(0.6, 0.8), 2),
                "taxable_income": round(revenue * random.uniform(0.15, 0.3), 2),
                "tax_paid": round(revenue * random.uniform(0.04, 0.08), 2),
                "filing_date": f"{int(year[2:]) + 2000}-09-{random.randint(15, 30)}",
                "status": "Filed",
            })
    return itrs


def generate_loan_applications(companies):
    """Generate mock loan applications."""
    applications = []
    for i, company in enumerate(companies):
        if random.random() < 0.7:  # 70% of companies apply for loans
            requested = random.uniform(5000000, 100000000)
            approved_pct = random.uniform(0.5, 1.0)
            
            applications.append({
                "application_id": f"LOAN{2024}{str(i+1).zfill(5)}",
                "cin": company["cin"],
                "loan_purpose": random.choice(["Working Capital", "Term Loan", "Equipment Finance", "Trade Finance"]),
                "requested_amount": round(requested, 2),
                "approved_amount": round(requested * approved_pct, 2),
                "interest_rate": round(random.uniform(9.0, 15.0), 2),
                "tenure_months": random.choice([12, 24, 36, 48, 60]),
                "application_date": "2024-01-15",
                "decision": random.choice(["APPROVED", "APPROVED", "CONDITIONAL", "REJECTED"]),
                "decision_date": "2024-02-20",
            })
    return applications


def generate_litigation(companies):
    """Generate mock litigation cases."""
    cases = []
    for company in companies:
        if random.random() < 0.3:  # 30% of companies have litigation
            num_cases = random.randint(1, 2)
            for j in range(num_cases):
                cases.append({
                    "cin": company["cin"],
                    "case_number": f"CS/{random.randint(100, 999)}/{random.randint(2020, 2024)}",
                    "court": random.choice(["Delhi High Court", "Bombay High Court", "Karnataka High Court", "District Court"]),
                    "case_type": random.choice(["Civil Suit", "Tax Dispute", "Contract Dispute", "Recovery Suit"]),
                    "amount": round(random.uniform(500000, 10000000), 2),
                    "status": random.choice(["Pending", "Pending", "Disposed"]),
                    "filing_date": f"{random.randint(2020, 2024)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
                })
    return cases


def generate_news_articles(companies):
    """Generate mock news articles."""
    articles = []
    sentiments = ["positive", "neutral", "negative"]
    headlines = [
        "{} reports strong quarterly results",
        "{} launches new product line",
        "{} faces regulatory scrutiny",
        "{} expands operations to new markets",
        "{} appoints new leadership team",
        "Industry experts praise {}'s innovation",
        "{} faces worker union protests",
        "{} wins major contract from government"
    ]
    
    for company in companies:
        if random.random() < 0.5:  # 50% of companies have news
            num_articles = random.randint(1, 3)
            for j in range(num_articles):
                headline_template = random.choice(headlines)
                sentiment = random.choice(sentiments)
                
                articles.append({
                    "cin": company["cin"],
                    "company_name": company["name"],
                    "headline": headline_template.format(company["name"]),
                    "source": random.choice(["Economic Times", "Business Standard", "Mint", "Financial Express"]),
                    "published_date": f"2024-{random.randint(1, 3):02d}-{random.randint(1, 28):02d}",
                    "sentiment": sentiment,
                    "relevance_score": round(random.uniform(0.5, 1.0), 2),
                })
    return articles


def main():
    print("Generating mock credit appraisal data...")
    
    # Generate all data
    companies = generate_companies(15)
    promoters = generate_promoters(companies)
    financial_statements = generate_financial_statements(companies)
    bank_statements = generate_bank_statements(companies)
    itrs = generate_itrs(companies)
    loan_applications = generate_loan_applications(companies)
    litigation = generate_litigation(companies)
    news = generate_news_articles(companies)
    
    # Save to JSON files
    datasets = {
        "companies.json": companies,
        "promoters.json": promoters,
        "financial_statements.json": financial_statements,
        "bank_statements.json": bank_statements,
        "itrs.json": itrs,
        "loan_applications.json": loan_applications,
        "litigation.json": litigation,
        "news_articles.json": news,
    }
    
    for filename, data in datasets.items():
        filepath = OUTPUT_DIR / filename
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        print(f"✓ Generated {filepath} ({len(data)} records)")
    
    print(f"\nTotal records: {sum(len(d) for d in datasets.values())}")
    print(f"Output directory: {OUTPUT_DIR.absolute()}")


if __name__ == "__main__":
    main()
