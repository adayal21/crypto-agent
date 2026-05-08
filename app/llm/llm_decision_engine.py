import ollama

def get_ai_decision(market_summary):

    prompt = f"""
You are an AI crypto trading analyst.

You must analyze the market summary and return ONLY ONE trading decision.

Rules:
- Choose exactly one:
  BUY
  SELL
  HOLD

- Return valid JSON only.
- No markdown.
- No extra text.

Format:

{{
    "action": "BUY or SELL or HOLD",
    "confidence": 0.0,
    "reason": "short reasoning"
}}

Market Summary:
{market_summary}
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