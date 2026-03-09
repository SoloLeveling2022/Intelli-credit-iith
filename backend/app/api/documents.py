"""
Document processing API - handles PDF uploads for bank statements, ITRs, financial statements.
"""
import uuid
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from app.core.pdf_processor import (
    extract_text_from_pdf,
    parse_bank_statement_pdf,
    parse_itr_pdf,
    parse_financial_statement_pdf,
)
from app.core.graph_db import ingest_bank_statement, ingest_itr, ingest_financial_statement

router = APIRouter()

# In-memory document store (for demo)
_document_store: dict[str, dict] = {}


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    cin: str = Query(...),
    document_type: str = Query(...),  # BANK_STATEMENT, ITR, BALANCE_SHEET, PNL, CASHFLOW
    year: str = Query(...),  # FY2023, FY2024, etc.
):
    """Upload and parse financial documents (PDF)."""
    
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    if document_type not in ("BANK_STATEMENT", "ITR", "BALANCE_SHEET", "PNL", "CASHFLOW", "AUDIT_REPORT"):
        raise HTTPException(status_code=400, detail=f"Invalid document_type: {document_type}")
    
    try:
        content = await file.read()
        
        # Extract text first
        extracted_text = extract_text_from_pdf(content)
        
        # Parse based on document type
        if document_type == "BANK_STATEMENT":
            parsed_data = parse_bank_statement_pdf(content)
            ingest_bank_statement(cin, parsed_data, year)
            
        elif document_type == "ITR":
            parsed_data = parse_itr_pdf(content)
            ingest_itr(cin, parsed_data, year)
            
        elif document_type in ("BALANCE_SHEET", "PNL", "CASHFLOW", "AUDIT_REPORT"):
            parsed_data = parse_financial_statement_pdf(content, document_type)
            ingest_financial_statement(cin, parsed_data, document_type, year)
            
        else:
            parsed_data = {"raw_text": extracted_text[:1000]}  # First 1000 chars
        
        # Store metadata
        doc_id = str(uuid.uuid4())
        _document_store[doc_id] = {
            "id": doc_id,
            "cin": cin,
            "filename": file.filename,
            "document_type": document_type,
            "year": year,
            "uploaded_at": datetime.now().isoformat(),
            "size_bytes": len(content),
            "parsed_data": parsed_data,
        }
        
        return {
            "status": "success",
            "document_id": doc_id,
            "cin": cin,
            "document_type": document_type,
            "year": year,
            "parsed_fields": len(parsed_data) if isinstance(parsed_data, dict) else 0,
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document processing failed: {str(e)}")


@router.get("/list")
async def list_documents(cin: str = Query(None), document_type: str = Query(None)):
    """List uploaded documents with optional filtering."""
    results = list(_document_store.values())
    
    if cin:
        results = [d for d in results if d["cin"] == cin]
    if document_type:
        results = [d for d in results if d["document_type"] == document_type]
    
    return {
        "total": len(results),
        "documents": [{
            "id": d["id"],
            "cin": d["cin"],
            "filename": d["filename"],
            "document_type": d["document_type"],
            "year": d["year"],
            "uploaded_at": d["uploaded_at"],
            "size_bytes": d["size_bytes"],
        } for d in results]
    }


@router.get("/{document_id}")
async def get_document_details(document_id: str):
    """Get detailed parsed data for a specific document."""
    if document_id not in _document_store:
        raise HTTPException(status_code=404, detail=f"Document {document_id} not found")
    return _document_store[document_id]


@router.delete("/{document_id}")
async def delete_document(document_id: str):
    """Delete a document from the system."""
    if document_id not in _document_store:
        raise HTTPException(status_code=404, detail=f"Document {document_id} not found")
    
    deleted = _document_store.pop(document_id)
    return {
        "status": "deleted",
        "document_id": document_id,
        "filename": deleted["filename"],
    }


@router.post("/batch-upload")
async def batch_upload_documents(
    files: list[UploadFile] = File(...),
    cin: str = Query(...),
):
    """Upload multiple documents at once (for complete loan application package)."""
    results = []
    errors = []
    
    for file in files:
        try:
            # Auto-detect document type from filename patterns
            filename_lower = file.filename.lower()
            if "bank" in filename_lower or "statement" in filename_lower:
                doc_type = "BANK_STATEMENT"
            elif "itr" in filename_lower or "tax" in filename_lower:
                doc_type = "ITR"
            elif "balance" in filename_lower or "bs" in filename_lower:
                doc_type = "BALANCE_SHEET"
            elif "pnl" in filename_lower or "profit" in filename_lower or "loss" in filename_lower:
                doc_type = "PNL"
            elif "cashflow" in filename_lower or "cash" in filename_lower:
                doc_type = "CASHFLOW"
            else:
                doc_type = "OTHER"
            
            # Try to extract year from filename (e.g., "2023", "FY2024")
            import re
            year_match = re.search(r'(FY)?(\d{4})', file.filename)
            year = f"FY{year_match.group(2)}" if year_match else "FY2024"
            
            content = await file.read()
            extracted_text = extract_text_from_pdf(content)
            
            doc_id = str(uuid.uuid4())
            _document_store[doc_id] = {
                "id": doc_id,
                "cin": cin,
                "filename": file.filename,
                "document_type": doc_type,
                "year": year,
                "uploaded_at": datetime.now().isoformat(),
                "size_bytes": len(content),
                "parsed_data": {"raw_text": extracted_text[:500]},
            }
            
            results.append({
                "document_id": doc_id,
                "filename": file.filename,
                "document_type": doc_type,
                "status": "success",
            })
            
        except Exception as e:
            errors.append({
                "filename": file.filename,
                "error": str(e),
            })
    
    return {
        "status": "completed",
        "cin": cin,
        "uploaded": len(results),
        "failed": len(errors),
        "results": results,
        "errors": errors,
    }
