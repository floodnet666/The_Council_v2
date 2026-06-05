"""
Analyst Agent - Rewrite for The Council 2.0 Architectural Overhaul
"""
from typing import Dict, Any, List
from langchain_core.messages import AIMessage
from engines.llm_engine import llm_engine
from engines.data_engine import DataEngine
from engines.query_engine import QueryEngine
from schemas.operations import DualSqlOperation
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from utils.logging_config import logger
import json
import re

class AnalystAgent:
    def __init__(self, data_engine: DataEngine):
        self.llm = llm_engine.get_llm()
        self.data_engine = data_engine
        self.query_engine = QueryEngine()

    async def _extract_deterministic_intent(self, user_query: str, dataset_schema: str) -> DualSqlOperation:
        """
        Usa o LLM exclusivamente para parseamento semântico, convertendo 
        linguagem humana para uma arquitetura de Dual-SQL nativa.
        """
        llm_with_tools = self.llm.with_structured_output(DualSqlOperation)
        
        prompt = f"""
        You are a strict Senior SQL Data Engineer and BI Analyst. 
        Analyze the user query and the dataset schema. Map it to TWO distinct SQL queries in PostgreSQL dialect:
        
        1. visual_query: Granular data needed to draw the chart or table (e.g. `SELECT order_date, SUM(lucro) AS total_lucro ... GROUP BY order_date`).
        2. analytical_query: A single-row global aggregation (e.g. `SELECT MIN(lucro) AS min_lucro, MAX(lucro) AS max_lucro, CORR(lucro, desconto) AS corr_lucro_desc`). This will be used to understand contours, patterns, and correlations!
        
        SQL GUIDELINES:
        - The table name is ALWAYS `data`.
        - DO NOT wrap the queries in markdown code blocks.
        - ALWAYS give an alias to computed columns (e.g. COUNT(*) AS total_vendas).
        - IMPORTANT (Polars SQL Dialect): `DATE_TRUNC`, `CURRENT_DATE`, and `INTERVAL` are NOT supported. 
        - CRITICAL BI LOGIC (Dates): "Last semester" or "Last year" MUST NOT use today's date. Check `string_profiles`. If a time column is Month names ('Jan', 'Feb'), filter using `IN ('Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')`.
        - CRITICAL BI LOGIC (Booleans/Flags): If calculating "Total" on a Boolean/String flag (e.g. Revenue='True'), DO NOT USE `SUM()`. Use `COUNT(*)` with a `WHERE` clause. 
        - CRITICAL BI LOGIC (Combining): If both relative time AND boolean logic apply, combine them: `WHERE Revenue = true AND Month IN (...)`.
        - CRITICAL BI LOGIC (Visual Query for Totals): If the user asks for a single scalar total, the `visual_query` MUST provide a trend by grouping by the time dimension (e.g. `SELECT Month, COUNT(*) AS total FROM data WHERE Revenue = true GROUP BY Month`). DO NOT select raw boolean columns!
        
        Dataset Schema & Data Profile (Pay extreme attention to string_profiles to know exact values to filter):
        {dataset_schema}
        
        User Query:
        "{user_query}"
        
        Output the JSON conforming to DualSqlOperation.
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
        # Enviar esquema completo (tipos, previews, distinct string values) para combater alucinações de dialeto.
        columns_schema = str({
            "columns": summary.get("columns", []),
            "dtypes": summary.get("technical_dtypes", {}),
            "string_profiles": summary.get("string_profiles", {}),
            "preview_data": summary.get("preview", [])
        })
        
        try:
            MAX_RETRIES = 2
            sql_op = await self._extract_deterministic_intent(message, columns_schema)
            
            for attempt in range(MAX_RETRIES + 1):
                visual_results = self.data_engine.execute_sql(sql_op.visual_query)
                analytical_results = self.data_engine.execute_sql(sql_op.analytical_query)
                
                # Sucesso em ambas
                if "error" not in visual_results and "error" not in analytical_results:
                    break
                    
                # Se falhar e ainda houver retentativas
                if attempt < MAX_RETRIES:
                    error_msg = visual_results.get("error", "") + " | " + analytical_results.get("error", "")
                    logger.warning(f"SQL Falhou. Iniciando Auto-Healing (Tentativa {attempt+1}): {error_msg}")
                    correction_prompt = f"""
                    Your previous SQL queries failed in the Polars SQL execution engine.
                    Error: {error_msg}
                    
                    Fix the queries using strict standard ANSI SQL (Polars dialect). Do not use Postgres-specific syntax like '::', 'DATE_TRUNC', 'STRING_AGG', or 'ILIKE'.
                    Previous Visual: {sql_op.visual_query}
                    Previous Analytical: {sql_op.analytical_query}
                    
                    Return ONLY the corrected JSON schema.
                    """
                    # Overwrite com o json corrigido
                    sql_op = await self._extract_deterministic_intent(correction_prompt, columns_schema)
                else:
                    # Falhou as 3 vezes
                    if "error" in visual_results:
                        return {"messages": [AIMessage(content=f"Error executing visual query after {MAX_RETRIES} retries: {visual_results['error']}", name="analyst")]}

            visual_data = visual_results['data']
            
            if "error" in analytical_results:
                analytical_data = [{"error": "Could not compute analytical query."}]
            else:
                analytical_data = analytical_results['data']
                
            # 3. Passo Conversacional (Ceticismo Analítico Sênior)
            logger.info("Gerando resposta textual a partir do Dossiê Analítico Seguro...")
            summary_prompt = ChatPromptTemplate.from_template(
                """You are a Senior BI Analyst for 'The Council'.
                Answer the user's question concisely based strictly on the global analytical dossier below.
                (Note: This dossier contains the mathematical truth: Min, Max, Averages, Correlations).
                
                USER QUESTION: {question}
                
                ANALYTICAL DOSSIER (JSON):
                {data}
                
                Keep your answer under 4 sentences. Be critical. If you see correlations, question causality. Do not leak raw JSON in the response.
                """
            )
            
            chain = summary_prompt | self.llm | StrOutputParser()
            summary = await chain.ainvoke({"question": message, "data": str(analytical_data)})
            
            state_update = {
                "messages": [AIMessage(content=summary, name="analyst")],
                "raw_data_context": visual_data, # Data real intacto vai pro Designer!
                "next_node": "reflection"
            }
            return state_update
            
        except Exception as e:
            return {
                "messages": [AIMessage(content=f"An unexpected error occurred during analysis: {e}", name="analyst")]
            }
