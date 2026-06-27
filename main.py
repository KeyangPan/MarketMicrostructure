from typing import Iterator, NamedTuple

import pandas as pd

from utils import load_book


class WindowSplit(NamedTuple):
    """One rolling walk-forward window: a train slice followed by a val slice.

    All bounds are half-open [start, end) on ``ts_event``. ``index`` is the
    0-based position of the window in the walk-forward sequence.
    """

    index: int
    train: pd.DataFrame
    val: pd.DataFrame
    train_start: pd.Timestamp
    train_end: pd.Timestamp  # == val_start
    val_end: pd.Timestamp


def session_bounds(
    df: pd.DataFrame,
    open_time: str = "09:30",
    close_time: str = "16:00",
    time_col: str = "ts_event",
) -> tuple[pd.Timestamp, pd.Timestamp]:
    """Fixed RTH open/close timestamps for the session's trading date (ET).

    The data is guaranteed to span the regular session, so anchoring to fixed
    clock boundaries (rather than the ragged first/last event) keeps windows
    aligned to clean minute marks and lets the final window reach the close.
    """
    ts = df[time_col]
    date = ts.iloc[0].date()
    tz = ts.dt.tz
    return (
        pd.Timestamp(f"{date} {open_time}", tz=tz),
        pd.Timestamp(f"{date} {close_time}", tz=tz),
    )


def holdout_split(
    df: pd.DataFrame,
    close_ts: pd.Timestamp,
    holdout_minutes: int = 60,
    time_col: str = "ts_event",
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Carve the final ``holdout_minutes`` before ``close_ts`` off as hold-out.

    The hold-out is reserved strictly for final reporting and must never enter
    any train/val window. Returns ``(trainable, holdout)``.

    Bounds are half-open: trainable = [open, cutoff), holdout = [cutoff, close).
    """
    ts = df[time_col]
    cutoff = close_ts - pd.Timedelta(minutes=holdout_minutes)
    return df[ts < cutoff], df[ts >= cutoff]


def rolling_windows(
    df: pd.DataFrame,
    session_start: pd.Timestamp,
    session_end: pd.Timestamp,
    window_minutes: int = 60,
    train_minutes: int = 50,
    step_minutes: int = 10,
    time_col: str = "ts_event",
) -> Iterator[WindowSplit]:
    """Yield rolling walk-forward train/val splits over [session_start, session_end).

    Each window spans ``window_minutes`` of wall-clock time, split into the
    first ``train_minutes`` for training and the remainder for validation. The
    window then advances by ``step_minutes`` (walk-forward). With the defaults
    (60 / 50 / 10) the 10-minute validation segments tile the range
    contiguously.

    Slicing is time-based on ``time_col`` (MBP data is irregularly spaced in
    event time, so a fixed row count would not give equal-duration windows).
    Bounds are half-open [start, end). Only windows whose clock end falls at or
    before ``session_end`` are emitted; a trailing partial window is dropped.

    Note: ``df`` should already have the final hold-out removed (see
    ``holdout_split``) so the hold-out never leaks into a val slice.
    """
    val_minutes = window_minutes - train_minutes
    if val_minutes <= 0:
        raise ValueError(
            f"train_minutes ({train_minutes}) must be < window_minutes "
            f"({window_minutes}) to leave room for validation."
        )

    ts = df[time_col]
    window = pd.Timedelta(minutes=window_minutes)
    train_len = pd.Timedelta(minutes=train_minutes)
    step = pd.Timedelta(minutes=step_minutes)

    index = 0
    start = session_start
    # Emit only fully-formed windows: the window must end at or before the
    # session end boundary.
    while start + window <= session_end:
        train_end = start + train_len  # also the validation start
        val_end = start + window

        train = df[(ts >= start) & (ts < train_end)]
        val = df[(ts >= train_end) & (ts < val_end)]

        yield WindowSplit(
            index=index,
            train=train,
            val=val,
            train_start=start,
            train_end=train_end,
            val_end=val_end,
        )

        index += 1
        start += step


if __name__ == "__main__":
    nvda = load_book("data/nvda_mbp1_2026-06-01.parquet")
    open_ts, close_ts = session_bounds(nvda)  # 09:30, 16:00 ET

    trainable, holdout = holdout_split(nvda, close_ts, holdout_minutes=60)
    # Windows tile [open, close - holdout); the final hold-out is excluded.
    windows_end = close_ts - pd.Timedelta(minutes=60)

    print(
        f"full: {len(nvda):,} rows "
        f"({nvda['ts_event'].min()} -> {nvda['ts_event'].max()})"
    )
    print(f"trainable: {len(trainable):,} rows | holdout: {len(holdout):,} rows\n")

    for w in rolling_windows(trainable, open_ts, windows_end):
        print(
            f"window {w.index:>2} | "
            f"train [{w.train_start:%H:%M} -> {w.train_end:%H:%M}) "
            f"{len(w.train):>7,} rows | "
            f"val [{w.train_end:%H:%M} -> {w.val_end:%H:%M}) "
            f"{len(w.val):>6,} rows"
        )


