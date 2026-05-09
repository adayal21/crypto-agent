from datetime import datetime

STOP_LOSS_PNL = -2.0

TAKE_PROFIT_PNL = 4.0

TRAILING_STOP_ACTIVATION_PNL = 2.0

TRAILING_STOP_DRAWDOWN = 1.0

WEAK_MOMENTUM_EXIT_THRESHOLD = 5


def evaluate_position_management(
    portfolio,
    unrealized_pnl,
    market_state,
    trade_setup
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

    trend_state = market_state.get(
        "trend_state"
    )

    momentum_state = market_state.get(
        "momentum_state"
    )

    macd_state = market_state.get(
        "macd_state"
    )

    # =========================
    # WEAK MOMENTUM TRACKING
    # =========================

    weak_momentum_count = portfolio.get(
        "weak_momentum_count",
        0
    )

    if (
        momentum_state == "weak bearish momentum"
    ):

        weak_momentum_count += 1

    else:

        weak_momentum_count = 0

    portfolio[
        "weak_momentum_count"
    ] = weak_momentum_count

    # =========================
    # STOP LOSS
    # =========================

    if unrealized_pnl <= STOP_LOSS_PNL:

        return {
            "action": "SELL",
            "confidence": 1.0,
            "reason":
                (
                    f"Stop loss triggered at "
                    f"{unrealized_pnl:.2f}% PnL."
                )
        }

    # =========================
    # TREND BREAKDOWN EXIT
    # =========================

    if (
        trend_state == "bearish"
        and macd_state == "bearish momentum crossover"
        and trade_setup["setup_type"] == "NO_SETUP"
    ):

        return {
            "action": "SELL",
            "confidence": 1.0,
            "reason":
                (
                    "Trend breakdown detected "
                    "with bearish momentum confirmation."
                )
        }

    # =========================
    # MOMENTUM DETERIORATION EXIT
    # =========================

    if (
        weak_momentum_count
        >= WEAK_MOMENTUM_EXIT_THRESHOLD
    ):

        return {
            "action": "SELL",
            "confidence": 1.0,
            "reason":
                (
                    "Momentum deterioration exit "
                    "triggered after repeated weakness."
                )
        }

    # =========================
    # TIME-BASED EXIT
    # =========================

    position_open_timestamp = portfolio.get(
        "position_open_timestamp"
    )

    if position_open_timestamp:

        opened_at = datetime.fromisoformat(
            position_open_timestamp
        )

        holding_hours = (
            datetime.utcnow() - opened_at
        ).total_seconds() / 3600

        if (
            holding_hours >= 6
            and unrealized_pnl < 0.5
        ):

            return {
                "action": "SELL",
                "confidence": 1.0,
                "reason":
                    (
                        "Time-based exit triggered "
                        "after weak continuation."
                    )
            }

    # =========================
    # TAKE PROFIT
    # =========================

    if unrealized_pnl >= TAKE_PROFIT_PNL:

        return {
            "action": "SELL",
            "confidence": 1.0,
            "reason":
                (
                    f"Take profit triggered at "
                    f"{unrealized_pnl:.2f}% PnL."
                )
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