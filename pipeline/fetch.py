import requests
import pandas as pd
from datetime import datetime

URL = "https://query1.finance.yahoo.com/v1/finance/screener/predefined/saved?count=50&scrIds=most_actives"

def fetch_data():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        resp = requests.get(URL, headers=headers)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print("❌ Error fetching data:", e)
        return pd.DataFrame()
    
    # Check structure
    if "finance" not in data or "result" not in data["finance"] or not data["finance"]["result"]:
        print("❌ Unexpected API structure.")
        return pd.DataFrame()
    
    quotes = data["finance"]["result"][0].get("quotes", [])
    if not quotes:
        print("❌ No data returned.")
        return pd.DataFrame()
    
    df = pd.DataFrame(quotes)
    
    # Select relevant columns
    df = df[["symbol", "shortName", "regularMarketPrice", "regularMarketChange",
             "regularMarketChangePercent", "regularMarketVolume"]].copy()
    df.rename(columns={
        "symbol": "Symbol",
        "shortName": "Name",
        "regularMarketPrice": "Price",
        "regularMarketChange": "Change",
        "regularMarketChangePercent": "PercentChange",
        "regularMarketVolume": "Volume"
    }, inplace=True)
    
    df["LastUpdated"] = datetime.now()
    
    return df