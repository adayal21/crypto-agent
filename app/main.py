import json
import time

from logger.market_logger import (
    log_market_cycle
)

from market_data.market_data import (
    fetch_market_data
)

from indicators.indicators import (
    add_indicators
)

from strategies.trade_setup_engine import (
    detect_trade_setup
)

from strategies.market_state_engine import (
    generate_market_state
)

from llm.llm_decision_engine import (
    get_ai_decision
)

from paper_trading.paper_trader import (
    execute_paper_trade
)

from paper_trading.paper_trader import (
    load_portfolio
)

# =========================
# CONTINUOUS LOOP
# =========================

while True:

    try:

        # One full cycle: collect data, evaluate setup, then paper trade.
        print("\n========================")
        print("NEW TRADING CYCLE")
        print("========================")

        # =========================
        # FETCH MARKET DATA
        # =========================

        df_5m = fetch_market_data(
            symbol='BTC/USDT',
            timeframe='5m'
        )

        df_1h = fetch_market_data(
            symbol='BTC/USDT',
            timeframe='1h'
        )

        # =========================
        # ADD INDICATORS
        # =========================

        df_5m = add_indicators(df_5m)

        df_1h = add_indicators(df_1h)

        # =========================
        # GENERATE SUMMARY
        # =========================

        market_summary = generate_market_state(
            df_5m,
            df_1h
        )

        print("\n=== MARKET STATE ===")

        print(market_summary)

        trade_setup = detect_trade_setup(
            df_5m,
            df_1h
        )

        print("\n=== TRADE SETUP ===")

        print(trade_setup)

        log_market_cycle(
            market_summary=market_summary,
            trade_setup=trade_setup,
            btc_price=df_5m.iloc[-1]['close']
        )

        # =========================
        # LOAD PORTFOLIO STATE
        # =========================

        portfolio = load_portfolio()

        btc_holdings = portfolio[
            "btc_holdings"
        ]

        avg_entry_price = portfolio.get(
            "avg_entry_price",
            0
        )

        current_price = (
            df_5m.iloc[-1]['close']
        )

        # =========================
        # UNREALIZED PNL
        # =========================

        if (
            btc_holdings > 0
            and avg_entry_price > 0
        ):

            # Percent gain/loss on the open BTC position.
            unrealized_pnl = (
                (
                    current_price
                    - avg_entry_price
                )
                / avg_entry_price
            ) * 100

        else:

            unrealized_pnl = 0

        print("\n=== POSITION STATUS ===")

        print(
            f"BTC Holdings: "
            f"{btc_holdings}"
        )

        print(
            f"Average Entry Price: "
            f"{avg_entry_price}"
        )

        print(
            f"Unrealized PnL: "
            f"{unrealized_pnl:.2f}%"
        )

        # =========================
        # NO SETUP FILTER
        # =========================

        if trade_setup["setup_type"] == "NO_SETUP":

            # Skip the LLM when the rule-based setup engine finds nothing.
            print("\nNo valid trade setup detected.")

            print("\nWaiting 5 minutes...\n")

            time.sleep(300)

            continue

        # =========================
        # AI DECISION
        # =========================

        ai_response = get_ai_decision(
            market_summary,
            trade_setup,
            btc_holdings,
            unrealized_pnl
        )

        # Ollama is instructed to return JSON only.
        decision = json.loads(ai_response)

        print("\n=== AI DECISION ===")

        print(decision)

        # =========================
        # EXECUTE PAPER TRADE
        # =========================

        execute_paper_trade(
            decision=decision,
            btc_price=df_5m.iloc[-1]['close']
        )

    except Exception as e:

        print("\nERROR OCCURRED:")

        print(e)

    # =========================
    # WAIT 5 MINUTES
    # =========================

    print("\nWaiting 5 minutes...\n")

    time.sleep(300)
