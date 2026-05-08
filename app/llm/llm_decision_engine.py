import ollama


def get_ai_decision(
    market_state,
    trade_setup,
    btc_holdings,
    unrealized_pnl
):

    # The LLM validates an existing setup; it does not create new signals.
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

- If currently holding BTC:
    - consider trend continuation
    - consider unrealized profit/loss
    - avoid unnecessary exits during healthy trends
    - avoid emotional reactions to short-term noise

- If not holding BTC:
    - BUY is allowed if setup quality is reasonable
    - NO_ACTION means stay out of the market

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



BTC Holdings:
{btc_holdings}

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
