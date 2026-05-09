import json

import ollama


def get_ai_decision(
    market_state,
    trade_setup,
    asset_symbol,
    asset_holdings,
    unrealized_pnl
):

    asset_name = (
        asset_symbol.split("/")[0]
    )

    setup_confidence = trade_setup.get(
        "confidence",
        0.50
    )

    market_state_payload = json.dumps(
        market_state,
        indent=2
    )

    trade_setup_payload = json.dumps(
        trade_setup,
        indent=2
    )

    holding_position = (
        asset_holdings > 0
    )

    # =========================
    # POSITION CONTEXT
    # =========================

    if holding_position:

        position_context = f"""
Current Position State:
- Currently holding {asset_name}
- Existing position should be actively managed
- HOLD_POSITION is allowed
- BUY is allowed only for exceptionally strong continuation setups where scaling into the position is justified
- SELL is allowed if:
    - reversal risk increases
    - momentum weakens significantly
    - trend structure deteriorates
    - continuation quality weakens
- Avoid emotional exits during healthy trends
- Evaluate continuation quality carefully
- HOLD_POSITION is preferred during healthy trends
"""

    else:

        position_context = f"""
Current Position State:
- No current {asset_name} position
- BUY is allowed if setup quality is reasonable
- HOLD_POSITION is invalid when no position exists
- SELL is invalid when no position exists
- NO_ACTION means remain out of the market
"""

    # =========================
    # PROMPT
    # =========================

    prompt = f"""
You are an AI trading evaluator.

A deterministic trading setup has already been detected.

Your job is:
- evaluate setup quality
- evaluate risk/reward
- validate trade execution decisions
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
Open a new position or scale into an existing strong position.

SELL:
Exit an existing position.

HOLD_POSITION:
Continue holding an existing open position.

NO_ACTION:
Remain out of the market with no position.

Behavior Rules:
- Be decisive
- Moderate-risk setups are acceptable
- Do not reject trades simply because uncertainty exists
- If trend alignment and setup quality are reasonable,
  execution is allowed
- Strong higher timeframe alignment increases confidence
- Weak momentum or conflicting structure lowers confidence

IMPORTANT:
- Hard stop-loss, take-profit, and trailing-stop
  systems already exist separately
- Do NOT force panic exits for small losses
- Focus primarily on continuation quality,
  trend health, and structural deterioration

Deterministic Setup Confidence:
{setup_confidence}

IMPORTANT:
- The setup engine has already calculated
  a deterministic confidence score
- Use this confidence as the base confidence
- Only adjust confidence slightly if market structure
  strongly supports or conflicts with the setup
- Do NOT invent arbitrary confidence values

Confidence Rules:
- 0.50 → weak setup
- 0.60 → uncertain/conflicting structure
- 0.70 → acceptable setup
- 0.85 → strong setup with alignment
- 0.95 → exceptional alignment across trend,
  momentum, and higher timeframe

{position_context}

Format:

{{
    "action": "BUY or SELL or HOLD_POSITION or NO_ACTION",
    "confidence": 0.0,
    "reason": "short reasoning"
}}

Current Position Information:

Asset:
{asset_name}

Holdings:
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