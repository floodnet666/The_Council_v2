"""
Teste End-to-End do AnalystAgent com QueryEngine
Simula interacao completa: upload de dados -> query analitica -> resposta
"""
import asyncio
import polars as pl
from engines.data_engine import DataEngine
from engines.query_engine import QueryEngine
from agents.analyst_agent import AnalystAgent
import json


async def test_analyst_with_query_engine():
    """Testa fluxo completo do AnalystAgent"""
    
    print("=" * 70)
    print("TESTE END-TO-END: AnalystAgent + QueryEngine")
    print("=" * 70)
    
    # 1. Criar dados de exemplo
    print("\n[1] Criando dataset de exemplo...")
    df = pl.DataFrame({
        "categoria": ["Eletronicos", "Roupas", "Eletronicos", "Alimentos", 
                      "Roupas", "Eletronicos", "Alimentos", "Roupas"],
        "valor": [1500, 250, 2000, 180, 300, 1200, 220, 400],
        "quantidade": [2, 5, 1, 10, 3, 2, 8, 4],
        "mes": ["Jan", "Jan", "Fev", "Fev", "Mar", "Mar", "Abr", "Abr"]
    })
    
    # Salvar como CSV
    csv_path = "test_vendas.csv"
    df.write_csv(csv_path)
    print(f"Dataset salvo em: {csv_path}")
    print(f"Registros: {len(df)}")
    print(f"Colunas: {df.columns}")
    
    # 2. Inicializar componentes
    print("\n[2] Inicializando componentes...")
    data_engine = DataEngine()
    analyst = AnalystAgent(data_engine)
    print("AnalystAgent inicializado com QueryEngine")
    
    # 3. Carregar dados
    print("\n[3] Carregando dados...")
    success = data_engine.load_data(csv_path)
    if success:
        print("Dados carregados com sucesso!")
    else:
        print("ERRO ao carregar dados")
        return
    
    # 4. Testar queries analiticas
    print("\n" + "=" * 70)
    print("TESTES DE QUERIES ANALITICAS")
    print("=" * 70)
    
    queries = [
        "Qual o total de valor vendido?",
        "Mostre o total de vendas por categoria",
        "Quais sao as estatisticas do dataset?",
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n--- TESTE {i} ---")
        print(f"Query: {query}")
        print("-" * 70)
        
        response = await analyst.run(query, active_file=csv_path)
        
        # Verifica se tem ANALYSIS_DATA
        if "ANALYSIS_DATA:" in response:
            parts = response.split("---")
            data_part = parts[0].replace("ANALYSIS_DATA:", "").strip()
            
            print("\n[DADOS ESTRUTURADOS]")
            try:
                data = json.loads(data_part)
                print(json.dumps(data, indent=2, ensure_ascii=False))
            except:
                print(data_part)
            
            if len(parts) > 1:
                print("\n[EXPLICACAO DO LLM]")
                print(parts[1].strip())
        else:
            print("\n[RESPOSTA]")
            print(response)
        
        print("\n" + "=" * 70)
    
    # 5. Testar query exploratoria
    print("\nTESTE DE QUERY EXPLORATORIA")
    print("=" * 70)
    
    query = "O que voce pode me dizer sobre esses dados?"
    print(f"Query: {query}")
    print("-" * 70)
    
    response = await analyst.run(query, active_file=csv_path)
    print("\n[RESPOSTA]")
    print(response)
    
    print("\n" + "=" * 70)
    print("TODOS OS TESTES CONCLUIDOS")
    print("=" * 70)
    
    # Limpar arquivo de teste
    import os
    os.remove(csv_path)
    print(f"\nArquivo de teste removido: {csv_path}")


if __name__ == "__main__":
    asyncio.run(test_analyst_with_query_engine())
