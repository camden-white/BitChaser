"""Project-wide configuration constants and filesystem paths."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
SNAPSHOT_DATA_DIR = DATA_DIR / "snapshot"

RAW_BTC_DAILY_PATH = RAW_DATA_DIR / "cryptocompare_btc_usd_daily.parquet"

LATEST_BTC_DAILY_PATH = PROCESSED_DATA_DIR / "btc_daily_latest.parquet"

DATE_FORMAT = "%Y-%m-%d"

GENESIS = "2009-01-03 18:15:05"

HIGHS = (
    "2011-06-08",
    "2013-11-29",
    "2017-12-17",
    "2021-11-10",
    "2025-10-06",
)

LOWS = (
    "2011-11-17",
    "2015-01-14",
    "2018-12-15",
    "2022-11-21",
)

HALVINGS = (
    "2012-11-28 15:24:38",
    "2016-07-09 16:46:13",
    "2020-05-11 19:23:43",
    "2024-04-20 00:09:27",
)
