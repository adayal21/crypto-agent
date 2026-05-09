import csv
from datetime import datetime

TRADE_LOG_FILE = (
    "app/runtime_data/trade_history.csv"
)


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

    with open(
        TRADE_LOG_FILE,
        mode='a',
        newline='',
        encoding='utf-8'
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            datetime.now(),
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