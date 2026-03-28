from langgraph.graph import StateGraph
from state.agent_state import AgentState

# Import agents
from agents.router_agent import router_agent
from agents.learning_agent import learning_agent
from agents.wealth_agent import wealth_agent
from agents.tax_agent import tax_agent
from agents.news_agent import news_agent
from agents.reflection_agent import reflection_agent
from features.daily_commute import run_daily_commute

# Create graph
graph = StateGraph(AgentState)

# NODES 
graph.add_node("router", router_agent)
graph.add_node("learning", learning_agent)
graph.add_node("wealth", wealth_agent)
graph.add_node("tax", tax_agent)
graph.add_node("news", news_agent)
graph.add_node("reflection", reflection_agent)

# ENTRY POINT 
graph.set_entry_point("router")

# ROUTING 
def route_agent(state):
    return state["route"]

graph.add_conditional_edges(
    "router",
    route_agent,
    {
        "learning": "learning",
        "wealth": "wealth",
        "tax": "tax",
        "news": "news"
    }
)

graph.add_edge("learning", "reflection")
graph.add_edge("wealth", "reflection")
graph.add_edge("tax", "reflection")
graph.add_edge("news", "reflection")

 
workflow = graph.compile()

while True:
    user_text = input("\nUser: ")

    result = workflow.invoke({
        "user_input": user_text
    })

    print("\nDetected Persona:", result["persona"])
    print("Detected Intent:", result["intent"])
    print("Routed To:", result["route"])

   
    if "daily commute" in user_text.lower():
        run_daily_commute(result["persona"])
        continue

    print(f"\nAI (Handled by {result['route']} agent):", result["response"])