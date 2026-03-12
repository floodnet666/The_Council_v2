from langgraph.graph import StateGraph, END
from typing import Dict, Any, Literal
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
import json

from .state import AgentState
from agents.router_agent import RouterAgent
from agents.analyst_agent import AnalystAgent
from agents.designer_agent import DesignerAgent
from agents.librarian_agent import LibrarianAgent
from agents.general_agent import GeneralAgent
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

# Initialize Memory Engine with Polars Knowledge Base
# Try to load from data/ directory first, fallback to custom index
import os
polars_kb_path = os.path.join("data", "faiss_index.bin")
if os.path.exists(polars_kb_path):
    memory_engine = MemoryEngine(
        index_path=polars_kb_path,
        metadata_path=os.path.join("data", "faiss_meta.json")
    )
    print("Using Polars Knowledge Base from data/")
else:
    memory_engine = MemoryEngine()
    # Seed Memory with basic info
    memory_engine.add_documents([
        "The Council works by routing messages to specialized agents.",
        "Analyst Agent handles data analysis using Polars.",
        "Librarian Agent checks the knowledge base (RAG).",
        "Designer Agent creates charts using Plotly.",
        "The Dark-Data theme is required for the UI."
    ])
    print("Using default memory engine with seeded documents")

# Instantiate Agents
analyst_agent = AnalystAgent(data_engine)
designer_agent = DesignerAgent(data_engine, viz_engine)
librarian_agent = LibrarianAgent(memory_engine)
general_agent = GeneralAgent()

# Nodes
async def router_node(state: AgentState):
    """
    Decides which agent should act next based on the last message.
    """
    with tracer.start_as_current_span("router_node"):
        messages = state["messages"]
        last_message = messages[-1]
        
        logger.info(f"Routing message: {last_message.content[:50]}...")
        
        router = RouterAgent()
        # Use LLM Router now
        intent = await router.route(last_message.content, {})
        
        logger.info(f"Router decision: {intent} | Reasoning: Input content matched {intent} specialized capabilities.")
        return {"next_node": intent}

from engines.data_engine import DataEngine, PandasSyntaxDetectedError

async def analyst_node(state: AgentState):
    with tracer.start_as_current_span("analyst_node") as main_span:
        file_path = state.get("active_file")
        messages = list(state["messages"])
        last_user_query = messages[-1].content
        
        # 1. Collaboration: Ask Librarian for Polars Syntax help
        logger.info("Librarian providenciou contexto de sintaxe para o Analyst")
        with tracer.start_as_current_span("librarian_collaboration") as sub_span:
            syntax_query = f"Polars syntax for {last_user_query}"
            sub_span.set_attribute("syntax_query", syntax_query)
            syntax_context = await librarian_agent.run(syntax_query, file_path)
            sub_span.set_attribute("syntax_context_len", len(syntax_context))
        
        max_retries = 2
        retry_count = 0
        current_input = last_user_query
        
        while retry_count <= max_retries:
            try:
                logger.info(f"Executing Analyst Agent (Attempt {retry_count + 1})")
                response = await analyst_agent.run(current_input, file_path, syntax_context=syntax_context)
                
                return {
                    "messages": [AIMessage(content=response, name="analyst")]
                }
            except PandasSyntaxDetectedError as e:
                retry_count += 1
                if retry_count > max_retries:
                    logger.error(f"Analyst Agent failed after {max_retries} retries: {e}")
                    return {
                        "messages": [AIMessage(content=f"Error: I was unable to generate valid Polars code after multiple attempts. Technical details: {e}", name="analyst")]
                    }
                
                logger.warning(f"Self-healing trigger: {e}. Retrying...")
                current_input = f"{last_user_query}\n\nERROR: {e}\nFIX: You used Pandas syntax. Rewrite the analysis using PURE POLARS (pl.col, df.filter, etc.)."
            except Exception as e:
                logger.error(f"Unexpected error in analyst_node: {e}")
                return {
                    "messages": [AIMessage(content=f"An unexpected error occurred during analysis: {e}", name="analyst")]
                }

async def librarian_node(state: AgentState):
    with tracer.start_as_current_span("librarian_node"):
        file_path = state.get("active_file")
        last_message = state["messages"][-1].content
        
        logger.info("Executing Librarian Agent (RAG)")
        response = await librarian_agent.run(last_message, file_path)

        return {
            "messages": [AIMessage(content=response, name="librarian")]
        }

async def general_node(state: AgentState):
    with tracer.start_as_current_span("general_node"):
        last_message = state["messages"][-1].content
        
        logger.info("Executing General Agent")
        response = await general_agent.run(last_message)
            
        return {
            "messages": [AIMessage(content=response, name="general")]
        }

async def designer_node(state: AgentState):
    with tracer.start_as_current_span("designer_node"):
        file_path = state.get("active_file")
        last_message = state["messages"][-1].content

        logger.info("Executing Designer Agent")
        response = await designer_agent.run(last_message, file_path)
        
        return {
            "messages": [AIMessage(content=response, name="designer")]
        }

# Conditional Logic
def route_decision(state: AgentState) -> Literal["analyst", "librarian", "general", "designer"]:
    return state["next_node"]

from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

# Module-level checkpointer instance
_checkpointer_context = None
_checkpointer = None

async def init_checkpointer():
    """Initialize the checkpointer context manager"""
    global _checkpointer_context, _checkpointer
    if _checkpointer is None:
        _checkpointer_context = AsyncSqliteSaver.from_conn_string("the_council.db")
        _checkpointer = await _checkpointer_context.__aenter__()
    return _checkpointer

# Graph Construction
async def create_graph():
    workflow = StateGraph(AgentState)
    
    workflow.add_node("router", router_node)
    workflow.add_node("analyst", analyst_node)
    workflow.add_node("librarian", librarian_node)
    workflow.add_node("designer", designer_node)
    workflow.add_node("general", general_node)

    # Entry point is router
    workflow.set_entry_point("router")
    
    # Router decides where to go
    workflow.add_conditional_edges(
        "router",
        route_decision,
        {
            "analyst": "analyst",
            "librarian": "librarian",
            "designer": "designer",
            "general": "general"
        }
    )
    
    # All agents go to END for this simple turn-based flow
    workflow.add_edge("analyst", END)
    workflow.add_edge("librarian", END)
    workflow.add_edge("designer", END)
    workflow.add_edge("general", END)
    
    # Add Persistence with AsyncSqliteSaver
    checkpointer = await init_checkpointer()
    return workflow.compile(checkpointer=checkpointer)

