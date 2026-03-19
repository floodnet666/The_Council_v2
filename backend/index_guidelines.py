import os
from engines.memory_engine import memory_engine

def index():
    print("Iniciando indexação de diretrizes Polars...")
    
    # Ingest file
    filepath = "docs/polars_guidelines.md"
    if os.path.exists(filepath):
         res = memory_engine.ingest_file(filepath)
         print(f"Resultado ingest_file: {res}")
         memory_engine.save()
         print("Index salvo com sucesso em data/faiss_index.bin")
    else:
         print(f"Arquivo não encontrado: {filepath}")

if __name__ == "__main__":
    index()
