import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

def fetch_scopus_literature():
    """
    Fetches peer-reviewed abstracts to ground the theoretical framework in KBV 
    and synthetic user research, ensuring JPIM compliance.
    """
    api_key = os.getenv("SCOPUS_API_KEY")
    if not api_key:
        raise ValueError("SCOPUS_API_KEY not found in .env file")

    base_url = "https://api.elsevier.com/content/search/scopus"
    headers = {
        "X-ELS-APIKey": api_key,
        "Accept": "application/json"
    }
    
    # Query prioritizing the intersection of AI, KBV, and front end of innovation
    query = 'TITLE-ABS-KEY("knowledge-based view" OR "artificial intelligence" AND "front end of innovation" OR "synthetic data")'
    
    params = {
        "query": query,
        "count": 25, 
        "sort": "citedby-count" # Pull highly cited papers for authority
    }
    
    print(f"Fetching literature from Scopus...")
    response = requests.get(base_url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        entries = data.get('search-results', {}).get('entry', [])
        
        output_path = "data/raw/scopus_literature.json"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(entries, f, indent=4)
        print(f"Success! {len(entries)} articles saved to {output_path}")
    else:
        print(f"API Error: {response.status_code} - {response.text}")

if __name__ == "__main__":
    fetch_scopus_literature()