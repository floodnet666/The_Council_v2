import requests
import time

def test_q46():
    url = "http://127.0.0.1:8001/chat"
    
    payload = {
        "message": "Gere um gráfico de barras das 10 cidades com maior venda de garrafas ('Bottles Sold').",
        "session_id": "test_chart_q46",
        "file_path": "uploads/Liquor_Sales.csv"
    }
    
    print("Sending Q46...")
    start_time = time.time()
    try:
        response = requests.post(url, json=payload, timeout=50)
        elapsed = time.time() - start_time
        print(f"✅ Elapsed: {elapsed:.2f}s | Status: {response.status_code}")
        print("\nResponse Preview:")
        print(response.json().get("response")[:1000])
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_q46()
