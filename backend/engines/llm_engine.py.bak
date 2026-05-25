from langchain_ollama import ChatOllama
from dotenv import load_dotenv
import os

load_dotenv()

# Configuration from env vars
MODEL_NAME = os.getenv("OLLAMA_MODEL", "qwen2.5:1.5b")
BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

class LLMEngine:
    def __init__(self):
        self.llm = ChatOllama(
            model=MODEL_NAME,
            base_url=BASE_URL,
            temperature=0.1
        )
    
    def get_llm(self):
        return self.llm

# Singleton instance
llm_engine = LLMEngine()
