import os
import time
import pytest
import polars as pl
from engines.data_engine import DataEngine

# Caminho do dataset gerado
DATASET_PATH = os.path.join(os.path.dirname(__file__), "../../tests/datasets/vendas_1M.csv")

@pytest.fixture(scope="module")
def engine():
    # Garante que o arquivo existe antes de rodar
    assert os.path.exists(DATASET_PATH), f"Dataset de teste não encontrado: {DATASET_PATH}"
    # Reseta o singleton para os testes
    DataEngine._instance = None
    eng = DataEngine()
    return eng

def test_etl_load_performance(engine):
    """
    Teste A: Verifica a performance de I/O do Polars ao carregar 1 Milhão de linhas.
    Deve ser sub-segundo (ou muito próximo, tolerância < 2.0s).
    """
    start_time = time.time()
    engine.load_data(DATASET_PATH)
    elapsed = time.time() - start_time
    
    # Gravar log de benchmark
    log_dir = os.path.join(os.path.dirname(__file__), "../../tests/logs")
    os.makedirs(log_dir, exist_ok=True)
    with open(os.path.join(log_dir, "etl_benchmark.log"), "a") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Load 1M rows: {elapsed:.4f}s\n")
        
    assert elapsed < 2.0, f"Tempo de carregamento inaceitável: {elapsed} segundos."
    assert engine.df is not None, "DataEngine LazyFrame is None após o load."

def test_etl_sanity_check(engine):
    """
    Teste C: Verifica se o Polars enxergou exatamente 1 milhão de linhas e 7 colunas.
    """
    # Materializa a contagem via collect()
    df_collected = engine.df.collect()
    assert df_collected.height == 1000000, f"Contagem de linhas falhou: {df_collected.height}"
    assert df_collected.width == 11, f"Contagem de colunas falhou (Esperado 7 originais + 4 derivadas): {df_collected.width}"

def test_etl_schema_inference(engine):
    """
    Teste B: Valida se a engine aplica tipos corretos.
    O critério vital é que data_venda deve ser pl.Datetime ou pl.Date, e não pl.Utf8.
    """
    schema = engine.df.collect_schema()
    
    # Print schema for debugging
    print("\nSCHEMA INFERIDO:\n", schema)
    
    assert schema["quantidade"] in [pl.Int64, pl.Int32], f"Tipo de quantidade incorreto: {schema['quantidade']}"
    assert schema["preco_unitario"] in [pl.Float64, pl.Float32], f"Tipo de preco incorreto: {schema['preco_unitario']}"
    assert schema["valor_total_venda"] in [pl.Float64, pl.Float32], f"Tipo de valor_total incorreto: {schema['valor_total_venda']}"
    
    # Teste Falho Intencional (Red Phase): A engine nativamente leria isso como String (Utf8).
    # O teste exige que o DataEngine já tenha tratado para Datetime!
    assert schema["data_venda"] in [pl.Datetime, pl.Date], f"Falha de Parsing Cronológico: data_venda está como {schema['data_venda']}, mas deveria ser Datetime."

def test_etl_temporal_manipulation(engine):
    """
    Teste D: Verifica manipulação cronológica nativa exigindo agrupamento por:
    - Mês
    - Dia da Semana (1-7)
    - Semestre (via lógica baseada no mês)
    """
    df = engine.df
    
    # 1. Dia da semana
    q_weekday = df.group_by(pl.col("data_venda").dt.weekday().alias("weekday")).agg(
        pl.col("valor_total_venda").sum().alias("total_vendas")
    ).sort("total_vendas", descending=True).collect()
    
    melhor_dia = q_weekday["weekday"][0]
    assert melhor_dia in [1, 2, 3, 4, 5, 6, 7], "Dia da semana inválido ou Nulo."
    
    # 2. Semestre
    q_semester = df.with_columns(
        ((pl.col("data_venda").dt.month() - 1) // 6 + 1).alias("semestre")
    ).group_by("semestre").agg(
        pl.col("valor_total_venda").sum().alias("total_vendas")
    ).sort("total_vendas", descending=True).collect()
    
    melhor_semestre = q_semester["semestre"][0]
    pior_semestre = q_semester["semestre"][-1]
    
    assert melhor_semestre in [1, 2], "Semestre inválido."
    assert pior_semestre in [1, 2], "Semestre inválido."
