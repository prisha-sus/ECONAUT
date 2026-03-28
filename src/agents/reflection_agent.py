from src.core.llm_provider import get_llm

llm = get_llm(provider="groq")

def reflection_agent(state):

    persona = state["persona"]
    intent = state["intent"]
    user_text = state["user_input"]
    original_response = state["response"]

    prompt = f"""
You are a Senior Financial Response Optimizer.

Your job is to improve the response so that it becomes:

1. Clear and easy to understand
2. Personalized based on persona
3. Actionable (tell the user exactly what to do next)
4. Aligned with financial products like learning platforms, market tools, and premium financial news
5. Short, precise, and helpful

-------------------------

User Persona: {persona}
User Intent: {intent}
User Message: {user_text}

Original Response:
{original_response}

-------------------------

Rewrite the response using the following rules:

If persona = first_time_investor:
- Use simple language
- Explain briefly
- Add step-by-step guidance
- Suggest a beginner learning path

If persona = experienced_investor:
- Skip basic explanations
- Focus on strategies, insights, and advanced tips

If intent = learning:
- Add a structured learning path

If intent = investment:
- Add smart next steps like how to analyze stocks

If intent = news:
- Focus on market insights and why it matters

If intent = tax_help:
- Focus on practical tax-saving actions

IMPORTANT:
End the response with ONE actionable next step for the user.

Return only the improved response.
"""

    result = llm.invoke(prompt)

    state["response"] = result.content

    return state