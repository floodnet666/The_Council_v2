import asyncio
import time
import os
import sys

# Add current dir to path to find engines, agents, workflow
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from workflow.graph import graph
from langchain_core.messages import HumanMessage

FILE_PATH = r"e:\The_Council_v2\backend\uploads\Liquor_Sales.csv"

QUESTIONS = [
    "1. Quantos registros totais existem no arquivo de vendas de bebidas?",
    "2. Qual é o valor total de vendas ('Sale (Dollars)') gerado considerando todas as linhas?",
    "3. Quantas vendas ocorreram na cidade de 'DES MOINES'?",
    "4. Agrupe as vendas por 'City' e liste as 10 cidades que mais geraram faturamento em dólares.",
    "5. Agrupe as vendas por 'Category Name' e me mostre o Top 5 de faturamento.",
    "6. Qual condado ('County') tem a média mais cara de preço de varejo ('State Bottle Retail')?",
    "7. Mostre as estatísticas descritivas (min, max, media) de 'Sale (Dollars)'.",
    "8. Filtre vendas da cidade 'CEDAR RAPIDS' e identifique o produto ('Item Description') mais vendido (soma de garrafas).",
    "9. Filtre as vendas que ocorreram depois de 01/01/2015 e grupe por categoria, sumando o número de garrafas.",
    "10. Qual fornecedor ('Vendor Name') vendeu a maior quantidade de garrafas no total ('Bottles Sold')?"
]

async def run_query(question: str, idx: int):
    print(f"\n--- [QUERY {idx+1}/10] {question} ---")
    start_t = time.time()
    
    initial_state = {
        "messages": [HumanMessage(content=question)],
        "session_id": f"offline_robust_{idx+1}",
        "file_path": FILE_PATH,
        "current_agent": "router" # start from router
    }
    
    try:
        # Avoid uvicorn/httpx layer, call graph directly
        result = await graph.ainvoke(initial_state)
        elapsed = time.time() - start_t
        print(f"-> SUCCESS in {elapsed:.2f}s")
        # Extract last message
        messages = result.get("messages", [])
        if messages:
             print(f"RESPONSE SNIPPET: {messages[-1].content[:200]}...")
        return {
            "id": idx + 1,
            "status": "success",
            "time_secs": elapsed
        }
    except Exception as e:
        elapsed = time.time() - start_t
        print(f"-> ERROR in {elapsed:.2f}s: {e}")
        import traceback
        traceback.print_exc()
        return {
            "id": idx + 1,
            "status": "error",
            "time_secs": elapsed,
            "error_text": str(e)
        }

async def main():
    print("Iniciando Teste Robusto OFFLINE (Direct Graph): 10 Perguntas")
    print(f"File: {FILE_PATH}\n")
    
    results = []
    
    for idx, question in enumerate(QUESTIONS):
        res = await run_query(question, idx)
        results.append(res)
        print("-" * 40)
        
    print("\n[FINALIZADO]")
    for r in results:
        print(f"Q{r['id']}: {r['status']} ({r['time_secs']:.2f}s)")

if __name__ == "__main__":
    asyncio.run(main())
