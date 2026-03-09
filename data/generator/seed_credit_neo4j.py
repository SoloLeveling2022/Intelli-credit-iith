"""
Seed Neo4j with mock credit appraisal data via the FastAPI backend.
Uploads companies, promoters, financial statements, bank statements, ITRs, loan applications, and news.
"""
import requests
import json
from pathlib import Path
import time

BACKEND_URL = "http://localhost:8000"
DATA_DIR = Path(__file__).parent.parent / "sample"


def upload_file(endpoint: str, filename: str, data_type: str = None, year: str = "FY2024"):
    """Upload a JSON file to the backend."""
    filepath = DATA_DIR / filename
    
    if not filepath.exists():
        print(f"⚠ {filename} not found, skipping...")
        return False
    
    with open(filepath, "r") as f:
        data = json.load(f)
    
    print(f"Uploading {filename} ({len(data)} records)...", end=" ")
    
    try:
        # Create a mock file upload
        files = {"file": (filename, json.dumps(data), "application/json")}
        
        params = {}
        if data_type:
            params["data_type"] = data_type
        if year and data_type in ["FINANCIAL_STATEMENT", "BANK_STATEMENT", "ITR"]:
            params["year"] = year
        
        response = requests.post(
            f"{BACKEND_URL}{endpoint}",
            files=files,
            params=params,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ {result.get('records_ingested', 0)} records ingested")
            return True
        else:
            print(f"✗ Error {response.status_code}: {response.text[:100]}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("✗ Backend not reachable. Is it running on :8000?")
        return False
    except Exception as e:
        print(f"✗ {str(e)}")
        return False


def main():
    print("=" * 60)
    print("Seeding Neo4j with Credit Appraisal Data")
    print("=" * 60)
    print(f"Backend: {BACKEND_URL}")
    print(f"Data source: {DATA_DIR.absolute()}\n")
    
    # Check backend health
    try:
        health = requests.get(f"{BACKEND_URL}/api/health", timeout=5)
        if health.status_code != 200:
            print("⚠ Backend health check failed. Continuing anyway...\n")
    except:
        print("⚠ Cannot reach backend. Make sure it's running on :8000\n")
        return
    
    success_count = 0
    total_uploads = 8
    
    # Upload in dependency order
    uploads = [
        ("/api/data/upload-companies", "companies.json", None),
        ("/api/data/upload-promoters", "promoters.json", None),
        ("/api/data/upload", "financial_statements.json", "FINANCIAL_STATEMENT"),
        ("/api/data/upload", "bank_statements.json", "BANK_STATEMENT"),
        ("/api/data/upload", "itrs.json", "ITR"),
        ("/api/data/upload", "loan_applications.json", "LOAN_APPLICATION"),
        ("/api/data/upload", "litigation.json", "LITIGATION"),
        ("/api/data/upload", "news_articles.json", "NEWS"),
    ]
    
    for endpoint, filename, data_type in uploads:
        if upload_file(endpoint, filename, data_type):
            success_count += 1
        time.sleep(0.5)  # Brief pause between uploads
    
    print(f"\n{'=' * 60}")
    print(f"Upload complete: {success_count}/{total_uploads} successful")
    print(f"{'=' * 60}")
    
    if success_count == total_uploads:
        print("\n✓ All data loaded successfully!")
        print("  → Open http://localhost:3000 to view the dashboard")
        print("  → Try running credit appraisal on the companies")
    else:
        print(f"\n⚠ {total_uploads - success_count} uploads failed")
        print("  → Check backend logs for errors")
        print("  → Ensure Neo4j is running and accessible")


if __name__ == "__main__":
    main()
