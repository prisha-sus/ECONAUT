import logging
from src.core.llm_provider import get_llm

logger = logging.getLogger(__name__)

# Initialize LLM with fallback support
llm = get_llm()  # Uses automatic fallback

def router_agent(state):
    """
    Route user queries to appropriate agents with robust error handling.
    """
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

    try:
        result = llm.invoke(prompt)
        output = result.content.lower() if result.content else ""

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

        # Map intent to route
        intent_to_route = {
            "learning": "learning",
            "investment": "wealth",
            "tax_help": "tax",
            "news": "news",
            "general": "learning"  # fallback
        }

        state["route"] = intent_to_route.get(state["intent"], "learning")

        logger.info(f"Router: persona={state['persona']}, intent={state['intent']}, route={state['route']}")

    except Exception as e:
        logger.error(f"Router agent failed: {e}")
        # Fallback routing based on keywords
        user_lower = user_text.lower()

        # Emergency keyword-based routing
        if any(word in user_lower for word in ["tax", "itr", "income tax", "filing"]):
            state["route"] = "tax"
            state["intent"] = "tax_help"
        elif any(word in user_lower for word in ["news", "market", "stock", "nifty", "sensex", "today"]):
            state["route"] = "news"
            state["intent"] = "news"
        elif any(word in user_lower for word in ["invest", "portfolio", "retirement", "saving", "wealth"]):
            state["route"] = "wealth"
            state["intent"] = "investment"
        else:
            state["route"] = "learning"
            state["intent"] = "learning"

        state["persona"] = "unknown"
        logger.info(f"Router fallback: route={state['route']} (LLM failed)")

    return state
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