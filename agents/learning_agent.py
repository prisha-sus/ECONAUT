from core.llm_config import get_llm

llm = get_llm()

def learning_agent(state):
    user_text = state["user_input"]
    persona = state["persona"]

    prompt = f"""
You are an AI Welcome Concierge for Economic Times.

The user wants to LEARN about the stock market.
The user persona is: {persona}

Your job:
1. Respond in simple beginner-friendly language
2. Do NOT give advanced trading strategies
3. Recommend ET Masterclass / beginner learning resources
4. Keep the answer short and helpful
5. Ask one follow-up question at the end

User message:
{user_text}
"""

    response = llm.invoke(prompt)

    state["response"] = response.content
    return state