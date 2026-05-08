def generate_market_summary(df):

    latest = df.iloc[-1]

    # Trend
    if latest['close'] > latest['ema_20']:
        trend = "bullish"
    else:
        trend = "bearish"

    # RSI State
    if latest['rsi'] > 70:
        rsi_state = "overbought"

    elif latest['rsi'] < 30:
        rsi_state = "oversold"

    else:
        rsi_state = "neutral"

    # MACD State
    if latest['macd'] > latest['macd_signal']:
        macd_state = "bullish crossover"

    else:
        macd_state = "bearish crossover"

    summary = f"""
BTC Market Summary

Current Price: {latest['close']}

Trend: {trend}

RSI: {latest['rsi']:.2f}
RSI State: {rsi_state}

MACD State: {macd_state}

ATR: {latest['atr']:.2f}
"""

    return summary