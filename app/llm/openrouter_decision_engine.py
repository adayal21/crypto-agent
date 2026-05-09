import json

from openai import OpenAI

from config.settings import (
    OPENROUTER_API_KEY,
    OPENROUTER_MODEL
)


client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY
)


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
    # PNL STATE
    # =========================

    if unrealized_pnl > 0:

        pnl_state = "profitable"

    elif unrealized_pnl < 0:

        pnl_state = "losing"

    else:

        pnl_state = "breakeven"

    # =========================
    # POSITION CONTEXT
    # =========================

    if holding_position:

        position_context = f"""
Current Position State:
- Currently holding {asset_name}
- Current PnL state is: {pnl_state}
- Existing position should be actively managed
- HOLD_POSITION is allowed
- BUY is allowed only for exceptionally strong continuation setups where scaling into the position is justified
- SELL is allowed if:
    - reversal risk increases
    - momentum weakens significantly
    - trend structure deteriorates
    - continuation quality weakens significantly
- Avoid emotional exits during healthy trends
- Continuation evaluation is MORE important than fresh entry quality
- Weakening entry quality alone does NOT require exiting
- If trend structure remains bullish:
    - HOLD_POSITION is generally preferred
- Existing winners should be allowed room to continue trending
- Existing losing positions should only exit on meaningful deterioration
- HOLD_POSITION should remain preferred unless meaningful deterioration appears
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
- When flat:
    - think like an ENTRY evaluator
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

IMPORTANT:
- When FLAT:
    - think primarily like an ENTRY evaluator
- When ALREADY HOLDING:
    - think primarily like a CONTINUATION evaluator
    - continuation quality matters MORE than fresh entry quality
    - weakening setup quality alone is NOT sufficient reason to exit

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
- Existing profitable trends should not be exited too aggressively

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

PnL State:
{pnl_state}

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

    response = client.chat.completions.create(

        model=OPENROUTER_MODEL,

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0.2,

        max_tokens=250
    )

    content = (
    response
    .choices[0]
    .message
    .content
)

    content = content.strip()

    if content.startswith("```json"):

        content = (
            content
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

    elif content.startswith("```"):

        content = (
            content
            .replace("```", "")
            .strip()
        )

    return content