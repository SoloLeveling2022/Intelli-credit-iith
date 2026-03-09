"""
Research API - external data gathering from news, MCA, eCourts, industry sources.
"""
from fastapi import APIRouter, HTTPException, Query
from app.core.research_agent import (
    search_company_news,
    fetch_mca_filings,
    search_ecourts_cases,
    search_promoter_background,
    analyze_industry_trends,
    check_cibil_commercial,
)

router = APIRouter()
CIN_PATTERN = r"^[A-Z][0-9]{5}[A-Z]{2}[0-9]{4}[A-Z]{3}[0-9]{6}$"


@router.get("/news")
async def get_company_news(
    cin: str = Query(..., min_length=21, max_length=21, pattern=CIN_PATTERN),
    company_name: str = Query(None),
    days: int = Query(90, ge=1, le=365),
):
    """Search for recent news articles about a company."""
    try:
        if not company_name:
            mca_data = await fetch_mca_filings(cin)
            query = mca_data.get("company_name") or cin
        else:
            query = company_name

        news_articles = await search_company_news(query, days)
        result = {
            "cin": cin,
            "total_articles": len(news_articles),
            "articles": news_articles,
        }
        
        if len(news_articles) == 0:
            print(f"⚠️  /api/research/news returned 0 articles for CIN {cin}, query: {query}")
        
        return result
    except Exception as e:
        print(f"❌ /api/research/news failed for CIN {cin}: {e}")
        raise HTTPException(status_code=500, detail=f"News search failed: {str(e)}")


@router.get("/mca")
async def get_mca_filings(
    cin: str = Query(..., min_length=21, max_length=21, pattern=CIN_PATTERN),
):
    """Fetch MCA (Ministry of Corporate Affairs) filings and compliance status."""
    try:
        filings = await fetch_mca_filings(cin)
        if filings.get("data_source") == "cin_derived":
            print(f"ℹ️  /api/research/mca returned CIN-derived data (not real MCA scrape) for CIN {cin}")
        return filings
    except Exception as e:
        print(f"❌ /api/research/mca failed for CIN {cin}: {e}")
        raise HTTPException(status_code=500, detail=f"MCA fetch failed: {str(e)}")


@router.get("/litigation")
async def get_litigation(
    cin: str = Query(..., min_length=21, max_length=21, pattern=CIN_PATTERN),
    company_name: str = Query(None),
):
    """Search eCourts for litigation cases involving the company."""
    try:
        cases = await search_ecourts_cases(company_name=company_name, cin=cin)
        result = {
            "cin": cin,
            "total_cases": len(cases),
            "pending_cases": len([c for c in cases if c.get("status") in {"pending", "Pending"}]),
            "cases": cases,
        }
        
        if len(cases) == 0:
            print(f"ℹ️  /api/research/litigation returned 0 cases for CIN {cin}")
        
        return result
    except Exception as e:
        print(f"❌ /api/research/litigation failed for CIN {cin}: {e}")
        raise HTTPException(status_code=500, detail=f"Litigation search failed: {str(e)}")


@router.get("/promoter")
async def get_promoter_background(promoter_name: str, pan: str = Query(None)):
    """Search for promoter's background, other directorships, past controversies."""
    try:
        background = await search_promoter_background(promoter_name, pan)
        return {
            "promoter_name": promoter_name,
            "pan": pan,
            "directorships": background.get("directorships", []),
            "past_defaults": background.get("past_defaults", []),
            "controversies": background.get("controversies", []),
            "credit_score_history": background.get("credit_score_history", []),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Promoter search failed: {str(e)}")


@router.get("/industry")
async def get_industry_trends(industry: str):
    """Analyze industry trends and outlook (for 'Conditions' C)."""
    try:
        trends = await analyze_industry_trends(industry)
        return {
            "industry": industry,
            "outlook": trends.get("outlook", "Neutral"),
            "growth_rate": trends.get("growth_rate"),
            "key_risks": trends.get("key_risks", []),
            "key_opportunities": trends.get("key_opportunities", []),
            "recent_news": trends.get("recent_news", []),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Industry analysis failed: {str(e)}")


@router.get("/cibil")
async def get_cibil_score(
    cin: str = Query(..., min_length=21, max_length=21, pattern=CIN_PATTERN),
    company_name: str = Query(None),
):
    """Fetch calculated CIBIL commercial credit score based on available data."""
    try:
        # Fetch all related data first
        mca_data = await fetch_mca_filings(cin)
        litigation_cases = await search_ecourts_cases(company_name=company_name, cin=cin)
        news_query = company_name or mca_data.get("company_name") or cin
        news = await search_company_news(news_query, lookback_days=90)

        # Calculate CIBIL score based on all data
        cibil_data = await check_cibil_commercial(cin, mca_data, litigation_cases, news)
        
        print(f"ℹ️  /api/research/cibil calculated score {cibil_data.get('credit_score')} for CIN {cin}")
        return cibil_data
    except Exception as e:
        print(f"❌ /api/research/cibil failed for CIN {cin}: {e}")
        raise HTTPException(status_code=500, detail=f"CIBIL check failed: {str(e)}")


@router.post("/comprehensive-research")
async def comprehensive_research(
    cin: str = Query(..., min_length=21, max_length=21, pattern=CIN_PATTERN),
    company_name: str = Query(...),
):
    """Run comprehensive research combining all external data sources."""
    results = {
        "cin": cin,
        "company_name": company_name,
        "timestamp": __import__("datetime").datetime.now().isoformat(),
    }
    
    # Gather data from all sources (with error handling)
    try:
        results["news"] = await search_company_news(company_name or cin, 90)
        if len(results["news"]) == 0:
            print(f"⚠️  Comprehensive research: 0 news articles for {cin}")
    except Exception as e:
        print(f"❌ Comprehensive research: News fetch failed for {cin}: {e}")
        results["news_error"] = str(e)
        results["news"] = []
    
    try:
        results["mca"] = await fetch_mca_filings(cin)
        if results["mca"].get("data_source") == "cin_derived":
            print(f"ℹ️  Comprehensive research: Using CIN-derived MCA data for {cin}")
    except Exception as e:
        print(f"❌ Comprehensive research: MCA fetch failed for {cin}: {e}")
        results["mca_error"] = str(e)
        results["mca"] = {}
    
    try:
        results["litigation"] = await search_ecourts_cases(company_name=company_name, cin=cin)
        if len(results["litigation"]) == 0:
            print(f"ℹ️  Comprehensive research: 0 litigation cases for {cin}")
    except Exception as e:
        print(f"❌ Comprehensive research: Litigation search failed for {cin}: {e}")
        results["litigation_error"] = str(e)
        results["litigation"] = []
    
    # Calculate CIBIL using all gathered data
    try:
        results["cibil"] = await check_cibil_commercial(
            cin,
            mca_data=results.get("mca"),
            litigation_cases=results.get("litigation"),
            news=results.get("news")
        )
    except Exception as e:
        results["cibil_error"] = str(e)
        results["cibil"] = {}
    
    # Calculate overall research score
    score = results.get("cibil", {}).get("credit_score", 50)
    
    results["research_score"] = score
    results["risk_level"] = "LOW" if score >= 75 else "MEDIUM" if score >= 50 else "HIGH" if score >= 25 else "CRITICAL"
    
    return results
