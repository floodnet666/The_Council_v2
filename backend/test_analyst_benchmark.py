import asyncio
import os
import sys

# Adiciona E:\The_Council_v2\backend ao PATH
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from engines.data_engine import DataEngine
from agents.analyst_agent import AnalystAgent

async def test_queries():
    # Cria os agentes
    data_engine = DataEngine()
    analyst = AnalystAgent(data_engine=data_engine)
    
    # Caminho do Dataset Online Shoppers
    dataset_path = r"C:\Users\thiag\Downloads\online_shoppers.csv"
    
    if not os.path.exists(dataset_path):
        print(f"Dataset não encontrado em: {dataset_path}")
        return

    print(f"Loading dataset: {dataset_path}")
    data_engine.load_data(dataset_path)

    # Dicionário de Queries por Nível de Dificuldade
    benchmarks = {
        "EASY (Agregações Básicas / Filtros Diretos)": [
            "1. Qual a média da taxa de rejeição (BounceRates)?",
            "2. Qual o total de receita (Revenue=True)?",
            "3. Quantos visitantes únicos (VisitorType='New_Visitor') existem?",
            "4. Qual o maior valor de PageValues registrado?",
            "5. Quantas visitas ocorreram em finais de semana (Weekend=True)?",
            "6. Qual a média de duração administrativa (Administrative_Duration)?",
            "7. Qual o menor tempo gasto em páginas Informativas (Informational_Duration)?"
        ],
        "MEDIUM (Group By, Filtros combinados, Sorting)": [
            "8. Qual o sistema operacional (OperatingSystems) mais comum entre os visitantes?",
            "9. Quantas visitas foram registradas para cada região (Region)?",
            "10. Qual a taxa de rejeição (BounceRates) média por tipo de visitante (VisitorType)?",
            "11. Qual o total de PageValues gerado no mês de 'May'?",
            "12. Qual o navegador (Browser) com a menor taxa de saída (ExitRates) média?",
            "13. Quais os 3 maiores valores de ProductRelated_Duration agrupados por mês?",
            "14. Qual o percentual de conversão (Revenue=True) para visitantes retornando (Returning_Visitor)?"
        ],
        "HARD (Múltiplos filtros, Séries Temporais, Correlação)": [
            "15. Qual o mês com maior média de PageValues para visitantes que geraram receita (Revenue=True)?",
            "16. Existe correlação entre BounceRates e ExitRates?",
            "17. Para os visitantes do sistema operacional 2, qual a região com mais visitas em Maio ('May')?",
            "18. Qual o tipo de tráfego (TrafficType) com maior tempo de retenção (ProductRelated_Duration) que também gerou receita?",
            "19. Qual o dia especial (SpecialDay) com maior pico de acessos nos finais de semana?",
            "20. Qual a soma total de ProductRelated_Duration para visitas do Browser 1 no mês de 'Nov' que não geraram receita (Revenue=False)?"
        ]
    }

    output_path = "backend/benchmark_results_20.txt"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("=== BENCHMARK DE DESEMPENHO - ANALYST AGENT (20 QUERIES) ===\n\n")

        for level, queries in benchmarks.items():
            f.write(f"\n{'='*20} {level} {'='*20}\n")
            print(f"Iniciando nível: {level}")
            
            for query in queries:
                f.write(f"\n--- QUERY: '{query}' ---\n")
                print(f"Executando: {query}")
                try:
                    response = await analyst.run(query, active_file=dataset_path)
                    f.write(f"\n[RESPOSTA]:\n{response}\n")
                except Exception as e:
                    f.write(f"\n[ERRO NA EXECUÇÃO]: {str(e)}\n")
                f.write("-" * 40 + "\n")

    print(f"\nBenchmark completo. Resultados salvos em: {output_path}")

if __name__ == "__main__":
    asyncio.run(test_queries())
