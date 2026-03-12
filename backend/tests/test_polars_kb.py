import requests

base_url = "http://localhost:8000"

print("=" * 60)
print("Testing LibrarianAgent with Polars Knowledge Base")
print("=" * 60)

# Test 1: Polars query
print("\n1. Testing Polars query...")
payload = {
    "message": "Como fazer group by no Polars?",
    "session_id": "test_polars_kb"
}
res = requests.post(f"{base_url}/chat", json=payload)
data = res.json()

print(f"Agent: {data['agent']}")
print(f"Response: {data['response'][:300]}...")

# Test 2: Another Polars query
print("\n2. Testing another Polars query...")
payload = {
    "message": "Como filtrar dados no Polars?",
    "session_id": "test_polars_kb"
}
res = requests.post(f"{base_url}/chat", json=payload)
data = res.json()

print(f"Agent: {data['agent']}")
print(f"Response: {data['response'][:300]}...")

# Test 3: System query (should still work)
print("\n3. Testing system query...")
payload = {
    "message": "O que é The Council?",
    "session_id": "test_polars_kb"
}
res = requests.post(f"{base_url}/chat", json=payload)
data = res.json()

print(f"Agent: {data['agent']}")
print(f"Response: {data['response'][:200]}...")

print("\n" + "=" * 60)
print("✓ Tests completed")
print("=" * 60)
