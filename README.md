# Market Microstructure — Factors

Factor definitions and the economic intuition behind them. All factors are
**causal** (computed from trailing windows only), so they are safe to use as
features against a future-price target. Implementations live in `factors.py`.

Notation:
- `bid_px / ask_px`, `bid_sz / ask_sz` — best bid/ask price and resting size (top of book).
- `mid = (bid_px + ask_px) / 2` — fair price between the quotes.
- `look_back_ticks` — trailing window measured in **events (rows)**.
- `look_back_trades` — trailing window measured in **trades** (`action == 'T'`).

---

## 1. Order Book Imbalance — `obi_ratio`

$$
\text{OBI} = \frac{\text{bid\_sz} - \text{ask\_sz}}{\text{bid\_sz} + \text{ask\_sz}} \in [-1, 1]
$$

**Logic.** Compares resting size at the best bid vs. the best ask. More size on
the bid (`OBI > 0`) means buy-side pressure — buyers are queued deeper than
sellers, so the price is more likely to tick up; `OBI < 0` is the opposite.
A snapshot of *static* book pressure at the top of book.

---

## 2. Net Liquidity Flow — `net_liquidity_flow`

Each event's `size` is signed by its effect on resting liquidity, then
normalized by total volume in the window:

$$
\text{add (A)} \to +\text{size}, \quad
\text{cancel (C)} \to -\text{size}, \quad
\text{trade (T)} \to -\text{size}
$$

$$
\text{flow} = \frac{\sum \text{signed size}}{\sum |\text{size}|}
\quad\text{over } \texttt{look\_back\_ticks} \in [-1, 1]
$$

**Logic.** Captures whether the book is *dynamically* building up or being torn
down. Adds supply liquidity (`+`); cancels withdraw it and trades consume it
(both `−`). `flow > 0` means liquidity is accumulating; `flow < 0` means it is
being removed faster than replenished. Volume-weighted, so large orders matter
more than message counts. Complements OBI: OBI is the static snapshot, this is
the flow.

---

## 3. Trend (Efficiency) Ratio — `trend_ratio`

$$
\text{net}  = \text{mid}_t - \text{mid}_{t-n}, \qquad
\text{path} = \sum_{i} |\Delta \text{mid}_i| \text{ over the window}
$$

$$
\text{trend\_ratio} = \frac{\text{net}}{\text{path}} \in [-1, 1]
$$

**Logic.** Measures how *efficiently* the mid moved — net displacement divided
by total distance travelled. `+1` is a clean straight-line up-trend (every step
in one direction), `-1` a clean down-trend, and `~0` a choppy / mean-reverting
path that wandered a lot but went nowhere. Captures *realized* momentum vs.
noise, where OBI/flow capture order-book pressure.

---

## 4. Change in Spread — `change_in_spread`

$$
\text{spread}_t = \text{ask\_px}_t - \text{bid\_px}_t, \qquad
\text{change\_in\_spread} = \text{spread}_t - \text{mean}_n(\text{spread})
$$

**Logic.** Deviation of the current spread from its recent rolling-mean norm.
`> 0` means the spread is wider than usual — liquidity drying up, rising
uncertainty or adverse-selection risk; `< 0` means tighter than usual (calmer,
more liquid). Comparing to the rolling mean denoises the point-to-point lag.
A liquidity-stress / volatility signal rather than a directional one.

---

## 5. Volume-Weighted Mid Deviation — `volume_weighted_mid_deviation` (VWMD)

$$
\text{VWAP}_{t,n} = \frac{\sum \text{TradeVol} \cdot \text{TradePrice}}{\sum \text{TradeVol}}
\quad\text{over the last } \texttt{look\_back\_trades} \text{ trades}
$$

$$
\text{VWMD}_t = \text{mid}_t - \text{VWAP}_{t,n}
$$

**Logic.** Gap between the *current quote* and where *recent trades actually
printed*. `> 0` means the mid sits above recent execution prices — buying lifted
the quote ahead of trades (upward pressure); `< 0` is the opposite. The VWAP is
computed over trades only, then carried forward to every row so non-trade ticks
still get a value.
