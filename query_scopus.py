import os
import requests
import json
from dotenv import load_dotenv

load_dotenv(".env")
SCOPUS_API_KEY = os.getenv("SCOPUS_API_KEY")

def query_scopus():
    headers = {
        "X-ELS-APIKey": SCOPUS_API_KEY,
        "Accept": "application/json"
    }
    
    # Query for JPIM articles from 2024-2026
    query = "ISSN(1540-5885 OR 0737-6782) AND PUBYEAR > 2023"
    url = f"https://api.elsevier.com/content/search/scopus?query={query}&count=25"
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            articles = data.get("search-results", {}).get("entry", [])
            print(f"Found {len(articles)} recent articles. Analyzing topics...")
            for article in articles[:10]:
                print(f"- {article.get('dc:title', 'No Title')}")
        else:
            print(f"Failed to fetch data: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Error querying Scopus: {str(e)}")

if __name__ == "__main__":
    query_scopus()
