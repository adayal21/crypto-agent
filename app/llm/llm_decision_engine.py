import json

import ollama


def get_ai_decision(
    market_state,
    trade_setup,
    asset_symbol,
    asset_holdings,
    unrealized_pnl
):

    asset_name = asset_symbol.split("/")[0]

    market_state_payload = json.dumps(
        market_state,
        indent=2
    )

    trade_setup_payload = json.dumps(
        trade_setup,
        indent=2
    )

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
    HOLD_POSITION
    NO_ACTION

Definitions:

BUY:
Open a new position.

SELL:
Exit an existing position.

HOLD_POSITION:
Continue holding an existing open position.

NO_ACTION:
Remain out of the market with no position.

- Be decisive.
- Moderate-risk setups are acceptable.
- Do not reject trades simply because uncertainty exists.
- If setup quality and trend alignment are reasonable,
  execution is allowed.

- If currently holding {asset_name}:
    - consider trend continuation
    - consider unrealized profit/loss
    - avoid unnecessary exits during healthy trends
    - avoid emotional reactions to short-term noise

- If currently holding {asset_name} and no new setup exists:
    - evaluate whether the current position should still be held
    - consider trend continuation
    - consider unrealized profit/loss
    - SELL is allowed if reversal risk becomes significant
    - NO_ACTION means continue holding the existing position

- If not holding {asset_name}:
    - BUY is allowed if setup quality is reasonable
    - NO_ACTION means stay out of the market

- Use NO_ACTION only if:
    - setup quality is weak
    - market structure is conflicting
    - risk/reward is poor

Format:

{{
    "action": "BUY or SELL or HOLD_POSITION or NO_ACTION",
    "confidence": 0.0,
    "reason": "short reasoning"
}}

Current Position Information:

{asset_name} Holdings:
{asset_holdings}

Unrealized PnL:
{unrealized_pnl:.2f}%

Market State:
{market_state_payload}

Trade Setup:
{trade_setup_payload}
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
