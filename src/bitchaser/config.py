"""Project-wide configuration constants and filesystem paths."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
SNAPSHOT_DATA_DIR = DATA_DIR / "snapshots"

RAW_BTC_DAILY_PATH = RAW_DATA_DIR / "cryptocompare_btc_usd_daily.parquet"

LATEST_BTC_DAILY_PATH = PROCESSED_DATA_DIR / "btc_daily_latest.parquet"

BTC_16_YEAR_SNAPSHOT_PATH = (
    SNAPSHOT_DATA_DIR / "btc_daily_2010-07-17_2026-07-16.parquet"
)
