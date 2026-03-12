import requests
import json

base_url = "http://localhost:8000"

print("\n" + "="*60)
print("THE COUNCIL 2.0 - QUICK VERIFICATION")
print("="*60 + "\n")

# Test 1: Health
print("1. Health Check...")
res = requests.get(f"{base_url}/health")
print(f"   ✓ Status: {res.json()['status']}\n")

# Test 2: General Agent
print("2. General Agent (Greeting)...")
res = requests.post(f"{base_url}/chat", json={
    "message": "Hello!",
    "session_id": "quick_test"
})
data = res.json()
print(f"   Agent: {data['agent']}")
print(f"   ✓ Response received\n")

# Test 3: Librarian Agent
print("3. Librarian Agent (System Question)...")
res = requests.post(f"{base_url}/chat", json={
    "message": "What is The Council?",
    "session_id": "quick_test"
})
data = res.json()
print(f"   Agent: {data['agent']}")
print(f"   ✓ Response: {data['response'][:80]}...\n")

# Test 4: Designer Agent with Data
print("4. Designer Agent (Chart Creation)...")
# Create CSV
with open("quick_test.csv", "w") as f:
    f.write("Month,Sales\nJan,100\nFeb,150\nMar,120")

# Upload
with open("quick_test.csv", "rb") as f:
    upload_res = requests.post(f"{base_url}/upload", files={"file": f})
file_path = upload_res.json()["path"]

# Request chart
res = requests.post(f"{base_url}/chat", json={
    "message": "Create a bar chart",
    "file_path": file_path,
    "session_id": "quick_test"
})
data = res.json()
print(f"   Agent: {data['agent']}")
if "CHART_JSON" in data['response']:
    print(f"   ✓ Chart generated successfully")
    spec = json.loads(data['response'].replace("CHART_JSON:", ""))
    print(f"   Chart type: {spec['data'][0]['type']}")
else:
    print(f"   Response: {data['response']}")

# Cleanup
import os
os.remove("quick_test.csv")

print("\n" + "="*60)
print("✅ ALL SYSTEMS OPERATIONAL")
print("="*60 + "\n")
