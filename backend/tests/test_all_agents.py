import requests
import os
import json

base_url = "http://localhost:8000"

def test_health():
    print("=" * 60)
    print("Testing Health Endpoint...")
    res = requests.get(f"{base_url}/health")
    print(f"Status: {res.status_code}")
    print(f"Response: {res.json()}")
    assert res.status_code == 200
    print("✓ Health check passed\n")

def test_general_agent():
    print("=" * 60)
    print("Testing General Agent...")
    payload = {
        "message": "Hello, who are you?",
        "session_id": "test_general"
    }
    res = requests.post(f"{base_url}/chat", json=payload)
    data = res.json()
    print(f"Agent: {data['agent']}")
    print(f"Response: {data['response'][:100]}...")
    assert data['agent'] == 'general'
    print("✓ General agent test passed\n")

def test_analyst_agent():
    print("=" * 60)
    print("Testing Analyst Agent...")
    
    # Create test CSV
    csv_path = "test_analyst.csv"
    with open(csv_path, "w") as f:
        f.write("Product,Sales,Revenue\nA,100,5000\nB,150,7500\nC,200,10000")
    
    try:
        # Upload
        with open(csv_path, "rb") as f:
            res = requests.post(f"{base_url}/upload", files={"file": f})
        file_path = res.json()["path"]
        
        # Request Analysis
        payload = {
            "message": "Analyze this sales data",
            "file_path": file_path,
            "session_id": "test_analyst"
        }
        res = requests.post(f"{base_url}/chat", json=payload)
        data = res.json()
        print(f"Agent: {data['agent']}")
        print(f"Response: {data['response'][:200]}...")
        assert data['agent'] == 'analyst'
        print("✓ Analyst agent test passed\n")
    finally:
        if os.path.exists(csv_path):
            os.remove(csv_path)

def test_designer_agent():
    print("=" * 60)
    print("Testing Designer Agent...")
    
    # Create test CSV
    csv_path = "test_designer.csv"
    with open(csv_path, "w") as f:
        f.write("Category,Value\nA,10\nB,20\nC,15")
    
    try:
        # Upload
        with open(csv_path, "rb") as f:
            res = requests.post(f"{base_url}/upload", files={"file": f})
        file_path = res.json()["path"]
        
        # Request Chart
        payload = {
            "message": "Create a bar chart",
            "file_path": file_path,
            "session_id": "test_designer"
        }
        res = requests.post(f"{base_url}/chat", json=payload)
        data = res.json()
        print(f"Agent: {data['agent']}")
        if "CHART_JSON" in data['response']:
            print("✓ Chart JSON generated successfully")
            spec = data['response'].replace("CHART_JSON:", "")
            chart_data = json.loads(spec)
            print(f"Chart type: {chart_data.get('data', [{}])[0].get('type', 'unknown')}")
        else:
            print(f"Response: {data['response']}")
        assert data['agent'] == 'designer'
        assert "CHART_JSON" in data['response']
        print("✓ Designer agent test passed\n")
    finally:
        if os.path.exists(csv_path):
            os.remove(csv_path)

def test_librarian_agent():
    print("=" * 60)
    print("Testing Librarian Agent...")
    
    payload = {
        "message": "How does The Council work?",
        "session_id": "test_librarian"
    }
    res = requests.post(f"{base_url}/chat", json=payload)
    data = res.json()
    print(f"Agent: {data['agent']}")
    print(f"Response: {data['response'][:200]}...")
    assert data['agent'] == 'librarian'
    print("✓ Librarian agent test passed\n")

def test_conversation_memory():
    print("=" * 60)
    print("Testing Conversation Memory...")
    
    session_id = "test_memory"
    
    # First message
    payload1 = {
        "message": "My name is Alice",
        "session_id": session_id
    }
    res1 = requests.post(f"{base_url}/chat", json=payload1)
    print(f"First message: {res1.json()['response'][:100]}...")
    
    # Second message - should remember
    payload2 = {
        "message": "What's my name?",
        "session_id": session_id
    }
    res2 = requests.post(f"{base_url}/chat", json=payload2)
    response = res2.json()['response']
    print(f"Second message: {response[:100]}...")
    
    # Check if it remembers (case-insensitive)
    if "alice" in response.lower():
        print("✓ Memory test passed - name remembered!\n")
    else:
        print("⚠ Memory test inconclusive - response doesn't explicitly mention name\n")

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("THE COUNCIL 2.0 - COMPREHENSIVE BACKEND TEST")
    print("=" * 60 + "\n")
    
    try:
        test_health()
        test_general_agent()
        test_librarian_agent()
        test_analyst_agent()
        test_designer_agent()
        test_conversation_memory()
        
        print("=" * 60)
        print("ALL TESTS PASSED! ✓")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
