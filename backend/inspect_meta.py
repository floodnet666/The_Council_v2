import json

# Load and inspect the metadata structure
with open("data/faiss_meta.json", "r", encoding="utf-8") as f:
    metadata = json.load(f)

print("Metadata keys:", list(metadata.keys()))
print("\nFirst few IDs:", metadata.get("ids", [])[:3] if "ids" in metadata else "No 'ids' key")

# Check if there's a 'documents' key
if "documents" in metadata:
    print(f"\nTotal documents: {len(metadata['documents'])}")
    print(f"First document preview: {metadata['documents'][0][:200]}...")
elif "ids" in metadata and "metadatas" in metadata:
    print(f"\nTotal IDs: {len(metadata['ids'])}")
    print("Structure appears to be Chroma-style with ids and metadatas")
else:
    print("\nUnknown structure. All keys:", metadata.keys())
    for key in list(metadata.keys())[:5]:
        val = metadata[key]
        print(f"  {key}: {type(val)} - {str(val)[:100] if not isinstance(val, (list, dict)) else f'length={len(val)}'}")
