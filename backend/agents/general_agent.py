from engines.llm_engine import llm_engine

class GeneralAgent:
    def __init__(self):
        self.llm = llm_engine.get_llm()

    async def run(self, message: str) -> str:
        try:
            response = (await self.llm.ainvoke(f"You are a helpful general assistant for 'The Council' AI system. User says: {message}")).content
        except:
            response = "I am the General Assistant. How can I help?"
        return response
