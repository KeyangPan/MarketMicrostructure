import pandas as pd

from factor_backtest import summarize_ic, walk_forward_ic
from train_test_splits import holdout_split, rolling_windows
from utils import load_book

if __name__ == "__main__":
    nvda = load_book("data/nvda_mbp1_2026-06-01.parquet")
    open_ts = pd.Timestamp("2026-06-01 09:30", tz="America/New_York")
    close_ts = pd.Timestamp("2026-06-01 16:00", tz="America/New_York")

    # Reserve the final hour for final reporting; never used during the study.
    trainable, holdout = holdout_split(nvda, close_ts, holdout_minutes=60)
    print(f"trainable: {len(trainable):,} rows | holdout: {len(holdout):,} rows\n")

    # Rolling walk-forward windows tile [open, close - holdout).
    windows_end = close_ts - pd.Timedelta(minutes=60)
    windows = list(rolling_windows(trainable, open_ts, windows_end))

    # Out-of-sample IC of each factor vs the next-100-event bid/ask move.
    ic_df = walk_forward_ic(windows)
    summary = summarize_ic(ic_df)

    pd.set_option("display.width", 120)
    print(summary.to_string(index=False))
