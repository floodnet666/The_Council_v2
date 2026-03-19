import pytest
from fastapi.testclient import TestClient
import os
import json
import polars as pl
from main import app  # Importa a aplicação FastAPI real

def test_full_conversational_and_deterministic_pipeline():
    """
    Testa o sistema EXATAMENTE como o Frontend o consome.
    Garante: Contrato HTTP, Fluidez Humana e Determinismo Matemático.
    """
    test_filename = "e2e_test_data.csv"
    
    # 1. Preparação: Dataset estático para conferência matemática
    df = pl.DataFrame({
        "produto": ["Monitor", "Teclado", "Monitor", "Mouse", "Teclado"],
        "venda": [1500, 200, 1500, 100, 200],
        "setor": ["TI", "TI", "TI", "TI", "TI"]
    })
    df.write_csv(test_filename)
    
    with TestClient(app) as client:
        try:
            # 2. Simula Upload via API
            with open(test_filename, "rb") as f:
                upload_res = client.post("/upload", files={"file": (test_filename, f, "text/csv")})
            assert upload_res.status_code == 200
            file_path = upload_res.json()["path"]

            # 3. Simula Chat: Pergunta que exige GroupBy
            payload = {
                "message": "Qual o total de vendas por produto?",
                "session_id": "test_session_123",
                "file_path": file_path
            }
            
            response = client.post("/chat", json=payload)
            assert response.status_code == 200
            data = response.json()
            
            # Forçar gravação em arquivo para debug absoluto
            with open("tests/debug_response.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            
            print(f"\n[DEBUG_TEST_HTTP_RESPONSE] data={json.dumps(data, indent=2)}")



            # --- VALIDAÇÕES CRÍTICAS ---
            
            # A. Validação de Contrato
            assert "response" in data
            assert "visual_data" in data
            assert data["status"] == "success"

            # B. Validação do Pilar 2 (Fluidez Humana)
            # O texto não pode conter lixo de programação ou JSON bruto
            chat_text = data["response"]
            assert "{" not in chat_text
            assert "ANALYSIS_DATA" not in chat_text
            assert len(chat_text) > 30  # Garante que houve uma explicação real

            # C. Validação do Pilar 1 (Determinismo Polars)
            # Monitor (1500+1500) deve ser 3000 EXATAMENTE.
            visual_data = data["visual_data"]
            monitor_data = next(item for item in visual_data if item["produto"] == "Monitor")
            assert monitor_data["venda_sum"] == 3000
            
            print("\n✅ TESTE E2E CONCLUÍDO COM SUCESSO!")
            print(f"Mensagem do Analista: {chat_text[:100]}...")
            print(f"Dados Determinísticos Recebidos: {visual_data}")

        finally:
            if os.path.exists(test_filename):
                os.remove(test_filename)

if __name__ == "__main__":
    test_full_conversational_and_deterministic_pipeline()

