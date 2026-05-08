STOP_LOSS_PNL = -2.0

TAKE_PROFIT_PNL = 4.0

TRAILING_STOP_ACTIVATION_PNL = 5.0

TRAILING_STOP_DRAWDOWN = 2.0


def evaluate_position_management(
    portfolio,
    unrealized_pnl
):

    asset_holdings = portfolio["asset_holdings"]

    if asset_holdings <= 0:

        return None

    highest_unrealized_pnl = portfolio.get(
        "highest_unrealized_pnl",
        unrealized_pnl
    )

    highest_unrealized_pnl = max(
        highest_unrealized_pnl,
        unrealized_pnl
    )

    portfolio[
        "highest_unrealized_pnl"
    ] = highest_unrealized_pnl

    # =========================
    # STOP LOSS
    # =========================

    if unrealized_pnl <= STOP_LOSS_PNL:

        return {
            "action": "SELL",
            "confidence": 1.0,
            "reason":
                f"Stop loss triggered at "
                f"{unrealized_pnl:.2f}% PnL."
        }

    # =========================
    # TAKE PROFIT
    # =========================

    if unrealized_pnl >= TAKE_PROFIT_PNL:

        return {
            "action": "SELL",
            "confidence": 1.0,
            "reason":
                f"Take profit triggered at "
                f"{unrealized_pnl:.2f}% PnL."
        }

    # =========================
    # TRAILING STOP
    # =========================

    drawdown_from_peak = (
        highest_unrealized_pnl
        - unrealized_pnl
    )

    if (
        highest_unrealized_pnl
        >= TRAILING_STOP_ACTIVATION_PNL
        and drawdown_from_peak
        >= TRAILING_STOP_DRAWDOWN
    ):

        return {
            "action": "SELL",
            "confidence": 1.0,
            "reason":
                (
                    "Trailing stop triggered after "
                    f"profit fell from "
                    f"{highest_unrealized_pnl:.2f}% "
                    f"to {unrealized_pnl:.2f}%."
                )
        }

    return None