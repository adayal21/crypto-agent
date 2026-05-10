# Crypto Agent

A local Python paper-trading framework for BTC/USD, ETH/USD, and SOL/USD.

The system combines:
- deterministic setup detection
- structured risk management
- local LLM-assisted decision refinement
- isolated paper portfolios
- Streamlit analytics
- deterministic execution authority

The architecture is designed so deterministic systems control:
- setups
- exits
- portfolio state
- semantic validation
- risk management

while the LLM is used only for:
- contextual refinement
- continuation evaluation
- trade-quality assessment

---

# Features

## Market Data
- Fetches OHLCV candles from Bybit using `ccxt`
- Uses:
  - 5-minute timeframe for execution
  - 1-hour timeframe for higher-timeframe confirmation

Supported assets:
- BTC/USD
- ETH/USD
- SOL/USD

---

# Technical Indicators

The system calculates:
- RSI
- EMA 20
- MACD
- ATR
- Relative Volume

---

# Deterministic Setup Engine

The setup engine detects:
- LONG setups
- SHORT setups
- REVERSAL setups
- NO_SETUP conditions

Each setup includes:
- setup quality
- deterministic confidence score
- structured reasoning

---

# Market State Engine

The market-state engine generates:
- trend state
- momentum state
- MACD state
- volatility state
- trade bias
- higher timeframe alignment
- trend acceleration
- relative volume state

---

# LLM Validation Layer

The local Ollama model:
- validates deterministic setups
- evaluates continuation quality
- evaluates structural deterioration
- refines BUY / SELL / HOLD decisions

The LLM:
- does NOT discover setups
- does NOT control stop losses
- does NOT override deterministic exits
- does NOT bypass semantic validation

---

# Deterministic Risk Management

The framework includes:
- hard stop loss
- take profit
- trailing stop
- trend deterioration exits
- time-based exits
- semantic action validation
- pyramiding protection
- overbought late-entry filtering

---

# Paper Trading Engine

Supports:
- isolated portfolios per asset
- simulated BUY / SELL execution
- continuation logic
- scale-ins
- investment tracking
- portfolio persistence
- trade logging
- analytics integration

---

# Project Structure

```text
app/
│
├── main.py
│   Main orchestration and trading loop
│
├── backtesting/
│   ├── backtester.py
│   │   Historical deterministic backtester
│   │
│   ├── historical_data.py
│   │   Historical candle fetching and caching
│   │
│   └── performance_report.py
│       Backtest reporting
│
├── dashboard/
│   ├── analytics.py
│   │   Portfolio analytics calculations
│   │
│   └── dashboard.py
│       Streamlit analytics dashboard
│
├── indicators/
│   └── indicators.py
│       Technical indicator calculations
│
├── llm/
│   └── llm_decision_engine.py
│       Ollama contextual validation layer
│
├── logger/
│   └── market_logger.py
│       Market-cycle logging
│
├── market_data/
│   └── market_data.py
│       Bybit OHLCV data fetching
│
├── paper_trading/
│   ├── paper_trader.py
│   │   Simulated execution engine
│   │
│   ├── portfolio_manager.py
│   │   Portfolio persistence
│   │
│   ├── trade_logger.py
│   │   Trade-history CSV logging
│   │
│   ├── btc_portfolio.json
│   ├── eth_portfolio.json
│   ├── sol_portfolio.json
│   │   Isolated portfolio states
│   │
│   └── trade_history.csv
│       Historical trade log
│
├── runtime_data/
│   Runtime persistence storage
│
└── strategies/
    ├── market_state_engine.py
    │   Market-state generation
    │
    ├── position_management_engine.py
    │   Deterministic risk management
    │
    └── trade_setup_engine.py
        Deterministic setup detection