import asyncio
import os
import sys
from pprint import pprint

# Adiciona E:\The_Council_v2\backend ao PATH
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from engines.data_engine import DataEngine
from agents.analyst_agent import AnalystAgent

async def test_queries():
    data_engine = DataEngine()
    analyst = AnalystAgent(data_engine)
    
    # Dataset path from previous feedback
    dataset_path = r"C:\Users\thiag\Downloads\online_shoppers.csv"
    if not os.path.exists(dataset_path):
        print(f"Dataset not found at {dataset_path}, trying uploads/Liquor_Sales.csv fallback")
        # Optional: try upload if downloads triggers permission issues
    
    print(f"Loading dataset: {dataset_path}")
    load_success = data_engine.load_data(dataset_path)
    if not load_success:
        print("Failed to load dataset.")
        return

    # Query 1: Triggers Aggregation (Dictionary output in QueryEngine)
    query1 = "Qual a média da taxa de rejeição (BounceRates) geral?"
    query2 = "Quantas visitas foram registradas para cada sistema operacional (OperatingSystems)?"

    # Save output to file to avoid console corruption
    with open("backend/benchmark_output.txt", "w", encoding="utf-8") as f:
        f.write(f"--- Testing Query 1: '{query1}' ---\n")
        response1 = await analyst.run(query1, active_file=dataset_path)
        f.write("\n[RESPONSE 1]\n")
        f.write(response1 + "\n")
        
        f.write(f"\n--- Testing Query 2: '{query2}' ---\n")
        response2 = await analyst.run(query2, active_file=dataset_path)
        f.write("\n[RESPONSE 2]\n")
        f.write(response2 + "\n")
    print("Test complete. Results saved to backend/benchmark_output.txt")

if __name__ == "__main__":
    asyncio.run(test_queries())
