from typing import TypedDict, Optional

class AgentState(TypedDict):
    user_input: str
    persona: Optional[str]
    intent: Optional[str]
    route: str
    response: Optional[str]