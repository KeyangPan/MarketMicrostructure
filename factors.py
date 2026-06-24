import pandas as pd
from utils import load_mbp1


def obi(df: pd.DataFrame) -> pd.Series:
    """Order Book Imbalance (top of book) for MBP-1 data.

    OBI = (bid_sz - ask_sz) / (bid_sz + ask_sz), using the best bid/ask sizes.

    Range is [-1, 1]:
        > 0  -> more resting size on the bid (buy-side pressure)
        < 0  -> more resting size on the ask (sell-side pressure)
        ~ 0  -> balanced book

    Parameters
    ----------
    df : pd.DataFrame
        MBP-1 data with columns ``bid_sz_00`` and ``ask_sz_00``.

    Returns
    -------
    pd.Series
        OBI value per row, aligned to ``df``'s index. NaN where the book is
        empty on both sides (bid_sz_00 + ask_sz_00 == 0).
    """
    # load_mbp1 casts sizes to signed int64, so bid - ask is safe (no unsigned
    # underflow) and int / int division below promotes to float64 automatically.
    bid = df["bid_sz_00"]
    ask = df["ask_sz_00"]
    total = bid + ask
    return (bid - ask) / total.where(total != 0)

def cancel_ratio(df: pd.DataFrame, look_back_ticks: int) -> pd.Series:
    """Rolling cancel-to-add ratio over the last ``look_back_ticks`` events.

    CR = (# cancel events) / (# add events) within the trailing window.

    A high value (>> 1) means many orders are placed then quickly pulled
    (fleeting/flickering quotes), typical of fast quoting activity.

    Parameters
    ----------
    df : pd.DataFrame
        MBP-1 data with an ``action`` column (A=Add, C=Cancel, ...).
    look_back_ticks : int
        Number of trailing events (rows) in the rolling window.

    Returns
    -------
    pd.Series
        Cancel-to-add ratio per row, aligned to ``df``'s index. NaN until the
        window is full, and NaN where no adds occurred in the window.
    """
    is_cancel = df["action"].eq("C")
    is_add = df["action"].eq("A")

    # NaN source #1 (warm-up): with min_periods=look_back_ticks the first
    # (look_back_ticks - 1) rows have an incomplete window
    cancels = is_cancel.rolling(look_back_ticks, min_periods=look_back_ticks).sum()
    adds = is_add.rolling(look_back_ticks, min_periods=look_back_ticks).sum()

    # NaN source #2 (undefined ratio): when adds == 0 (no add events in the
    # window) adds.where(adds != 0) makes the denominator NaN, so the ratio is
    # NaN rather than inf. Rare here since adds are ~43% of events.
    return cancels / adds.where(adds != 0)

nvda_mbp1 = load_mbp1("data/nvda_mbp1_2026-06-01.parquet")

nvda_mbp1["obi"] = obi(nvda_mbp1)
nvda_mbp1["cancel_ratio"] = cancel_ratio(nvda_mbp1, look_back_ticks=100)
