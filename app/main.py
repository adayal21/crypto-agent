import json
import time

from market_data.market_data import (
    fetch_market_data
)

from indicators.indicators import (
    add_indicators
)

from strategies.market_summary import (
    generate_market_summary
)

from llm.llm_decision_engine import (
    get_ai_decision
)

from paper_trading.paper_trader import (
    execute_paper_trade
)

# =========================
# CONTINUOUS LOOP
# =========================

while True:

    try:

        print("\n========================")
        print("NEW TRADING CYCLE")
        print("========================")

        # =========================
        # FETCH MARKET DATA
        # =========================

        df = fetch_market_data()

        # =========================
        # ADD INDICATORS
        # =========================

        df = add_indicators(df)

        # =========================
        # GENERATE SUMMARY
        # =========================

        market_summary = (
            generate_market_summary(df)
        )

        print("\n=== MARKET SUMMARY ===")

        print(market_summary)

        # =========================
        # AI DECISION
        # =========================

        ai_response = get_ai_decision(
            market_summary
        )

        decision = json.loads(ai_response)

        print("\n=== AI DECISION ===")

        print(decision)

        # =========================
        # EXECUTE PAPER TRADE
        # =========================

        execute_paper_trade(
            decision=decision,
            btc_price=df.iloc[-1]['close']
        )

    except Exception as e:

        print("\nERROR OCCURRED:")

        print(e)

    # =========================
    # WAIT 5 MINUTES
    # =========================

    print("\nWaiting 5 minutes...\n")

    time.sleep(300)