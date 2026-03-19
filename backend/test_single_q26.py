import requests
import time
import json

url = "http://localhost:8001/chat"
payload = {
    "message": "26. Filtre as vendas que ocorreram depois de 01/01/2015 e grupe por categoria, sumando o número de garrafas.",
    "session_id": "test_q26_final"
}

print(f"Sending request to {url}...")
start = time.time()
try:
    resp = requests.post(url, json=payload, timeout=40)
    elapsed = time.time() - start
    print(f"\n✅ Finished in {elapsed:.2f}s")
    print(f"Status Code: {resp.status_code}")
    
    if resp.status_code == 200:
        data = resp.json()
        print("\n--- Response ---")
        print(data.get("response", "No response text"))
        print("\n--- Agent ---")
        print(data.get("agent", "unknown"))
    else:
        print(f"Error: {resp.text}")
        
except requests.exceptions.Timeout:
    print(f"❌ Client Timeout reached after {time.time() - start:.2f}s")
except Exception as e:
    print(f"❌ Error: {e}")
