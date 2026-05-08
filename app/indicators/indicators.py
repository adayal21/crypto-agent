import pandas_ta as ta

def add_indicators(df):

    df['rsi'] = ta.rsi(
        df['close'],
        length=14
    )

    df['ema_20'] = ta.ema(
        df['close'],
        length=20
    )

    macd = ta.macd(df['close'])

    df['macd'] = macd['MACD_12_26_9']

    df['macd_signal'] = macd['MACDs_12_26_9']

    df['atr'] = ta.atr(
        df['high'],
        df['low'],
        df['close'],
        length=14
    )

    return df