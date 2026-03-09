"""
Data ingestion API - uploads financial documents, company data, financial statements.
Supports JSON, CSV for structured data and PDF for financial documents.
"""
import json
import csv
import io
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.core.graph_db import (
    get_driver,
    ingest_company,
    ingest_promoter,
    ingest_financial_statement,
    ingest_bank_statement,
    ingest_itr,
    ingest_litigation,
    ingest_news_article,
)
from app.core.pdf_processor import (
    parse_bank_statement_pdf,
    parse_itr_pdf,
    parse_financial_statement_pdf,
)

router = APIRouter()


def _parse_upload(file_content: bytes, filename: str) -> list[dict]:
    """Parse uploaded JSON or CSV file."""
    text = file_content.decode("utf-8")
    if filename.endswith(".json"):
        data = json.loads(text)
    elif filename.endswith(".csv"):
        reader = csv.DictReader(io.StringIO(text))
        data = list(reader)
    else:
        raise HTTPException(status_code=400, detail="Only JSON and CSV files supported")
    if not isinstance(data, list):
        data = [data]
    return data


@router.post("/upload")
async def upload_data(
    file: UploadFile = File(...),
    data_type: str = "COMPANY",  # COMPANY, PROMOTER, FINANCIAL_STATEMENT, BANK_STATEMENT, ITR, LITIGATION, NEWS
    year: str = "FY2024",
):
    """Upload structured financial data (JSON/CSV) or PDF documents."""
    
    content = await file.read()
    
    # Handle PDF uploads
    if file.filename.endswith(".pdf"):
        if data_type == "BANK_STATEMENT":
            parsed_data = parse_bank_statement_pdf(content)
        elif data_type == "ITR":
            parsed_data = parse_itr_pdf(content)
        elif data_type in ("BALANCE_SHEET", "PNL", "CASHFLOW"):
            parsed_data = parse_financial_statement_pdf(content, data_type)
        else:
            raise HTTPException(status_code=400, detail=f"PDF upload not supported for {data_type}")
        
        # Store parsed PDF data as single record
        data = [parsed_data]
    else:
        # Handle structured JSON/CSV uploads
        data = _parse_upload(content, file.filename)
    
    driver = get_driver()
    ingested = 0

    with driver.session() as session:
        for record in data:
            # Convert string numbers to float where applicable
            for field in ["revenue", "profit", "total_assets", "total_liabilities", "paid_up_capital",
                         "net_worth", "total_income", "total_deductions", "tax_paid",
                         "opening_balance", "closing_balance", "total_credits", "total_debits"]:
                if field in record and isinstance(record[field], str):
                    try:
                        record[field] = float(record[field])
                    except ValueError:
                        pass
            
            # Route to appropriate ingest function
            if data_type == "COMPANY":
                session.execute_write(ingest_company, record)
            elif data_type == "PROMOTER":
                session.execute_write(ingest_promoter, record)
            elif data_type == "FINANCIAL_STATEMENT":
                session.execute_write(ingest_financial_statement, record, year)
            elif data_type == "BANK_STATEMENT":
                session.execute_write(ingest_bank_statement, record.get("cin"), record, year)
            elif data_type == "ITR":
                session.execute_write(ingest_itr, record.get("cin"), record, year)
            elif data_type == "LITIGATION":
                session.execute_write(ingest_litigation, record)
            elif data_type == "NEWS":
                session.execute_write(ingest_news_article, record)
            else:
                raise HTTPException(status_code=400, detail=f"Invalid data_type: {data_type}")
            
            ingested += 1

    return {
        "status": "success",
        "data_type": data_type,
        "year": year,
        "records_ingested": ingested,
        "file_type": "PDF" if file.filename.endswith(".pdf") else "JSON/CSV",
    }


@router.post("/upload-companies")
async def upload_companies(file: UploadFile = File(...)):
    """Upload company master data (CIN, name, industry, etc.)."""
    content = await file.read()
    data = _parse_upload(content, file.filename)

    driver = get_driver()
    ingested = 0

    with driver.session() as session:
        for record in data:
            record.setdefault("status", "Active")
            record.setdefault("incorporation_date", "2020-01-01")
            session.execute_write(ingest_company, record)
            ingested += 1

    return {"status": "success", "companies_ingested": ingested}


@router.post("/upload-promoters")
async def upload_promoters(file: UploadFile = File(...)):
    """Upload promoter/director data."""
    content = await file.read()
    data = _parse_upload(content, file.filename)

    driver = get_driver()
    ingested = 0

    with driver.session() as session:
        for record in data:
            session.execute_write(ingest_promoter, record)
            ingested += 1

    return {"status": "success", "promoters_ingested": ingested}
