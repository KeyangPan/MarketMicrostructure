import pandas as pd
from utils import load_mbp1


def obi_ratio(df: pd.DataFrame) -> pd.Series:
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

def net_liquidity_flow(df: pd.DataFrame, look_back_ticks: int) -> pd.Series:
    """Volume-weighted net liquidity flow over the last ``look_back_ticks`` events.

    Each event's ``size`` is signed by its effect on resting liquidity:
        add (A)    -> +size   (liquidity supplied)
        cancel (C) -> -size   (liquidity withdrawn)
        trade (T)  -> -size   (liquidity consumed)
    then normalized by the total volume in the window:

        flow = sum(signed size) / sum(|size|)   over the window

    Range is [-1, 1]:
        > 0 -> book is net building up (more adds than cancels+trades)
        < 0 -> book is net being torn down
        ~ 0 -> balanced

    Parameters
    ----------
    df : pd.DataFrame
        MBP-1 data with ``action`` (A/C/T) and ``size`` columns.
    look_back_ticks : int
        Number of trailing events (rows) in the rolling window.

    Returns
    -------
    pd.Series
        Net liquidity flow per row, aligned to ``df``'s index. NaN: warm-up rows
        before the window is full.
    """
    sign = df["action"].map({"A": 1, "C": -1, "T": -1}).fillna(0)
    signed = sign * df["size"]

    # NaN: warm-up rows where the window is not yet full. The denominator (sum of
    # sizes, all >= 1) is never 0 over a full window, so no divide-by-zero guard.
    roll = lambda s: s.rolling(look_back_ticks, min_periods=look_back_ticks).sum()
    return roll(signed) / roll(df["size"])


def trend_ratio(df: pd.DataFrame, look_back_ticks: int) -> pd.Series:
    """Trend (efficiency) ratio of the mid-price over the last ``look_back_ticks``.

    Net move divided by the total path travelled across the window:

        net  = mid[t] - mid[t - look_back_ticks]
        path = sum(|mid.diff()|) over the same window
        trend_ratio = net / path

    Range is [-1, 1]:
        +1 -> a clean, straight-line up-trend (every step in one direction)
        -1 -> a clean down-trend
        ~0 -> choppy / mean-reverting (lots of movement, little net progress)

    Parameters
    ----------
    df : pd.DataFrame
        Data with a ``mid_price`` column (added by ``load_mbp1``).
    look_back_ticks : int
        Number of trailing events (rows) in the rolling window.

    Returns
    -------
    pd.Series
        Trend ratio per row, aligned to ``df``'s index.
    """
    mid = (df["bid_px_00"] + df["ask_px_00"]) / 2

    # Net signed change over the window (spans the same look_back_ticks steps
    # as the path sum below).
    net = mid - mid.shift(look_back_ticks)

    # Total absolute distance travelled within the window.
    # NaN: warm-up rows where the window is not yet full.
    path = mid.diff().abs().rolling(look_back_ticks, min_periods=look_back_ticks).sum()

    # NaN: when path == 0 (mid never moved, undefined trend; avoids 0/0).
    return net / path.where(path != 0)


def change_in_spread(df: pd.DataFrame, look_back_ticks: int) -> pd.Series:
    """Deviation of the bid-ask spread from its rolling mean.

        spread_t         = ask_px_00 - bid_px_00
        change_in_spread = spread_t - mean_n(spread)

    Positive -> spread is currently wider than its recent norm (liquidity drying
    up / rising uncertainty); negative -> tighter than usual. Comparing to the
    rolling mean denoises the point-to-point lag.

    Parameters
    ----------
    df : pd.DataFrame
        MBP-1 data with ``bid_px_00`` and ``ask_px_00``.
    look_back_ticks : int
        Number of trailing rows in the rolling-mean window.

    Returns
    -------
    pd.Series
        Spread deviation per row. NaN: warm-up rows before the window is full.
    """
    spread = df["ask_px_00"] - df["bid_px_00"]

    # NaN: warm-up rows where the rolling-mean window is not yet full.
    rolling_mean = spread.rolling(look_back_ticks, min_periods=look_back_ticks).mean()
    return spread - rolling_mean


def volume_weighted_mid_deviation(df: pd.DataFrame, look_back_trades: int) -> pd.Series:
    """Deviation of the mid-price from the trade VWAP of the last ``look_back_trades`` trades.

        VWMD_t = mid_t - VWAP_{t,n}
        VWAP_{t,n} = sum(TradeVol * TradePrice) / sum(TradeVol)  over the last n trades

    Positive -> mid sits above where recent trades printed (buying lifted the
    quote ahead of executions); negative -> the opposite.

    Parameters
    ----------
    df : pd.DataFrame
        MBP-1 data with ``action`` ('T' = trade), ``price``, ``size`` and the
        best bid/ask price columns.
    look_back_trades : int
        Number of trailing *trades* in the VWAP window.

    Returns
    -------
    pd.Series
        VWMD per row. NaN: rows before the first full window of trades exists.
    """
    is_trade = df["action"].eq("T")
    price = df.loc[is_trade, "price"]
    vol = df.loc[is_trade, "size"]

    # Rolling VWAP over the last look_back_trades trades (indexed on trade rows).
    # NaN: warm-up trades before the window is full.
    pv = (price * vol).rolling(look_back_trades, min_periods=look_back_trades).sum()
    v = vol.rolling(look_back_trades, min_periods=look_back_trades).sum()
    vwap_trades = pv / v.where(v != 0)

    # Carry the last computed VWAP forward to every row, so non-trade ticks also
    # get a deviation. Leading rows (before n trades occur) stay NaN.
    vwap = vwap_trades.reindex(df.index).ffill()

    mid = (df["bid_px_00"] + df["ask_px_00"]) / 2
    return mid - vwap


nvda_mbp1 = load_mbp1("data/nvda_mbp1_2026-06-01.parquet")

nvda_mbp1["obi_ratio"] = obi_ratio(nvda_mbp1)
nvda_mbp1["net_liquidity_flow"] = net_liquidity_flow(nvda_mbp1, look_back_ticks=100)
nvda_mbp1["trend_ratio"] = trend_ratio(nvda_mbp1, look_back_ticks=100)
nvda_mbp1["change_in_spread"] = change_in_spread(nvda_mbp1, look_back_ticks=100)
nvda_mbp1["vwmd"] = volume_weighted_mid_deviation(nvda_mbp1, look_back_trades=100)
