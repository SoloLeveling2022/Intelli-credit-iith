from pydantic import BaseModel, Field
from datetime import date, datetime
from enum import Enum
from typing import Optional, Literal


class RiskIndicator(str, Enum):
    """Types of risk indicators found during credit analysis"""
    REVENUE_INFLATION = "REVENUE_INFLATION"
    CASHFLOW_NEGATIVE = "CASHFLOW_NEGATIVE"
    LITIGATION_FOUND = "LITIGATION_FOUND"
    DEBT_COVENANT_BREACH = "DEBT_COVENANT_BREACH"
    RELATED_PARTY_TRANSACTIONS = "RELATED_PARTY_TRANSACTIONS"
    AUDIT_QUALIFICATION = "AUDIT_QUALIFICATION"
    DECLINING_MARGINS = "DECLINING_MARGINS"
    WORKING_CAPITAL_SHORTAGE = "WORKING_CAPITAL_SHORTAGE"
    SHELL_COMPANY_INDICATOR = "SHELL_COMPANY_INDICATOR"
    PROMOTER_DEFAULT_HISTORY = "PROMOTER_DEFAULT_HISTORY"
    CIRCULAR_TRANSACTIONS = "CIRCULAR_TRANSACTIONS"
    SUSPICIOUS_BANK_ACTIVITY = "SUSPICIOUS_BANK_ACTIVITY"


class Severity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class CreditGrade(str, Enum):
    """Credit rating grades"""
    AAA = "AAA"
    AA = "AA"
    A = "A"
    BBB = "BBB"
    BB = "BB"
    B = "B"
    C = "C"
    D = "D"


class DocumentType(str, Enum):
    """Types of financial documents"""
    BANK_STATEMENT = "BANK_STATEMENT"
    ITR = "ITR"  # Income Tax Return
    BALANCE_SHEET = "BALANCE_SHEET"
    PROFIT_LOSS = "PROFIT_LOSS"
    CASHFLOW_STATEMENT = "CASHFLOW_STATEMENT"
    RATING_REPORT = "RATING_REPORT"
    ANNUAL_REPORT = "ANNUAL_REPORT"
    AUDIT_REPORT = "AUDIT_REPORT"
    GST_RETURN = "GST_RETURN"
    SANCTION_LETTER = "SANCTION_LETTER"
    LEGAL_NOTICE = "LEGAL_NOTICE"
    BOARD_MINUTES = "BOARD_MINUTES"


class Company(BaseModel):
    """Company/Borrower profile"""
    company_id: str = Field(..., description="Unique identifier (PAN or CIN)")
    legal_name: str
    trade_name: Optional[str] = None
    cin: Optional[str] = Field(None, pattern=r"^[A-Z]{1}[0-9]{5}[A-Z]{2}[0-9]{4}[A-Z]{3}[0-9]{6}$")
    pan: str = Field(..., pattern=r"^[A-Z]{5}[0-9]{4}[A-Z]{1}$")
    industry: str
    incorporation_date: Optional[date] = None
    registration_type: str = "Private Limited"
    status: str = "Active"
    address: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None


class Promoter(BaseModel):
    """Company promoter/director information"""
    promoter_id: str
    name: str
    pan: Optional[str] = Field(None, pattern=r"^[A-Z]{5}[0-9]{4}[A-Z]{1}$")
    din: Optional[str] = Field(None, description="Director Identification Number")
    company_id: str
    designation: str = "Director"
    stake_percentage: float = 0.0
    cibil_score: Optional[int] = Field(None, ge=300, le=900)
    default_history: bool = False


class FinancialDocument(BaseModel):
    """Financial document (bank statement, ITR, financial statement, etc.)"""
    document_id: str
    document_type: DocumentType
    company_id: str
    document_date: date
    period_start: Optional[date] = None
    period_end: Optional[date] = None
    amount: Optional[float] = None
    currency: str = "INR"
    source: str = "uploaded"
    file_path: Optional[str] = None
    parsed_data: Optional[dict] = None


class BankStatement(BaseModel):
    """Bank statement model"""
    statement_id: str
    company_id: str
    bank_name: str
    account_number: str
    period_start: date
    period_end: date
    opening_balance: float
    closing_balance: float
    total_credits: float
    total_debits: float
    average_balance: float
    bounce_count: int = 0
    transactions: list[dict] = []


class ITR(BaseModel):
    """Income Tax Return"""
    itr_id: str
    company_id: str
    assessment_year: str  # Format: "2025-26"
    filing_date: date
    total_income: float
    tax_paid: float
    refund_amount: float = 0.0
    profit_before_tax: float
    revenue: float
    status: str = "Filed"


class FinancialStatement(BaseModel):
    """Balance Sheet, P&L, Cash Flow Statement"""
    statement_id: str
    company_id: str
    statement_type: Literal["balance_sheet", "profit_loss", "cashflow"]
    financial_year: str  # Format: "2024-25"
    date_of_statement: date
    revenue: Optional[float] = None
    profit_after_tax: Optional[float] = None
    total_assets: Optional[float] = None
    total_liabilities: Optional[float] = None
    equity: Optional[float] = None
    current_assets: Optional[float] = None
    current_liabilities: Optional[float] = None
    long_term_debt: Optional[float] = None
    ebitda: Optional[float] = None


class RatingReport(BaseModel):
    """Credit rating from agencies"""
    report_id: str
    company_id: str
    agency: str  # CRISIL, ICRA, CARE, etc.
    rating: str
    outlook: str = "Stable"
    rating_date: date
    validity_date: Optional[date] = None


class Litigation(BaseModel):
    """Litigation/legal case"""
    case_id: str
    company_id: Optional[str] = None
    promoter_id: Optional[str] = None
    case_number: str
    case_type: str  # Civil, Criminal, Tax, Labour
    court: str
    filing_date: date
    status: str = "Pending"
    amount_involved: float = 0.0
    description: str


class NewsArticle(BaseModel):
    """News article about company/promoter"""
    article_id: str
    company_id: Optional[str] = None
    promoter_id: Optional[str] = None
    title: str
    source: str
    published_date: date
    url: Optional[str] = None
    sentiment: Literal["positive", "negative", "neutral"] = "neutral"
    summary: str


class SiteVisit(BaseModel):
    """Site visit/due diligence notes"""
    visit_id: str
    company_id: str
    visit_date: date
    visited_by: str
    location: str
    capacity_utilization: Optional[float] = Field(None, ge=0, le=100)
    observations: str
    photos: list[str] = []
    risk_adjustment: Literal["positive", "negative", "neutral"] = "neutral"


class RiskAssessmentResult(BaseModel):
    """Result of credit risk analysis"""
    id: str
    indicator_type: RiskIndicator
    severity: Severity
    company_id: str
    document_id: Optional[str] = None
    field_name: Optional[str] = None
    expected_value: Optional[str] = None
    actual_value: Optional[str] = None
    amount_impact: float = 0.0
    description: str
    detected_date: datetime


class FiveCsScore(BaseModel):
    """Five C's of Credit scoring"""
    character_score: float = Field(..., ge=0, le=100)
    capacity_score: float = Field(..., ge=0, le=100)
    capital_score: float = Field(..., ge=0, le=100)
    collateral_score: float = Field(..., ge=0, le=100)
    conditions_score: float = Field(..., ge=0, le=100)
    character_factors: list[str] = []
    capacity_factors: list[str] = []
    capital_factors: list[str] = []
    collateral_factors: list[str] = []
    conditions_factors: list[str] = []


class CreditRisk(BaseModel):
    """Credit risk assessment for a company"""
    company_id: str
    legal_name: str
    risk_score: float = Field(..., ge=0, le=100)
    risk_level: RiskLevel
    credit_grade: CreditGrade
    five_cs: FiveCsScore
    loan_amount_recommended: Optional[float] = None
    interest_rate_recommended: Optional[float] = None
    risk_factors: list[str] = []
    mitigation_measures: list[str] = []
    assessment_date: datetime


class CAMSection(BaseModel):
    """Credit Appraisal Memo section"""
    id: str
    application_id: str
    section_type: Literal[
        "executive_summary",
        "company_profile",
        "promoter_background",
        "financial_analysis",
        "five_cs_analysis",
        "industry_analysis",
        "risk_assessment",
        "collateral_evaluation",
        "recommendation"
    ]
    content: str
    data_points: list[dict] = []
    recommendation: str = ""
    generated_at: datetime


class LoanApplication(BaseModel):
    """Loan application"""
    application_id: str
    company_id: str
    loan_amount_requested: float
    loan_purpose: str
    loan_tenure_months: int
    collateral_offered: Optional[str] = None
    application_date: date
    status: Literal["submitted", "under_review", "approved", "rejected", "conditional"] = "submitted"


class CreditDecision(BaseModel):
    """Final credit decision"""
    decision_id: str
    application_id: str
    company_id: str
    decision: Literal["APPROVED", "REJECTED", "CONDITIONAL"]
    loan_amount_approved: Optional[float] = None
    interest_rate: Optional[float] = None
    tenure_months: Optional[int] = None
    conditions: list[str] = []
    justification: str
    decided_by: str
    decision_date: datetime


class AppraisalRequest(BaseModel):
    """Request to run credit appraisal"""
    application_id: str
    company_id: Optional[str] = None
    force: bool = False


class DashboardStats(BaseModel):
    """Dashboard statistics"""
    total_companies: int
    total_applications: int
    total_documents: int
    high_risk_companies: int
    total_credit_exposure: float
    pending_appraisals: int
    indicator_breakdown: dict[str, int]
    severity_breakdown: dict[str, int]
    grade_distribution: dict[str, int]


class NotificationSettings(BaseModel):
    channel: Literal["email", "webhook"] = "email"
    enabled: bool = True
    email_to: Optional[str] = None
    webhook_url: Optional[str] = None
    notify_on_critical: bool = True
