from core.llm_config import get_llm

llm = get_llm()

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

    state["response"] = response.content
    return state