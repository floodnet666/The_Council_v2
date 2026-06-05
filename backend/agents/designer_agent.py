from typing import Dict, Any
from langchain_core.messages import AIMessage
from engines.llm_engine import llm_engine
from engines.data_engine import DataEngine
from engines.visualization_engine import VisualizationEngine
from engines.query_engine import QueryEngine
from schemas.operations import ChartSchema
from utils.json_utils import safe_json_dumps

class DesignerAgent:
    def __init__(self, data_engine: DataEngine, viz_engine: VisualizationEngine):
        self.llm = llm_engine.get_llm()
        self.data_engine = data_engine
        self.viz_engine = viz_engine
        self.query_engine = QueryEngine()

    async def run(self, message: str, active_file: str = None, aggregated_data: list = None) -> Dict[str, Any]:
        if not active_file:
            return {
                "messages": [AIMessage(content="I need a dataset to create a chart. Please upload a file first.", name="designer")]
            }
            
        # Ensure data is loaded
        if self.data_engine.df is None or self.data_engine.metadata.get("source") != active_file:
            success = self.data_engine.load_data(active_file)
            if not success:
                return {
                    "messages": [AIMessage(content=f"Could not load data from {active_file}.", name="designer")]
                }
        
        # Configure QueryEngine
        self.query_engine.set_dataframe(self.data_engine.df)
        
        try:
            # Proteção Anti-Crash de payload para a UI: Truncar se o Analyst retornar linhas puras massivas
            if aggregated_data and len(aggregated_data) > 1000:
                aggregated_data = aggregated_data[:1000]

            # Coleta uma amostra de dados para contexto do LLM
            if aggregated_data:
                sample_data = aggregated_data[:3]
                available_columns = list(aggregated_data[0].keys()) if len(aggregated_data) > 0 else []
            else:
                try:
                    sample_data = self.data_engine.df.head(3).collect().to_dicts()
                    available_columns = self.data_engine.df.columns
                except Exception:
                    sample_data = []
                    available_columns = []

            # 2. Usar LLM estruturado para extrair a intenção visual
            prompt = f"""
            Você é um Designer Agent. Sua função é mapear a requisição de visualização do usuário para um ChartSchema rígido.
            
            Colunas Disponíveis: {available_columns}
            Dados Amostrais (RAG): {safe_json_dumps(sample_data, indent=2)}
            
            Requisição: "{message}"
            
            Retorne o ChartSchema correspondente para renderização nativa.
            """
            
            llm_structured = self.llm.with_structured_output(ChartSchema)
            chart_config = await llm_structured.ainvoke(prompt)
            
            # 3. Gerar descrição simples
            desc_prompt = f"""
            Você é o Designer Agent. Foi gerada uma configuração de gráfico: {chart_config.model_dump()}.
            Crie uma descrição fluida e breve (1 frase) sobre o que este visualizador demonstra.
            """
            try:
                description = (await self.llm.ainvoke(desc_prompt)).content
            except:
                description = "Aqui está a visualização solicitada baseada nos seus dados."
                
            return {
                "messages": [AIMessage(content=description, name="designer")],
                "visual_schema": chart_config.model_dump()
            }
            
        except Exception as e:
            return {
                "messages": [AIMessage(content=f"I encountered an error while designing your chart: {e}", name="designer")]
            }

