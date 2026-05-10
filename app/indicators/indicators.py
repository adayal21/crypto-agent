import pandas_ta as ta


def add_indicators(df):

    # =========================
    # RSI
    # =========================

    df['rsi'] = ta.rsi(
        df['close'],
        length=14
    )

    # =========================
    # EMA STRUCTURE
    # =========================

    df['ema_20'] = ta.ema(
        df['close'],
        length=20
    )

    df['ema_50'] = ta.ema(
        df['close'],
        length=50
    )

    # =========================
    # EMA SPREAD
    # =========================

    df['ema_spread_pct'] = (
        (
            abs(
                df['ema_20']
                - df['ema_50']
            )
        )
        / df['close']
    ) * 100

    # =========================
    # MACD
    # =========================

    macd = ta.macd(
        df['close']
    )

    df['macd'] = (
        macd['MACD_12_26_9']
    )

    df['macd_signal'] = (
        macd['MACDs_12_26_9']
    )

    # =========================
    # ATR
    # =========================

    df['atr'] = ta.atr(
        df['high'],
        df['low'],
        df['close'],
        length=14
    )

    # =========================
    # NORMALIZED ATR
    # =========================

    df['atr_pct'] = (
        df['atr']
        / df['close']
    ) * 100

    # =========================
    # ADX
    # =========================

    adx = ta.adx(
        df['high'],
        df['low'],
        df['close'],
        length=14
    )

    df['adx'] = (
        adx['ADX_14']
    )

    # =========================
    # VOLUME STRUCTURE
    # =========================

    df['volume_sma_20'] = (
        df['volume']
        .rolling(window=20)
        .mean()
    )

    df['volume_ratio'] = (
        df['volume']
        / df['volume_sma_20']
    )

    return df