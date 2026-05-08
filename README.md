# Crypto Agent

A local Python paper-trading bot for BTC/USDT. The bot combines deterministic market setup detection with a local LLM decision step, then records simulated trades against a JSON portfolio.

## What It Does

- Fetches BTC/USDT OHLCV candles from Bybit with `ccxt`.
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
  market_data/market_data.py      Bybit OHLCV data fetching
  indicators/indicators.py        Technical indicator calculations
  strategies/
    market_state_engine.py        Market state summary generation
    trade_setup_engine.py         Deterministic setup detection
  llm/llm_decision_engine.py      Ollama trade validation prompt
  paper_trading/
    paper_trader.py               Paper trade execution
    portfolio_manager.py          Portfolio JSON persistence
    trade_logger.py               Trade CSV logging
    portfolio.json                Current paper portfolio state
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

## Trading Flow

1. `main.py` fetches BTC/USDT candles for `5m` and `1h`.
2. `add_indicators()` enriches both dataframes with technical indicators.
3. `generate_market_state()` describes trend, momentum, volatility, volume, and higher-timeframe alignment.
4. `detect_trade_setup()` decides whether there is a deterministic setup.
5. If the setup is not `NO_SETUP`, `get_ai_decision()` asks Ollama for a JSON decision.
6. `execute_paper_trade()` applies the decision to the paper portfolio when confidence is high enough.
7. The bot logs market cycles and trade history.

## Paper Trading Rules

- Buys use a fixed simulated investment amount of `$1000`.
- Additional buys are skipped while BTC is already held.
- Sells close the full BTC position.
- Decisions below `0.75` confidence are ignored.
- Portfolio state is stored in `app/paper_trading/portfolio.json`.

## Notes

- This is a paper-trading prototype, not financial advice.
- The bot assumes it is run from the project root because some paths are relative.
- The LLM is used only as a validator after deterministic setup detection.
- If Ollama returns malformed JSON, the current loop catches the error and continues on the next cycle.
