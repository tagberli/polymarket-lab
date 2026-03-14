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

def orderbook_imbalance(book, depth=5) -> pd.DataFrame:
    bids = book.bids
    asks = book.asks

    bid_volume = sum(float(bid.size) for bid in bids)
    ask_volume = sum(float(ask.size) for ask in asks)
    total_volume = bid_volume + ask_volume

    # calculate the imbalance to use as a signal in future
    imbalance = None if total_volume == 0 else (bid_volume - ask_volume) / total_volume
    return {
        "bid_volume": bid_volume,
        "ask_volume": ask_volume,
        "imbalance": imbalance
    }



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
            
            stats = orderbook_imbalance(book)
            
            print("Token ID:", token_id)
            for k, v in stats.items():
                print(f"{k}: {v}")
            print("-----\n")
            
        except Exception as e:
            print("Error:", e)
            continue

    print("--------------\n")
            



