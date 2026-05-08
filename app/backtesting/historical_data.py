import os
import time
from datetime import datetime, timedelta

import ccxt
import pandas as pd

DATA_DIR = "data"

exchange = ccxt.bybit()


def get_cache_path(
    asset_symbol,
    timeframe
):

    file_symbol = (
        asset_symbol
        .replace("/", "_")
        .replace(":", "_")
    )

    return os.path.join(
        DATA_DIR,
        f"{file_symbol}_{timeframe}.csv"
    )


def load_historical_data(
    asset_symbol,
    timeframe,
    days=90,
    refresh=False
):

    cache_path = get_cache_path(
        asset_symbol,
        timeframe
    )

    if (
        os.path.exists(cache_path)
        and not refresh
    ):

        df = pd.read_csv(cache_path)

        df["timestamp"] = pd.to_datetime(
            df["timestamp"]
        )

        return df

    return fetch_and_cache_historical_data(
        asset_symbol=asset_symbol,
        timeframe=timeframe,
        days=days,
        cache_path=cache_path
    )


def fetch_and_cache_historical_data(
    asset_symbol,
    timeframe,
    days,
    cache_path
):

    os.makedirs(
        DATA_DIR,
        exist_ok=True
    )

    since = int(
        (
            datetime.utcnow()
            - timedelta(days=days)
        ).timestamp()
        * 1000
    )

    all_candles = []

    while True:

        candles = exchange.fetch_ohlcv(
            asset_symbol,
            timeframe=timeframe,
            since=since,
            limit=1000
        )

        if not candles:

            break

        all_candles.extend(candles)

        last_timestamp = candles[-1][0]

        if last_timestamp <= since:

            break

        since = last_timestamp + 1

        time.sleep(
            exchange.rateLimit / 1000
        )

        if len(candles) < 1000:

            break

    df = pd.DataFrame(
        all_candles,
        columns=[
            "timestamp",
            "open",
            "high",
            "low",
            "close",
            "volume"
        ]
    )

    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        unit="ms"
    )

    df = (
        df
        .drop_duplicates(subset=["timestamp"])
        .sort_values("timestamp")
        .reset_index(drop=True)
    )

    df.to_csv(
        cache_path,
        index=False
    )

    return df
