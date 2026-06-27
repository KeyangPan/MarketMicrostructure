import pandas as pd


def load_book(path: str) -> pd.DataFrame:
    """Load a Databento parquet file, restricted to regular trading hours (ET).

    Handles MBP-1, MBP-10, and MBO schemas. All bid/ask size and count columns
    that exist (e.g. bid_sz_00..bid_sz_09 for MBP-10, none for MBO) plus `size`
    are cast from unsigned to signed int64 so that differences like
    bid_sz - ask_sz cannot underflow and wrap around.
    """
    df = pd.read_parquet(path)

    # Size/count columns are unsigned (uint32). Cast to signed int64 to avoid
    # underflow/wraparound on differences. Match every depth level.
    int_cols = [
        c for c in df.columns
        if c.startswith(("bid_sz_", "ask_sz_", "bid_ct_", "ask_ct_"))
    ]
    if "size" in df.columns:
        int_cols.append("size")
    df[int_cols] = df[int_cols].astype("int64")

    df["ts_event"] = pd.to_datetime(df["ts_event"]).dt.tz_convert("America/New_York")
    df = (
        df.set_index("ts_event")
        .between_time("09:30", "16:00")
        .reset_index()
    )
    return df
