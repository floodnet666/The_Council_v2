"""
Script de teste para QueryEngine
Testa análises determinísticas sem depender de LLM
"""
import polars as pl
from engines.query_engine import QueryEngine
import json


def create_sample_data():
    """Cria dados de exemplo para teste"""
    return pl.DataFrame({
        "categoria": ["A", "B", "A", "C", "B", "A", "C", "B", "A", "C"],
        "valor": [100, 150, 200, 120, 180, 90, 140, 160, 110, 130],
        "quantidade": [5, 3, 8, 4, 6, 2, 7, 5, 3, 4],
        "mes": ["Jan", "Jan", "Fev", "Fev", "Mar", "Mar", "Abr", "Abr", "Mai", "Mai"]
    }).lazy()


def test_aggregation():
    """Testa agregações"""
    print("\n=== TESTE 1: AGREGAÇÃO ===")
    df = create_sample_data()
    engine = QueryEngine(df)
    
    queries = [
        "Qual o total de valor?",
        "Qual a média de quantidade?",
        "Quantos registros existem?"
    ]
    
    for query in queries:
        print(f"\nQuery: {query}")
        result = engine.execute_query(query)
        print(json.dumps(result, indent=2, ensure_ascii=False))


def test_group_by():
    """Testa group by"""
    print("\n=== TESTE 2: GROUP BY ===")
    df = create_sample_data()
    engine = QueryEngine(df)
    
    queries = [
        "Total por categoria",
        "Agrupar por categoria"
    ]
    
    for query in queries:
        print(f"\nQuery: {query}")
        result = engine.execute_query(query)
        print(json.dumps(result, indent=2, ensure_ascii=False))


def test_describe():
    """Testa estatísticas descritivas"""
    print("\n=== TESTE 3: DESCRIBE ===")
    df = create_sample_data()
    engine = QueryEngine(df)
    
    query = "Mostre estatísticas do dataset"
    print(f"\nQuery: {query}")
    result = engine.execute_query(query)
    print(json.dumps(result, indent=2, ensure_ascii=False))


def test_top_n():
    """Testa top N"""
    print("\n=== TESTE 4: TOP N ===")
    df = create_sample_data()
    engine = QueryEngine(df)
    
    queries = [
        "Top 5 maiores valores",
        "3 menores quantidades"
    ]
    
    for query in queries:
        print(f"\nQuery: {query}")
        result = engine.execute_query(query)
        print(json.dumps(result, indent=2, ensure_ascii=False))


def test_cache():
    """Testa sistema de cache"""
    print("\n=== TESTE 5: CACHE ===")
    df = create_sample_data()
    engine = QueryEngine(df)
    
    query = "Total de valor"
    
    print("Primeira execução (sem cache):")
    result1 = engine.execute_query(query)
    print(f"Cache size: {len(engine.cache)}")
    
    print("\nSegunda execução (com cache):")
    result2 = engine.execute_query(query)
    print(f"Cache size: {len(engine.cache)}")
    print(f"Resultados idênticos: {result1 == result2}")


def test_query_type_detection():
    """Testa detecção de tipo de query"""
    print("\n=== TESTE 6: DETECÇÃO DE TIPO ===")
    engine = QueryEngine()
    
    test_queries = [
        ("Qual o total de vendas?", "aggregation"),
        ("Agrupar por categoria", "group_by"),
        ("Mostre estatísticas", "describe"),
        ("Top 10 produtos", "top_n"),
        ("Filtrar apenas categoria A", "filter"),
        ("Ordenar por valor", "sort"),
    ]
    
    for query, expected_type in test_queries:
        detected = engine.detect_query_type(query)
        status = "[OK]" if detected == expected_type else "[FAIL]"
        print(f"{status} Query: '{query}' -> Detectado: {detected} (Esperado: {expected_type})")


if __name__ == "__main__":
    print("TESTANDO QUERY ENGINE")
    print("=" * 60)
    
    test_query_type_detection()
    test_aggregation()
    test_group_by()
    test_describe()
    test_top_n()
    test_cache()
    
    print("\n" + "=" * 60)
    print("TODOS OS TESTES CONCLUIDOS")
