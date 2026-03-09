"""CAM (Credit Appraisal Memo) Generator - Creates formal credit appraisal documents"""

import io
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
import os


TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")


def generate_cam_document(
    company_name: str,
    application_id: str,
    loan_amount: float,
    five_cs_analysis: dict,
    financial_analysis: dict,
    risk_indicators: list,
    decision: str,
    interest_rate: float,
    justification: str,
) -> bytes:
    """Generate complete CAM document as PDF (stub implementation)"""
    
    # TODO: Implement full CAM generation with python-docx or Jinja2 + xhtml2pdf
    # Template structure:
    # 1. Executive Summary
    # 2. Company Profile
    # 3. Promoter Background
    # 4. Financial Analysis (3 years trend)
    # 5. Five C's Assessment
    # 6. Industry & Market Analysis
    # 7. Risk Assessment
    # 8. Collateral Evaluation
    # 9. Terms & Conditions
    # 10. Recommendation
    
    html_content = f"""
    <html>
    <head>
        <title>Credit Appraisal Memo - {company_name}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; }}
            h2 {{ color: #34495e; margin-top: 30px; }}
            table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
            th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
            th {{ background-color: #3498db; color: white; }}
            .decision-approved {{ color: green; font-weight: bold; }}
            .decision-rejected {{ color: red; font-weight: bold; }}
            .decision-conditional {{ color: orange; font-weight: bold; }}
        </style>
    </head>
    <body>
        <h1>Credit Appraisal Memo</h1>
        <p><strong>Generated:</strong> {datetime.now().strftime("%B %d, %Y")}</p>
        <p><strong>Application ID:</strong> {application_id}</p>
       
        <h2>1. Executive Summary</h2>
        <table>
            <tr><th>Borrower</th><td>{company_name}</td></tr>
            <tr><th>Loan Amount Requested</th><td>INR {loan_amount:,.2f}</td></tr>
            <tr><th>Recommended Interest Rate</th><td>{interest_rate:.2f}%</td></tr>
            <tr><th>Decision</th><td class="decision-{decision.lower()}">{decision}</td></tr>
        </table>
        
        <h2>2. Company Profile</h2>
        <p>[STUB] Company background, business model, management team would appear here.</p>
        
        <h2>3. Promoter Background</h2>
        <p>[STUB] Detailed promoter analysis, track record, other ventures would appear here.</p>
        
        <h2>4. Financial Analysis</h2>
        <p>[STUB] 3-year financial trends, ratio analysis, cash flow assessment would appear here.</p>
        <table>
            <tr><th>Metric</th><th>FY 2024</th><th>FY 2023</th><th>FY 2022</th></tr>
            <tr><td>Revenue</td><td>[Data]</td><td>[Data]</td><td>[Data]</td></tr>
            <tr><td>EBITDA</td><td>[Data]</td><td>[Data]</td><td>[Data]</td></tr>
            <tr><td>PAT</td><td>[Data]</td><td>[Data]</td><td>[Data]</td></tr>
        </table>
        
        <h2>5. Five C's of Credit Assessment</h2>
        <table>
            <tr><th>Factor</th><th>Score</th><th>Assessment</th></tr>
            <tr><td>Character</td><td>{five_cs_analysis.get('character_score', 0):.1f}/100</td><td>{', '.join(five_cs_analysis.get('character_factors', []))}</td></tr>
            <tr><td>Capacity</td><td>{five_cs_analysis.get('capacity_score', 0):.1f}/100</td><td>{', '.join(five_cs_analysis.get('capacity_factors', []))}</td></tr>
            <tr><td>Capital</td><td>{five_cs_analysis.get('capital_score', 0):.1f}/100</td><td>{', '.join(five_cs_analysis.get('capital_factors', []))}</td></tr>
            <tr><td>Collateral</td><td>{five_cs_analysis.get('collateral_score', 0):.1f}/100</td><td>{', '.join(five_cs_analysis.get('collateral_factors', []))}</td></tr>
            <tr><td>Conditions</td><td>{five_cs_analysis.get('conditions_score', 0):.1f}/100</td><td>{', '.join(five_cs_analysis.get('conditions_factors', []))}</td></tr>
        </table>
        
        <h2>6. Industry Analysis</h2>
        <p>[STUB] Sector outlook, competitive position, market opportunities/threats would appear here.</p>
        
        <h2>7. Risk Assessment</h2>
        <p><strong>Risk Indicators Found:</strong> {len(risk_indicators)}</p>
        <ul>
            {"".join([f"<li>{ind.get('description', '')}</li>" for ind in risk_indicators[:5]])}
        </ul>
        
        <h2>8. Collateral Evaluation</h2>
        <p>[STUB] Asset valuation, security coverage ratio would appear here.</p>
        
        <h2>9. Proposed Terms & Conditions</h2>
        <ul>
            <li>Loan Amount: INR {loan_amount:,.2f}</li>
            <li>Interest Rate: {interest_rate:.2f}% per annum</li>
            <li>Tenure: [To be finalized]</li>
            <li>Security: [To be specified]</li>
        </ul>
        
        <h2>10. Recommendation</h2>
        <p class="decision-{decision.lower()}"><strong>{decision}</strong></p>
        <p>{justification}</p>
        
        <hr style="margin-top: 50px;">
        <p><em>Note: This is a stub implementation. Full CAM generation with all sections and proper formatting to be implemented.</em></p>
    </body>
    </html>
    """
    
    # TODO: Convert HTML to PDF using xhtml2pdf or weasyprint
    # from xhtml2pdf import pisa
    # buffer = io.BytesIO()
    # pisa.CreatePDF(io.StringIO(html_content), dest=buffer)
    # return buffer.getvalue()
    
    # For now, return HTML as bytes
    return html_content.encode('utf-8')


def generate_cam_section(
    section_type: str,
    company_data: dict,
    financial_data: dict = None,
    risk_data: dict = None
) -> str:
    """Generate individual CAM section (stub implementation)"""
    
    sections = {
        "executive_summary": f"[STUB] Executive summary for {company_data.get('company_name', 'Company')} would be generated here with key highlights and recommendation.",
        "company_profile": f"[STUB] Detailed company profile including history, business model, products/services, management team.",
        "promoter_background": f"[STUB] Promoter analysis including educational background, business experience, track record, other ventures.",
        "financial_analysis": f"[STUB] Comprehensive 3-year financial analysis with ratios, trends, and peer benchmarking.",
        "five_cs_analysis": f"[STUB] Detailed Five C's assessment with supporting data and analysis.",
        "industry_analysis": f"[STUB] Industry overview, market size, growth trends, competitive landscape, regulatory environment.",
        "risk_assessment": f"[STUB] Comprehensive risk evaluation covering credit risk, operational risk, market risk, mitigants.",
        "collateral_evaluation": f"[STUB] Asset valuation, security adequacy, legal enforceability assessment.",
        "recommendation": f"[STUB] Final credit recommendation with clear justification and proposed terms.",
    }
    
    return sections.get(section_type, "[STUB] Section content to be generated")
