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

    portfolio = load_portfolio(
        asset_symbol
    )

    cash_balance = portfolio[
        "cash_balance"
    ]

    asset_holdings = portfolio[
        "asset_holdings"
    ]

    avg_entry_price = portfolio.get(
        "avg_entry_price",
        0
    )

    action = decision["action"]

    confidence = decision["confidence"]

    execution_status = (
        "SKIPPED_NO_ACTION"
    )

    investment_amount = 0

    print("\n=== PAPER TRADING ===")

    # =========================
    # CONFIDENCE FILTER
    # =========================

    if confidence < 0.65:

        execution_status = (
            "SKIPPED_LOW_CONFIDENCE"
        )

        print("\nConfidence too low.")
        print("NO TRADE EXECUTED")

    # =========================
    # BUY
    # =========================

    elif action == "BUY":

        # =========================
        # SCALE-IN
        # =========================

        if asset_holdings > 0:

            if confidence >= 0.90:

                investment_amount = (
                    cash_balance * 0.05
                )

                if investment_amount > 0:

                    additional_asset = (
                        investment_amount
                        / asset_price
                    )

                    existing_position_value = (
                        asset_holdings
                        * avg_entry_price
                    )

                    total_position_value = (
                        existing_position_value
                        + investment_amount
                    )

                    asset_holdings += (
                        additional_asset
                    )

                    avg_entry_price = (
                        total_position_value
                        / asset_holdings
                    )

                    cash_balance -= (
                        investment_amount
                    )

                    execution_status = (
                        "EXECUTED_SCALE_IN"
                    )

                    print(
                        "\nSCALE-IN BUY EXECUTED"
                    )

            else:

                execution_status = (
                    "SKIPPED_ALREADY_HOLDING"
                )

                print(
                    f"\nAlready holding "
                    f"{asset_symbol}."
                )

        # =========================
        # NEW POSITION
        # =========================

        else:

            investment_amount = (
                cash_balance * 0.10
            )

            if investment_amount > 0:

                asset_bought = (
                    investment_amount
                    / asset_price
                )

                cash_balance -= (
                    investment_amount
                )

                asset_holdings += (
                    asset_bought
                )

                avg_entry_price = (
                    asset_price
                )

                portfolio[
                    "highest_unrealized_pnl"
                ] = 0

                execution_status = (
                    "EXECUTED_BUY"
                )

                print("\nBUY EXECUTED")

    # =========================
    # SELL
    # =========================

    elif action == "SELL":

        if asset_holdings > 0:

            position_value = (
                asset_holdings
                * asset_price
            )

            investment_amount = (
                position_value
            )

            cash_balance += (
                position_value
            )

            asset_holdings = 0

            avg_entry_price = 0

            portfolio[
                "highest_unrealized_pnl"
            ] = 0

            execution_status = (
                "EXECUTED_SELL"
            )

            print("\nSELL EXECUTED")

        else:

            execution_status = (
                "SKIPPED_NO_HOLDINGS"
            )

            print(
                f"\nNo {asset_symbol} "
                f"holdings to sell."
            )

    # =========================
    # HOLD POSITION
    # =========================

    elif action == "HOLD_POSITION":

        execution_status = (
            "HOLDING_POSITION"
        )

        print(
            "\nHolding existing position."
        )

    # =========================
    # NO ACTION
    # =========================

    else:

        execution_status = (
            "NO_ACTION"
        )

        print("\nNO ACTION")

    # =========================
    # SAVE PORTFOLIO
    # =========================

    portfolio["cash_balance"] = (
        cash_balance
    )

    portfolio["asset_holdings"] = (
        asset_holdings
    )

    portfolio["avg_entry_price"] = (
        avg_entry_price
    )

    if asset_holdings <= 0:

        portfolio[
            "highest_unrealized_pnl"
        ] = 0

    save_portfolio(
        portfolio,
        asset_symbol
    )

    # =========================
    # PORTFOLIO VALUE
    # =========================

    portfolio_value = (
        cash_balance
        + (
            asset_holdings
            * asset_price
        )
    )

    # =========================
    # TRADE LOGGING
    # =========================

    log_trade(
        asset_symbol=asset_symbol,
        status=execution_status,
        action=action,
        confidence=confidence,
        asset_price=asset_price,
        portfolio_value=portfolio_value,
        investment_amount=investment_amount,
        reason=decision["reason"]
    )

    print("\n=== PORTFOLIO STATUS ===")

    print(
        f"Cash Balance: "
        f"${cash_balance:.2f}"
    )

    print(
        f"{asset_symbol} Holdings: "
        f"{asset_holdings:.6f}"
    )

    print(
        f"Portfolio Value: "
        f"${portfolio_value:.2f}"
    )