"""Functions for loading processed Bitcoin market data."""

from __future__ import annotations

from pathlib import Path
from typing import Final

import pandas as pd

from bitchaser.config import LATEST_BTC_DAILY_PATH, SNAPSHOT_DATA_DIR

REQUIRED_COLUMNS: Final[tuple[str, ...]] = (
    "date",
    "days",
    "open",
    "high",
    "low",
    "close",
    "volume_btc",
    "volume_usd",
)


def to_utc_timestamp(
    value: str | pd.Timestamp,
) -> pd.Timestamp:
    """Convert a date-like value to a UTC-aware timestamp."""
    timestamp = pd.Timestamp(value)

    if timestamp.tzinfo is None:
        return timestamp.tz_localize("UTC")

    return timestamp.tz_convert("UTC")


def load_btc_daily(
    *,
    path: Path,
    start: str | pd.Timestamp | None = None,
    end: str | pd.Timestamp | None = None,
) -> pd.DataFrame:
    """
    Load a locally stored Bitcoin daily dataset.

    The required price columns are validated, while all
    additional columns—such as block_height, block_era,
    difficulty, hashrate, and block_time—are preserved.
    """
    if not path.exists():
        raise FileNotFoundError(f"Data was not found at {path}.")

    frame = pd.read_parquet(path)

    missing_columns = set(REQUIRED_COLUMNS).difference(frame.columns)

    if missing_columns:
        missing = ", ".join(sorted(missing_columns))

        raise ValueError(f"Dataset is missing columns: {missing}")

    # Preserve every column stored in the Parquet file.
    frame = frame.copy()

    frame["date"] = pd.to_datetime(
        frame["date"],
        utc=True,
        errors="raise",
    )

    if start is not None:
        start_date = to_utc_timestamp(start)

        frame = frame.loc[frame["date"] >= start_date]

    if end is not None:
        end_date = to_utc_timestamp(end)

        frame = frame.loc[frame["date"] <= end_date]

    return frame.sort_values("date").reset_index(drop=True)


def load_latest(
    *,
    start: str | pd.Timestamp | None = None,
    end: str | pd.Timestamp | None = None,
) -> pd.DataFrame:
    """Load the most recently generated Bitcoin dataset."""
    return load_btc_daily(
        path=LATEST_BTC_DAILY_PATH,
        start=start,
        end=end,
    )


def load_snapshot() -> pd.DataFrame:
    """Load the cashed snapshot."""
    try:
        snapshot_path = next(f for f in SNAPSHOT_DATA_DIR.iterdir() if f.is_file())
    except StopIteration:
        print("ERROR: Snapshot not found. Run `make snapshot` first.")
        quit()
    return load_btc_daily(path=snapshot_path)
