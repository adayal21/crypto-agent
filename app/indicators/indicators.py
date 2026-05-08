import pandas_ta as ta

def add_indicators(df):

    # Momentum: helps detect oversold, neutral, or strong bullish zones.
    df['rsi'] = ta.rsi(
        df['close'],
        length=14
    )

    # Volume benchmark: used to compare current volume against recent norm.
    df['volume_sma_20'] = (
        df['volume']
        .rolling(window=20)
        .mean()
    )

    # Short trend baseline for current timeframe direction.
    df['ema_20'] = ta.ema(
        df['close'],
        length=20
    )

    # MACD gives momentum confirmation for setup detection.
    macd = ta.macd(df['close'])

    df['macd'] = macd['MACD_12_26_9']

    df['macd_signal'] = macd['MACDs_12_26_9']

    # ATR approximates current volatility.
    df['atr'] = ta.atr(
        df['high'],
        df['low'],
        df['close'],
        length=14
    )

    return df
