import csv
import os

from datetime import datetime

TRADE_LOG_FILE = (
    "app/runtime_data/trade_history.csv"
)

TRADE_HEADERS = [
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


def log_trade(
    asset_symbol,
    status,
    action,
    confidence,
    asset_price,
    portfolio_value,
    investment_amount,
    reason
):

    file_exists = os.path.exists(
        TRADE_LOG_FILE
    )

    with open(
        TRADE_LOG_FILE,
        mode='a',
        newline='',
        encoding='utf-8'
    ) as file:

        writer = csv.writer(file)

        # =========================
        # WRITE HEADER ONCE
        # =========================

        if not file_exists:

            writer.writerow(
                TRADE_HEADERS
            )

        writer.writerow([
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            asset_symbol,
            status,
            action,
            confidence,
            asset_price,
            portfolio_value,
            investment_amount,
            reason
        ])

    print("\nTrade logged successfully.")