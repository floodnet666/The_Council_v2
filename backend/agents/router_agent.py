from typing import Dict, Any, Literal
from engines.llm_engine import llm_engine
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

class RouterAgent:
    def __init__(self):
        self.llm = llm_engine.get_llm()
        self.prompt = ChatPromptTemplate.from_template(
            """
            You are the Router for 'The Council', an advanced AI analytics system.
            You must route the user's request to ONE of the following agents:
            
            - analyst: For analyzing EXISTING uploaded data, statistics, summarizing datasets
              Examples: "analyze this data", "what's in the dataset", "show me statistics", "summarize the data"
            
            - designer: For creating charts, graphs, plots, visualizations from data
              Examples: "create a chart", "make a bar graph", "visualize this data", "plot the data"
            
            - librarian: For HOW-TO questions, programming help, Polars documentation, system documentation
              Examples: "how to do X in Polars", "como fazer group by", "how does this work", "what is The Council"
            
            - general: For greetings, small talk, or anything not related to the above
              Examples: "hello", "hi", "how are you", "thank you"
            
            - reporting: For executive summaries, session reports, or questions like "what did we discover?"
              Examples: "gera um relatório", "resumo executivo", "relatório final", "o que descobrimos?"

            User Request: "{message}"
            
            Think step by step:
            1. Is this asking HOW TO do something (programming/Polars)? -> librarian
            2. Is this about creating a visualization? -> designer
            3. Is this about analyzing EXISTING data? -> analyst  
            4. Is this asking how the system works or for documentation? -> librarian
            5. Is this asking for a summary or executive report? -> reporting
            6. Is this just a greeting or casual chat? -> general
            
            Return ONLY ONE WORD: analyst, designer, librarian, reporting, or general
            """
        )
        self.chain = self.prompt | self.llm | StrOutputParser()

    async def route(self, message: str, context: Dict[str, Any]) -> Literal["analyst", "general", "librarian", "designer", "reporting"]:
        message_lower = message.lower()
        
        # 🚀 BYPASS DETERMINÍSTICO PARA ACELERAÇÃO DE BENCHMARKS 
        if any(word in message_lower for word in ["total", "soma", "média", "count", "quantos", "maior", "menor", "agrupe", "por", "qual", "quais"]):
            if any(chart in message_lower for chart in ["gráfico", "grafico", "plotar", "plot"]):
                return "designer"
            return "analyst"
            
        try:
            intent = await self.chain.ainvoke({"message": message})
            intent = intent.strip().lower()
            valid_intents = ["analyst", "general", "librarian", "designer", "reporting"]
            
            for v in valid_intents:
                if v in intent:
                    return v
            return "general"
        except Exception as e:
            print(f"Router Error: {e}")
            return "general"
