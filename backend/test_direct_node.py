import time
from engines.data_engine import DataEngine
from engines.query_engine import QueryEngine

def test_direct():
    print("Direct Execution Speed Test")
    # 1. Warmup Cache
    start_warm = time.time()
    engine_data = DataEngine()
    df = engine_data.load_data("uploads\\Liquor_Sales.csv")
    print(f"Cache Warmup/Fetch: {time.time() - start_warm:.4f}s")
    
    engine = QueryEngine(df)
    
    # Q1. Quantos registros totais
    print("\nExecuting Q1 Direct...")
    start_q1 = time.time()
    res = engine.execute_aggregation("Quantos registros totais existem no arquivo", [])
    print(f"Q1 Core Execution: {time.time() - start_q1:.4f}s")
    print(f"Q1 Result: {res}")
    
    # Q16. Top 10 cidades faturamento
    print("\nExecuting Q16 GroupBy Direct...")
    start_q16 = time.time()
    res16 = engine.execute_group_by("Agrupe as vendas por 'City' e liste as 10 cidades que mais geraram faturamento", [])
    print(f"Q16 Core Execution: {time.time() - start_q16:.4f}s")
    print(f"Q16 Result Count: {len(res16.get('results', []))}")

if __name__ == "__main__":
    test_direct()
