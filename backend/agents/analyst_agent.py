"""
Analyst Agent - Rewrite for The Council 2.0 Architectural Overhaul
Utilizes deterministic extraction mapping queries to AST, executing Polars safely,
and providing fluid chat generation isolated from structured data.
"""
from typing import Dict, Any, List
from langchain_core.messages import AIMessage
from engines.llm_engine import llm_engine
from engines.data_engine import DataEngine
from engines.query_engine import QueryEngine
from schemas.operations import PolarsOperation
import json

class AnalystAgent:
    def __init__(self, data_engine: DataEngine):
        self.llm = llm_engine.get_llm()
        self.structured_llm = self.llm.with_structured_output(PolarsOperation)
        self.data_engine = data_engine
        self.query_engine = QueryEngine()

    async def run_conversational(self, message: str, active_file: str = None) -> Dict[str, Any]:
        """
        Executa o fluxo completo do Analyst Agent respeitando a Separação de Estado Agêntico.
        Retorna o dicionário para mutation do AgentState (graph).
        """
        if not active_file:
            return {"messages": [AIMessage(content="I am the Analyst. Please upload a dataset so I can analyze it.", name="analyst")]}

        # Validate/load
        if self.data_engine.df is None or self.data_engine.metadata.get("source") != active_file:
            success = self.data_engine.load_data(active_file)
            if not success:
                return {"messages": [AIMessage(content=f"Could not load data from {active_file}.", name="analyst")]}

        # Setup QueryEngine
        self.query_engine.set_dataframe(self.data_engine.df)
        summary = self.data_engine.get_summary()
        
        # 1. Extract Deterministic Intent
        try:
            operation_ast = await self._extract_deterministic_intent(message, summary)
        except Exception as e:
            return {"messages": [AIMessage(content=f"Failed to map query to deterministic operations. Error: {e}", name="analyst")]}

        # 2. Execute Data Deterministic Logic
        if operation_ast.operation_type == "unknown":
            # Fallback for purely conversational or unmapped operations
            chat_msg = await self._generate_fluid_explanation(operation_ast, {}, message, summary)
            return {
                "messages": [AIMessage(content=chat_msg, name="analyst")],
                "raw_data_context": None
            }

        raw_data = self.query_engine.execute_deterministic_operation(operation_ast)

        # 3. Generate Fluid Human Explanation
        chat_message = await self._generate_fluid_explanation(operation_ast, raw_data, message, summary)

        # 4. Return Graph State Mutation
        return {
            "messages": [AIMessage(content=chat_message, name="analyst")],
            "raw_data_context": raw_data if "error" not in raw_data else None
        }

    async def _extract_deterministic_intent(self, query: str, summary: Dict[str, Any]) -> PolarsOperation:
        """Utilizes Structured Outputs to map natural language to a Polars AST."""
        columns_list = summary.get("columns", [])
        prompt = f"""
        Você é o motor de roteamento lógico do Analyst Agent.
        Seu único trabalho é mapear a intenção do usuário para uma estrutura PolarsOperation perfeitamente válida.
        
        DATASET SCHEMA E COLUNAS DISPONÍVEIS:
        {columns_list}
        
        PERGUNTA DO USUÁRIO: "{query}"
        
        Mapeie precisamente os campos exigidos. Se houver menção a "maior", "top", "melhor", o sort decrescente é TRUE.
        A operação DEVE constar na lista literal (aggregation, group_by, top_n, top_n_per_group, describe, etc).
        Se a pergunta for ambígua ou impossível com manipulação Polars básica, retorne "unknown".
        """
        return await self.structured_llm.ainvoke(prompt)

    async def _generate_fluid_explanation(self, operation: PolarsOperation, raw_data: Dict[str, Any], query: str, summary: Dict[str, Any]) -> str:
        """Provides human fluid text analyzing the pure raw data, isolated from JSON glue."""
        if "error" in raw_data:
            return f"I encountered an error while trying to process the data deterministically: {raw_data['error']}"

        # Get preview limited
        data_preview = raw_data.get("data", [])
        if isinstance(data_preview, list):
            data_preview = data_preview[:15] # limit memory for LLM context
            
        prompt = f"""
        SYSTEM: Senior Data Analyst. Respond in the language of the user's query. Provide an honest and strictly accurate interpretation of the numerical data based ONLY on the JSON supplied.
        NO JSON IN THE FINAL TEXT. Do NOT output a JSON block or code blocks. Just fluid, human language that feels like a conversation with an executive.
        
        User Query: "{query}"
        Executed Deterministic Operation: {operation.operation_type}
        
        DADOS RESULTANTES BRUTOS DA MÁQUINA (NÃO EXIBA ESTE JSON DIRETAMENTE):
        {json.dumps(data_preview, indent=2, default=str)}
        
        REGRAS DE FORMATAÇÃO HUMANA (SENIOR EXECUTIVE):
        - NUNCA inclua blocos ```json ou imprima o objeto Data. O sistema de UI já recebe o JSON separadamente.
        - Apenas fale fluentemente sobre as conclusões.
        - Arredonde e humanize os números (ex 1.5M, 10k, 34%, etc).
        - Seja direto, caloroso e responda à pergunta imediatamente. Comece entregando a resposta principal e depois comente o contexto.
        """
        response = await self.llm.ainvoke(prompt)
        return response.content.strip()
