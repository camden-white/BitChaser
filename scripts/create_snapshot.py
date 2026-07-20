#!/usr/bin/env python

"""Create the fixed 16-year research snapshot."""

from __future__ import annotations

import pandas as pd

from bitchaser.config import BTC_16_YEAR_SNAPSHOT_PATH
from bitchaser.data.load import load_latest
from bitchaser.data.update import write_parquet_atomically

START_DATE = "2010-07-17"
END_DATE = "2026-07-16"
EXPECTED_OBSERVATIONS = 5_844


def main() -> None:
    """Create the immutable 16-year research snapshot."""
    if BTC_16_YEAR_SNAPSHOT_PATH.exists():
        raise FileExistsError(
            "The research snapshot already exists. "
            "Delete it manually only if you intentionally "
            "want to recreate it."
        )

    snapshot = load_latest(
        start=START_DATE,
        end=END_DATE,
    )

    expected_start = pd.Timestamp(
        START_DATE,
        tz="UTC",
    )
    expected_end = pd.Timestamp(
        END_DATE,
        tz="UTC",
    )

    actual_start = snapshot["date"].min()
    actual_end = snapshot["date"].max()

    if actual_start != expected_start:
        raise RuntimeError(
            f"Expected first date {expected_start.date()}, "
            f"but found {actual_start.date()}."
        )

    if actual_end != expected_end:
        raise RuntimeError(
            f"Expected last date {expected_end.date()}, "
            f"but found {actual_end.date()}. "
            "Run `make data` first."
        )

    if len(snapshot) != EXPECTED_OBSERVATIONS:
        raise RuntimeError(
            f"Expected {EXPECTED_OBSERVATIONS:,} observations, "
            f"but found {len(snapshot):,}."
        )

    write_parquet_atomically(
        snapshot,
        BTC_16_YEAR_SNAPSHOT_PATH,
    )

    print(
        f"Created snapshot with {len(snapshot):,} observations at "
        f"{BTC_16_YEAR_SNAPSHOT_PATH}"
    )


if __name__ == "__main__":
    main()
