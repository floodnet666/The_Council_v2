import polars as pl
from engines.semantic_engine import SemanticEngine

def test_semantic_detection():
    engine = SemanticEngine()
    
    # Create a dummy dataframe with various types
    df = pl.DataFrame({
        "user_id": list(range(100)),
        "price": [10.5] * 100,
        "status": ["active"] * 50 + ["inactive"] * 50,
        "created_at": ["2023-01-01"] * 100,
        "description": ["Text"] * 100,
        "year": [2021] * 100,
        "score": [1, 2] * 50 # 100 rows, only 2 unique values
    })
    
    meta = engine.detect_semantic_types(df)
    
    for col, info in meta.items():
        print(f"Col: {col}")
        print(f"  Semantic Type: {info['semantic_type']}")
        print(f"  Ambiguous: {info['is_ambiguous']}")
        if info['is_ambiguous']:
            print(f"  Reason: {info['ambiguity_reason']}")
        print(f"  Suggested Technical Type: {info['suggested_dtype']}")
        print("-" * 20)

if __name__ == "__main__":
    test_semantic_detection()
