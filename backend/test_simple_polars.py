import requests

base_url = "http://localhost:8000"

# Test Polars query
payload = {
    "message": "Como fazer group by no Polars?",
    "session_id": "test_kb"
}
res = requests.post(f"{base_url}/chat", json=payload)
data = res.json()

print(f"Agent: {data['agent']}")
print(f"\nFull Response:\n{data['response']}")
print(f"\nStatus: {data['status']}")
