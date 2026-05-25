import pytest
from fastapi.testclient import TestClient
import os
import json
import polars as pl

# 1. INJEÇÃO DO MODELO ANTES DAS IMPORTAÇÕES PARA GARANTIR OVERRIDE
os.environ["OLLAMA_MODEL"] = "hf.co/mradermacher/gemma-4-E2B-it-uncensored-GGUF:Q8_0"

from main import app
from engines.data_engine import PandasSyntaxDetectedError

def test_gemma_tool_calling_and_polars_determinism():
    """
    Testa se o Gemma-4-E2B suporta perfeitamente o Tool Calling (PolarsOperation)
    sem alucinar código Pandas e mantendo a integridade da Semantic Orchestra.
    """
    test_filename = "e2e_gemma_test.csv"
    
    # Dataset control
    df = pl.DataFrame({
        "produto": ["Monitor", "Teclado", "Monitor", "Mouse", "Teclado"],
        "venda": [1500, 200, 1500, 100, 200],
        "setor": ["TI", "TI", "TI", "TI", "TI"]
    })
    df.write_csv(test_filename)
    
    with TestClient(app) as client:
        try:
            # A. Upload
            with open(test_filename, "rb") as f:
                upload_res = client.post("/upload", files={"file": (test_filename, f, "text/csv")})
            assert upload_res.status_code == 200
            file_path = upload_res.json()["path"]

            # B. Intenção Analítica Complexa (Exige Tool Calling: group_by + sum)
            payload = {
                "message": "Qual o total de vendas por produto?",
                "session_id": "gemma_session_001",
                "file_path": file_path
            }
            
            response = client.post("/chat", json=payload)
            assert response.status_code == 200
            data = response.json()
            
            # --- VALIDAÇÕES DE TOOL CALLING E DETERMINISMO ---
            
            assert data["status"] == "success", f"Gemma falhou na execução estruturada: {data}"
            assert "response" in data
            assert "visual_data" in data

            # C. Validação de Ausência de Alucinação Pandas na resposta verbal
            chat_text = data["response"].lower()
            assert "pandas" not in chat_text, "Gemma alucinou referências ao Pandas na resposta"
            assert "pd.dataframe" not in chat_text
            assert ".loc" not in chat_text
            assert "iloc" not in chat_text
            
            # D. Validação de Tool Calling Estruturado (Matemática Exata via Polars AST)
            visual_data = data.get("visual_data")
            assert visual_data is not None, f"Visual data is None! Resposta do agente: {chat_text}"
            assert len(visual_data) > 0, "AST falhou em gerar dados"
            
            monitor_data = next(item for item in visual_data if item["produto"] == "Monitor")
            assert monitor_data["venda_sum"] == 3000, "Erro de Tool Calling: Agregação sum() mal resolvida pelo AST."
            
            print(f"\n[SUCESSO] Gemma-4-E2B-it-uncensored processou Tool Calling e sintaxe Polars corretamente!")
            print(f"[SUCESSO] Resposta fluida gerada: {chat_text[:120]}...")

        finally:
            if os.path.exists(test_filename):
                os.remove(test_filename)

if __name__ == "__main__":
    test_gemma_tool_calling_and_polars_determinism()

def test_gemma_designer_chart_generation():
    """
    Testa se o DesignerAgent, ao usar Gemma-4-E2B, extrai a intenção visual para
    um ChartSchema válido sem alucinar código de bibliotecas gráficas ou Pandas.
    """
    test_filename = "e2e_gemma_chart_test.csv"
    
    # Dataset control
    df = pl.DataFrame({
        "produto": ["Monitor", "Teclado", "Mouse"],
        "vendas": [1500, 200, 100],
    })
    df.write_csv(test_filename)
    
    with TestClient(app) as client:
        try:
            # A. Upload
            with open(test_filename, "rb") as f:
                upload_res = client.post("/upload", files={"file": (test_filename, f, "text/csv")})
            assert upload_res.status_code == 200
            file_path = upload_res.json()["path"]

            # B. Intenção de Design (Aciona DesignerAgent)
            payload = {
                "message": "Gere um gráfico de barras com as vendas por produto",
                "session_id": "gemma_session_002",
                "file_path": file_path
            }
            
            response = client.post("/chat", json=payload)
            assert response.status_code == 200
            data = response.json()
            
            # --- VALIDAÇÕES DE VISUAL SCHEMA ---
            assert data["status"] == "success", f"Gemma falhou na execução estruturada: {data}"
            assert "response" in data
            
            # Garante que o roteamento foi pro Designer e ele cuspiu o Schema visual
            visual_schema = data.get("visual_config")
            assert visual_schema is not None, f"Visual schema is None! Resposta do agente: {data['response']}"
            
            # Valida as propriedades obrigatórias do ChartSchema
            assert "chart_type" in visual_schema
            assert "x_axis" in visual_schema
            assert "y_axis" in visual_schema
            
            # Checa se o modelo escolheu bar chart baseado no prompt "gráfico de barras"
            assert visual_schema["chart_type"] in ["bar", "column", "histogram"]
            assert visual_schema["x_axis"] == "produto"
            
            # C. Validação Anti-Alucinação
            chat_text = data["response"].lower()
            assert "pandas" not in chat_text
            assert "matplotlib" not in chat_text
            assert "plt.show" not in chat_text
            assert "import seaborn" not in chat_text
            
            print(f"\n[SUCESSO] Gemma-4-E2B gerou o ChartSchema perfeitamente: {visual_schema}")

        finally:
            if os.path.exists(test_filename):
                os.remove(test_filename)
