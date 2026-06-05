from langgraph.graph import StateGraph, END
from typing import Literal
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
import os

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
from engines.visualization_engine import VisualizationEngine

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
        
        if intent == "designer":
            return {"next_node": "analyst", "wants_chart": True}
            
        return {"next_node": intent, "wants_chart": False}

async def analyst_node(state: AgentState):
    with tracer.start_as_current_span("analyst_node"):
        file_path = state.get("active_file")
        messages = list(state["messages"])
        last_user_message = next((m for m in reversed(messages) if isinstance(m, HumanMessage)), messages[-1])
        current_input = last_user_message.content
        syntax_context = ""
        
        retry_count = 0
        max_retries = 3
        
        while retry_count <= max_retries:
            try:
                logger.info(f"Executing Analyst Agent (Attempt {retry_count + 1})")
                state_update = await analyst_agent.run(current_input, file_path, syntax_context=syntax_context)
                return state_update
            except Exception as e:
                logger.error(f"Error in analyst_node: {e}")
                retry_count += 1
                if retry_count > max_retries:
                    return {
                        "messages": [AIMessage(content=f"Error executing analysis: {e}", name="analyst")]
                    }


async def reflection_node(state: AgentState):
    """
    Atua como o 'Editor-Chefe'. Verifica se a mensagem final
    gerada pelo analista tem qualidade sênior e não vazou dados estruturados.
    """
    with tracer.start_as_current_span("reflection_node"):
        last_message = state["messages"][-1].content
        
        logger.info("Executando Reflection Node (Supervisor)")
        
        # Heurística de segurança
        if "```json" in last_message or "{" in last_message or "ANALYSIS_DATA:" in last_message:
            logger.warning("Reflection detectou vazamento de dados estruturados na conversa. Exigindo reescrita.")
            return {
                "messages": [SystemMessage(content="SUPERVISOR OVERRIDE: Your last message leaked raw JSON or dictionary syntax. Rewrite it as a fluent human response. DO NOT include raw data structures.")],
                "next_node": "analyst"
            }
            
        logger.info("Resposta conversacional aprovada pelo Supervisor.")
        
        if state.get("wants_chart"):
            return {"next_node": "designer"}
            
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
        aggregated_data = state.get("raw_data_context", [])
        
        logger.info("Executing Designer Agent")
        state_update = await designer_agent.run(last_message, file_path, aggregated_data)
        return state_update


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

import aiosqlite

async def init_checkpointer():
    global _checkpointer_context, _checkpointer
    if _checkpointer is None:
        # [SENIOR ENGINEERING] Resiliência a Crashes e Deadlocks
        # 1. Timeout de 15s para garantir que processos bloqueantes cedam (Deadlock Recovery)
        conn = await aiosqlite.connect("the_council.db", timeout=15.0)
        
        # 2. WAL Mode (Write-Ahead Logging) evita que falhas abruptas do servidor corrompam o DB
        # e permite leituras concorrentes enquanto gravações estão acontecendo.
        await conn.execute("PRAGMA journal_mode=WAL;")
        
        # 3. Espera ativa no driver em caso de Lock pendente (Zumbi), evitando travamento infinito
        await conn.execute("PRAGMA busy_timeout=5000;")
        await conn.execute("PRAGMA synchronous=NORMAL;")
        
        _checkpointer = AsyncSqliteSaver(conn)
        await _checkpointer.setup()
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
    
    workflow.add_edge("analyst", "reflection")
    
    # O nó de reflexão decide se volta pro analista ou finaliza
    workflow.add_conditional_edges(
        "reflection",
        lambda state: state.get("next_node", "END"),
        {
            "analyst": "analyst", # Loop de correção ativado
            "designer": "designer",
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
