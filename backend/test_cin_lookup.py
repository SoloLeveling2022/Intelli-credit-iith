"""Test CIN to company name lookup"""
import httpx
from bs4 import BeautifulSoup
import asyncio

async def test_zaubacorp_lookup(cin: str):
    """Test fetching company details from Zaubacorp"""
    url = f"https://www.zaubacorp.com/company/{cin}/Company-Details"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                headers={"User-Agent": "Mozilla/5.0"},
                follow_redirects=True,
                timeout=15.0
            )
            
            print(f"Status: {response.status_code}")
            print(f"URL: {response.url}")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                
                # Try to find company name
                title = soup.find("title")
                if title:
                    print(f"Title: {title.get_text(strip=True)[:100]}")
                
                # Look for h1 tags
                h1_tags = soup.find_all("h1", limit=5)
                print(f"H1 tags found: {len(h1_tags)}")
                for h1 in h1_tags:
                    text = h1.get_text(strip=True)
                    if text and len(text) > 5:
                        print(f"  H1: {text[:100]}")
                
                # Look for company name class
                name_div = soup.find("div", class_="company-name")
                if name_div:
                    print(f"Company Name div: {name_div.get_text(strip=True)}")
                
                # Look for meta tags
                meta = soup.find("meta", property="og:title")
                if meta:
                    print(f"OG Title: {meta.get('content', '')[:100]}")
                    
    except Exception as e:
        print(f"Error: {e}")

async def test_gnews_api():
    """Test GNews API"""
    url = "https://gnews.io/api/v4/search?q=software&lang=en&max=3&apikey=demo"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=15.0)
            print(f"GNews Status: {response.status_code}")
            data = response.json()
            print(f"Articles: {len(data.get('articles', []))}")
            if data.get('articles'):
                print(f"Sample title: {data['articles'][0].get('title', '')[:80]}")
    except Exception as e:
        print(f"GNews Error: {e}")


if __name__ == "__main__":
    cin = "U72200KA2007PTC043114"
    print(f"Testing CIN: {cin}\n")
    
    print("=== Testing Zaubacorp Lookup ===")
    asyncio.run(test_zaubacorp_lookup(cin))
    
    print("\n=== Testing GNews API ===")
    asyncio.run(test_gnews_api())
