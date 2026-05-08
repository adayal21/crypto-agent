import csv
from datetime import datetime

TRADE_LOG_FILE = (
    "app/paper_trading/trade_history.csv"
)

def log_trade(
    status,
    action,
    confidence,
    btc_price,
    portfolio_value,
    reason
):

    # Append one row per AI decision, including skipped trade reasons.
    with open(
        TRADE_LOG_FILE,
        mode='a',
        newline='',
        encoding='utf-8'
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            datetime.now(),
            status,
            action,
            confidence,
            btc_price,
            portfolio_value,
            reason
        ])

    print("\nTrade logged successfully.")
