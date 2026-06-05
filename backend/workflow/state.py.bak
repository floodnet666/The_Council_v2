from typing import TypedDict, Annotated, List, Dict, Any, Union, Optional
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
    
    # NEW ARCHITECTURAL FIELDS:
    # raw_data_context: Stores PURE JSON payload returned from Polars
    raw_data_context: Optional[Dict[str, Any]]
    
    # visual_schema: Stores instructions from DesignerAgent for Plotly (if needed later)
    visual_schema: Optional[Dict[str, Any]]
