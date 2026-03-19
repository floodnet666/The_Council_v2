import asyncio
import os
import sys
import json
import polars as pl
from typing import Dict, Any

# Adiciona o diretório backend ao path para importação
sys.path.append(os.path.join(os.getcwd(), "backend"))

from agents.analyst_agent import AnalystAgent
from engines.data_engine import DataEngine
from utils.json_utils import safe_json_dumps

async def run_heuristic_test():
    print("=== THE COUNCIL 2.0 - HEURISTIC VERIFICATION ===")
    
    data_engine = DataEngine()
    analyst = AnalystAgent(data_engine)
    
    csv_path = r"E:\The_Council_v2\backend\uploads\Liquor_Sales.csv"
    
    if not os.path.exists(csv_path):
        print(f"ERROR: File not found at {csv_path}")
        return

    print(f"\n[1/3] Carregando arquivo: {csv_path}...")
    # Simula o carregamento que o AnalystAgent faz
    success = data_engine.load_data(csv_path)
    if not success:
        print("Failed to load data.")
        return
    
    print("Metadata extraída:")
    summary = data_engine.get_summary()
    print(f"Colunas: {len(summary['columns'])}")
    print(f"Linhas detectadas: {summary['row_count']}")
    
    queries = [
        "Quais os 3 produtos mais vendidos (em valor) por categoria?",
        "Total de vendas por ano e Vendor Name?",
        "Média de custo de garrafa por County?",
        "Quais as 5 categorias com maior volume vendido em litros?",
        "Top 5 cidades com maior valor total de vendas?"
    ]
    
    print("\n[2/3] Executando Queries Heurísticas...\n")
    
    results = []
    
    for i, q in enumerate(queries, 1):
        print(f"TESTE {i}: {q}")
        print("-" * 50)
        
        # O contexto de sintaxe pode ser vazio para este teste de caixa preta
        response = await analyst.run(q, active_file=csv_path, syntax_context="Use pl.col for all access. Prefer 'Name' columns over ID columns for grouping.")
        
        print(f"RESPOSTA:\n{response}")
        print("=" * 80 + "\n")
        
        results.append({
            "query": q,
            "response": response
        })
        
    # Salva resultado para análise do agente
    with open("/tmp/heuristic_test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    asyncio.run(run_heuristic_test())
