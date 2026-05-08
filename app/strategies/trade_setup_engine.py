def detect_trade_setup(
    df_5m,
    df_1h
):

    # The latest 5-minute candle drives the immediate entry setup.
    latest = df_5m.iloc[-1]

    trend_bullish = (
        latest['close'] > latest['ema_20']
    )

    higher_tf_bullish = (
        df_1h.iloc[-1]['close']
        > df_1h.iloc[-1]['ema_20']
    )

    macd_bullish = (
        latest['macd']
        > latest['macd_signal']
    )

    rsi = latest['rsi']

    # =========================
    # LONG SETUP
    # =========================

    if (
        trend_bullish
        and higher_tf_bullish
        and 50 <= rsi <= 75
    ):

        setup_quality = "strong"

        reason = (
            "Bullish trend aligned with higher timeframe confirmation."
        )

        # Momentum confirmation improves setup quality
        if not macd_bullish:

            setup_quality = "moderate"

            reason = (
                "Bullish trend present but momentum confirmation is weaker."
            )

        return {
            "setup_type": "LONG_SETUP",
            "setup_quality": setup_quality,
            "reason": reason
        }

    # =========================
    # REVERSAL SETUP
    # =========================

    elif (
        not trend_bullish
        and not higher_tf_bullish
        and macd_bullish
        and rsi < 35
    ):

        # Aggressive long: bearish trend, but momentum may be reversing.
        return {
            "setup_type": "REVERSAL_SETUP",
            "setup_quality": "aggressive",
            "reason":
                "Possible bullish reversal from oversold conditions."
        }

    # =========================
    # SHORT SETUP
    # =========================

    elif (
        not trend_bullish
        and not higher_tf_bullish
        and not macd_bullish
        and rsi < 45
    ):

        # Downtrend continuation: bearish trend and momentum align.
        return {
            "setup_type": "SHORT_SETUP",
            "setup_quality": "moderate",
            "reason":
                "Bearish trend with negative momentum confirmation."
        }

    # =========================
    # NO SETUP
    # =========================

    else:

        return {
            "setup_type": "NO_SETUP",
            "setup_quality": "none",
            "reason":
                "No strong trade structure detected."
        }
