import ccxt
import pandas as pd

exchange = ccxt.bybit()

def fetch_market_data(
    symbol='BTC/USDT',
    timeframe='5m',
    limit=100
):

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

    df['timestamp'] = pd.to_datetime(
        df['timestamp'],
        unit='ms'
    )

    return df