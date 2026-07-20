"""Functions for loading raw and processed market data."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from bitchaser.config import (
    BTC_16_YEAR_SNAPSHOT_PATH,
    LATEST_BTC_DAILY_PATH,
)

REQUIRED_COLUMNS = [
    "date",
    "days",
    "open",
    "high",
    "low",
    "close",
    "volume_btc",
    "volume_usd",
]


def load_btc_daily(
    *,
    path: Path,
    start: str | None = None,
    end: str | None = None,
) -> pd.DataFrame:
    """Load a locally stored BTC/USD daily dataset."""
    if not path.exists():
        raise FileNotFoundError(f"Data was not found at {path}.")

    frame = pd.read_parquet(path)

    missing_columns = set(REQUIRED_COLUMNS).difference(frame.columns)

    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Dataset is missing columns: {missing}")

    frame = frame.loc[:, REQUIRED_COLUMNS].copy()

    frame["date"] = pd.to_datetime(
        frame["date"],
        utc=True,
        errors="raise",
    )

    if start is not None:
        start_date = pd.Timestamp(start, tz="UTC")
        frame = frame.loc[frame["date"] >= start_date]

    if end is not None:
        end_date = pd.Timestamp(end, tz="UTC")
        frame = frame.loc[frame["date"] <= end_date]

    return frame.sort_values("date").reset_index(drop=True)


def load_latest(
    *,
    start: str | None = None,
    end: str | None = None,
) -> pd.DataFrame:
    """Load the most recently generated BTC dataset."""
    return load_btc_daily(
        path=LATEST_BTC_DAILY_PATH,
        start=start,
        end=end,
    )


def load_snapshot() -> pd.DataFrame:
    """Load the fixed 16-year BitChaser research dataset."""
    return load_btc_daily(
        path=BTC_16_YEAR_SNAPSHOT_PATH,
    )
