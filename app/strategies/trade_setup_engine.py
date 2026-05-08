def detect_trade_setup(
    df_5m,
    df_1h
):

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
        and macd_bullish
        and 50 <= rsi <= 70
    ):

        return {
            "setup_type": "LONG_SETUP",
            "setup_quality": "moderate",
            "reason":
                "Bullish trend with positive momentum confirmation."
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