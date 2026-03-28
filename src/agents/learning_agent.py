from src.core.llm_provider import get_llm
import json
import os

llm = get_llm(provider="groq")

# Load masterclasses
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
with open(os.path.join(DATA_DIR, 'et_masterclasses.json'), 'r') as f:
    masterclasses = json.load(f)

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

    # Add relevant masterclasses
    relevant_mc = [mc for mc in masterclasses if 'beginner' in mc.get('target_audience', '').lower() or 'general' in mc.get('target_audience', '').lower()]
    if relevant_mc:
        mc_text = "\n\nRecommended Masterclasses:\n" + "\n".join([f"- {mc['title']}: {mc['description']} ({mc['url']})" for mc in relevant_mc[:2]])
        state["response"] = response.content + mc_text
    else:
        state["response"] = response.content
    return state