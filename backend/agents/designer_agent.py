from typing import Dict, Any
from langchain_core.messages import AIMessage
from engines.llm_engine import llm_engine
from engines.data_engine import DataEngine
from engines.visualization_engine import VisualizationEngine
from engines.query_engine import QueryEngine
import json
from utils.json_utils import safe_json_dumps

class DesignerAgent:
    def __init__(self, data_engine: DataEngine, viz_engine: VisualizationEngine):
        self.llm = llm_engine.get_llm()
        self.data_engine = data_engine
        self.viz_engine = viz_engine
        self.query_engine = QueryEngine()

    async def run(self, message: str, active_file: str = None) -> str:
        if not active_file:
            return "I need a dataset to create a chart. Please upload a file first."
            
        # Ensure data is loaded
        if self.data_engine.df is None or self.data_engine.metadata.get("source") != active_file:
            success = self.data_engine.load_data(active_file)
            if not success:
                return f"Could not load data from {active_file}."
        
        # Configure QueryEngine
        self.query_engine.set_dataframe(self.data_engine.df)
        
        # Use LLM only to refine the query for the QueryEngine if needed, 
        # or just pass the message directly to QueryEngine.
        # QueryEngine is already smart enough to detect patterns.
        
        try:
            # 1. Execute deterministic query to get data for the chart
            query_result = self.query_engine.execute_query(message)
            
            if "error" in query_result:
                return f"Error preparing data for chart: {query_result['error']}"
            
            # 2. Generate chart spec using VisualizationEngine
            # We can use the original message as title
            spec = self.viz_engine.create_chart_from_query_result(query_result, title=message)
            
            # 3. Use LLM to provide a brief context/description of the chart being shown
            prompt = f"""
            You are the Designer Agent. I have generated a chart for the user's request: "{message}".
            The data used was: {safe_json_dumps(query_result.get('results', [])[:3], indent=2)}
            
            Provide a very brief (1 sentence) professional description of what this chart shows.
            """
            try:
                description = (await self.llm.ainvoke(prompt)).content
            except:
                description = "Here is the visualization you requested."
            
            return f"CHART_JSON:{spec}\n\n{description}"
            
        except Exception as e:
            return f"I encountered an error while designing your chart: {e}"
