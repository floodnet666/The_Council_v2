import os
import pytest
import polars as pl
from engines.data_engine import DataEngine

# Caminho do dataset gerado
DATASET_PATH = os.path.join(os.path.dirname(__file__), "../../tests/datasets/vendas_complexas_100k.csv")

@pytest.fixture(scope="module")
def engine():
    assert os.path.exists(DATASET_PATH), f"Dataset não encontrado: {DATASET_PATH}"
    DataEngine._instance = None
    eng = DataEngine()
    eng.load_data(DATASET_PATH)
    return eng

def test_sql_schema_inference(engine):
    """
    Testa se o DataEngine converteu múltiplas colunas de string vazia em Datetime com Nulos.
    """
    schema = engine.df.collect_schema()
    assert schema["order_date"] in [pl.Datetime, pl.Date], "order_date falhou no parser."
    assert schema["ship_date"] in [pl.Datetime, pl.Date], "ship_date falhou no parser. Pode não ter lidado bem com strings nulas."
    assert schema["delivery_date"] in [pl.Datetime, pl.Date], "delivery_date falhou no parser."

def test_sql_date_math(engine):
    """
    Testa a capacidade do SQLContext de subtrair datas (Data delivery - Data Order).
    O Polars SQL suporta DATEDIFF ou subtração direta de colunas datetime?
    """
    # Hipótese 1: Subtração direta ANSI SQL (delivery_date - order_date)
    query_direct = "SELECT AVG(delivery_date - order_date) AS media_dias FROM data WHERE status_pedido = 'Delivered'"
    res = engine.execute_sql(query_direct)
    
    # Se der erro, falhará o teste. Queremos ver o erro.
    assert "error" not in res, f"Polars SQL não suporta subtração direta de datas: {res.get('error')}"
    
    # Verifica o tipo de retorno
    media_raw = res["data"][0]["media_dias"]
    assert media_raw is not None, "Média de dias retornou nula."
    print(f"Sucesso Subtração Direta! Retornou: {media_raw}")

def test_sql_case_when_nulls(engine):
    """
    Testa manipulação de Nulos e lógica condicional.
    """
    query = """
    SELECT 
        status_pedido,
        SUM(CASE WHEN delivery_date IS NULL THEN 1 ELSE 0 END) as entregas_pendentes
    FROM data
    GROUP BY status_pedido
    ORDER BY entregas_pendentes DESC
    """
    res = engine.execute_sql(query)
    
    assert "error" not in res, f"Erro no CASE WHEN / IS NULL: {res.get('error')}"
    
    # Valida se os cancelados e em processamento tem entregas pendentes
    data = res["data"]
    assert len(data) > 0
    print(f"Sucesso CASE WHEN Nulls: {data}")

def test_sql_business_logic(engine):
    """
    Testa aritmética entre 3 colunas de negócio (Bruto - Desconto - Frete = Líquido).
    """
    query = """
    SELECT 
        AVG(valor_bruto - valor_desconto - valor_frete) as media_lucro_liquido
    FROM data
    WHERE status_pedido = 'Delivered'
    """
    res = engine.execute_sql(query)
    assert "error" not in res, f"Erro na Aritmética de negócio: {res.get('error')}"
    
    liquido = res["data"][0]["media_lucro_liquido"]
    assert liquido is not None
    assert isinstance(liquido, float)
    print(f"Sucesso Lógica de Negócio: {liquido}")
