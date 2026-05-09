def detect_trade_setup(
    df_5m,
    df_1h
):

    # =========================
    # LATEST MARKET DATA
    # =========================

    latest = df_5m.iloc[-1]

    higher_tf_latest = df_1h.iloc[-1]

    # =========================
    # TREND CONDITIONS
    # =========================

    trend_bullish = (
        latest['close']
        > latest['ema_20']
    )

    higher_tf_bullish = (
        higher_tf_latest['close']
        > higher_tf_latest['ema_20']
    )

    trend_bearish = (
        latest['close']
        < latest['ema_20']
    )

    higher_tf_bearish = (
        higher_tf_latest['close']
        < higher_tf_latest['ema_20']
    )

    # =========================
    # MOMENTUM CONDITIONS
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

    volume_ratio = latest.get(
        'volume_ratio',
        1
    )

    strong_volume = (
        volume_ratio >= 1.2
    )

    # =========================
    # LONG SETUP — STRONG
    # =========================

    if (
        trend_bullish
        and higher_tf_bullish
        and macd_bullish
        and 55 <= rsi <= 70
    ):

        confidence = 0.85

        if strong_volume:

            confidence += 0.05

        confidence = min(
            confidence,
            0.95
        )

        return {
            "setup_type": "LONG_SETUP",
            "setup_quality": "strong",
            "confidence": round(
                confidence,
                2
            ),
            "reason":
                (
                    "Bullish trend aligned across "
                    "higher timeframe and momentum."
                )
        }

    # =========================
    # LONG SETUP — MODERATE
    # =========================

    elif (
        trend_bullish
        and higher_tf_bullish
        and 50 <= rsi <= 75
    ):

        confidence = 0.70

        if macd_bullish:

            confidence += 0.05

        if strong_volume:

            confidence += 0.05

        confidence = min(
            confidence,
            0.85
        )

        return {
            "setup_type": "LONG_SETUP",
            "setup_quality": "moderate",
            "confidence": round(
                confidence,
                2
            ),
            "reason":
                (
                    "Bullish trend present but "
                    "momentum confirmation is weaker."
                )
        }

    # =========================
    # REVERSAL SETUP
    # =========================

    elif (
        trend_bearish
        and higher_tf_bearish
        and macd_bullish
        and rsi < 35
    ):

        confidence = 0.65

        if strong_volume:

            confidence += 0.05

        confidence = min(
            confidence,
            0.75
        )

        return {
            "setup_type": "REVERSAL_SETUP",
            "setup_quality": "aggressive",
            "confidence": round(
                confidence,
                2
            ),
            "reason":
                (
                    "Possible bullish reversal "
                    "from oversold conditions."
                )
        }

    # =========================
    # SHORT SETUP — STRONG
    # =========================

    elif (
        trend_bearish
        and higher_tf_bearish
        and macd_bearish
        and rsi < 45
    ):

        confidence = 0.85

        if strong_volume:

            confidence += 0.05

        confidence = min(
            confidence,
            0.95
        )

        return {
            "setup_type": "SHORT_SETUP",
            "setup_quality": "strong",
            "confidence": round(
                confidence,
                2
            ),
            "reason":
                (
                    "Bearish trend aligned across "
                    "higher timeframe and momentum."
                )
        }

    # =========================
    # SHORT SETUP — MODERATE
    # =========================

    elif (
        trend_bearish
        and higher_tf_bearish
        and rsi < 50
    ):

        confidence = 0.70

        if macd_bearish:

            confidence += 0.05

        if strong_volume:

            confidence += 0.05

        confidence = min(
            confidence,
            0.85
        )

        return {
            "setup_type": "SHORT_SETUP",
            "setup_quality": "moderate",
            "confidence": round(
                confidence,
                2
            ),
            "reason":
                (
                    "Bearish trend present but "
                    "momentum confirmation is weaker."
                )
        }

    # =========================
    # NO SETUP
    # =========================

    else:

        return {
            "setup_type": "NO_SETUP",
            "setup_quality": "none",
            "confidence": 0.50,
            "reason":
                (
                    "No strong trade structure "
                    "detected."
                )
        }