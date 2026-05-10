def generate_market_state(
        df_15m,
        df_1h
    ):

    market_state = (
        generate_structured_market_state(
            df_15m,
            df_1h
        )
    )

    readable_market_state = f"""
Market State Analysis

Trend State:
{market_state["trend_state"]}

Momentum State:
{market_state["momentum_state"]}

Trend Acceleration:
{market_state["trend_acceleration"]}

MACD State:
{market_state["macd_state"]}

Volatility State:
{market_state["volatility_state"]}

Trend Strength:
{market_state["trend_strength"]}

Market Regime:
{market_state["market_regime"]}

Trade Bias:
{market_state["trade_bias"]}

Higher Timeframe State:
{market_state["higher_timeframe_state"]}

Volume State:
{market_state["volume_state"]}
"""

    return readable_market_state


def generate_structured_market_state(
        df_15m,
        df_1h
    ):

    latest = df_15m.iloc[-1]

    # =========================
    # TREND STATE
    # =========================

    trend_bullish = (
        latest['ema_20']
        > latest['ema_50']
    )

    if trend_bullish:

        trend_state = "bullish"

    else:

        trend_state = "bearish"

    # =========================
    # HIGHER TIMEFRAME
    # =========================

    higher_tf_bullish = (
        df_1h.iloc[-1]['ema_20']
        > df_1h.iloc[-1]['ema_50']
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

    ema_slope = (
        latest['ema_20']
        - df_15m.iloc[-5]['ema_20']
    )

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

    if rsi < 35:

        momentum_state = (
            "weak bearish momentum"
        )

    elif rsi < 55:

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

    atr_pct = latest['atr_pct']

    if atr_pct > 1.5:

        volatility_state = (
            "high volatility"
        )

    elif atr_pct < 0.25:

        volatility_state = (
            "compressed volatility"
        )

    else:

        volatility_state = (
            "normal volatility"
        )

    # =========================
    # ADX TREND STRENGTH
    # =========================

    adx = latest['adx']

    if adx >= 25:

        trend_strength = (
            "strong trend"
        )

    elif adx >= 18:

        trend_strength = (
            "moderate trend"
        )

    else:

        trend_strength = (
            "weak trend"
        )

    # =========================
    # MARKET REGIME
    # =========================

    if (
        adx < 15
        or latest['ema_spread_pct'] < 0.15
    ):

        market_regime = (
            "choppy ranging market"
        )

    elif (
        atr_pct < 0.25
    ):

        market_regime = (
            "low volatility compression"
        )

    else:

        market_regime = (
            "tradable trend environment"
        )

    # =========================
    # VOLUME STATE
    # =========================

    if latest['volume_ratio'] >= 1.2:

        volume_state = (
            "high relative volume"
        )

    else:

        volume_state = (
            "weak relative volume"
        )

    # =========================
    # TRADE BIAS
    # =========================

    if (
        trend_state == "bullish"
        and trend_strength == "strong trend"
        and market_regime
        == "tradable trend environment"
    ):

        trade_bias = (
            "trend continuation"
        )

    else:

        trade_bias = (
            "unclear market structure"
        )

    return {
        "trend_state": trend_state,
        "momentum_state": momentum_state,
        "trend_acceleration": trend_acceleration,
        "macd_state": macd_state,
        "volatility_state": volatility_state,
        "trend_strength": trend_strength,
        "market_regime": market_regime,
        "trade_bias": trade_bias,
        "higher_timeframe_state": higher_tf_state,
        "volume_state": volume_state
    }