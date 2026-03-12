import json
import os
import faiss
import numpy as np

# Test reading the FAISS index and metadata
data_dir = "data"
index_path = os.path.join(data_dir, "faiss_index.bin")
meta_path = os.path.join(data_dir, "faiss_meta.json")

print("Testing FAISS Knowledge Base...")
print("=" * 60)

# 1. Check if files exist
print(f"\n1. Checking files...")
print(f"   Index exists: {os.path.exists(index_path)}")
print(f"   Metadata exists: {os.path.exists(meta_path)}")

# 2. Load metadata
print(f"\n2. Loading metadata...")
with open(meta_path, 'r', encoding='utf-8') as f:
    metadata = json.load(f)

print(f"   Total documents: {len(metadata)}")
if metadata:
    print(f"   First doc preview: {metadata[0][:100]}...")
    print(f"   Last doc preview: {metadata[-1][:100]}...")

# 3. Load FAISS index
print(f"\n3. Loading FAISS index...")
index = faiss.read_index(index_path)
print(f"   Index dimension: {index.d}")
print(f"   Total vectors: {index.ntotal}")

# 4. Check if it's about Polars
print(f"\n4. Checking content...")
polars_mentions = sum(1 for doc in metadata if 'polars' in doc.lower())
print(f"   Documents mentioning 'polars': {polars_mentions}")

# 5. Sample some documents
print(f"\n5. Sample documents:")
for i in [0, len(metadata)//2, -1]:
    print(f"\n   Doc {i}:")
    print(f"   {metadata[i][:200]}...")

print("\n" + "=" * 60)
print("✓ FAISS Knowledge Base is readable!")
