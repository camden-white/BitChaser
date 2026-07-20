#!/usr/bin/env python

"""Update locally stored BTC data through yesterday."""

from __future__ import annotations

from dotenv import load_dotenv

from bitchaser.config import (
    LATEST_BTC_DAILY_PATH,
    PROJECT_ROOT,
    RAW_BTC_DAILY_PATH,
)
from bitchaser.data.cryptocompare import (
    fetch_btc_daily_ohlcv,
)
from bitchaser.data.preprocess import (
    preprocess_btc_daily,
)
from bitchaser.data.update import write_parquet_atomically


def main() -> None:
    """Download, process, and store the latest BTC dataset."""
    load_dotenv(
        PROJECT_ROOT / ".env",
        override=True,
    )

    print("Downloading BTC/USD daily data...")

    raw = fetch_btc_daily_ohlcv()

    write_parquet_atomically(
        raw,
        RAW_BTC_DAILY_PATH,
    )

    print(f"Saved {len(raw):,} raw observations to {RAW_BTC_DAILY_PATH}")

    processed = preprocess_btc_daily(raw)

    write_parquet_atomically(
        processed,
        LATEST_BTC_DAILY_PATH,
    )

    print(f"Saved {len(processed):,} processed observations to {LATEST_BTC_DAILY_PATH}")

    first_date = processed["date"].min().date()
    last_date = processed["date"].max().date()

    print(f"Date range: {first_date} through {last_date}")


if __name__ == "__main__":
    main()
