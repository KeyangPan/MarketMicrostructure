import pandas as pd

nvda_mbp1 = pd.read_parquet('data/nvda_mbp1_2026-06-01.parquet')

nvda_mbp1["ts_event"] = (

    pd.to_datetime(nvda_mbp1["ts_event"])

    .dt.tz_convert("America/New_York")

)

nvda_mbp1 = (
    nvda_mbp1.set_index("ts_event")
    .between_time("09:30", "16:00")
    .reset_index()
)

print(nvda_mbp1["ts_event"].tail())

nvda_mbp1['action'].value_counts()