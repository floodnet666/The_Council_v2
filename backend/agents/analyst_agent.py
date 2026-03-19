"""
Analyst Agent - Rewrite for The Council 2.0 Architectural Overhaul
"""
from typing import Dict, Any, List
from langchain_core.messages import AIMessage
from engines.llm_engine import llm_engine
from engines.data_engine import DataEngine
from engines.query_engine import QueryEngine
from schemas.operations import PolarsOperation
import json
import re

class AnalystAgent:
    def __init__(self, data_engine: DataEngine):
        self.llm = llm_engine.get_llm()
        self.data_engine = data_engine
        self.query_engine = QueryEngine()

    async def _extract_deterministic_intent(self, user_query: str, dataset_schema: str) -> PolarsOperation:
        """
        Usa o LLM exclusivamente para parseamento semântico, convertendo 
        linguagem humana para uma AST (Abstract Syntax Tree) do Polars.
        """
        llm_with_tools = self.llm.with_structured_output(PolarsOperation)
        
        prompt = f"""
        You are a strict data router. Analyze the user query and the available dataset columns.
        Map the query to the correct PolarsOperation.
        
        OPERATION GUIDELINES:
        - USE 'group_by' when the query asks for aggregates (sum, total, count, average) with a categorical breakdown or grouping (e.g., "vendas por produto", "total per sector").
        - USE 'aggregation' ONLY when asking for single comprehensive numbers representing the whole dataset (e.g., "total total de vendas", "média geral de preço").
        - USE 'top_n' when asking for highest, lowest, best, worst, limited outputs sorted by a metric.
        
        Dataset Schema:
        {dataset_schema}
        
        User Query:
        "{user_query}"
        
        Do not answer the query. Just output the JSON configuration for the operation conforming to your tool template.
        """
        return await llm_with_tools.ainvoke(prompt)


    async def run(self, message: str, active_file: str = None, syntax_context: str = "") -> dict:
        if not active_file:
            return {
                "messages": [AIMessage(content="I am the Analyst. Please upload a dataset so I can analyze it.", name="analyst")]
            }
        
        # Carrega dados
        success = self.data_engine.load_data(active_file)
        if not success:
            return {
                "messages": [AIMessage(content=f"Could not load data from {active_file}.", name="analyst")]
            }
            
        self.query_engine.set_dataframe(self.data_engine.df)
        summary = self.data_engine.get_summary()
        columns_schema = str(summary.get("columns", []))
        
        try:
            # 1. Passo Determinístico (Semântica -> Polars AST)
            polars_op = await self._extract_deterministic_intent(message, columns_schema)
            
            # 2. Execução Matemática (Rápida e Determinística)
            raw_results = self.query_engine.execute_deterministic_operation(polars_op)
            
            if "error" in raw_results:
                return {
                    "messages": [AIMessage(content=f"Error executing analysis: {raw_results['error']}", name="analyst")]
                }
                
            # 3. Passo Conversacional (Fluidez Humana)
            prompt = f"""
            You are a Senior Data Analyst representing 'The Council'. 
            The user asked: "{message}"
            
            You performed a deterministic calculation on the dataset and obtained the following EXACT result:
            {raw_results['data']}
            
            INSTRUCTIONS:
            - Respond directly to the user in a fluid, highly professional, and insightful manner.
            - Mention the key numbers from the result to prove the analysis.
            - DO NOT output raw JSON, dictionaries, or tables in your text. The system UI will render the charts separately based on the raw data.
            - Provide a brief insight or recommendation based on these numbers.
            """
            
            human_response = await self.llm.ainvoke(prompt)
            
            # Retorna as mutações separadas para o LangGraph State!
            return {
                "messages": [AIMessage(content=human_response.content, name="analyst")],
                "raw_data_context": raw_results['data']
            }
            
        except Exception as e:
            return {
                "messages": [AIMessage(content=f"An unexpected error occurred during analysis: {e}", name="analyst")]
            }
