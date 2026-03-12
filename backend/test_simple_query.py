"""
Teste simples do QueryEngine
"""
import polars as pl
from engines.query_engine import QueryEngine
import json


# Criar dados de exemplo
df = pl.DataFrame({
    "categoria": ["A", "B", "A", "C", "B", "A"],
    "valor": [100, 150, 200, 120, 180, 90],
}).lazy()

# Inicializar engine
engine = QueryEngine(df)

# Teste 1: Agregação
print("=== TESTE 1: Agregacao ===")
result = engine.execute_query("Qual o total de valor?")
print(json.dumps(result, indent=2, ensure_ascii=False))

# Teste 2: Group By
print("\n=== TESTE 2: Group By ===")
result = engine.execute_query("Total por categoria")
print(json.dumps(result, indent=2, ensure_ascii=False))

# Teste 3: Describe
print("\n=== TESTE 3: Describe ===")
result = engine.execute_query("Mostre estatisticas")
print(json.dumps(result, indent=2, ensure_ascii=False))

print("\n=== TESTES CONCLUIDOS ===")
