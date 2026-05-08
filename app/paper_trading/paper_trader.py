from paper_trading.trade_logger import log_trade
from paper_trading.portfolio_manager import (
    load_portfolio,
    save_portfolio
)


def execute_paper_trade(
    decision,
    asset_price,
    asset_symbol
):

    # Load the latest simulated account before applying the AI decision.
    portfolio = load_portfolio(asset_symbol)

    cash_balance = portfolio["cash_balance"]

    asset_holdings = portfolio["asset_holdings"]

    avg_entry_price = portfolio.get(
        "avg_entry_price",
        0
    )

    action = decision["action"]

    confidence = decision["confidence"]

    # Stored in CSV so skipped decisions are separated from real trades.
    execution_status = "SKIPPED_NO_ACTION"

    print("\n=== PAPER TRADING ===")

    # =========================
    # CONFIDENCE FILTER
    # =========================

    if confidence < 0.75:

        execution_status = "SKIPPED_LOW_CONFIDENCE"

        print("\nConfidence too low.")
        print("NO TRADE EXECUTED")

    elif action == "BUY":

        if asset_holdings > 0:

            execution_status = "SKIPPED_ALREADY_HOLDING"

            print(f"\nAlready holding {asset_symbol}.")
            print("Skipping additional BUY.")

        else:

            # Fixed sizing keeps the paper trader simple and predictable.
            investment_amount = 1000

            if cash_balance >= investment_amount:

                asset_bought = (
                    investment_amount / asset_price
                )

                cash_balance -= investment_amount

                asset_holdings += asset_bought

                avg_entry_price = asset_price

                portfolio["highest_unrealized_pnl"] = 0

                execution_status = "EXECUTED_BUY"

                print("\nBUY EXECUTED")

            else:

                execution_status = "SKIPPED_INSUFFICIENT_CASH"

                print("\nNot enough cash.")

    elif action == "SELL":

        if asset_holdings > 0:

            cash_balance += (
                asset_holdings * asset_price
            )

            asset_holdings = 0
            avg_entry_price = 0

            portfolio["highest_unrealized_pnl"] = 0

            execution_status = "EXECUTED_SELL"

            print("\nSELL EXECUTED")

        else:

            execution_status = "SKIPPED_NO_HOLDINGS"

            print(f"\nNo {asset_symbol} holdings to sell.")

    else:

        print("\nNO ACTION")

    # =========================
    # SAVE UPDATED PORTFOLIO
    # =========================

    portfolio["cash_balance"] = cash_balance

    portfolio["asset_holdings"] = asset_holdings

    portfolio["avg_entry_price"] = avg_entry_price

    if asset_holdings <= 0:

        portfolio["highest_unrealized_pnl"] = 0
    
    save_portfolio(
        portfolio,
        asset_symbol
    )

    # =========================
    # PORTFOLIO STATUS
    # =========================

    portfolio_value = (
        cash_balance
        + (asset_holdings * asset_price)
    )

    # Log both the requested action and what actually happened.
    log_trade(
        asset_symbol=asset_symbol,
        status=execution_status,
        action=action,
        confidence=confidence,
        asset_price=asset_price,
        portfolio_value=portfolio_value,
        reason=decision["reason"]
    )
    
    print("\n=== PORTFOLIO STATUS ===")

    print(f"Cash Balance: ${cash_balance:.2f}")

    print(f"{asset_symbol} Holdings: {asset_holdings:.6f}")

    print(f"Portfolio Value: ${portfolio_value:.2f}")
