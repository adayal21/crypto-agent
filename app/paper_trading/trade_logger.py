import csv
from datetime import datetime

TRADE_LOG_FILE = (
    "app/paper_trading/trade_history.csv"
)

def log_trade(
    action,
    confidence,
    btc_price,
    portfolio_value,
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
            action,
            confidence,
            btc_price,
            portfolio_value,
            reason
        ])

    print("\nTrade logged successfully.")