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

        "highest_unrealized_pnl": 0,

        "position_open_timestamp": None,

        "weak_momentum_count": 0,

        "scale_in_count": 0
    }


def load_portfolio(asset_symbol):

    portfolio_file = get_portfolio_file(
        asset_symbol
    )

    if not os.path.exists(portfolio_file):

        portfolio = create_default_portfolio()

        save_portfolio(
            portfolio,
            asset_symbol
        )

        return portfolio

    with open(portfolio_file, "r") as file:

        portfolio = json.load(file)

    # =========================
    # BACKWARD COMPATIBILITY
    # =========================

    if "position_open_timestamp" not in portfolio:

        portfolio[
            "position_open_timestamp"
        ] = None

    if "weak_momentum_count" not in portfolio:

        portfolio[
            "weak_momentum_count"
        ] = 0

    if "scale_in_count" not in portfolio:

        portfolio[
            "scale_in_count"
        ] = 0

    return portfolio


def save_portfolio(
    portfolio,
    asset_symbol
):

    portfolio_file = get_portfolio_file(
        asset_symbol
    )

    with open(portfolio_file, "w") as file:

        json.dump(
            portfolio,
            file,
            indent=4
        )

    print("\nPortfolio saved successfully.")