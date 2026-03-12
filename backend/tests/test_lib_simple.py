import requests

base_url = "http://localhost:8000"

# Test librarian routing
payload = {
    "message": "How does The Council work?",
    "session_id": "test_lib"
}
res = requests.post(f"{base_url}/chat", json=payload)
data = res.json()
print(f"Agent: {data['agent']}")
print(f"Response: {data['response']}")
print(f"Status: {data['status']}")
