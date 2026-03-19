import json
from typing import Dict, Any, List, Optional
from langchain_core.messages import SystemMessage
from engines.llm_engine import llm_engine
from engines.data_engine import DataEngine
from engines.artifact_store import artifact_store
import polars as pl
from utils.logging_config import logger

class ReportingAgent:
    """
    Reporting Agent - Generates executive summaries and automated insights.
    Uses current ArtifactStore and DataEngine state.
    """
    def __init__(self, data_engine: DataEngine):
        self.llm = llm_engine.get_llm()
        self.data_engine = data_engine

    def _profile_dataset(self) -> str:
        if self.data_engine.df is None:
            return "No dataset loaded."

        lines = []
        try:
            schema = self.data_engine.df.collect_schema()
            cols = schema.names()
            lines.append(f"Columns: {', '.join(cols)}")
            
            # Use cached summary bits if available
            summary = self.data_engine.get_summary()
            lines.append(f"Row count: {summary.get('row_count')}")
            
            date_cols = [c for c, t in schema.items() if t == pl.Date or t == pl.Datetime]
            if date_cols:
                lines.append(f"Temporal data detected in: {', '.join(date_cols)}")
        except Exception as e:
            lines.append(f"Profile error: {e}")
        return "\n".join(lines)

    async def generate_executive_report(self, messages: Optional[List[Any]] = None) -> str:
        """Generates a high-level summary of the session findings."""
        profile_txt = self._profile_dataset()
        artifacts = artifact_store.snapshot()
        results = artifacts.get("results", [])
        
        if not results:
            return "No analysis has been performed yet to generate an executive report." if not messages else "Nenhuma análise foi realizada ainda."

        # Detect language from messages or default to PT-BR (if context suggests it)
        lang_instruction = "Matches the language of the user's last request or the overall session history."
        if messages:
            last_message = messages[-1].content
            lang_instruction = f"Matches the language of the query: '{last_message}'"
        
        # Prepare context for LLM
        findings_summary = []
        for res in results[-5:]: # Use last 5 analysis
            findings_summary.append(f"- {res.get('title')}: {res.get('rows')} registros encontrados.")

        prompt = f"""
        Você é um Consultor de Dados Sênior. Sua tarefa é criar um Relatório Executivo conciso.
        
        CONTEXTO DO DATASET:
        {profile_txt}
        
        RESUMO DAS ANÁLISES REALIZADAS:
        {chr(10).join(findings_summary)}
        
        REQUISITOS:
        1. LANGUAGE: {lang_instruction}
        2. BE DIRECT AND PROFESSIONAL ("Executive Tone").
        3. Highlight 3 main conclusions (insights).
        4. Identify potential risks or opportunities based on the data.
        
        Format:
        ## Executive Report / Relatório Executivo
        [Summary paragraph]
        
        ### Key Insights / Principais Insights
        - [Insight 1]
        - [Insight 2]
        - [Insight 3]
        
        ### Next Steps / Próximos Passos
        - [Suggested action]
        """
        
        try:
             response = (await self.llm.ainvoke(prompt)).content
             return response
        except Exception as e:
             logger.error(f"[ReportingAgent Error] {e}")
             return f"Erro ao gerar relatório: {e}"

# Singleton instance
# Note: In the graph it will be initialized with the shared data_engine
