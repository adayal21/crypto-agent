from paper_trading.trade_logger import log_trade
from paper_trading.portfolio_manager import (
    load_portfolio,
    save_portfolio
)


def execute_paper_trade(
    decision,
    btc_price
):

    portfolio = load_portfolio()

    cash_balance = portfolio["cash_balance"]

    btc_holdings = portfolio["btc_holdings"]

    avg_entry_price = portfolio.get(
        "avg_entry_price",
        0
    )

    action = decision["action"]

    confidence = decision["confidence"]

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

        if btc_holdings > 0:

            execution_status = "SKIPPED_ALREADY_HOLDING"

            print("\nAlready holding BTC.")
            print("Skipping additional BUY.")

        else:

            investment_amount = 1000

            if cash_balance >= investment_amount:

                btc_bought = (
                    investment_amount / btc_price
                )

                cash_balance -= investment_amount

                btc_holdings += btc_bought

                avg_entry_price = btc_price

                execution_status = "EXECUTED_BUY"

                print("\nBUY EXECUTED")

            else:

                execution_status = "SKIPPED_INSUFFICIENT_CASH"

                print("\nNot enough cash.")

    elif action == "SELL":

        if btc_holdings > 0:

            cash_balance += (
                btc_holdings * btc_price
            )

            btc_holdings = 0
            avg_entry_price = 0

            execution_status = "EXECUTED_SELL"

            print("\nSELL EXECUTED")

        else:

            execution_status = "SKIPPED_NO_HOLDINGS"

            print("\nNo BTC holdings to sell.")

    else:

        print("\nNO ACTION")

    # =========================
    # SAVE UPDATED PORTFOLIO
    # =========================

    portfolio["cash_balance"] = cash_balance

    portfolio["btc_holdings"] = btc_holdings

    portfolio["avg_entry_price"] = avg_entry_price
    
    save_portfolio(portfolio)

    # =========================
    # PORTFOLIO STATUS
    # =========================

    portfolio_value = (
        cash_balance
        + (btc_holdings * btc_price)
    )

    log_trade(
        status=execution_status,
        action=action,
        confidence=confidence,
        btc_price=btc_price,
        portfolio_value=portfolio_value,
        reason=decision["reason"]
    )
    
    print("\n=== PORTFOLIO STATUS ===")

    print(f"Cash Balance: ${cash_balance:.2f}")

    print(f"BTC Holdings: {btc_holdings:.6f}")

    print(f"Portfolio Value: ${portfolio_value:.2f}")
