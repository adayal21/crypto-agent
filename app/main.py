import json
import time
import subprocess
import sys

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
    generate_market_state,
    generate_structured_market_state
)

from strategies.position_management_engine import (
    evaluate_position_management
)

from llm.openrouter_decision_engine import (
    get_ai_decision
)

from paper_trading.paper_trader import (
    execute_paper_trade
)

from paper_trading.portfolio_manager import (
    load_portfolio,
    save_portfolio
)

ASSETS = [
    "BTC/USD",
    "ETH/USD",
    "SOL/USD"
]

# =========================
# START STREAMLIT DASHBOARD
# =========================

try:

    subprocess.Popen([

        sys.executable,
        "-m",
        "streamlit",
        "run",
        "app/dashboard/dashboard.py",

        "--server.address=0.0.0.0",

        "--server.port=8501"

    ])

    print(
        "\nStreamlit dashboard launched successfully."
    )

except Exception as e:

    print(
        "\nFailed to launch Streamlit dashboard:"
    )

    print(e)

# =========================
# CONTINUOUS LOOP
# =========================

while True:

    print("\n========================")
    print("NEW TRADING CYCLE")
    print("========================")

    for asset_symbol in ASSETS:

        try:

            asset_name = (
                asset_symbol.split("/")[0]
            )

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
            # MARKET STATE
            # =========================

            market_summary = (
                generate_market_state(
                    df_5m,
                    df_1h
                )
            )

            market_context = (
                generate_structured_market_state(
                    df_5m,
                    df_1h
                )
            )

            print("\n=== MARKET STATE ===")

            print(market_summary)

            # =========================
            # TRADE SETUP
            # =========================

            trade_setup = detect_trade_setup(
                df_5m,
                df_1h
            )

            # =========================
            # OVERBOUGHT ENTRY FILTER
            # =========================

            if (
                market_context.get(
                    "momentum_state"
                ) == "overbought condition"
                and trade_setup["setup_type"]
                == "LONG_SETUP"
            ):

                trade_setup["confidence"] = max(
                    0.50,
                    trade_setup["confidence"] - 0.10
                )

                if (
                    trade_setup["setup_quality"]
                    == "strong"
                ):

                    trade_setup["setup_quality"] = (
                        "moderate"
                    )

                trade_setup["reason"] += (
                    " Late-entry overbought "
                    "risk detected."
                )

            print("\n=== TRADE SETUP ===")

            print(trade_setup)

            # =========================
            # LOG MARKET CYCLE
            # =========================

            current_price = (
                df_5m.iloc[-1]['close']
            )

            log_market_cycle(
                asset_symbol=asset_symbol,
                market_summary=market_summary,
                trade_setup=trade_setup,
                asset_price=current_price
            )

            # =========================
            # LOAD PORTFOLIO
            # =========================

            portfolio = load_portfolio(
                asset_symbol
            )

            asset_holdings = portfolio[
                "asset_holdings"
            ]

            avg_entry_price = portfolio.get(
                "avg_entry_price",
                0
            )

            scale_in_count = portfolio.get(
                "scale_in_count",
                0
            )

            # =========================
            # UNREALIZED PNL
            # =========================

            unrealized_pnl = 0

            if (
                asset_holdings > 0
                and avg_entry_price > 0
            ):

                unrealized_pnl = (
                    (
                        current_price
                        - avg_entry_price
                    )
                    / avg_entry_price
                ) * 100

            print("\n=== POSITION STATUS ===")

            print(
                f"{asset_name} Holdings: "
                f"{asset_holdings:.6f}"
            )

            print(
                f"Average Entry Price: "
                f"{avg_entry_price:.2f}"
            )

            print(
                f"Current Price: "
                f"{current_price:.2f}"
            )

            print(
                f"Unrealized PnL: "
                f"{unrealized_pnl:.2f}%"
            )

            # =========================
            # DETERMINISTIC POSITION MANAGEMENT
            # =========================

            position_exit_decision = evaluate_position_management(
                portfolio,
                unrealized_pnl,
                market_context,
                trade_setup
            )

            if asset_holdings > 0:

                save_portfolio(
                    portfolio,
                    asset_symbol
                )

            # =========================
            # FORCED EXIT OVERRIDE
            # =========================

            if position_exit_decision:

                print(
                    "\n=== POSITION MANAGEMENT EXIT ==="
                )

                print(position_exit_decision)

                execute_paper_trade(
                    decision=position_exit_decision,
                    asset_price=current_price,
                    asset_symbol=asset_symbol,
                    unrealized_pnl=unrealized_pnl
                )

                continue

            # =========================
            # SHORT SETUP BLOCK
            # =========================

            if (
                trade_setup["setup_type"]
                == "SHORT_SETUP"
                and asset_holdings <= 0
            ):

                print(
                    "\nSHORT setup detected "
                    "but short-selling is disabled."
                )

                continue

            # =========================
            # NO SETUP + NO POSITION
            # =========================

            if (
                trade_setup["setup_type"]
                == "NO_SETUP"
                and asset_holdings <= 0
            ):

                print(
                    "\nNo valid trade setup detected."
                )

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

            try:

                decision = json.loads(
                    ai_response
                )

            except json.JSONDecodeError:

                print(
                    "\nInvalid AI JSON response."
                )

                print(ai_response)

                continue

            # =========================
            # MARKET STATE EXTRACTION
            # =========================

            trend_state = market_context.get(
                "trend_state"
            )

            momentum_state = market_context.get(
                "momentum_state"
            )

            higher_tf_state = market_context.get(
                "higher_timeframe_state"
            )

            # =========================
            # DETERMINISTIC ACTION VALIDATION
            # =========================

            decision["invalid_semantic_action"] = False

            if (
                asset_holdings <= 0
                and decision["action"]
                == "HOLD_POSITION"
            ):

                decision["invalid_semantic_action"] = True

                decision["action"] = (
                    "NO_ACTION"
                )

                decision["confidence"] = min(
                    decision["confidence"],
                    0.70
                )

                decision["reason"] = (
                    "No active position exists."
                )

            if (
                asset_holdings <= 0
                and decision["action"]
                == "SELL"
            ):

                decision["invalid_semantic_action"] = True

                decision["action"] = (
                    "NO_ACTION"
                )

                decision["confidence"] = min(
                    decision["confidence"],
                    0.70
                )

                decision["reason"] = (
                    "No holdings exist to sell."
                )

            # =========================
            # HOLD POSITION OVERRIDE
            # =========================

            if (
                asset_holdings > 0
                and decision["action"]
                == "HOLD_POSITION"
                and trend_state == "bearish"
                and momentum_state
                == "weak bearish momentum"
            ):

                decision = {
                    "action": "SELL",
                    "confidence": 1.0,
                    "reason":
                        (
                            "Deterministic override "
                            "triggered due to bearish "
                            "trend deterioration."
                        )
                }

            # =========================
            # HOLD CONFIDENCE NORMALIZATION
            # =========================

            if (
                decision["action"]
                == "HOLD_POSITION"
            ):

                decision["confidence"] = min(
                    decision["confidence"],
                    0.80
                )

            # =========================
            # BEARISH BUY BLOCK
            # =========================

            if (
                decision["action"] == "BUY"
                and trend_state == "bearish"
                and higher_tf_state
                != "higher timeframe bullish"
            ):

                decision["action"] = (
                    "NO_ACTION"
                )

                decision["reason"] = (
                    "BUY blocked due to bearish "
                    "higher timeframe structure."
                )

            # =========================
            # MAX PYRAMIDING PROTECTION
            # =========================

            if (
                decision["action"] == "BUY"
                and asset_holdings > 0
                and scale_in_count >= 3
            ):

                decision["action"] = (
                    "NO_ACTION"
                )

                decision["reason"] = (
                    "Scale-in blocked due to "
                    "max pyramiding limit."
                )

            # =========================
            # CONFIDENCE SANITY FILTER
            # =========================

            if (
                trade_setup["setup_quality"]
                == "moderate"
                and decision["confidence"] > 0.90
            ):

                decision["confidence"] = 0.85

            # =========================
            # DETERMINISTIC CONFIDENCE FLOOR
            # =========================

            if (
                trade_setup["confidence"] >= 0.75
                and decision["action"] == "BUY"
                and decision["confidence"]
                < trade_setup["confidence"]
            ):

                decision["confidence"] = (
                    trade_setup["confidence"]
                )

                decision["reason"] += (
                    " Confidence aligned to "
                    "deterministic setup score."
                )

            # =========================
            # DETERMINISTIC SETUP OVERRIDE
            # =========================

            if (
                trade_setup["setup_type"] != "NO_SETUP"
                and trade_setup["setup_type"] != "SHORT_SETUP"
                and trade_setup["confidence"] >= 0.75
                and decision["action"] == "NO_ACTION"
                and not decision.get(
                    "invalid_semantic_action",
                    False
                )
            ):

                decision["action"] = "BUY"

                decision["confidence"] = max(
                    decision["confidence"],
                    trade_setup["confidence"]
                )

                decision["reason"] = (
                    "Deterministic setup confidence "
                    "override triggered."
                )

            print("\n=== AI DECISION ===")

            print(decision)

            # =========================
            # EXECUTE PAPER TRADE
            # =========================

            execute_paper_trade(
                decision=decision,
                asset_price=current_price,
                asset_symbol=asset_symbol,
                unrealized_pnl=unrealized_pnl
            )

        except Exception as e:

            print(
                f"\nERROR OCCURRED "
                f"FOR {asset_symbol}:"
            )

            print(e)

    # =========================
    # WAIT 5 MINUTES
    # =========================

    print("\nWaiting 5 minutes...\n")

    time.sleep(300)