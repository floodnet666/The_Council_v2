from typing import TypedDict, Annotated, List, Dict, Any, Union
from langchain_core.messages import BaseMessage
import operator

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    language: str
    dataset_schema: Dict[str, Any]
    active_file: str
    next_node: str
    # metadata can store session info
    metadata: Dict[str, Any]
