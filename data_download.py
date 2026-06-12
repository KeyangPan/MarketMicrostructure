import databento as db
from dotenv import load_dotenv
import os

load_dotenv()
databento_api_key = os.getenv("DATABENTO_API_KEY")

def download_stock_data(symbol:str,
                        date:str,
                        schema:str = 'MBP-10'):
    client = db.Historical(key=databento_api_key)

    data = client.timeseries.get_range(
        dataset="XNAS.ITCH",
        schema=schema,
        symbols=[symbol],
        start=f"{date}T00:30",
        end=f"{date}T23:30",
        # path=f"data/{symbol.lower()}_mbp10_{date}.dbn.zst",  # stream to disk instead of RAM
    )

    data.to_parquet(f"data/{symbol.lower()}_{schema}_{date}.parquet")

# download_stock_data('NVDA',
#                     '2026-06-01',
#                     'MBP-1')