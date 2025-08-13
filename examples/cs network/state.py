from typing import Annotated, TypedDict


class GraphState(TypedDict):
    messages: Annotated[list, "List of messages"]

