from core.llm_config import get_llm

llm = get_llm()

def router_agent(state):
    user_text = state["user_input"]

    prompt = f"""
You are an AI financial assistant.

From the user message below, identify:

1. User Persona:
   - first time investor
   - experienced investor
   - unknown

2. User Intent:
   - learning
   - investment
   - tax help
   - news
   - general

IMPORTANT:
If the user is asking about stock market updates, business news, or what is happening in the market today, classify it as: news

User message:
{user_text}

Return ONLY in this format:
persona: ___
intent: ___
"""

    result = llm.invoke(prompt)
    output = result.content.lower()

    # Default values
    state["persona"] = "unknown"
    state["intent"] = "general"
    state["route"] = "learning"   # safe fallback

    # Extract persona
    if "persona:" in output:
        persona_value = output.split("persona:")[1].split("\n")[0].strip()
        state["persona"] = persona_value.replace(" ", "_")

    # Extract intent
    if "intent:" in output:
       intent_value = output.split("intent:")[1].split("\n")[0].strip()
       state["intent"] = intent_value.replace(" ", "_")

    # -------- MULTI AGENT ROUTING --------
    intent = state["intent"]

    if intent == "learning":
        state["route"] = "learning"

    elif intent == "investment":
        state["route"] = "wealth"

    elif intent == "tax_help":
        state["route"] = "tax"
    elif intent == "news":
        state["route"] = "news"

    else:
        state["route"] = "learning"

    return state