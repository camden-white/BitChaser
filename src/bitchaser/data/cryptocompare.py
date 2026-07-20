from __future__ import annotations

import os
from typing import Any, cast

import httpx
import pandas as pd

HISTORICAL_DAILY_URL = "https://min-api.cryptocompare.com/data/v2/histoday"

MAX_OBSERVATIONS_PER_REQUEST = 2_000

RAW_COLUMNS = [
    "date",
    "open",
    "high",
    "low",
    "close",
    "volume_btc",
    "volume_usd",
]


def fetch_btc_daily_ohlcv(
    start: str = "2010-07-17",
    end: str | None = None,
    api_key: str | None = None,
) -> pd.DataFrame:
    """Fetch aggregated daily BTC/USD OHLCV data from CCCAGG.

    Parameters
    ----------
    start
        Earliest UTC date to retain, formatted as YYYY-MM-DD.
    end
        Latest completed UTC date to retrieve, formatted as
        YYYY-MM-DD. Defaults to yesterday.
    api_key
        CryptoCompare API key. Defaults to the
        CRYPTOCOMPARE_API_KEY environment variable.

    Returns
    -------
    pandas.DataFrame
        Daily BTC/USD OHLCV data ordered from oldest to newest.
    """
    start_date = pd.Timestamp(start, tz="UTC")

    if end is None:
        end_date = pd.Timestamp.now(tz="UTC").normalize() - pd.Timedelta(days=1)
    else:
        end_date = pd.Timestamp(end, tz="UTC")

    if end_date < start_date:
        raise ValueError("end must be on or after start.")

    start_timestamp = int(start_date.timestamp())
    next_timestamp = int(end_date.timestamp())

    resolved_api_key = api_key or os.getenv("CRYPTOCOMPARE_API_KEY")

    if not resolved_api_key:
        raise RuntimeError(
            "CRYPTOCOMPARE_API_KEY was not found. "
            "Define it in .env or pass api_key explicitly."
        )

    headers = {
        "authorization": f"Apikey {resolved_api_key}",
    }

    records: list[dict[str, Any]] = []

    with httpx.Client(
        headers=headers,
        timeout=30.0,
        follow_redirects=True,
    ) as client:
        while next_timestamp >= start_timestamp:
            response = client.get(
                HISTORICAL_DAILY_URL,
                params={
                    "fsym": "BTC",
                    "tsym": "USD",
                    "e": "CCCAGG",
                    "aggregate": 1,
                    "limit": MAX_OBSERVATIONS_PER_REQUEST,
                    "toTs": next_timestamp,
                    "extraParams": "BitChaser",
                },
            )

            response.raise_for_status()

            payload: dict[str, Any] = response.json()

            if payload.get("Response") == "Error":
                message = payload.get(
                    "Message",
                    "Unknown CryptoCompare API error",
                )
                raise RuntimeError(f"CryptoCompare API error: {message}")

            outer_data = payload.get("Data")

            if not isinstance(outer_data, dict):
                raise RuntimeError("The API returned an unexpected response structure.")

            payload_raw: object = response.json()

            if not isinstance(payload_raw, dict):
                raise RuntimeError("The API returned an unexpected response structure.")

            payload = cast(dict[str, object], payload_raw)

            if payload.get("Response") == "Error":
                message = payload.get("Message")

                if not isinstance(message, str):
                    message = "Unknown CryptoCompare API error"

                raise RuntimeError(f"CryptoCompare API error: {message}")

            outer_data_raw = payload.get("Data")

            if not isinstance(outer_data_raw, dict):
                raise RuntimeError("The API returned an unexpected response structure.")

            outer_data = cast(
                dict[str, object],
                outer_data_raw,
            )

            batch_data = outer_data.get("Data")

            if not isinstance(batch_data, list):
                raise RuntimeError(
                    "The API response did not contain an observation list."
                )

            batch_items = cast(
                list[object],
                batch_data,
            )

            if not all(isinstance(record, dict) for record in batch_items):
                raise RuntimeError(
                    "The API observation list contained an unexpected value."
                )

            batch = [cast(dict[str, Any], record) for record in batch_items]

            if not batch:
                break

            records.extend(batch)

            earliest_timestamp = min(int(record["time"]) for record in batch)

            if earliest_timestamp <= start_timestamp:
                break

            new_next_timestamp = earliest_timestamp - 1

            if new_next_timestamp >= next_timestamp:
                raise RuntimeError("API pagination did not move backward.")

            next_timestamp = new_next_timestamp

    if not records:
        raise RuntimeError("The API returned no BTC/USD observations.")

    frame = pd.DataFrame.from_records(records)

    if "time" not in frame.columns:
        raise RuntimeError("The API observations did not contain timestamps.")

    frame["date"] = pd.to_datetime(
        frame["time"],
        unit="s",
        utc=True,
    ).dt.normalize()

    frame = frame.rename(
        columns={
            "volumefrom": "volume_btc",
            "volumeto": "volume_usd",
        }
    )

    frame = frame.loc[:, RAW_COLUMNS].copy()

    frame = frame.drop_duplicates(
        subset=["date"],
        keep="last",
    )

    date_mask = frame["date"].between(
        start_date,
        end_date,
    )

    frame = frame.loc[date_mask].copy()

    frame = frame.sort_values(
        by=["date"],
    )

    frame = frame.reset_index(
        drop=True,
    )

    return frame
