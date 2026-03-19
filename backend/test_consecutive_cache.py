import requests
import time

def query(q, sess):
    url = "http://localhost:8001/chat"
    payload = {"message": q, "session_id": sess}
    print(f"\nSending: {q} (Session: {sess})...")
    start = time.time()
    try:
        resp = requests.post(url, json=payload, timeout=45)
        elapsed = time.time() - start
        print(f"✅ Elapsed: {elapsed:.2f}s | Status: {resp.status_code}")
        if resp.status_code == 200:
            print(f"Response: {str(resp.json().get('response', 'No response'))[:200]}...")
    except Exception as e:
         print(f"❌ Error: {e}")

if __name__ == "__main__":
    # Q26 will Warmup cache (Session isolation means it must load FROM singleton CACHE on consecutive calls)
    query("26. Filtre as vendas que ocorreram depois de 01/01/2015 e grupe por categoria.", "sess_consec_1")
    # Q27 must be immediate
    query("27. Qual 'Vendor Name' tem a maior variedade de produtos únicos ofertados?", "sess_consec_2")
