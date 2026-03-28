from core.llm_config import get_llm

llm = get_llm()

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

    state["response"] = response.content
    return state