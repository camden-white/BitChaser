"""Utilities for safely writing data files."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def write_parquet_atomically(
    frame: pd.DataFrame,
    path: Path,
) -> None:
    """Write a DataFrame without leaving a partial output file."""
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary_path = path.with_name(f".{path.name}.tmp")

    try:
        frame.to_parquet(
            temporary_path,
            engine="pyarrow",
            compression="snappy",
            index=False,
        )

        temporary_path.replace(path)
    finally:
        temporary_path.unlink(missing_ok=True)
