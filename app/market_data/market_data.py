import ccxt
import pandas as pd

exchange = ccxt.binance()

def fetch_market_data(
    symbol='BTC/USDT',
    timeframe='5m',
    limit=100
):

    # Fetch recent candles from Bybit in CCXT's standard OHLCV format.
    ohlcv = exchange.fetch_ohlcv(
        symbol,
        timeframe=timeframe,
        limit=limit
    )

    df = pd.DataFrame(
        ohlcv,
        columns=[
            'timestamp',
            'open',
            'high',
            'low',
            'close',
            'volume'
        ]
    )

    # Convert exchange timestamps from milliseconds into pandas datetimes.
    df['timestamp'] = pd.to_datetime(
        df['timestamp'],
        unit='ms'
    )

    return df
