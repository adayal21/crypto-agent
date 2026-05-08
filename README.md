# Crypto Agent

A local Python paper-trading bot for BTC/USDT, ETH/USDT, and SOL/USDT. The bot combines deterministic market setup detection with a local LLM decision step, then records simulated trades against isolated JSON portfolios.

## What It Does

- Fetches BTC/USDT, ETH/USDT, and SOL/USDT OHLCV candles from Bybit with `ccxt`.
- Builds 5-minute and 1-hour market context.
- Calculates RSI, EMA 20, MACD, ATR, and relative volume.
- Detects long, short, reversal, or no-trade setups.
- Sends valid setups to a local Ollama model for trade validation.
- Executes simulated paper trades.
- Persists portfolio state and trade history locally.

## Project Structure

```text
app/
  main.py                         Main continuous trading loop
  backtesting/
    backtester.py                 Deterministic historical strategy simulator
    historical_data.py            Bybit historical data fetch/cache helpers
    performance_report.py         Backtest summary reporting
  dashboard/
    analytics.py                  Dashboard metric calculations
    dashboard.py                  Local Streamlit analytics dashboard
  market_data/market_data.py      Bybit OHLCV data fetching
  indicators/indicators.py        Technical indicator calculations
  strategies/
    market_state_engine.py        Market state summary generation
    position_management_engine.py Stop loss, take profit, and trailing stop rules
    trade_setup_engine.py         Deterministic setup detection
  llm/llm_decision_engine.py      Ollama trade validation prompt
  paper_trading/
    paper_trader.py               Paper trade execution
    portfolio_manager.py          Portfolio JSON persistence
    trade_logger.py               Trade CSV logging
    btc_portfolio.json            BTC paper portfolio state
    eth_portfolio.json            ETH paper portfolio state
    sol_portfolio.json            SOL paper portfolio state
    trade_history.csv             Trade history log
  logger/market_logger.py         Market cycle logging
```

## Requirements

This project expects Python and these packages to be installed:

```bash
pip install ccxt pandas pandas-ta ollama
```

You also need Ollama running locally with the configured model available:

```bash
ollama pull qwen2.5:3b
```

## Running The Bot

Run from the project root:

```bash
python app/main.py
```

The bot runs continuously and waits 5 minutes between trading cycles.

## Running A Backtest

Run a deterministic backtest from the project root:

```bash
python app/backtesting/backtester.py
```

By default, this tests BTC/USDT, ETH/USDT, and SOL/USDT over the last 90 days. It uses the existing indicator, setup, and position-management logic, but it does not call Ollama and does not modify live paper portfolios.

Useful options:

```bash
python app/backtesting/backtester.py --days 30
python app/backtesting/backtester.py --assets BTC/USDT ETH/USDT
python app/backtesting/backtester.py --refresh
```

Historical candles are cached as CSV files under `data/` so repeated backtests run faster.

## Running The Dashboard

Install Streamlit if needed:

```bash
pip install streamlit
```

Run the local analytics dashboard:

```bash
streamlit run app/dashboard/dashboard.py
```

Then open:

```text
http://localhost:8501
```

The dashboard reads the live paper-trading CSV and isolated portfolio JSON files. It does not modify trades, portfolios, or strategy logic.

## Trading Flow

1. `main.py` scans BTC/USDT, ETH/USDT, and SOL/USDT independently.
2. `add_indicators()` enriches both dataframes with technical indicators.
3. `generate_market_state()` describes trend, momentum, volatility, volume, and higher-timeframe alignment.
4. `detect_trade_setup()` decides whether there is a deterministic setup.
5. If the setup is not `NO_SETUP`, `get_ai_decision()` asks Ollama for a JSON decision.
6. `execute_paper_trade()` applies the decision to the paper portfolio when confidence is high enough.
7. The bot logs market cycles and trade history.

## Paper Trading Rules

- Buys use a fixed simulated investment amount of `$1000`.
- Each asset has its own isolated paper portfolio.
- Additional buys are skipped while that asset is already held.
- Sells close the full position for that asset.
- Decisions below `0.75` confidence are ignored.
- Portfolio state is stored in separate `btc_portfolio.json`, `eth_portfolio.json`, and `sol_portfolio.json` files.

## Notes

- This is a paper-trading prototype, not financial advice.
- The bot assumes it is run from the project root because some paths are relative.
- The LLM is used only as a validator after deterministic setup detection.
- If Ollama returns malformed JSON, the current loop catches the error and continues on the next cycle.
