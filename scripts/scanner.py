import pandas as pd
import requests
import websockets
import json
from py_clob_client.client import ClobClient

client = ClobClient("https://clob.polymarket.com", chain_id=137)

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
clean_markets = clean_up(markets)

print(markets.head())
print("---------------\n")
print(markets.columns)
print("---------------\n")
print(clean_markets)
print("---------------\n")

# order book for each markets
print("\nORDER BOOK DATA\n")

# https://docs.polymarket.com/trading/orderbook
for _, row in markets.iterrows():
    market_id = row["id"]
    market_question = row["question"]
    token_field = row["clobTokenIds"]

    if pd.isna(token_field):
        continue

    # there two token ids a "yes" and a "no"" id
    token_ids = json.loads(row["clobTokenIds"])


    print("Market ID:", market_id)
    print("Market Question:", market_question)
    
    for token_id in token_ids:
        try: # using try just in case some data doesnt exist
            book = client.get_order_book(token_id)
            bids = book.bids
            asks = book.asks
            bid_volume = float(bids[0].size) if bids else None
            ask_volume = float(asks[0].size) if asks else None

            # calculate the imbalance to use as a signal in future
            imbalance = None
            if bid_volume is not None and ask_volume is not None:
                imbalance = (bid_volume - ask_volume) / (bid_volume + ask_volume)
             
            print("Token Id:", token_id)
            print("Bid Volume:", bid_volume)
            print("Ask Volume:", ask_volume)
            print("Imbalance:", imbalance)
            
        except Exception as e:
            print("Error:", e)
            continue

    print("--------------\n")
            



