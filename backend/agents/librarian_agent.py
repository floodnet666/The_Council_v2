from typing import Dict, Any, List
from langchain_core.messages import AIMessage
from engines.llm_engine import llm_engine
from engines.memory_engine import MemoryEngine
import os

class LibrarianAgent:
    def __init__(self, memory_engine: MemoryEngine):
        self.llm = llm_engine.get_llm()
        self.memory_engine = memory_engine
        self._ingested_files = set()

    async def run(self, message: str, active_file: str = None) -> str:
        # Auto-ingest if file provided and not already indexed in this session
        if active_file and os.path.exists(active_file) and active_file not in self._ingested_files:
            ext = os.path.splitext(active_file)[1].lower()
            if ext in [".pdf", ".txt", ".md"]:
                 self.memory_engine.ingest_file(active_file)
                 self._ingested_files.add(active_file)
        
        results = self.memory_engine.search(message, k=3)
        
        if results:
             # Enhance with LLM
             context = "\n".join([f"- {r}" for r in results])
             prompt = f"""
             You are the Librarian Agent. Answer the user query based ONLY on the following context.
             If the answer is not in the context, say you don't know based on the archive.
             
             Context:
             {context}
             
             User Query: {message}
             """
             try:
                 response = (await self.llm.ainvoke(prompt)).content
                 return f"LIBRARIAN_RESPONSE:\n{response}"
             except:
                 return f"LIBRARIAN_RESPONSE:\nFound in Archives:\n{context}"
        else:
             return "LIBRARIAN_RESPONSE:\nNo relevant documents found in the archives."
