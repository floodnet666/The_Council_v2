from typing import TypedDict, Annotated, List, Dict, Any, Union, Optional
from langchain_core.messages import BaseMessage
import operator

def manage_messages(left: List[BaseMessage], right: List[BaseMessage]) -> List[BaseMessage]:
    """Reducer for messages: preserves SystemPrompt at index 0 and truncates the oldest messages to prevent KV cache bloat."""
    all_msgs = left + right
    if len(all_msgs) > 20:
        # Retorna a primeira msg (SystemMessage) + as últimas 19
        return [all_msgs[0]] + all_msgs[-19:]
    return all_msgs

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], manage_messages]
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
    
    # wants_chart: Signal from Router to chain Analyst -> Designer
    wants_chart: Optional[bool]
