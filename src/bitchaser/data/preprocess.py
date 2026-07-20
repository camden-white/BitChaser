"""Functions for cleaning and validating Bitcoin OHLC data."""

from __future__ import annotations

import pandas as pd

BITCOIN_LAUNCH_DATE = pd.Timestamp(
    "2009-01-03",
    tz="UTC",
)

RAW_COLUMNS = [
    "date",
    "open",
    "high",
    "low",
    "close",
    "volume_btc",
    "volume_usd",
]

NUMERIC_COLUMNS = [
    "open",
    "high",
    "low",
    "close",
    "volume_btc",
    "volume_usd",
]

PROCESSED_COLUMNS = [
    "date",
    "days",
    "open",
    "high",
    "low",
    "close",
    "volume_btc",
    "volume_usd",
]


def preprocess_btc_daily(
    frame: pd.DataFrame,
) -> pd.DataFrame:
    """Validate and preprocess daily BTC/USD OHLCV data.

    Parameters
    ----------
    frame
        Raw BTC/USD data returned by CryptoCompare.

    Returns
    -------
    pandas.DataFrame
        Validated data with the number of days since Bitcoin's
        January 3, 2009 launch date.
    """
    missing_columns = set(RAW_COLUMNS).difference(frame.columns)

    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Raw data is missing required columns: {missing}")

    processed = frame.loc[:, RAW_COLUMNS].copy()

    processed["date"] = pd.to_datetime(
        processed["date"],
        utc=True,
        errors="raise",
    ).dt.normalize()

    for column in NUMERIC_COLUMNS:
        processed[column] = pd.to_numeric(
            processed[column],
            errors="raise",
        )

    processed = (
        processed.drop_duplicates(
            subset="date",
            keep="last",
        )
        .sort_values("date")
        .reset_index(drop=True)
    )

    if processed.empty:
        raise ValueError("The raw BTC dataset contains no observations.")

    if (processed["date"] < BITCOIN_LAUNCH_DATE).any():
        raise ValueError("The dataset contains a date before January 3, 2009.")

    processed.insert(
        1,
        "days",
        (processed["date"] - BITCOIN_LAUNCH_DATE).dt.days.astype("int64"),
    )

    return processed.loc[:, PROCESSED_COLUMNS]
