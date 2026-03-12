from typing import Dict, Any, List
from langchain_core.messages import AIMessage
from engines.llm_engine import llm_engine
from engines.data_engine import DataEngine
from engines.query_engine import QueryEngine
import json
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

    async def run(self, message: str, active_file: str = None) -> str:
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
        
        # Detecta se é uma query analítica ou exploratória
        query_lower = message.lower()
        is_analytical = any(word in query_lower for word in [
            "total", "soma", "média", "count", "quantos", "por categoria",
            "group by", "agrupar", "top", "maior", "menor", "estatísticas"
        ])
        
        # Prepare ambiguity report
        ambiguity_report = ""
        if ambiguities:
            ambiguity_report = "\n\n⚠️ **Semantic Note:** Some columns have ambiguous classifications:\n"
            for col, reason in ambiguities.items():
                ambiguity_report += f"- Column `{col}` ({semantic_types.get(col)}): {reason}\n"

        if is_analytical:
            # Executa análise determinística
            analysis_result = self.query_engine.execute_query(message)
            
            if "error" in analysis_result:
                return f"Error executing analysis: {analysis_result['error']}"
            
            # Formata resultado estruturado
            result_json = safe_json_dumps(analysis_result, indent=2)
            
            # LLM explica os resultados
            prompt = f"""
            You are the Analyst Agent. You performed a deterministic analysis on the dataset.
            
            Semantic Context:
            {safe_json_dumps(semantic_types, indent=2)}
            
            Analysis Results (JSON):
            {result_json}
            
            User Query: "{message}"
            
            Please provide a clear, professional explanation of these results in natural language.
            Start with the key findings, then provide context and insights.
            Keep it concise but informative.
            
            Format your response as:
            1. Key Finding: [main result]
            2. Details: [breakdown of results]
            3. Insight: [what this means]
            """
            
            try:
                explanation = (await self.llm.ainvoke(prompt)).content
                
                # Retorna dados estruturados + explicação + avisos
                return f"ANALYSIS_DATA:\n{result_json}\n\n---\n\n{explanation}{ambiguity_report}"
                
            except Exception as e:
                # Fallback: retorna apenas os dados
                return f"ANALYSIS_DATA:\n{result_json}\n\n(LLM explanation unavailable: {e}){ambiguity_report}"
        
        else:
            # Query exploratória - usa comportamento original
            summary_text = f"Columns: {', '.join(summary.get('columns', []))}\nPreview:\n{safe_json_dumps(summary.get('preview', []), indent=2)}"
            
            prompt = f"""
            You are the Analyst Agent. You have access to a dataset.
            
            Semantic Mapping:
            {safe_json_dumps(semantic_types, indent=2)}
            
            Data Summary:
            {summary_text}
            
            User Query: "{message}"
            
            Please provide a brief, professional summary of what this data seems to represent and suggest 3 potential insights or analyses.
            Mention if there are any significant semantic ambiguities (listed below if any).
            
            Ambiguities:
            {safe_json_dumps(ambiguities, indent=2)}
            """
            
            try:
                response = (await self.llm.ainvoke(prompt)).content
            except Exception as e:
                response = f"Data Loaded. Summary: {summary_text}. (LLM Error: {e})"
                
            return f"{response}{ambiguity_report}"
