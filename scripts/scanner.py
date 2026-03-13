import pandas as pd
import requests
import websockets


response = requests.get(
    "https://gamma-api.polymarket.com/markets",
    
    params={"active": "true",
            "enableOrderBook" : "true",
            "closed": "false",
            "limit": 5
            }

)

IMPORTANT_MARKET_COLS = ["id", "question", "outcomePrices", "spread", "volume", "oneHourPriceChange"]

def clean_up(markets: pd.DataFrame) -> pd.DataFrame:
    return markets.filter(items=IMPORTANT_MARKET_COLS) 

markets = pd.json_normalize(response.json())

print(markets.head())
print("---------------")
print(markets.columns)
print("---------------")
# clean up
clean_markets = clean_up(markets)

print(clean_markets)
