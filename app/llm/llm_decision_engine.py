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
- HOLD_POSITION is STRICTLY FORBIDDEN when no position exists
- SELL is STRICTLY FORBIDDEN when no position exists
- If no position exists:
    - you must choose either BUY or NO_ACTION
    - HOLD_POSITION is invalid
    - SELL is invalid
- If deterministic setup confidence is 0.75 or higher:
    - BUY is generally preferred unless strong structural conflict exists
- NO_ACTION means remain out of the market
"""

    # =========================
    # PROMPT
    # =========================

    prompt = f"""
You are an AI trading evaluator.

A deterministic trading setup has already been detected.

You are NOT discovering setups.
You are ONLY validating and refining deterministic decisions.

Your job is:
- evaluate continuation quality
- evaluate structural alignment
- evaluate trend health
- evaluate risk/reward quality
- validate trade execution decisions

Return valid JSON only.

==================================================
VALID ACTIONS
==================================================

Choose EXACTLY one:

BUY
SELL
HOLD_POSITION
NO_ACTION

==================================================
ACTION DEFINITIONS
==================================================

BUY:
- Open a new position
- OR scale into an existing winning position
- Allowed only if setup quality is acceptable

SELL:
- Exit an existing position
- Allowed only if a position already exists

HOLD_POSITION:
- Continue holding an EXISTING open position
- STRICTLY FORBIDDEN when no position exists

NO_ACTION:
- Stay out of the market with no position
- Used when setup quality is weak or unclear

==================================================
CRITICAL RULES
==================================================

- Deterministic setup engine already detected the setup
- Do NOT reject valid setups too aggressively
- Moderate-quality setups are tradable
- Uncertainty alone is NOT a reason to reject trades
- The deterministic confidence score is the PRIMARY confidence reference
- Only adjust confidence slightly based on structure quality
- Do NOT invent arbitrary confidence values
- When no position exists, think like an ENTRY evaluator
- Do NOT reason as if already holding a position
- HOLD_POSITION should only be used for active open positions

==================================================
RISK MANAGEMENT
==================================================

IMPORTANT:
- Hard stop-loss systems already exist
- Take-profit systems already exist
- Trailing-stop systems already exist
- Deterministic trend breakdown exits already exist

Therefore:
- Do NOT panic-sell small losses
- Focus on continuation quality and structure deterioration
- Healthy trends should usually continue holding

==================================================
POSITION RULES
==================================================

{position_context}

==================================================
CONFIDENCE RULES
==================================================

Deterministic Setup Confidence:
{setup_confidence}

Confidence Guidelines:

0.50 → weak setup
0.60 → conflicting structure
0.70 → acceptable setup
0.75 → tradable continuation
0.85 → strong aligned setup
0.95 → exceptional alignment

IMPORTANT:
- Confidence should remain close to deterministic confidence
- Large deviations require strong justification
- Do NOT always output 0.85

==================================================
OUTPUT FORMAT
==================================================

{{
    "action": "BUY or SELL or HOLD_POSITION or NO_ACTION",
    "confidence": 0.0,
    "reason": "short reasoning"
}}

==================================================
CURRENT POSITION
==================================================

Asset:
{asset_name}

Holdings:
{asset_holdings}

Unrealized PnL:
{unrealized_pnl:.2f}%

==================================================
MARKET STATE
==================================================

{market_state_payload}

==================================================
TRADE SETUP
==================================================

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