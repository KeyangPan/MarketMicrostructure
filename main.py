import pandas as pd
from utils import load_book

nvda_mbp1 = load_book('data/nvda_mbp1_2026-06-01.parquet').head(10)

nvda_mbo = load_book("data/nvda_mbo_2026-06-01.parquet").head(20)