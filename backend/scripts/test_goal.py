import requests
import json

url = "http://127.0.0.1:8000/chat"
payload = {
    "message": "qual o total de vendas do ultimo semestre?",
    "session_id": "test_goal",
    "file_path": "uploads/online_shoppers.csv"
}

print("Iniciando requisição de teste para o Backend...")
try:
    response = requests.post(url, json=payload, timeout=60)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("Resposta do Backend:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        if "error" in data.get("status", "") or "timeout" in data.get("status", ""):
            print("FALHA LÓGICA NO BACKEND.")
            exit(1)
        else:
            print("SUCESSO: A query foi resolvida sem erros estruturais.")
            exit(0)
    else:
        print(f"Erro HTTP: {response.text}")
        exit(1)
except Exception as e:
    print(f"Erro de conexão: {e}")
    exit(1)
