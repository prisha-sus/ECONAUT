from src.core.llm_provider import get_llm
from src.tools.cross_sell_engine import evaluate_cross_sell_opportunity

llm = get_llm(provider="groq")

def tax_agent(state):
    user_text = state["user_input"]

    prompt = f"""
You are an AI Financial Planning Assistant for Economic Times.

The user needs help with TAX saving or financial planning.

Your job:
1. Explain tax-saving options simply
2. Mention investment-based tax-saving options (like ELSS)
3. Keep the response beginner-friendly
4. Ask one follow-up question at the end

User message:
{user_text}
"""

    response = llm.invoke(prompt)

    # Check for cross-sell opportunities
    cross_sell = evaluate_cross_sell_opportunity(user_text)
    if cross_sell:
        state["response"] = response.content + "\n\n" + cross_sell
    else:
        state["response"] = response.content
    return state