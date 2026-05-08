def strategy_engine(df):

    latest = df.iloc[-1]

    rsi = latest["rsi"]

    macd = latest["macd"]

    macd_signal = latest["macd_signal"]

    # =========================
    # MACD STATE
    # =========================

    if macd > macd_signal:
        macd_state = "bullish"
    else:
        macd_state = "bearish"

    # =========================
    # STRATEGY LOGIC
    # =========================

    if rsi < 30 and macd_state == "bullish":

        action = "BUY"

        confidence = 0.8

    elif rsi > 70 and macd_state == "bearish":

        action = "SELL"

        confidence = 0.8

    else:

        action = "HOLD"

        confidence = 0.6

    return {
        "action": action,
        "confidence": confidence
    }