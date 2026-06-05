import faiss
import numpy as np
import os
import json
from typing import List
from langchain_community.embeddings import HuggingFaceEmbeddings

class MemoryEngine:
    def __init__(self, index_path: str = "data/faiss_index.bin", metadata_path: str = "data/faiss_meta.json"):
        self.index_path = index_path
        self.metadata_path = metadata_path
        self.model = None
        self.index = None
        self.documents = []
        self._is_loaded = False

    def _load_lazy(self):
        if not self._is_loaded:
            print("Loading Embedding Model (Ollama)...")
            self.model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            self.dimension = 384
            
            # Try to load existing index and metadata
            if os.path.exists(self.index_path):
                print(f"Loading FAISS index from {self.index_path}...")
                self.index = faiss.read_index(self.index_path)
                
                # Load metadata if exists
                if os.path.exists(self.metadata_path):
                    print(f"Loading metadata from {self.metadata_path}...")
                    with open(self.metadata_path, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                        # Support both formats: list of docs or dict with 'documents' key
                        if isinstance(metadata, list):
                            self.documents = metadata
                        elif isinstance(metadata, dict) and 'documents' in metadata:
                            self.documents = metadata['documents']
                        else:
                            print("Warning: Unknown metadata format, using empty documents list")
                    print(f"Loaded {len(self.documents)} documents from metadata")
            else:
                self.index = faiss.IndexFlatL2(self.dimension)
                
            self._is_loaded = True

    def add_documents(self, docs: List[str]):
        self._load_lazy()
        if not docs:
            return
        
        embeddings = self.model.embed_documents(docs)
        self.index.add(np.array(embeddings, dtype='float32'))
        self.documents.extend(docs)
        # Save usually happens here or manually
        
    def search(self, query: str, k: int = 3) -> List[str]:
        self._load_lazy()
        query_vector = self.model.embed_documents([query])
        distances, indices = self.index.search(np.array(query_vector, dtype='float32'), k)
        
        results = []
        for i in range(k):
            idx = indices[0][i]
            if idx != -1 and idx < len(self.documents):
                results.append(self.documents[idx])
        
        return results

    def save(self):
         if self.index:
            print(f"Saving FAISS index to {self.index_path}...")
            faiss.write_index(self.index, self.index_path)
            
            print(f"Saving metadata to {self.metadata_path}...")
            with open(self.metadata_path, 'w', encoding='utf-8') as f:
                json.dump({"documents": self.documents}, f, ensure_ascii=False, indent=2)

    def ingest_file(self, file_path: str):
        self._load_lazy()
        if not os.path.exists(file_path):
            return "File not found."
            
        text = ""
        ext = os.path.splitext(file_path)[1].lower()
        
        try:
            if ext == ".txt" or ext == ".md":
                with open(file_path, "r", encoding="utf-8") as f:
                    text = f.read()
            elif ext == ".pdf":
                try:
                    from pypdf import PdfReader
                    reader = PdfReader(file_path)
                    for page in reader.pages:
                        text += page.extract_text() + "\n"
                except ImportError:
                    return "pypdf not installed."
            else:
                return f"Unsupported file type: {ext}"
            
            if text:
                # Naive chunking
                chunks = [text[i:i+500] for i in range(0, len(text), 500)]
                self.add_documents(chunks)
                return f"Ingested {len(chunks)} chunks from {os.path.basename(file_path)}."
            else:
                return "Empty file."
        except Exception as e:
            return f"Error ingesting file: {e}"

# Global singleton instance
memory_engine = MemoryEngine()
