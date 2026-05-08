import argparse
import os
import sys

APP_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        ".."
    )
)

if APP_DIR not in sys.path:

    sys.path.insert(
        0,
        APP_DIR
    )

from backtesting.historical_data import load_historical_data
from backtesting.performance_report import build_performance_report
from indicators.indicators import add_indicators
from strategies.position_management_engine import evaluate_position_management
from strategies.trade_setup_engine import detect_trade_setup

ASSETS = [
    "BTC/USDT",
    "ETH/USDT",
    "SOL/USDT"
]

STARTING_BALANCE = 10000
INVESTMENT_AMOUNT = 1000
MIN_CANDLES = 60


def create_backtest_portfolio():

    return {
        "cash_balance": STARTING_BALANCE,
        "asset_holdings": 0,
        "avg_entry_price": 0,
        "highest_unrealized_pnl": 0
    }


def calculate_unrealized_pnl(
    portfolio,
    current_price
):

    asset_holdings = portfolio["asset_holdings"]
    avg_entry_price = portfolio["avg_entry_price"]

    if (
        asset_holdings <= 0
        or avg_entry_price <= 0
    ):

        return 0

    return (
        (
            current_price
            - avg_entry_price
        )
        / avg_entry_price
    ) * 100


def calculate_portfolio_value(
    portfolio,
    current_price
):

    return (
        portfolio["cash_balance"]
        + (
            portfolio["asset_holdings"]
            * current_price
        )
    )


def build_entry_decision(
    trade_setup,
    portfolio
):

    setup_type = trade_setup["setup_type"]
    asset_holdings = portfolio["asset_holdings"]

    if (
        asset_holdings <= 0
        and setup_type in [
            "LONG_SETUP",
            "REVERSAL_SETUP"
        ]
    ):

        return {
            "action": "BUY",
            "confidence": 1.0,
            "reason": trade_setup["reason"]
        }

    if (
        asset_holdings > 0
        and setup_type == "SHORT_SETUP"
    ):

        return {
            "action": "SELL",
            "confidence": 1.0,
            "reason":
                "Short setup detected while holding a long position."
        }

    return {
        "action": "NO_ACTION",
        "confidence": 1.0,
        "reason": "No deterministic backtest action."
    }


def execute_backtest_trade(
    portfolio,
    decision,
    asset_symbol,
    asset_price,
    timestamp,
    trades,
    trade_pnls
):

    action = decision["action"]
    asset_holdings = portfolio["asset_holdings"]

    if action == "BUY":

        if asset_holdings > 0:

            return

        if portfolio["cash_balance"] < INVESTMENT_AMOUNT:

            return

        asset_bought = (
            INVESTMENT_AMOUNT
            / asset_price
        )

        portfolio["cash_balance"] -= INVESTMENT_AMOUNT
        portfolio["asset_holdings"] = asset_bought
        portfolio["avg_entry_price"] = asset_price
        portfolio["highest_unrealized_pnl"] = 0

        trades.append({
            "timestamp": timestamp,
            "asset_symbol": asset_symbol,
            "action": "BUY",
            "price": asset_price,
            "reason": decision["reason"]
        })

    elif (
        action == "SELL"
        and asset_holdings > 0
    ):

        entry_price = portfolio["avg_entry_price"]

        trade_pnl = (
            (
                asset_price
                - entry_price
            )
            / entry_price
        ) * 100

        portfolio["cash_balance"] += (
            asset_holdings
            * asset_price
        )

        portfolio["asset_holdings"] = 0
        portfolio["avg_entry_price"] = 0
        portfolio["highest_unrealized_pnl"] = 0

        trade_pnls.append(trade_pnl)

        trades.append({
            "timestamp": timestamp,
            "asset_symbol": asset_symbol,
            "action": "SELL",
            "price": asset_price,
            "pnl": trade_pnl,
            "reason": decision["reason"]
        })


def run_asset_backtest(
    asset_symbol,
    days,
    refresh
):

    df_5m = load_historical_data(
        asset_symbol=asset_symbol,
        timeframe="5m",
        days=days,
        refresh=refresh
    )

    df_1h = load_historical_data(
        asset_symbol=asset_symbol,
        timeframe="1h",
        days=days,
        refresh=refresh
    )

    if (
        len(df_5m) < MIN_CANDLES
        or len(df_1h) < MIN_CANDLES
    ):

        return {
            "asset_symbol": asset_symbol,
            "starting_balance": STARTING_BALANCE,
            "ending_balance": STARTING_BALANCE,
            "return_pct": 0,
            "trades": [],
            "trade_pnls": [],
            "equity_curve": [
                STARTING_BALANCE
            ],
            "skipped_reason":
                "Not enough historical candles for indicator warmup."
        }

    df_5m = add_indicators(df_5m)
    df_1h = add_indicators(df_1h)

    portfolio = create_backtest_portfolio()
    trades = []
    trade_pnls = []
    equity_curve = [
        STARTING_BALANCE
    ]

    for index in range(
        MIN_CANDLES,
        len(df_5m)
    ):

        current_time = df_5m.iloc[index]["timestamp"]
        current_price = df_5m.iloc[index]["close"]

        df_5m_slice = df_5m.iloc[
            :index + 1
        ].dropna()

        df_1h_slice = df_1h[
            df_1h["timestamp"] <= current_time
        ].dropna()

        if (
            len(df_5m_slice) < MIN_CANDLES
            or len(df_1h_slice) < MIN_CANDLES
        ):

            continue

        unrealized_pnl = calculate_unrealized_pnl(
            portfolio,
            current_price
        )

        exit_decision = evaluate_position_management(
            portfolio,
            unrealized_pnl
        )

        if exit_decision:

            execute_backtest_trade(
                portfolio=portfolio,
                decision=exit_decision,
                asset_symbol=asset_symbol,
                asset_price=current_price,
                timestamp=current_time,
                trades=trades,
                trade_pnls=trade_pnls
            )

        else:

            trade_setup = detect_trade_setup(
                df_5m_slice,
                df_1h_slice
            )

            entry_decision = build_entry_decision(
                trade_setup,
                portfolio
            )

            execute_backtest_trade(
                portfolio=portfolio,
                decision=entry_decision,
                asset_symbol=asset_symbol,
                asset_price=current_price,
                timestamp=current_time,
                trades=trades,
                trade_pnls=trade_pnls
            )

        equity_curve.append(
            calculate_portfolio_value(
                portfolio,
                current_price
            )
        )

    final_price = df_5m.iloc[-1]["close"]

    ending_balance = calculate_portfolio_value(
        portfolio,
        final_price
    )

    return_pct = (
        (
            ending_balance
            - STARTING_BALANCE
        )
        / STARTING_BALANCE
    ) * 100

    return {
        "asset_symbol": asset_symbol,
        "starting_balance": STARTING_BALANCE,
        "ending_balance": ending_balance,
        "return_pct": return_pct,
        "trades": trades,
        "trade_pnls": trade_pnls,
        "equity_curve": equity_curve
    }


def run_backtest(
    assets,
    days,
    refresh
):

    results = []

    for asset_symbol in assets:

        print(f"Backtesting {asset_symbol}...")

        result = run_asset_backtest(
            asset_symbol=asset_symbol,
            days=days,
            refresh=refresh
        )

        results.append(result)

    print(
        build_performance_report(results)
    )


def parse_args():

    parser = argparse.ArgumentParser(
        description="Run deterministic crypto strategy backtests."
    )

    parser.add_argument(
        "--days",
        type=int,
        default=90,
        help="Number of historical days to test."
    )

    parser.add_argument(
        "--assets",
        nargs="+",
        default=ASSETS,
        help="Asset symbols to backtest."
    )

    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Refetch market data instead of using cached CSV files."
    )

    return parser.parse_args()


if __name__ == "__main__":

    args = parse_args()

    run_backtest(
        assets=args.assets,
        days=args.days,
        refresh=args.refresh
    )
