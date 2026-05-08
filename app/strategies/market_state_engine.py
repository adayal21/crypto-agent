def generate_market_state(
        df_5m,
        df_1h
    ):

    # Use the latest 5-minute candle as the current market snapshot.
    latest = df_5m.iloc[-1]

    # =========================
    # TREND STATE
    # =========================

    if latest['close'] > latest['ema_20']:

        trend_state = "bullish"

    else:

        trend_state = "bearish"

    higher_tf_bullish = (
        df_1h.iloc[-1]['close']
        > df_1h.iloc[-1]['ema_20']
    )

    # EMA slope shows whether the short-term trend is gaining strength.
    ema_slope = (
        latest['ema_20']
        - df_5m.iloc[-5]['ema_20']
    )

    if higher_tf_bullish:

        higher_tf_state = (
            "higher timeframe bullish"
        )

    else:

        higher_tf_state = (
            "higher timeframe bearish"
        )
    
    # =========================
    # TREND ACCELERATION
    # =========================

    if ema_slope > 0:

        trend_acceleration = (
            "trend strengthening"
        )

    else:

        trend_acceleration = (
            "trend weakening"
        )
    
    # =========================
    # RSI STATE
    # =========================

    rsi = latest['rsi']

    if rsi < 30:

        momentum_state = (
            "oversold reversal zone"
        )

    elif rsi < 45:

        momentum_state = (
            "weak bearish momentum"
        )

    elif rsi < 60:

        momentum_state = (
            "neutral momentum"
        )

    elif rsi < 70:

        momentum_state = (
            "strong bullish momentum"
        )

    else:

        momentum_state = (
            "overbought condition"
        )

    # =========================
    # MACD STATE
    # =========================

    if latest['macd'] > latest['macd_signal']:

        macd_state = (
            "bullish momentum crossover"
        )

    else:

        macd_state = (
            "bearish momentum crossover"
        )

    # =========================
    # VOLATILITY STATE
    # =========================

    atr = latest['atr']

    if atr > 300:

        volatility_state = (
            "high volatility"
        )

    else:

        volatility_state = (
            "normal volatility"
        )

    # =========================
    # TRADE BIAS
    # =========================

    if (
        trend_state == "bullish"
        and "bullish" in macd_state
        and "strong bullish" in momentum_state
    ):

        # Trend, momentum, and MACD all point in the same direction.
        trade_bias = (
            "potential breakout continuation"
        )

    elif (
        trend_state == "bearish"
        and "oversold" in momentum_state
    ):

        trade_bias = (
            "possible reversal setup"
        )

    elif (
        "overbought" in momentum_state
    ):

        trade_bias = (
            "late entry risk"
        )

    else:

        trade_bias = (
            "unclear market structure"
        )

    # =========================
    # VOLUME STATE
    # =========================

    if (
        latest['volume']
        > latest['volume_sma_20']
    ):

        # High relative volume means current move has stronger participation.
        volume_state = (
            "high relative volume"
        )

    else:

        volume_state = (
            "weak relative volume"
        )

    market_state = f"""
Market State Analysis

Trend State:
{trend_state}

Momentum State:
{momentum_state}

Trend Acceleration:
{trend_acceleration}

MACD State:
{macd_state}

Volatility State:
{volatility_state}

Trade Bias:
{trade_bias}

Higher Timeframe State:
{higher_tf_state}

Volume State:
{volume_state}
"""

    return market_state
