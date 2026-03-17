from typing import Dict, Any, List
from langchain_core.messages import AIMessage
from engines.llm_engine import llm_engine
from engines.data_engine import DataEngine
from engines.query_engine import QueryEngine
import json
import re
from engines.artifact_store import artifact_store
from utils.json_utils import safe_json_dumps

class AnalystAgent:
    """
    Analyst Agent - Executa análises determinísticas usando QueryEngine
    LLM é usado apenas para explicar resultados, não para cálculos
    """
    def __init__(self, data_engine: DataEngine):
        self.llm = llm_engine.get_llm()
        self.data_engine = data_engine
        self.query_engine = QueryEngine()

    async def run(self, message: str, active_file: str = None, syntax_context: str = "") -> str:
        if not active_file:
            return "I am the Analyst. Please upload a dataset so I can analyze it."
        
        # Try validation/loading
        if self.data_engine.df is None or self.data_engine.metadata.get("source") != active_file:
            success = self.data_engine.load_data(active_file)
            if not success:
                return f"Could not load data from {active_file}."
        
        # Configura QueryEngine com o DataFrame atual
        self.query_engine.set_dataframe(self.data_engine.df)
        
        summary = self.data_engine.get_summary()
        semantic_types = summary.get("semantic_types", {})
        ambiguities = summary.get("ambiguities", {})
        
        # Detecta se é uma query analítica, exploratória ou de simulação
        query_lower = message.lower()
        
        is_simulation = any(word in query_lower for word in [
            "simule", "preveja", "projeção", "projeto", "forecast", "simulate", "predict",
            "tendência", "trend", "ml", "correlação", "regressão", "cluster"
        ])
        
        is_sql_needed = any(word in query_lower for word in [
            "select", "from", "where", "join", "group by", "order by", "sql",
            "filtre", "filtrar", "depois", "antes", "acima", "abaixo", "entre", "período"
        ])

        is_analytical = is_simulation or is_sql_needed or any(word in query_lower for word in [
            "total", "soma", "média", "count", "quantos", "por categoria",
            "agrupar", "top", "maior", "menor", "estatísticas",
            "vendidos", "produtos", "quais", "ranking", "most", "sold", "by",
            "cada", "distribuição", "percentual"
        ])
        
        # Prepare ambiguity report
        ambiguity_report = ""
        if ambiguities:
            ambiguity_report = "\n\n⚠️ **Semantic Note:** Some columns have ambiguous classifications:\n"
            for col, reason in ambiguities.items():
                ambiguity_report += f"- Column `{col}` ({semantic_types.get(col)}): {reason}\n"

        if is_analytical:
            used_code = ""
            # Seleciona motor de execução
            if is_simulation:
                # O LLM deve gerar o código Python
                prompt_code = f"Gere APENAS o código Polars/Python para: {message}. Use 'lf' como LazyFrame. Salve o resultado final na variável 'result'."
                code_resp = await self.llm.ainvoke(prompt_code)
                used_code = f"```python\n{code_resp.content}\n```"
                analysis_result = self.data_engine.execute_python(code_resp.content)
            elif is_sql_needed:
                # O LLM deve gerar o SQL
                prompt_sql = f"Gere APENAS o SQL (Polars dialect) para: {message}. A tabela chama-se 'data'."
                sql_resp = await self.llm.ainvoke(prompt_sql)
                # Clean SQL if LLM adds markdown
                sql_query = re.sub(r"```sql|```", "", sql_resp.content).strip()
                used_code = f"```sql\n{sql_query}\n```"
                analysis_result = self.data_engine.execute_sql(sql_query)
            else:
                # Tenta deterministic primeiro (QueryEngine)
                analysis_result = self.query_engine.execute_query(message)
                
                # Fallback para SQL se QueryEngine falhar ou for inconclusivo
                if "error" in analysis_result or not analysis_result.get("results"):
                    prompt_sql = f"Gere APENAS o SQL (Polars dialect) para: {message}. A tabela chama-se 'data'."
                    sql_resp = await self.llm.ainvoke(prompt_sql)
                    sql_query = re.sub(r"```sql|```", "", sql_resp.content).strip()
                    used_code = f"```sql\n{sql_query}\n```"
                    analysis_result = self.data_engine.execute_sql(sql_query)
                else:
                    used_code = f"```json\n// Query Engine Interno\n{safe_json_dumps(analysis_result.get('metadata', {}))}\n```"
            
            if "error" in analysis_result:
                return f"Error executing analysis: {analysis_result['error']}\n\n**Tentativa de Código:**\n{used_code}"
            
            # Formata um resumo dos dados para o LLM (não o JSON inteiro se for gigante)
            sample_results = analysis_result.get("results") or analysis_result.get("data") or []
            if isinstance(sample_results, list) and len(sample_results) > 10:
                result_preview = sample_results[:10]
                result_json_for_llm = f"{safe_json_dumps(result_preview)} ... [TRUNCATED for brevity, total rows: {len(sample_results)}]"
            else:
                result_json_for_llm = safe_json_dumps(analysis_result)

            # LLM explica os resultados
            prompt = f"""
            SYSTEM: Senior Data Analyst. Respond in user's query language. Max 1-2 sentence executive summary.
            POLLARS ONLY. No Pandas.
            
            Analysis results (Sample):
            {result_json_for_llm}
            
            User Query: "{message}"
            
            Task: Provide an EXTREMELY CONCISE executive summary (max 20 words).
            Format:
            1. Conclusão Principal: [Max 10 words]
            2. Detalhes: [Max 10 words]
            """
            
            try:
                # Record in ArtifactStore for reporting (Phase 10) - FULL DATA for persistence
                artifact_store.record_result(
                    title=f"Analysis: {message[:50]}...",
                    data=analysis_result.get("results") or analysis_result.get("data"),
                    meta={"query": message, "type": analysis_result.get("query_type")}
                )

                explanation = "Análise concluída com sucesso."
                
                # Para o UI, enviamos os dados completos e o rastreio (evidence)
                result_json_full = safe_json_dumps(analysis_result, indent=2)
                return f"ANALYSIS_DATA:\n{result_json_full}\n\n---\n\n{explanation}{ambiguity_report}\n\n<details><summary>🔍 Código Fonte Executado</summary>\n\n{used_code}\n\n</details>"
                
            except Exception as e:
                # Fallback: retorna apenas os dados
                result_json_full = safe_json_dumps(analysis_result, indent=2)
                return f"ANALYSIS_DATA:\n{result_json_full}\n\n(LLM explanation unavailable: {e}){ambiguity_report}\n\n<details><summary>🔍 Código Fonte Executado</summary>\n\n{used_code}\n\n</details>"
        
        else:
            # Query exploratória - usa comportamento original
            summary_text = f"Columns: {', '.join(summary.get('columns', []))}\nPreview:\n{safe_json_dumps(summary.get('preview', []), indent=2)}"
            
            prompt = f"""
            SYSTEM: You are a Polars Expert Analyst. You MUST NOT suggest or use Pandas syntax.
            Always recommend Polars expressions (pl.col, df.filter, etc.).
            
            SOURCE OF TRUTH (Librarian Context):
            {syntax_context if syntax_context else "No specific context provided. Follow standard Polars documentation."}
            
            You are the Analyst Agent. You have access to a dataset.
            
            Semantic Mapping:
            {safe_json_dumps(semantic_types, indent=2)}
            
            Data Summary:
            {summary_text}
            
            User Query: "{message}"
            
            Please provide a brief, professional summary of what this data seems to represent and suggest 3 potential insights or analyses.
            Everything MUST be written in the user's language (matching the language of their query).
            Mention if there are any significant semantic ambiguities (listed below if any).
            
            Ambiguities:
            {safe_json_dumps(ambiguities, indent=2)}
            """
            
            try:
                response = (await self.llm.ainvoke(prompt)).content
                
                # Logic to detect and validate code blocks for Polars integrity
                code_blocks = re.findall(r"```python\n(.*?)\n```", response, re.DOTALL)
                for code in code_blocks:
                    self.data_engine.validate_polars_syntax(code)
                
            except Exception as e:
                # Se for PandasSyntaxDetectedError, deixa subir para o grafo tratar o self-healing
                if "Pandas syntax detected" in str(e):
                    raise
                response = f"Data Loaded. Summary: {summary_text}. (LLM Error: {e})"
                
            return f"{response}{ambiguity_report}"
