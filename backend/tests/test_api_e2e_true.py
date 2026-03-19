import pytest
from fastapi.testclient import TestClient
import os
import json
import asyncio

# Setup env for testing
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")

from main import app, lifespan
from engines.data_engine import DataEngine

@pytest.fixture(scope="module")
def client():
    # We must run the lifespan to initialize the graph
    with TestClient(app) as c:
        yield c

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_analyst_fluid_response_and_data_separation(client):
    """
    Tests the True E2E Contract for the False Positive Paradox.
    Verifies that the LLM explanation in 'response' does not contain raw JSON,
    and the deterministic data is isolated in 'visual_data'.
    """
    payload = {
        "message": "Quais são as 3 cidades com mais garrafas vendidas?",
        "session_id": "test_e2e_true_01",
        "file_path": "uploads/Liquor_Sales.csv"
    }
    
    response = client.post("/chat", json=payload)
    assert response.status_code == 200, f"Error: {response.text}"
    
    data = response.json()
    assert data["status"] == "success"
    assert "analyst" in data["agent"].lower()
    
    # 1. The conversational message must NOT contain RAW JSON or code blocks
    chat_message = data["response"]
    assert "```json" not in chat_message, "Prompt Glue Detected: JSON code block leaked into chat message."
    assert "ANALYSIS_DATA:" not in chat_message, "Prompt Glue Detected: Raw string tag leaked into chat message."
    assert "{" not in chat_message and "[" not in chat_message, "Reflective check: Braces/Brackets found in fluid chat."

    # 2. The structural data must be present and correctly isolated
    visual_data = data.get("visual_data")
    assert visual_data is not None, "visual_data key is missing or None."
    assert isinstance(visual_data, dict), "visual_data should be a dictionary"
    
    # 3. Check for operation AST
    assert "operation" in visual_data
    assert visual_data["operation"] in ["group_by", "top_n", "top_n_per_group", "aggregation"]
    assert "data" in visual_data
    
    # 4. Check array length
    result_array = visual_data["data"]
    assert isinstance(result_array, list)
    assert len(result_array) == 3, f"Expected 3 rows, got {len(result_array)}"
    
    # 5. Check logical correctness
    row_strings = json.dumps(result_array).upper()
    assert "DES MOINES" in row_strings or "CEDAR RAPIDS" in row_strings
    
    print("\n--- E2E TRUE TEST PASSED ---")
    print(f"Chat Message (Fluid, localized): {chat_message}")
    print(f"Visual Data AST Operation: {visual_data['operation']}")
    print(f"Visual Data Payload (Separated): {result_array}")
