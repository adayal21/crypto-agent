import ollama


def get_ai_decision(
    market_state,
    trade_setup,
    btc_holdings,
    unrealized_pnl
):

    has_position = btc_holdings > 0

    position_state = (
        "OPEN_LONG_POSITION"
        if has_position
        else "NO_POSITION"
    )

    formatted_btc_holdings = (
        f"{btc_holdings:.8f} BTC"
    )

    prompt = f"""
You are an AI trading evaluator.

A deterministic trading setup has already been detected.

Your job is:
- evaluate setup quality
- evaluate risk/reward
- decide whether trade execution is justified
- manage existing positions intelligently

You are NOT discovering setups.
You are ONLY validating them.

Return valid JSON only.

Rules:
- Choose exactly one:
    BUY
    SELL
    NO_ACTION

- Be decisive.
- Moderate-risk setups are acceptable.
- Do not reject trades simply because uncertainty exists.
- If setup quality and trend alignment are reasonable,
  execution is allowed.

- If already holding a position:
    - the current position state will be OPEN_LONG_POSITION
    - BUY means adding to the existing position
    - this paper trader does not add to existing BTC positions
    - choose NO_ACTION when the best decision is to keep holding
    - choose SELL only when exit risk is justified
    - consider trend continuation
    - consider unrealized profit/loss
    - avoid unnecessary exits during healthy trends
    - avoid emotional reactions to short-term noise
    - avoid overtrading

- Use NO_ACTION only if:
    - setup quality is weak
    - market structure is conflicting
    - risk/reward is poor

Format:

{{
    "action": "BUY or SELL or NO_ACTION",
    "confidence": 0.0,
    "reason": "short reasoning"
}}

Current Position Information:

Position State:
{position_state}

BTC Holdings:
{formatted_btc_holdings}

Unrealized PnL:
{unrealized_pnl:.2f}%

Market State:
{market_state}

Trade Setup:
{trade_setup}
"""

    response = ollama.chat(
        model='qwen2.5:3b',
        messages=[
            {
                'role': 'user',
                'content': prompt
            }
        ],
        options={
            'temperature': 0.2
        }
    )

    return response['message']['content']
