import sys
from pathlib import Path

import streamlit as st

DASHBOARD_DIR = Path(__file__).resolve().parent
APP_DIR = DASHBOARD_DIR.parent

if str(APP_DIR) not in sys.path:

    sys.path.insert(
        0,
        str(APP_DIR)
    )

from analytics import (
    build_closed_trades,
    build_equity_curve,
    calculate_summary_metrics,
    load_portfolios,
    load_trades
)

st.set_page_config(
    page_title="Crypto Agent Dashboard",
    layout="wide"
)

st.title("Crypto Agent Dashboard")

trades = load_trades()
portfolios = load_portfolios(trades)

if portfolios.empty:

    st.warning(
        "No portfolio data available."
    )

    st.stop()

asset_options = sorted(
    portfolios["asset_symbol"].unique()
)

selected_assets = st.sidebar.multiselect(
    "Assets",
    asset_options,
    default=asset_options
)

if selected_assets:

    trades = trades[
        trades["asset_symbol"].isin(selected_assets)
    ]

    portfolios = portfolios[
        portfolios["asset_symbol"].isin(selected_assets)
    ]

closed_trades = build_closed_trades(trades)
metrics = calculate_summary_metrics(
    trades,
    closed_trades
)

portfolio_total = portfolios[
    "portfolio_value"
].sum()

cash_total = portfolios[
    "cash_balance"
].sum()

position_total = portfolios[
    "position_value"
].sum()

top_metrics = st.columns(4)

top_metrics[0].metric(
    "Portfolio Value",
    f"${portfolio_total:,.2f}"
)

top_metrics[1].metric(
    "Cash",
    f"${cash_total:,.2f}"
)

top_metrics[2].metric(
    "Open Position Value",
    f"${position_total:,.2f}"
)

top_metrics[3].metric(
    "Total Decisions",
    metrics["total_decisions"]
)

performance_metrics = st.columns(5)

performance_metrics[0].metric(
    "Win Rate",
    f"{metrics['win_rate']:.2f}%"
)

performance_metrics[1].metric(
    "Avg PnL",
    f"{metrics['avg_pnl']:.2f}%"
)

performance_metrics[2].metric(
    "Avg Hold Time",
    f"{metrics['avg_hold_hours']:.2f}h"
)

performance_metrics[3].metric(
    "Max Drawdown",
    f"{metrics['max_drawdown']:.2f}%"
)

performance_metrics[4].metric(
    "Profit Factor",
    f"{metrics['profit_factor']:.2f}"
)

st.subheader("Current Portfolios")

st.dataframe(
    portfolios[
        [
            "asset_symbol",
            "cash_balance",
            "asset_holdings",
            "avg_entry_price",
            "latest_price",
            "position_value",
            "portfolio_value",
            "highest_unrealized_pnl"
        ]
    ],
    use_container_width=True,
    hide_index=True
)

left_chart, right_chart = st.columns(2)

with left_chart:

    st.subheader("Trade Status")

    if trades.empty:

        st.info("No trade history yet.")

    else:

        status_counts = trades[
            "status"
        ].value_counts()

        st.bar_chart(status_counts)

with right_chart:

    st.subheader("Actions By Asset")

    if trades.empty:

        st.info("No trade history yet.")

    else:

        action_counts = (
            trades
            .groupby([
                "asset_symbol",
                "action"
            ])
            .size()
            .reset_index(name="count")
            .pivot(
                index="asset_symbol",
                columns="action",
                values="count"
            )
            .fillna(0)
        )

        st.bar_chart(action_counts)

st.subheader("Portfolio Value Over Time")

equity_curve = build_equity_curve(trades)

if equity_curve.empty:

    st.info("No portfolio value history yet.")

else:

    equity_chart = equity_curve.pivot_table(
        index="timestamp",
        columns="asset_symbol",
        values="portfolio_value",
        aggfunc="last"
    )

    st.line_chart(equity_chart)

st.subheader("Closed Trades")

if closed_trades.empty:

    st.info("No closed trades yet.")

else:

    st.dataframe(
        closed_trades,
        use_container_width=True,
        hide_index=True
    )

st.subheader("Recent Trade Decisions")

if trades.empty:

    st.info("No trade decisions yet.")

else:

    recent_trades = trades.sort_values(
        "timestamp",
        ascending=False
    )

    st.dataframe(
        recent_trades,
        use_container_width=True,
        hide_index=True
    )
