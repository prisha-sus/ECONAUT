from src.core.llm_provider import get_llm

llm = get_llm(provider="groq")

def experienced_agent(state):
    user_text = state["user_input"]

    prompt = f"""
    The user is an experienced investor.

    Respond in a professional and direct tone.

    The response must:
    1. Avoid beginner explanations
    2. Focus on strategy, market insights, or tools
    3. Suggest one advanced ET product (like ET Prime or market analysis tools)

    User message:
    {user_text}
    """

    result = llm.invoke(prompt)
    state["response"] = result.content
    return state