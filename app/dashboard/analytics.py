import json

from pathlib import Path

import pandas as pd

from config.settings import (
    RUNTIME_DATA_DIR
)

# =========================
# FILE PATHS
# =========================

TRADE_HISTORY_FILE = (
    RUNTIME_DATA_DIR
    / "trade_history.csv"
)

def get_portfolio_file(
    asset_symbol
):

    normalized_symbol = (
        asset_symbol
        .lower()
        .replace("/", "_")
    )

    return (
        RUNTIME_DATA_DIR
        / f"{normalized_symbol}_portfolio.json"
    )

# =========================
# TRADE COLUMNS
# =========================

TRADE_COLUMNS = [
    "timestamp",
    "asset_symbol",
    "status",
    "action",
    "confidence",
    "asset_price",
    "portfolio_value",
    "investment_amount",
    "reason"
]

# =========================
# LOAD TRADES
# =========================


def load_trades():

    from pandas.errors import (
        EmptyDataError
    )

    if not TRADE_HISTORY_FILE.exists():

        return pd.DataFrame(
            columns=TRADE_COLUMNS
        )

    try:

        trades = pd.read_csv(
            TRADE_HISTORY_FILE
        )

    except EmptyDataError:

        return pd.DataFrame(
            columns=TRADE_COLUMNS
        )

    # Ensure backward compatibility
    for column in TRADE_COLUMNS:

        if column not in trades.columns:

            trades[column] = None

    trades = trades[TRADE_COLUMNS]

    return trades

    # =========================
    # TYPE CONVERSIONS
    # =========================

    trades["timestamp"] = pd.to_datetime(
        trades["timestamp"],
        errors="coerce"
    )

    trades["confidence"] = pd.to_numeric(
        trades["confidence"],
        errors="coerce"
    )

    trades["asset_price"] = pd.to_numeric(
        trades["asset_price"],
        errors="coerce"
    )

    trades["portfolio_value"] = pd.to_numeric(
        trades["portfolio_value"],
        errors="coerce"
    )

    trades["investment_amount"] = pd.to_numeric(
        trades["investment_amount"],
        errors="coerce"
    )

    return trades.dropna(
        subset=["timestamp"]
    )

# =========================
# LOAD PORTFOLIOS
# =========================


def load_portfolios(trades):

    portfolio_rows = []

    portfolio_files = (
        RUNTIME_DATA_DIR.glob(
            "*_portfolio.json"
        )
    )

    for portfolio_file in portfolio_files:

        try:

            with open(
                portfolio_file,
                "r"
            ) as file:

                portfolio = json.load(file)

            asset_symbol = (
                portfolio
                .get(
                    "asset_symbol",
                    portfolio_file
                    .stem
                    .replace(
                        "_portfolio",
                        ""
                    )
                    .upper()
                    .replace(
                        "_",
                        "/"
                    )
                )
            )

            latest_price = 0

            if not trades.empty:

                asset_trades = trades[
                    trades[
                        "asset_symbol"
                    ]
                    == asset_symbol
                ]

                if not asset_trades.empty:

                    latest_price = (
                        asset_trades
                        .iloc[-1]
                        ["asset_price"]
                    )

            holdings = portfolio.get(
                "asset_holdings",
                0
            )

            cash_balance = portfolio.get(
                "cash_balance",
                0
            )

            position_value = (
                holdings
                * latest_price
            )

            portfolio_value = (
                cash_balance
                + position_value
            )

            portfolio_rows.append({

                "asset_symbol":
                    asset_symbol,

                "cash_balance":
                    cash_balance,

                "asset_holdings":
                    holdings,

                "avg_entry_price":
                    portfolio.get(
                        "avg_entry_price",
                        0
                    ),

                "latest_price":
                    latest_price,

                "position_value":
                    position_value,

                "portfolio_value":
                    portfolio_value,

                "highest_unrealized_pnl":
                    portfolio.get(
                        "highest_unrealized_pnl",
                        0
                    )
            })

        except Exception:

            continue

    return pd.DataFrame(
        portfolio_rows
    )

# =========================
# GET LATEST PRICE
# =========================


def get_latest_price(
    trades,
    asset_symbol,
    fallback_price
):

    asset_trades = trades[
        trades["asset_symbol"]
        == asset_symbol
    ]

    if not asset_trades.empty:

        latest_price = (
            asset_trades.iloc[-1][
                "asset_price"
            ]
        )

        if pd.notna(latest_price):

            return latest_price

    return fallback_price or 0

# =========================
# BUILD CLOSED TRADES
# =========================


def build_closed_trades(trades):

    executed = trades[
        trades["status"].isin([
            "EXECUTED_BUY",
            "EXECUTED_SELL",
            "EXECUTED_SCALE_IN"
        ])
    ].sort_values("timestamp")

    open_positions = {}

    closed_trades = []

    for _, trade in executed.iterrows():

        asset_symbol = trade[
            "asset_symbol"
        ]

        action = trade["action"]

        # =========================
        # OPEN POSITION
        # =========================

        if action == "BUY":

            open_positions[
                asset_symbol
            ] = trade

        # =========================
        # CLOSE POSITION
        # =========================

        elif (
            action == "SELL"
            and asset_symbol
            in open_positions
        ):

            entry = open_positions.pop(
                asset_symbol
            )

            entry_price = entry[
                "asset_price"
            ]

            exit_price = trade[
                "asset_price"
            ]

            investment_amount = entry.get(
                "investment_amount",
                0
            )

            if (
                pd.isna(entry_price)
                or pd.isna(exit_price)
                or entry_price <= 0
            ):

                continue

            pnl_pct = (
                (
                    exit_price
                    - entry_price
                )
                / entry_price
            ) * 100

            pnl_amount = (
                investment_amount
                * pnl_pct
                / 100
            )

            hold_time = (
                trade["timestamp"]
                - entry["timestamp"]
            )

            closed_trades.append({

                "asset_symbol":
                    asset_symbol,

                "entry_time":
                    entry["timestamp"],

                "exit_time":
                    trade["timestamp"],

                "entry_price":
                    entry_price,

                "exit_price":
                    exit_price,

                "investment_amount":
                    investment_amount,

                "pnl_pct":
                    pnl_pct,

                "pnl_amount":
                    pnl_amount,

                "hold_hours":
                    (
                        hold_time.total_seconds()
                        / 3600
                    ),

                "exit_reason":
                    trade["reason"]
            })

    return pd.DataFrame(closed_trades)

# =========================
# MAX DRAWDOWN
# =========================


def calculate_max_drawdown(trades):

    values = trades[
        "portfolio_value"
    ].dropna()

    if values.empty:

        return 0

    running_peak = values.cummax()

    drawdowns = (
        (
            values
            - running_peak
        )
        / running_peak
    ) * 100

    return drawdowns.min()

# =========================
# SUMMARY METRICS
# =========================


def calculate_summary_metrics(
    trades,
    closed_trades
):

    executed_trades = trades[
        trades["status"]
        .astype(str)
        .str.startswith("EXECUTED")
    ]

    skipped_trades = trades[
        trades["status"]
        .astype(str)
        .str.startswith("SKIPPED")
    ]

    if closed_trades.empty:

        win_rate = 0
        avg_pnl = 0
        avg_hold_hours = 0
        profit_factor = 0

    else:

        wins = closed_trades[
            closed_trades[
                "pnl_amount"
            ] > 0
        ]

        losses = closed_trades[
            closed_trades[
                "pnl_amount"
            ] <= 0
        ]

        win_rate = (
            len(wins)
            / len(closed_trades)
        ) * 100

        avg_pnl = closed_trades[
            "pnl_pct"
        ].mean()

        avg_hold_hours = closed_trades[
            "hold_hours"
        ].mean()

        gross_profit = wins[
            "pnl_amount"
        ].sum()

        gross_loss = abs(
            losses[
                "pnl_amount"
            ].sum()
        )

        profit_factor = (
            gross_profit / gross_loss
            if gross_loss > 0
            else gross_profit
        )

    return {

        "total_decisions":
            len(trades),

        "executed_trades":
            len(executed_trades),

        "skipped_trades":
            len(skipped_trades),

        "closed_trades":
            len(closed_trades),

        "win_rate":
            win_rate,

        "avg_pnl":
            avg_pnl,

        "avg_hold_hours":
            avg_hold_hours,

        "max_drawdown":
            calculate_max_drawdown(
                trades
            ),

        "profit_factor":
            profit_factor
    }

# =========================
# EQUITY CURVE
# =========================


def build_equity_curve(trades):

    if trades.empty:

        return pd.DataFrame(
            columns=[
                "timestamp",
                "asset_symbol",
                "portfolio_value"
            ]
        )

    equity = trades[
        [
            "timestamp",
            "asset_symbol",
            "portfolio_value"
        ]
    ].dropna()

    return equity.sort_values(
        "timestamp"
    )