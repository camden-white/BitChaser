"""Tests for OHLC preprocessing."""

import pandas as pd

from bitchaser.data.preprocess import (
    preprocess_btc_daily,
)


def test_preprocess_btc_daily_calculates_days() -> None:
    raw = pd.DataFrame(
        {
            "date": pd.to_datetime(
                [
                    "2010-07-17",
                    "2009-01-04",
                    "2009-01-03",
                ],
                utc=True,
            ),
            "open": [0.05, 0.0, 0.0],
            "high": [0.05, 0.0, 0.0],
            "low": [0.05, 0.0, 0.0],
            "close": [0.05, 0.0, 0.0],
            "volume_btc": [20.0, 0.0, 0.0],
            "volume_usd": [1.0, 0.0, 0.0],
        }
    )

    result = preprocess_btc_daily(raw)

    assert result["days"].tolist() == [0, 1, 560]

    assert result.columns.tolist() == [
        "date",
        "days",
        "open",
        "high",
        "low",
        "close",
        "volume_btc",
        "volume_usd",
    ]
