================================================================================
DATA DESCRIPTION — Market Microstructure
================================================================================

Source:   Databento (https://databento.com)
Format:   Apache Parquet
Date:     2026-06-01 (single trading session)
Symbols:  NVDA (NVIDIA), SPY (S&P 500 ETF)

--------------------------------------------------------------------------------
FILES
--------------------------------------------------------------------------------
  nvda_mbp1_2026-06-01.parquet     NVDA  — MBP-1  (top of book / L1)   ~96 MB
  nvda_mbp10_2026-06-01.parquet    NVDA  — MBP-10 (10 levels / L2)    ~208 MB
  spy_mbp10_2026-06-01.parquet     SPY   — MBP-10 (10 levels / L2)    ~216 MB

--------------------------------------------------------------------------------
SCHEMA TYPES
--------------------------------------------------------------------------------
MBP = "Market By Price": resting orders are aggregated per price level. At a
given price you see the total size and the number of orders (count), NOT the
individual orders.

  MBP-1   Best bid and best ask only (the inside quote, "top of book"). Each
          record carries the event that changed the book plus the resulting BBO.

  MBP-10  Top 10 price levels on each side (bid and ask), giving depth of book.
          Same record structure as MBP-1, extended to 10 levels per side.

--------------------------------------------------------------------------------
COLUMNS
--------------------------------------------------------------------------------
Event / metadata (all files):
  ts_event        Timestamp of the event (UTC nanoseconds; tz-convert to ET).
  rtype           Record type code.
  publisher_id    Databento publisher / venue identifier.
  instrument_id   Numeric instrument identifier.
  action          Book action: A=Add, C=Cancel, M=Modify, T=Trade, F=Fill,
                  R=Clear. (Use df['action'].value_counts() to inspect.)
  side            Side of the event: B=Bid, A=Ask, N=None/neutral.
  depth           Book level affected by this event (0 = top).
  price           Price of the event (fixed-point; scaled by 1e-9 in raw feeds).
  size            Size of the event.
  flags           Bitfield of record flags (e.g. last-in-packet, snapshot).
  ts_in_delta     Matching-engine-to-capture latency (nanoseconds).
  sequence        Venue sequence number (monotonic ordering).
  symbol          Ticker string (e.g. "NVDA", "SPY").

Book levels (per level NN = 00..00 for MBP-1, 00..09 for MBP-10):
  bid_px_NN       Bid price at level NN (00 = best bid).
  ask_px_NN       Ask price at level NN (00 = best ask).
  bid_sz_NN       Total resting bid size at level NN.
  ask_sz_NN       Total resting ask size at level NN.
  bid_ct_NN       Number of orders making up the bid size at level NN.
  ask_ct_NN       Number of orders making up the ask size at level NN.

Column counts: MBP-1 = 19 columns (1 level), MBP-10 = 73 columns (10 levels).

--------------------------------------------------------------------------------
NOTES
--------------------------------------------------------------------------------
- Timestamps are UTC; convert with tz_convert("America/New_York") for the
  regular session, then filter between_time("09:30", "16:00") for RTH.
- Data covers the full feed, including pre/post-market — filter as needed.
- Prices may be fixed-point integers in raw Databento output; verify scaling
  before treating them as dollars.
================================================================================
