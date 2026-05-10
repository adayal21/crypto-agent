def detect_trade_setup(
    df_15m,
    df_1h
):

    latest = df_15m.iloc[-1]

    higher_tf_latest = df_1h.iloc[-1]

    # =========================
    # REGIME FILTERS
    # =========================

    adx = latest['adx']

    atr_pct = latest['atr_pct']

    ema_spread = latest['ema_spread_pct']

    volume_ratio = latest['volume_ratio']

    if (
        adx < 15
        or atr_pct < 0.25
        or ema_spread < 0.10
        or volume_ratio < 0.85
    ):

        return {
            "setup_type": "NO_SETUP",
            "setup_quality": "none",
            "confidence": 0.50,
            "reason":
                (
                    "No-trade regime filter "
                    "activated due to weak "
                    "trend structure or "
                    "compressed conditions."
                )
        }

    # =========================
    # TREND CONDITIONS
    # =========================

    trend_bullish = (
        latest['ema_20']
        > latest['ema_50']
    )

    higher_tf_bullish = (
        higher_tf_latest['ema_20']
        > higher_tf_latest['ema_50']
    )

    trend_bearish = (
        latest['ema_20']
        < latest['ema_50']
    )

    higher_tf_bearish = (
        higher_tf_latest['ema_20']
        < higher_tf_latest['ema_50']
    )

    # =========================
    # MOMENTUM
    # =========================

    macd_bullish = (
        latest['macd']
        > latest['macd_signal']
    )

    macd_bearish = (
        latest['macd']
        < latest['macd_signal']
    )

    rsi = latest['rsi']

    # =========================
    # STRONG LONG
    # =========================

    if (
        trend_bullish
        and higher_tf_bullish
        and macd_bullish
        and 55 <= rsi <= 68
        and adx >= 25
    ):

        return {
            "setup_type": "LONG_SETUP",
            "setup_quality": "strong",
            "confidence": 0.85,
            "reason":
                (
                    "Strong bullish trend "
                    "with volatility expansion "
                    "and higher timeframe "
                    "alignment."
                )
        }

    # =========================
    # MODERATE LONG
    # =========================

    elif (
        trend_bullish
        and higher_tf_bullish
        and rsi >= 52
        and adx >= 20
    ):

        return {
            "setup_type": "LONG_SETUP",
            "setup_quality": "moderate",
            "confidence": 0.70,
            "reason":
                (
                    "Bullish trend structure "
                    "detected with acceptable "
                    "continuation quality."
                )
        }

    # =========================
    # STRONG SHORT
    # =========================

    elif (
        trend_bearish
        and higher_tf_bearish
        and macd_bearish
        and rsi <= 45
        and adx >= 25
    ):

        return {
            "setup_type": "SHORT_SETUP",
            "setup_quality": "strong",
            "confidence": 0.85,
            "reason":
                (
                    "Strong bearish trend "
                    "with downside continuation "
                    "structure."
                )
        }

    # =========================
    # NO SETUP
    # =========================

    return {
        "setup_type": "NO_SETUP",
        "setup_quality": "none",
        "confidence": 0.50,
        "reason":
            (
                "No statistically favorable "
                "trade structure detected."
            )
    }