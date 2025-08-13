from typing import Annotated, TypedDict, Optional


class GraphState(TypedDict):
    messages: Annotated[list, "List of messages"]
    routing_decision: Optional[str]

