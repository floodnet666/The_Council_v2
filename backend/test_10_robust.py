import requests
import time
import os

PORTS = [8000, 8001]
FILE_PATH = r"e:\The_Council_v2\backend\uploads\Liquor_Sales.csv"

# 10 Perguntas Selecionadas (Variedade de Operações e Volume)
QUESTIONS = [
    "1. Quantos registros totais existem no arquivo de vendas de bebidas?",
    "2. Qual é o valor total de vendas ('Sale (Dollars)') gerado considerando todas as linhas?",
    "3. Quantas vendas ocorreram na cidade de 'DES MOINES'?",
    "4. Agrupe as vendas por 'City' e liste as 10 cidades que mais geraram faturamento em dólares.",
    "5. Agrupe as vendas por 'Category Name' e me mostre o Top 5 de faturamento.",
    "6. Qual condado ('County') tem a média mais cara de preço de varejo ('State Bottle Retail')?",
    "7. Mostre as estatísticas descritivas (min, max, media) de 'Sale (Dollars)'.",
    "8. Filtre vendas da cidade 'CEDAR RAPIDS' e identifique o produto ('Item Description') mais vendido (soma de garrafas).",
    "9. Filtre as vendas que ocorreram depois de 01/01/2015 e grupe por categoria, sumando o número de garrafas.",
    "10. Qual fornecedor ('Vendor Name') vendeu a maior quantidade de garrafas no total ('Bottles Sold')?"
]

def detect_port():
    for port in PORTS:
        try:
            url = f"http://localhost:{port}/"
            # Try a simple GET
            resp = requests.get(url, timeout=2)
            if resp.status_code in [200, 404]: # 404 might mean server is up but root is not defined
                print(f"[INFO] Backend detectado na porta {port}")
                return port
        except:
            pass
    return None

def main():
    port = detect_port()
    if not port:
        print("[ERRO] Nenhum backend ativo encontrado nas portas 8000 ou 8001. Abortando.")
        return

    api_url = f"http://localhost:{port}/chat"
    print("Iniciando Teste Robusto: 10 Perguntas")
    print(f"Alvo: {api_url}")
    print(f"File: {FILE_PATH}\n")

    results = []
    errors = 0

    for idx, question in enumerate(QUESTIONS):
        print(f"[{idx+1}/10] Perguntando: {question}")
        start_t = time.time()
        session = f"robust_test_q{idx+1}"
        
        payload = {
            "message": question,
            "session_id": session,
            "file_path": FILE_PATH
        }
        
        try:
            # timeout de 300s pois o dataset é grande (4.7GB) e o primeiro load_data pode demorar
            resp = requests.post(api_url, json=payload, timeout=300)
            elapsed = time.time() - start_t
            
            if resp.status_code == 200:
                data = resp.json()
                results.append({
                    "id": idx + 1,
                    "question": question,
                    "status": "sucesso",
                    "time_secs": round(elapsed, 2),
                    "response": data.get("response", "")[:100] + "..."
                })
                print(f"  -> Sucesso em {elapsed:.2f}s")
            else:
                errors += 1
                results.append({
                    "id": idx + 1,
                    "question": question,
                    "status": f"http_{resp.status_code}",
                    "time_secs": round(elapsed, 2),
                    "error_text": resp.text[:200]
                })
                print(f"  -> ERRO HTTP {resp.status_code}")
                
        except Exception as e:
            elapsed = time.time() - start_t
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
    report_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_robust_report.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Relatório de Teste Robusto (10 Perguntas)\n\n")
        f.write(f"**Total Perguntas:** {len(QUESTIONS)}\n")
        f.write(f"**Sucessos:** {len(QUESTIONS) - errors}\n")
        f.write(f"**Erros:** {errors}\n\n")
        f.write("## Detalhes\n\n")
        for res in results:
            f.write(f"### Q{res['id']}: {res['question']}\n")
            f.write(f"- Status: {res['status']}\n")
            f.write(f"- Tempo: {res['time_secs']}s\n")
            if 'response' in res:
                f.write(f"- Resposta: {res['response']}\n")
            if 'error_text' in res:
                f.write(f"- Erro: {res['error_text']}\n")
            f.write("\n")

    print(f"\n[FINALIZADO] Relatório gravado em: {report_path}")

if __name__ == "__main__":
    main()
