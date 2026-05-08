def calculate_max_drawdown(equity_curve):

    peak = equity_curve[0]
    max_drawdown = 0

    for equity in equity_curve:

        peak = max(
            peak,
            equity
        )

        drawdown = (
            (equity - peak)
            / peak
        ) * 100

        max_drawdown = min(
            max_drawdown,
            drawdown
        )

    return max_drawdown


def build_performance_report(results):

    lines = [
        "",
        "========================",
        "BACKTEST RESULTS",
        "========================"
    ]

    combined_starting_balance = 0
    combined_ending_balance = 0

    for result in results:

        symbol = result["asset_symbol"]
        starting_balance = result["starting_balance"]
        ending_balance = result["ending_balance"]
        return_pct = result["return_pct"]
        trades = result["trades"]
        trade_pnls = result["trade_pnls"]
        equity_curve = result["equity_curve"]
        skipped_reason = result.get("skipped_reason")

        wins = [
            pnl
            for pnl in trade_pnls
            if pnl > 0
        ]

        losses = [
            pnl
            for pnl in trade_pnls
            if pnl <= 0
        ]

        max_drawdown = calculate_max_drawdown(
            equity_curve
        )

        best_trade = max(
            trade_pnls,
            default=0
        )

        worst_trade = min(
            trade_pnls,
            default=0
        )

        combined_starting_balance += starting_balance
        combined_ending_balance += ending_balance

        lines.extend([
            "",
            f"{symbol}",
            "-" * len(symbol),
            f"Starting Balance: ${starting_balance:.2f}",
            f"Ending Balance: ${ending_balance:.2f}",
            f"Return: {return_pct:.2f}%",
            f"Executed Trades: {len(trades)}",
            f"Closed Trades: {len(trade_pnls)}",
            f"Wins: {len(wins)}",
            f"Losses: {len(losses)}",
            f"Max Drawdown: {max_drawdown:.2f}%",
            f"Best Trade: {best_trade:.2f}%",
            f"Worst Trade: {worst_trade:.2f}%"
        ])

        if skipped_reason:

            lines.append(
                f"Note: {skipped_reason}"
            )

    combined_return = (
        (
            combined_ending_balance
            - combined_starting_balance
        )
        / combined_starting_balance
    ) * 100

    lines.extend([
        "",
        "Combined",
        "--------",
        f"Starting Balance: ${combined_starting_balance:.2f}",
        f"Ending Balance: ${combined_ending_balance:.2f}",
        f"Return: {combined_return:.2f}%",
        ""
    ])

    return "\n".join(lines)
