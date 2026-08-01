#!/usr/bin/env python

"""Create or replace the fixed 16-year research snapshot."""

from __future__ import annotations

import pandas as pd

from bitchaser.config import SNAPSHOT_DATA_DIR
from bitchaser.data.load import load_latest
from bitchaser.data.update import write_parquet_atomically


def main() -> None:
    """Create or replace the snapshot."""

    print("Enter start and end dates for snapshot (YYYY-MM-DD)")
    start_date = input("Start Date: ")
    end_date = input("End Date: ")

    snapshot = load_latest(
        start=start_date,
        end=end_date,
    )

    expected_start = pd.Timestamp(
        start_date,
        tz="UTC",
    )
    expected_end = pd.Timestamp(
        end_date,
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
            "Run `make data` to update dataset."
        )

    snapshot_file = f"btc_daily_{start_date}_{end_date}.parquet"
    snapshot_path = SNAPSHOT_DATA_DIR / snapshot_file

    write_parquet_atomically(
        snapshot,
        snapshot_path,
    )

    print(f"Created snapshot with {len(snapshot):,} observations at {snapshot_path}")


if __name__ == "__main__":
    main()
