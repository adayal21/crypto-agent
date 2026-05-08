import ollama

def get_ai_decision(
    market_summary,
    action
):

    prompt = f"""
You are an AI crypto trading analyst.

The trading strategy already selected:

ACTION: {action}

Your task:
- Explain briefly WHY this action makes sense.
- Use RSI, MACD, ATR and trend context.
- Return ONLY the explanation text.
- No JSON.
- No markdown.
- Keep it under 2 sentences.

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