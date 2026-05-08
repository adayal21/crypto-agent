import json

PORTFOLIO_FILE = "app/paper_trading/portfolio.json"


def load_portfolio():

    # Read current paper-trading cash, holdings, and entry price.
    with open(PORTFOLIO_FILE, "r") as file:

        portfolio = json.load(file)

    return portfolio


def save_portfolio(portfolio):

    # Persist the updated simulated account after each cycle.
    with open(PORTFOLIO_FILE, "w") as file:

        json.dump(
            portfolio,
            file,
            indent=4
        )
    print("\nPortfolio saved successfully.")
