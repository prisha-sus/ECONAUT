from src.core.llm_provider import get_llm
from src.tools.rag_engine import load_json_data, build_vector_store  # or use FAISS directly

llm = get_llm(provider="groq")

def news_agent(state):
    user_text = state["user_input"]

    prompt = f"""
You are an AI News Concierge for Economic Times.

The user is interested in business news, stock market updates, or financial trends.

Your job:
1. Respond like a premium news assistant
2. Mention ET Prime / premium articles
3. Keep the tone professional and informative
4. Ask one follow-up question

User message:
{user_text}
"""

    response = llm.invoke(prompt)

    state["response"] = response.content
    return state