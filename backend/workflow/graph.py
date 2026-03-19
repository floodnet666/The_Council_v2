from langgraph.graph import StateGraph, END
from typing import Dict, Any, Literal
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
import json
import os
import re

from .state import AgentState
from agents.router_agent import RouterAgent
from agents.analyst_agent import AnalystAgent
from agents.designer_agent import DesignerAgent
from agents.librarian_agent import LibrarianAgent
from agents.general_agent import GeneralAgent
from agents.reporting_agent import ReportingAgent
from utils.logging_config import logger
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

from engines.data_engine import DataEngine
from engines.memory_engine import MemoryEngine
from engines.visualization_engine import VisualizationEngine
from engines.llm_engine import llm_engine

# Global instances (simple demo persistence)
data_engine = DataEngine()
viz_engine = VisualizationEngine()

# memory_engine is now a singleton imported from engines.memory_engine
from engines.memory_engine import memory_engine

# Seed Memory with basic info if it's the first time
polars_kb_path = os.path.join("data", "faiss_index.bin")
if os.path.exists(polars_kb_path):
    print("Using Polars Knowledge Base from data/")
else:
    memory_engine.add_documents([
        "The Council works by routing messages to specialized agents.",
        "Analyst Agent handles data analysis strictly through deterministic Pydantic AST execution.",
        "Librarian Agent checks the knowledge base (RAG).",
        "Designer Agent creates charts using Plotly.",
        "The Dark-Data theme is required for the UI."
    ])
    print("Using default memory engine with seeded documents")

# Instantiate Agents
analyst_agent = AnalystAgent(data_engine)
designer_agent = DesignerAgent(data_engine, viz_engine)
librarian_agent = LibrarianAgent()
general_agent = GeneralAgent()
reporting_agent = ReportingAgent(data_engine)

# Nodes
async def router_node(state: AgentState):
    """
    Decides which agent should act next based on the last message.
    """
    with tracer.start_as_current_span("router_node"):
        messages = state["messages"]
        # Pega a ultima mensagem gerada pelo user
        last_user_message = next((m for m in reversed(messages) if isinstance(m, HumanMessage)), messages[-1])
        
        logger.info(f"Routing message: {last_user_message.content[:50]}...")
        
        router = RouterAgent()
        intent = await router.route(last_user_message.content, {})
        
        logger.info(f"Router decision: {intent} | Reasoning: Input content matched {intent} specialized capabilities.")
        return {"next_node": intent}

async def analyst_node(state: AgentState):
    with tracer.start_as_current_span("analyst_node"):
        file_path = state.get("active_file")
        messages = list(state["messages"])
        last_user_message = next((m for m in reversed(messages) if isinstance(m, HumanMessage)), messages[-1])
        last_user_query = last_user_message.content
        
        logger.info("Executing Analyst Agent (Deterministic AST Mode)")
        try:
            # We no longer request generic python code, we cast strictly into Pydantic models.
            state_update = await analyst_agent.run_conversational(last_user_query, file_path)
            # The agent returns state updates dict
            return state_update
            
        except Exception as e:
            logger.error(f"Error in analyst_node: {e}")
            return {
                "messages": [AIMessage(content=f"Error executing analysis: {e}", name="analyst")]
            }

async def reflection_node(state: AgentState):
    """
    Evaluates Analyst's response. Did it leak JSON array inside the chat response?
    If so, routes back to analyst to fix it. Otherwise -> END.
    """
    with tracer.start_as_current_span("reflection_node"):
        last_message = state["messages"][-1]
        
        if last_message.name != "analyst":
            return {"next_node": "END"}
            
        content = last_message.content
        logger.info("Running Reflection on Analyst output...")
        
        # Simple heuristic check for prompt glue (JSON array `[` or `{...}` inside text)
        has_json_array = re.search(r'\[[\s\n]*\{.*\}[\s\n]*\]', content, re.DOTALL)
        has_json_block = "```json" in content
        
        if has_json_array or has_json_block:
            logger.warning("Reflection Failed: Analyst leaked JSON or Raw Data in conversation response. Forcing Rewrite.")
            correction_message = SystemMessage(
                content="CRITICAL SYSTEM FEEDBACK: You leaked raw JSON data or JSON code blocks into the response text. NEVER output the raw data directly in the chat string. Rewrite your previous message to just talk about the conclusions fluently without pasting the json payload. I repeat: No JSON."
            )
            return {
                "messages": [correction_message],
                "next_node": "analyst"  # Go back
            }
        else:
            logger.info("Reflection Passed: Analyst response is clean and human-like.")
            return {"next_node": "END"}

async def librarian_node(state: AgentState):
    with tracer.start_as_current_span("librarian_node"):
        file_path = state.get("active_file")
        last_message = state["messages"][-1].content
        
        logger.info("Executing Librarian Agent (RAG)")
        response = await librarian_agent.run(last_message, file_path)

        return {"messages": [AIMessage(content=response, name="librarian")]}

async def general_node(state: AgentState):
    with tracer.start_as_current_span("general_node"):
        last_message = state["messages"][-1].content
        logger.info("Executing General Agent")
        response = await general_agent.run(last_message)
        return {"messages": [AIMessage(content=response, name="general")]}

async def designer_node(state: AgentState):
    with tracer.start_as_current_span("designer_node"):
        file_path = state.get("active_file")
        last_message = state["messages"][-1].content
        logger.info("Executing Designer Agent")
        response = await designer_agent.run(last_message, file_path)
        return {"messages": [AIMessage(content=response, name="designer")]}

async def reporting_node(state: AgentState):
    with tracer.start_as_current_span("reporting_node"):
        logger.info("Executing Reporting Agent (Executive Summary)")
        response = await reporting_agent.generate_executive_report(messages=state.get("messages"))
        return {"messages": [AIMessage(content=response, name="reporting")]}

# Conditional Logic
def route_decision(state: AgentState) -> Literal["analyst", "librarian", "general", "designer", "reporting"]:
    return state["next_node"]

def reflection_decision(state: AgentState) -> Literal["analyst", "END"]:
    # Using string exact match due to langgraph conditional string expectations
    return state["next_node"] if state["next_node"] == "analyst" else "END"

from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

_checkpointer_context = None
_checkpointer = None

async def init_checkpointer():
    global _checkpointer_context, _checkpointer
    if _checkpointer is None:
        _checkpointer_context = AsyncSqliteSaver.from_conn_string("the_council.db")
        _checkpointer = await _checkpointer_context.__aenter__()
    return _checkpointer

async def create_graph():
    workflow = StateGraph(AgentState)
    
    workflow.add_node("router", router_node)
    workflow.add_node("analyst", analyst_node)
    workflow.add_node("reflection", reflection_node)
    workflow.add_node("librarian", librarian_node)
    workflow.add_node("designer", designer_node)
    workflow.add_node("general", general_node)
    workflow.add_node("reporting", reporting_node)

    workflow.set_entry_point("router")
    
    workflow.add_conditional_edges(
        "router",
        route_decision,
        {
            "analyst": "analyst",
            "librarian": "librarian",
            "designer": "designer",
            "general": "general",
            "reporting": "reporting"
        }
    )
    
    # Analyst goes to Reflection
    workflow.add_edge("analyst", "reflection")
    
    # Reflection decides either to fix Analyst or STOP
    workflow.add_conditional_edges(
        "reflection",
        reflection_decision,
        {
            "analyst": "analyst",
            "END": END
        }
    )
    
    # Other agents end directly
    workflow.add_edge("librarian", END)
    workflow.add_edge("designer", END)
    workflow.add_edge("general", END)
    workflow.add_edge("reporting", END)
    
    checkpointer = await init_checkpointer()
    return workflow.compile(checkpointer=checkpointer)
