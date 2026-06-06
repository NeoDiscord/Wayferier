from mcp.server.fastmcp import FastMCP
import requests
import json
import os
import sys
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()
mcp = FastMCP("Wayfarer")
API_KEY = os.environ.get("SAM_API_KEY")

@mcp.tool()
def search_live_contracts(keyword: str = None, limit: int = 5) -> str:
    # search sam database for contracts so agents can use to find rfps etcs etc
    # reqs keyword
    url = "https://api.sam.gov/opportunities/v2/search"
    today = datetime.now()
   
    # prob change this in future to be able to select timeframe
    daysago = today - timedelta(days=14)
    date_to = today.strftime("%m/%d/%Y")
    date_from = daysago.strftime("%m/%d/%Y")
    
    # Base parameters required by the GSA API
    params = {
        "api_key": API_KEY,
        "limit": limit,
        "postedFrom": date_from,
        "postedTo": date_to,
        "ptype": "o" 
    }
    # o limits to open btw the uhh ptype
    
   # keyword to title map
    if keyword:
        params["title"] = keyword

    # generate and cleanly output url string to terminal sys.stderr
    prepared_request = requests.Request('GET', url, params=params).prepare()
    print(f"\n Compiling...", file=sys.stderr)
    print(f"Generated API URL: {prepared_request.url}\n", file=sys.stderr)

    headers = {"User-Agent": "Wayfarer/1.0"}

    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        contracts = data.get("opportunitiesData", [])
        clean_results = []
        
        for contract in contracts:
            clean_results.append({
                "agency": contract.get("fullParentPathName", "Unknown Agency"),
                "title": contract.get("title", "No Title"),
                "id": contract.get("solicitationNumber", "N/A"),
                "url": contract.get("uiLink", "N/A")
            })
            
        return json.dumps(clean_results, indent=2)

    except Exception as e:
        # err
        return f"Error fetching from government database: {str(e)}"


app = mcp.sse_app

if __name__ == "__main__":
    mcp.run(transport="sse")