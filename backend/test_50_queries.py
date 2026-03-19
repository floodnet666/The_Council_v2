import requests
import time
import json
import os

API_URL = "http://localhost:8001/chat"
FILE_PATH = r"e:\The_Council_v2\backend\uploads\Liquor_Sales.csv"

QUESTIONS = [
    # Nível 1: Fácil (Filtros Simples, Contagens Básico, Valores Únicos) - 15 perguntas
    "1. Quantos registros totais existem no arquivo de vendas de bebidas?",
    "2. Qual a data da venda mais antiga e da mais recente?",
    "3. Qual é o valor total de vendas ('Sale (Dollars)') gerado considerando todas as linhas?",
    "4. Liste os nomes de 5 lojas únicas diferentes encontradas neste dataset.",
    "5. Qual é o endereço e cidade da loja com 'Store Number' 2191?",
    "6. Quantos condados ('County') diferentes registraram vendas?",
    "7. Qual é a soma total do custo das garrafas ('State Bottle Cost')?",
    "8. Quantos litros totais ('Volume Sold (Liters)') foram vendidos?",
    "9. Retorne as 5 primeiras linhas da tabela para eu ver os dados.",
    "10. Qual é a descrição do item ('Item Description') mais frequente ou primeiro da lista?",
    "11. Qual o total de itens vendidos onde a categoria é 'Vodka' ou similar?",
    "12. Quantas vendas ocorreram na cidade de 'DES MOINES'?",
    "13. Qual é a média do volume das garrafas em mililitros ('Bottle Volume (ml)')?",
    "14. Quantas vendas tem a loja de nome 'Hy-Vee' apenas na cidade 'WATERLOO'?",
    "15. Qual é o nome do fornecedor ('Vendor Name') associado ao 'Vendor Number' 260?",

    # Nível 2: Médio (Agrupamentos, Ordenações, Condições Múltiplas) - 20 perguntas
    "16. Agrupe as vendas por 'City' e liste as 10 cidades que mais geraram faturamento em dólares.",
    "17. Qual fornecedor ('Vendor Name') vendeu a maior quantidade de garrafas no total ('Bottles Sold')?",
    "18. Qual é a loja ('Store Name') com o maior volume vendido em galões ('Volume Sold (Gallons)')?",
    "19. Agrupe as vendas por 'Category Name' e me mostre o Top 5 de faturamento.",
    "20. Qual condado ('County') tem a média mais cara de preço de varejo ('State Bottle Retail')?",
    "21. Em qual mês e ano ocorreram o maior número de transações separadas na base?",
    "22. Gere uma tabela listando a 'City' e sua soma total de litros vendidos, apenas para garrafas com volume > 1000ml.",
    "23. Liste as 3 lojas com o maior lucro absoluto estimado (Venda total menos Custo de garrafa x garrafas vendidas).",
    "24. Qual cidade tem o menor faturamento médio por registro de venda?",
    "25. Conte o número de vendas para cada dia da semana (segunda a domingo).",
    "26. Filtre as vendas que ocorreram depois de 01/01/2015 e grupe por categoria, sumando o número de garrafas.",
    "27. Qual 'Vendor Name' tem a maior variedade de produtos únicos ('Item Number') ofertados?",
    "28. Compare as vendas de Vodka e de Whiskey. Qual teve maior faturamento?",
    "29. Qual é o percentual aproximado do faturamento total que pertence à cidade de 'DES MOINES'?",
    "30. Existe alguma loja que comprou mais de 1000 garrafas em uma única transação?",
    "31. Mostre as estatísticas descritivas (min, max, media) de 'Sale (Dollars)'.",
    "32. Em média, qual é a diferença absoluta entre o preço de varejo da loja e o custo da garrafa?",
    "33. Filtre vendas da cidade 'CEDAR RAPIDS' e identifique o produto ('Item Description') mais vendido (soma de garrafas).",
    "34. Agrupe por 'Store Name' e mostre quantas Lojas diferentes têm o mesmo nome. Quais os nomes mais comuns?",
    "35. Qual é o mês com o maior volume em Litros da história do dataset?",

    # Nível 3: Difícil (Análises Temporais e Heurísticas Analíticas Complexas) - 10 perguntas
    "36. Qual é a variação percentual de vendas (faturamento) do primeiro semestre para o segundo semestre de 2015? Calcule dinamicamente.",
    "37. Identifique os Top 3 fornecedores que têm o maior lucro projetado por litro vendido.",
    "38. Para a cidade 'DES MOINES', como a média de preço de varejo varia ao longo dos meses do ano de 2012?",
    "39. Descubra qual conjunto Condado/Cidade concentra os maiores outliers de preço (acima do percentil 95 ou limite superior equivalente).",
    "40. Calcule a correlação entre o custo da garrafa e o número de garrafas vendidas. Há uma correlação linear obvia?",
    "41. Crie um rank das 5 categorias menos vendidas que ainda geraram algum faturamento positivo.",
    "42. Verifique se o somatório do 'Bottle Volume (ml)' vezes 'Bottles Sold' bate com o 'Volume Sold (Liters)' para as primeiras 10 transações.",
    "43. Quais os 2 meses do ano global onde geralmente as vendas despencam (menor soma de vendas históricas conjuntas)?",
    "44. Liste o share do mercado (faturamento): descubra qual % a loja número 1 ocupa diante de todo o faturamento da base.",
    "45. Execute um agrupamento com rolling window (média móvel mensal) do faturamento total global, se o duckdb/polars permitir, caso contrário apenas agregue mensal.",

    # Gráficos (Esses fecham o total de 50) - 5 perguntas de gráficos
    "46. Pode gerar um gráfico de barras com as 10 cidades que mais venderam garrafas?",
    "47. Eu quero um gráfico de pizza mostrando a proporção de vendas (em dólares) dos Top 5 Condados.",
    "48. Crie um gráfico de linha do faturamento total ao longo dos anos-mês (ex: Jan/2012, Fev/2012).",
    "49. Crie um gráfico de dispersão (scatter plot) cruzando o 'State Bottle Cost' (eixo X) e o 'State Bottle Retail' (eixo Y).",
    "50. Construa um gráfico de barras comparando as categorias de produto Top 8 que mais venderam garrafas totais.",
]

def main():
    print(f"Iniciando Teste Automático: 50 Perguntas ({len(QUESTIONS)} total)")
    print(f"Alvo: {API_URL}")
    print(f"File: {FILE_PATH}")
    
    results = []
    total_time = 0
    errors = 0
    
    for idx, question in enumerate(QUESTIONS):
        if idx < 25:
            continue
        print(f"[{idx+1}/{len(QUESTIONS)}] Perguntando: {question[:80]}...")
        start_t = time.time()
        
        current_session = f"stress_test_50_q{idx+1}"
        
        payload = {
            "message": question,
            "session_id": current_session,
            "file_path": FILE_PATH
        }
        
        try:
            resp = requests.post(API_URL, json=payload, timeout=300)
            elapsed = time.time() - start_t
            total_time += elapsed
            
            if resp.status_code == 200:
                data = resp.json()
                results.append({
                    "id": idx + 1,
                    "question": question,
                    "status": "sucesso",
                    "time_secs": round(elapsed, 2),
                    "response": data.get("response", "")[:200] + "..." if len(data.get("response", "")) > 200 else data.get("response", ""),
                    "agent": data.get("agent", "")
                })
                print(f"  -> Sucesso em {elapsed:.2f}s | Agente: {data.get('agent', '')}")
            else:
                errors += 1
                results.append({
                    "id": idx + 1,
                    "question": question,
                    "status": "http_erro",
                    "time_secs": round(elapsed, 2),
                    "error_text": resp.text
                })
                print(f"  -> ERRO HTTP {resp.status_code}")
                
        except Exception as e:
            elapsed = time.time() - start_t
            total_time += elapsed
            errors += 1
            print(f"  -> ERRO CRITICO: {str(e)}")
            results.append({
                "id": idx + 1,
                "question": question,
                "status": "erro_conexao",
                "time_secs": round(elapsed, 2),
                "error_text": str(e)
            })

    # Save Markdown report
    report_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_50_report.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Relatório de Stress Test: The Council v2\n\n")
        f.write(f"**Total Perguntas:** {len(QUESTIONS)}\n")
        f.write(f"**Sucessos:** {len(QUESTIONS) - errors}\n")
        f.write(f"**Erros:** {errors}\n")
        f.write(f"**Tempo Total Execução:** {total_time:.2f} segundos\n")
        f.write(f"**Duração Média por Pergunta:** {total_time/len(QUESTIONS):.2f} segundos\n\n")
        
        f.write("## Detalhamento\n\n")
        for res in results:
            f.write(f"### Q{res['id']}: {res['question']}\n")
            f.write(f"- Status: {res['status']}\n")
            f.write(f"- Tempo: {res['time_secs']}s\n")
            if 'agent' in res:
                f.write(f"- Agente: {res['agent']}\n")
            if 'response' in res:
                f.write(f"- Resposta: {res['response'].strip().replace(chr(10), ' ')}\n")
            if 'error_text' in res:
                f.write(f"- Erro: {res['error_text']}\n")
            f.write("\n")
            
    # Save JSON snapshot
    json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_50_results.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n[FINALIZADO] Relatório gravado em: {report_path}")
    print(f"Total Tempo: {total_time:.2f}s | Erros: {errors}")

if __name__ == "__main__":
    main()
