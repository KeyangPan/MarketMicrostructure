import pandas as pd


def load_mbp1(path: str) -> pd.DataFrame:
    """Load an MBP-1 parquet file and restrict to regular trading hours (ET)."""
    df = pd.read_parquet(path)

    # Size/count columns are unsigned (uint32). Cast to signed int64 so that
    # differences like bid_sz - ask_sz cannot underflow and wrap around.
    INT_COLS = ["bid_sz_00", "ask_sz_00", "bid_ct_00", "ask_ct_00", "size"]
    df[INT_COLS] = df[INT_COLS].astype("int64")

    df["ts_event"] = pd.to_datetime(df["ts_event"]).dt.tz_convert("America/New_York")
    df = (
        df.set_index("ts_event")
        .between_time("09:30", "16:00")
        .reset_index()
    )
    return df
