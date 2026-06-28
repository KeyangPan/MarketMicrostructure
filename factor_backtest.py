"""Walk-forward factor evaluation.

The core primitive is ``build_dataset``, which turns a slice of book data into a
factor matrix ``X`` and a forward-return target frame ``y``. The IC study below
consumes it on each window's validation slice; the same builder feeds the
later Lasso model (fit on a window's train ``(X, y)``, predict on its val).
"""

from typing import Iterable, Sequence

import numpy as np
import pandas as pd

from factors import compute_factors
from data_splits import WindowSplit

DEFAULT_HORIZON = 100
DEFAULT_TARGETS = ("bid_px_00", "ask_px_00", "mid_px_00")


def forward_change(df: pd.DataFrame, col: str, horizon: int) -> pd.Series:
    """Forward simple return of ``col`` over the next ``horizon`` events:
    (col[t+h] - col[t]) / col[t].

    Computed within ``df`` only, so the last ``horizon`` rows are NaN rather than
    borrowing values from beyond the slice (no leakage across window bounds).
    Inf (from a zero/empty quote in the denominator) is mapped to NaN so it can
    be dropped downstream rather than corrupting a correlation or regression.
    """
    ret = (df[col].shift(-horizon) - df[col]) / df[col]
    return ret.replace([np.inf, -np.inf], np.nan)


def build_dataset(
    df: pd.DataFrame,
    horizon: int = DEFAULT_HORIZON,
    targets: Sequence[str] = DEFAULT_TARGETS,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Build the factor matrix ``X`` and forward-target frame ``y`` for ``df``.

    X: one column per registered factor.
    y: one column ``<target>_ret`` per target -- the forward simple *return* of
       that quote over the next ``horizon`` ticks, not a price level.

    Both are aligned to ``df``'s index; rows with NaN (factor warm-up at the head,
    target look-ahead at the tail) are left in place for the caller to drop.

    ``mid_px_00`` is a derived column (mean of best bid/ask), materialized here so
    it can be used as a target alongside the raw quote columns.
    """
    df = df.copy()
    if "mid_px_00" not in df.columns:
        df["mid_px_00"] = (df["bid_px_00"] + df["ask_px_00"]) / 2

    X = compute_factors(df)
    y = pd.DataFrame(
        {f"{col}_ret": forward_change(df, col, horizon) for col in targets},
        index=df.index,
    )
    return X, y


def walk_forward_ic(
    windows: Iterable[WindowSplit],
    horizon: int = DEFAULT_HORIZON,
    targets: Sequence[str] = DEFAULT_TARGETS,
    method: str = "spearman",
) -> pd.DataFrame:
    """Per-window, out-of-sample IC of each factor vs each forward target.

    For every window's *validation* slice, computes the correlation between each
    factor and each forward target. Spearman (rank) by default, since factors
    and returns are heavy-tailed. NaNs are dropped per factor/target pair so each
    IC uses the largest valid sample.

    Spearman is computed as Pearson on ranks (identical, and avoids a scipy
    dependency that pandas' method="spearman" would pull in).

    Returns a tidy frame with columns: window, factor, target, ic, n.
    """
    rows = []
    for w in windows:
        X, y = build_dataset(w.val, horizon, targets)
        for factor in X.columns:
            for target in y.columns:
                pair = pd.concat([X[factor], y[target]], axis=1).dropna()
                if method == "spearman":
                    pair = pair.rank()
                    corr_method = "pearson"
                else:
                    corr_method = method
                ic = (
                    pair.iloc[:, 0].corr(pair.iloc[:, 1], method=corr_method)
                    if len(pair) > 1
                    else np.nan
                )
                rows.append(
                    {
                        "window": w.index,
                        "factor": factor,
                        "target": target,
                        "ic": ic,
                        "n": len(pair),
                    }
                )
    return pd.DataFrame(rows)


def summarize_ic(ic_df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate per-window IC into stability stats for each (factor, target).

    mean_ic  : average IC across windows (sign + magnitude of edge)
    ic_std   : window-to-window IC volatility
    ir       : mean_ic / ic_std (information ratio; consistency of the edge)
    hit_rate : fraction of windows whose IC agrees in sign with mean_ic
    """

    def agg(g: pd.DataFrame) -> pd.Series:
        ic = g["ic"]
        mean_ic = ic.mean()
        std = ic.std()
        return pd.Series(
            {
                "n_windows": int(ic.notna().sum()),
                "mean_ic": mean_ic,
                "ic_std": std,
                # "ir": mean_ic / std if std else np.nan,
            }
        )

    return (
        ic_df.groupby(["factor", "target"])[["ic"]]
        .apply(agg)
        .reset_index()
        .sort_values(["factor", 'target'], ascending=True)
        .reset_index(drop=True)
    )
