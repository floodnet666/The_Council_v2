import os
import json
import time
import uuid
import polars as pl
from fastapi.testclient import TestClient

os.environ["OLLAMA_MODEL"] = "hf.co/mradermacher/gemma-4-E2B-it-uncensored-GGUF:Q8_0"

import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from main import app

QUESTIONS = [
    "Qual a média de dias entre a data de pedido e a data de entrega?",
    "Qual o lucro líquido total (valor bruto menos desconto e frete) por categoria?",
    "Quantos pedidos existem agrupados por status_pedido?",
    "Qual a soma do valor bruto agrupada por produto?",
    "Qual a média de valor de frete para pedidos cancelados?",
    "Qual é o desconto médio concedido por produto?",
    "Quantas entregas pendentes (delivery_date nulo) temos por categoria?",
    "Qual a soma do valor bruto agrupado por categoria?",
    "Qual o valor total de frete pago agrupado por produto?",
    "Qual a diferença média em dias entre o envio (ship_date) e a entrega (delivery_date)?",
    "Liste a quantidade de registros agrupados por categoria.",
    "Qual a média de valor bruto dos pedidos em Processing?",
    "Qual o lucro líquido médio dos pedidos Delivered?",
    "Qual a soma dos descontos para os pedidos com status Shipped?",
    "Quais são os totais de vendas (valor bruto) agrupados por status do pedido?",
    "Quantos dias em média um pedido passa aguardando envio (ship_date - order_date)?",
    "Qual a soma de lucro líquido por status do pedido?",
    "Qual a soma de frete agrupada por status_pedido?",
    "Mostre o valor de frete médio por categoria.",
    "Qual o total líquido (bruto - desconto) gerado por cada produto?",
    "Qual a média de valor líquido por categoria?",
    "Qual é a soma do valor de frete por categoria de produto?",
    "Mostre o total de descontos dados por status de pedido.",
    "Qual é a soma do valor bruto, frete e desconto por categoria?",
    "Qual o total de pedidos Cancelled por categoria?",
    "Qual o lucro líquido total de todo o dataset?",
    "Qual a média de valor de desconto cobrado por categoria?",
    "Qual o total de valor bruto menos desconto agrupado por produto?",
    "Qual a média de frete para pedidos com status Delivered?",
    "Mostre a contagem total de pedidos agrupados por produto."
]

def run_benchmark_iteration(client, file_path, iteration_name):
    results = {}
    print(f"\n--- INICIANDO ITERAÇÃO: {iteration_name} ---")
    for i, q in enumerate(QUESTIONS):
        print(f"[{iteration_name}] Processando Q{i+1}/30: {q}")
        session_id = f"bench_{iteration_name}_q{i}"
        
        payload = {
            "message": q,
            "session_id": session_id,
            "file_path": file_path
        }
        
        start_time = time.time()
        try:
            response = client.post("/chat", json=payload)
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                results[f"Q{i+1}"] = {
                    "query": q,
                    "status": data.get("status"),
                    "visual_data": data.get("visual_data"),
                    "response": data.get("response"),
                    "time_seconds": round(elapsed, 2)
                }
            else:
                results[f"Q{i+1}"] = {
                    "query": q,
                    "status": "error",
                    "error": response.text,
                    "time_seconds": round(elapsed, 2)
                }
        except Exception as e:
            elapsed = time.time() - start_time
            results[f"Q{i+1}"] = {
                "query": q,
                "status": "exception",
                "error": str(e),
                "time_seconds": round(elapsed, 2)
            }
            
    with open(f"bench_{iteration_name}.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)
        
    return results

def compare_results(res1, res2):
    print("\n--- COMPARANDO AS DUAS EXECUÇÕES (DETERMINISMO) ---")
    divergences = 0
    for i in range(1, 31):
        key = f"Q{i}"
        r1 = res1.get(key, {})
        r2 = res2.get(key, {})
        
        status1 = r1.get("status")
        status2 = r2.get("status")
        
        data1 = r1.get("visual_data")
        data2 = r2.get("visual_data")
        
        if status1 != status2:
            print(f"[{key}] DIVERGÊNCIA DE STATUS: Run1={status1} | Run2={status2}")
            divergences += 1
            continue
            
        if data1 != data2:
            print(f"[{key}] DIVERGÊNCIA DE DADOS:")
            print(f"  Run 1: {data1}")
            print(f"  Run 2: {data2}")
            divergences += 1
        else:
            print(f"[{key}] EXACT MATCH (Determinismo Comprovado).")
            
    if divergences == 0:
        print("\n[SUCESSO] 100% DE DETERMINISMO! Todas as 30 respostas retornaram valores rigorosamente idênticos nas duas iterações.")
    else:
        print(f"\n[FALHA] Encontradas {divergences} divergências matemáticas ou estruturais nas execuções.")

def main():
    test_filename = os.path.join(os.path.dirname(__file__), "../../tests/datasets/vendas_complexas_100k.csv")
    
    with TestClient(app) as client:
        print(f"Fazendo upload de: {test_filename}")
        with open(test_filename, "rb") as f:
            upload_res = client.post("/upload", files={"file": ("vendas_complexas_100k.csv", f, "text/csv")})
        
        file_path = upload_res.json()["path"]
        
        res1 = run_benchmark_iteration(client, file_path, "RUN_1")
        res2 = run_benchmark_iteration(client, file_path, "RUN_2")
        
        compare_results(res1, res2)

if __name__ == "__main__":
    main()
