import json
import os

PORTFOLIO_DIR = "app/runtime_data"


def get_asset_key(asset_symbol):

    return asset_symbol.split("/")[0].lower()


def get_portfolio_file(asset_symbol):

    asset_key = get_asset_key(asset_symbol)

    return os.path.join(
        PORTFOLIO_DIR,
        f"{asset_key}_portfolio.json"
    )


def create_default_portfolio():

    return {
        "cash_balance": 10000,
        "asset_holdings": 0,
        "avg_entry_price": 0,
        "highest_unrealized_pnl": 0
    }


def load_portfolio(asset_symbol):

    # Read current paper-trading cash, holdings, and entry price.
    portfolio_file = get_portfolio_file(asset_symbol)

    if not os.path.exists(portfolio_file):

        portfolio = create_default_portfolio()

        save_portfolio(
            portfolio,
            asset_symbol
        )

        return portfolio

    with open(portfolio_file, "r") as file:

        portfolio = json.load(file)

    return portfolio


def save_portfolio(
    portfolio,
    asset_symbol
):

    # Persist the updated simulated account after each cycle.
    portfolio_file = get_portfolio_file(asset_symbol)

    with open(portfolio_file, "w") as file:

        json.dump(
            portfolio,
            file,
            indent=4
        )
    print("\nPortfolio saved successfully.")
