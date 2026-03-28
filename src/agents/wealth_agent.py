from src.core.llm_provider import get_llm
from src.tools.cross_sell_engine import evaluate_cross_sell_opportunity

llm = get_llm(provider="groq")

def wealth_agent(state):
    user_text = state["user_input"]
    persona = state["persona"]

    prompt = f"""
You are an AI Wealth Assistant for Economic Times Markets.

The user wants investment suggestions or market insights.
User persona: {persona}

Your job:
1. Understand what the user wants (stocks / investment ideas / sectors)
2. Respond in a professional tone
3. Suggest ET Markets insights or stock discovery features
4. Keep the response short
5. Ask one follow-up question

User message:
{user_text}
"""

    response = llm.invoke(prompt)

    # Check for cross-sell opportunities
    cross_sell = evaluate_cross_sell_opportunity(user_text)
    if cross_sell != "[NO CROSS-SELL TRIGGERED] Maintain standard conversational flow.":
        state["response"] = response.content + "\n\n" + cross_sell
    else:
        state["response"] = response.content
    return state