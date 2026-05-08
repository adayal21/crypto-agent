from datetime import datetime


def log_market_cycle(
    market_summary,
    trade_setup,
    btc_price
):

    # Keep a readable audit trail of each market scan.
    with open(
        'market_analysis_log.txt',
        mode='a'
    ) as file:

        file.write(
            "\n"
            + "=" * 60
            + "\n"
        )

        file.write(
            f"TIME: {datetime.now()}\n"
        )

        file.write(
            f"BTC PRICE: {btc_price}\n\n"
        )

        file.write(
            "MARKET STATE:\n"
        )

        file.write(
            f"{market_summary}\n\n"
        )

        file.write(
            "TRADE SETUP:\n"
        )

        file.write(
            f"{trade_setup}\n"
        )

        file.write(
            "\n"
            + "=" * 60
            + "\n"
        )
