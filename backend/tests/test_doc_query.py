import requests

base_url = "http://localhost:8000"

# Test with explicit documentation query
payload = {
    "message": "Preciso de ajuda com a documentação do Polars sobre group by",
    "session_id": "test_kb2"
}
res = requests.post(f"{base_url}/chat", json=payload)
data = res.json()

print(f"Agent: {data['agent']}")
print(f"\nFull Response:\n{data['response']}")
