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

from strategies.market_state_engine import (
    generate_structured_market_state
)

from strategies.position_management_engine import (
    evaluate_position_management
)

from llm.llm_decision_engine import (
    get_ai_decision
)

from paper_trading.paper_trader import (
    execute_paper_trade
)

from paper_trading.portfolio_manager import (
    load_portfolio
)

from paper_trading.portfolio_manager import (
    save_portfolio
)

ASSETS = [
    "BTC/USDT",
    "ETH/USDT",
    "SOL/USDT"
]

# =========================
# CONTINUOUS LOOP
# =========================

while True:

    # One full cycle: scan every isolated asset portfolio.
    print("\n========================")
    print("NEW TRADING CYCLE")
    print("========================")

    for asset_symbol in ASSETS:

        try:

            asset_name = asset_symbol.split("/")[0]

            print("\n------------------------")
            print(f"ASSET: {asset_symbol}")
            print("------------------------")

            # =========================
            # FETCH MARKET DATA
            # =========================

            df_5m = fetch_market_data(
                symbol=asset_symbol,
                timeframe='5m'
            )

            df_1h = fetch_market_data(
                symbol=asset_symbol,
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

            market_context = generate_structured_market_state(
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
                asset_symbol=asset_symbol,
                market_summary=market_summary,
                trade_setup=trade_setup,
                asset_price=df_5m.iloc[-1]['close']
            )

            # =========================
            # LOAD PORTFOLIO STATE
            # =========================

            portfolio = load_portfolio(asset_symbol)

            asset_holdings = portfolio[
                "asset_holdings"
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
                asset_holdings > 0
                and avg_entry_price > 0
            ):

                # Percent gain/loss on the open asset position.
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
                f"{asset_name} Holdings: "
                f"{asset_holdings}"
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
            # POSITION MANAGEMENT
            # =========================

            position_exit_decision = evaluate_position_management(
                portfolio,
                unrealized_pnl
            )

            if asset_holdings > 0:

                save_portfolio(
                    portfolio,
                    asset_symbol
                )

            if position_exit_decision:

                print("\n=== POSITION MANAGEMENT EXIT ===")

                print(position_exit_decision)

                execute_paper_trade(
                    decision=position_exit_decision,
                    asset_price=current_price,
                    asset_symbol=asset_symbol
                )

                continue

            # =========================
            # NO SETUP FILTER
            # =========================

            if (
                trade_setup["setup_type"] == "NO_SETUP"
                and asset_holdings == 0
            ):

                # Skip the LLM only when there is no setup and no open position.
                print("\nNo valid trade setup detected.")

                continue

            # =========================
            # AI DECISION
            # =========================

            ai_response = get_ai_decision(
                market_context,
                trade_setup,
                asset_symbol,
                asset_holdings,
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
                asset_price=current_price,
                asset_symbol=asset_symbol
            )

        except Exception as e:

            print(f"\nERROR OCCURRED FOR {asset_symbol}:")

            print(e)

    # =========================
    # WAIT 5 MINUTES
    # =========================

    print("\nWaiting 5 minutes...\n")

    time.sleep(300)
