import requests
import json
import re
import os
import time

API_URL = "http://localhost:8001/chat"
GABARITO_PATH = "gabarito.json"
FILE_PATH = "uploads/Liquor_Sales.csv"

QUESTIONS = [
    # Nível 1: Fácil
    "Quantos registros totais existem no arquivo de vendas de bebidas?",
    "Qual a data da venda mais antiga e da mais recente?",
    "Qual é o valor total de vendas ('Sale (Dollars)') gerado considerando todas as linhas?",
    "Liste os nomes de 5 lojas únicas diferentes encontradas neste dataset.",
    "Qual é o endereço e cidade da loja com 'Store Number' 2191?",
    "Quantos condados ('County') diferentes registraram vendas?",
    "Qual é a soma total do custo das garrafas ('State Bottle Cost')?",
    "Quantos litros totais ('Volume Sold (Liters)') foram vendidos?",
    "Retorne as 5 primeiras linhas da tabela para eu ver os dados.",
    "Qual é a descrição do item ('Item Description') mais frequente ou primeiro da lista?",
    "Qual o total de itens vendidos onde a categoria é 'Vodka' ou similar?",
    "Quantas vendas ocorreram na cidade de 'DES MOINES'?",
    "Qual é a média do volume das garrafas em mililitros ('Bottle Volume (ml)')?",
    "Quantas vendas tem a loja de nome 'Hy-Vee' apenas na cidade 'WATERLOO'?",
    "Qual é o nome do fornecedor ('Vendor Name') associado ao 'Vendor Number' 260?",

    # Nível 2: Médio
    "Agrupe as vendas por 'City' e liste as 10 cidades que mais geraram faturamento em dólares.",
    "Qual fornecedor ('Vendor Name') vendeu a maior quantidade de garrafas no total ('Bottles Sold')?",
    "Qual é a loja ('Store Name') com o maior volume vendido em galões ('Volume Sold (Gallons)')?",
    "Agrupe as vendas por 'Category Name' e me mostre o Top 5 de faturamento.",
    "Qual condado ('County') tem a média mais cara de preço de varejo ('State Bottle Retail')?",
    "Em qual mês e ano ocorreram o maior número de transações separadas na base?",
    "Gere uma tabela listando a 'City' e sua soma total de litros vendidos, apenas para garrafas com volume > 1000ml.",
    "Liste as 3 lojas com o maior lucro absoluto estimado (Venda total menos Custo de garrafa x garrafas vendidas).",
    "Qual cidade tem o menor faturamento médio por registro de venda?",
    "Conte o número de vendas para cada dia da semana (segunda a domingo).",
    "Filtre as vendas que ocorreram depois de 01/01/2015 e grupe por categoria, sumando o número de garrafas.",
    "Qual 'Vendor Name' tem a maior variedade de produtos únicos ('Item Number') ofertados?",
    "Compare as vendas de Vodka e de Whiskey. Qual teve maior faturamento?",
    "Qual é o percentual aproximado do faturamento total que pertence à cidade de 'DES MOINES'?",
    "Existe alguma loja que comprou mais de 1000 garrafas em uma única transação?",
    "Mostre as estatísticas descritivas (min, max, media) de 'Sale (Dollars)'.",
    "Em média, qual é a diferença absoluta entre o preço de varejo da loja e o custo da garrafa?",
    "Filtre vendas da cidade 'CEDAR RAPIDS' e identifique o produto ('Item Description') mais vendido (soma de garrafas).",
    "Agrupe por 'Store Name' e mostre quantas Lojas diferentes têm o mesmo nome. Quais os nomes mais comuns?",
    "Qual é o mês com o maior volume em Litros da história do dataset?",

    # Nível 3 & Gráficos
    "Qual é a variação percentual de vendas (faturamento) do primeiro semestre para o segundo semestre de 2015? Calcule dinamicamente.",
    "Identifique os Top 3 fornecedores que têm o maior lucro projetado por litro vendido.",
    "Para a cidade 'DES MOINES', como a média de preço de varejo varia ao longo dos meses do ano de 2012?",
    "Descubra qual conjunto Condado/Cidade concentra os maiores outliers de preço (acima do percentil 95 ou limite superior equivalente).",
    "Calcule a correlação entre o custo da garrafa e o número de garrafas vendidas. Há uma correlação linear obvia?",
    "Crie um rank das 5 categorias menos vendidas que ainda geraram algum faturamento positivo.",
    "Verifique se o somatório do 'Bottle Volume (ml)' vezes 'Bottles Sold' bate com o 'Volume Sold (Liters)' para as primeiras 10 transações.",
    "Quais os 2 meses do ano global onde geralmente as vendas despencam (menor soma de vendas históricas conjuntas)?",
    "Liste le share do mercado (faturamento): descubra qual % a loja número 1 ocupa diante de todo o faturamento da base.",
    "Execute um agrupamento com rolling window (média móvel mensal) do faturamento total global, se o duckdb/polars permitir, caso contrário apenas agregue mensal.",
    "Gere um gráfico de barras com as 10 cidades que mais venderam garrafas?",
    "Eu quero um gráfico de pizza mostrando a proporção de vendas (em dólares) dos Top 5 Condados.",
    "Crie um gráfico de linha do faturamento total ao longo dos anos-mês (ex: Jan/2012, Fev/2012).",
    "Crie um gráfico de dispersão (scatter plot) cruzando o 'State Bottle Cost' (eixo X) e o 'State Bottle Retail' (eixo Y).",
    "Construa um gráfico de barras comparando as categorias de produto Top 8 que mais venderam garrafas totais.",
]

def load_gabarito():
    if not os.path.exists(GABARITO_PATH):
        raise FileNotFoundError(f"Falta o {GABARITO_PATH}. Rode criar_gabarito.py primeiro.")
    with open(GABARITO_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def extract_analysis_data(response_text):
    """Extrai o bloco ANALYSIS_DATA do texto da resposta"""
    try:
        match = re.search(r'ANALYSIS_DATA:\n(.*?)\n\n---', response_text, re.DOTALL)
        if match:
            return json.loads(match.group(1))
        # Fallback se split for diferente
        match = re.search(r'ANALYSIS_DATA:\n(.*)', response_text, re.DOTALL)
        if match:
             # Try strictly loading what's below
             lines = match.group(1).split("\n\n")
             return json.loads(lines[0])
    except Exception as e:
         print(f"  -> Erro ao parsear ANALYSIS_DATA: {e}")
    return None

def fuzzy_equal(a, b):
    # Comparar números com floats/linhas
    try:
        if abs(float(a) - float(b)) < 0.05:
            return True
    except:
        pass
        
    if str(a).lower().strip() == str(b).lower().strip():
        return True
        
    return a == b

def compare_results(system_data, ideal_data):
    if not system_data:
        return False
    
    sys_list = system_data.get("results") if isinstance(system_data, dict) else system_data
    ideal_list = ideal_data
    
    # Unwrapping single-value dicts to match scalars
    if isinstance(sys_list, dict) and len(sys_list) == 1 and not isinstance(ideal_list, dict):
         sys_list = list(sys_list.values())[0]
         
    if isinstance(ideal_list, dict) and len(ideal_list) == 1 and not isinstance(sys_list, dict):
         ideal_list = list(ideal_list.values())[0]
    
    if not isinstance(ideal_list, (list, dict)) and not isinstance(sys_list, (list, dict)):
         res = fuzzy_equal(sys_list, ideal_list)
         if not res:
              print(f"    [FAIL] Scalar: sys={sys_list} vs ideal={ideal_list}")
         return res
         
    if isinstance(ideal_list, list) and isinstance(sys_list, list):
         for i in range(min(len(ideal_list), len(sys_list))):
              item_i = ideal_list[i]
              item_s = sys_list[i]
              if isinstance(item_i, dict) and isinstance(item_s, dict):
                   for k, v in item_i.items():
                        if k in item_s:
                             if not fuzzy_equal(v, item_s[k]):
                                  print(f"    [FAIL] Key {k}: sys={item_s[k]} vs ideal={v}")
                                  return False
              else:
                   if not fuzzy_equal(item_i, item_s):
                        print(f"    [FAIL] Item {i}: sys={item_s} vs ideal={item_i}")
                        return False
         return True
         
    return fuzzy_equal(sys_list, ideal_list)

def main():
    print("Iniciando Comparação com Gabarito...")
    gabarito = load_gabarito()
    report = []
    
    for idx, question in enumerate(QUESTIONS):
        q_id = str(idx + 1)
        print(f"[{q_id}/50] Analisando: {question[:60]}...")
        
        payload = {
            "message": question,
            "session_id": f"compare_gabarito_q{q_id}",
            "file_path": FILE_PATH
        }
        
        try:
            resp = requests.post(API_URL, json=payload, timeout=50)
            if resp.status_code == 200:
                data = resp.json()
                text = data.get("response", "")
                sys_data = extract_analysis_data(text)
                ideal_data = gabarito.get(q_id)
                
                match = compare_results(sys_data, ideal_data)
                report.append({
                    "id": q_id,
                    "question": question,
                    "match": match,
                    "sys_data": sys_data if sys_data else "Failed parsing",
                    "ideal": ideal_data
                })
                print(f"  -> Match: {'✅ OK' if match else '❌ DIVERGENTE'}")
            else:
                print(f"  -> HTTP Erro: {resp.status_code}")
                report.append({"id": q_id, "question": question, "match": False, "ideal": gabarito.get(q_id)})
        except Exception as e:
            print(f"  -> Erro: {e}")
            report.append({"id": q_id, "question": question, "match": False, "ideal": gabarito.get(q_id)})
    
    # Gerar Relatório
    with open("comparison_report.md", "w", encoding="utf-8") as f:
        f.write("# Relatório de Comparação Determinística\n\n")
        f.write("| ID | Pergunta | Status |\n")
        f.write("| --- | --- | --- |\n")
        for r in report:
            f.write(f"| {r['id']} | {r['question']} | {'✅ MATCH' if r['match'] else '❌ DIVERGE'} |\n")
    print("\nRelatório salvo em comparison_report.md")

if __name__ == "__main__":
    main()
