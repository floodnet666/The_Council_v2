import polars as pl
from typing import Optional, List, Dict, Any
from engines.semantic_engine import SemanticEngine

class DataEngine:
    def __init__(self):
        self.df: Optional[pl.LazyFrame] = None
        self.metadata: Dict[str, Any] = {}
        self.semantic_engine = SemanticEngine()

    def load_data(self, file_path: str):
        """
        Loads data into a LazyFrame with semantic type detection.
        Uses infer_schema_length=0 to prevent early inference crashes.
        """
        try:
            # 1. Initial Load (Lazy)
            if file_path.endswith('.csv'):
                # Force everything to String initially to prevent ANY primitive parsing errors
                # We read only headers first to get names
                try:
                    headers = pl.read_csv(file_path, n_rows=0).columns
                    overrides = {col: pl.String for col in headers}
                    base_df = pl.scan_csv(file_path, schema_overrides=overrides)
                except:
                    # Fallback if header read fails
                    base_df = pl.scan_csv(file_path, infer_schema_length=0)
            elif file_path.endswith('.parquet'):
                base_df = pl.scan_parquet(file_path)
            else:
                raise ValueError("Unsupported file format")
            
            # 2. Semantic Analysis on a sample
            # We collect a sample to validate our semantic decisions
            sample_df = base_df.limit(200).collect()
            semantic_meta = self.semantic_engine.detect_semantic_types(sample_df)
            
            # 3. Apply Casting Plan based on semantic decisions
            casting_plan = self.semantic_engine.get_casting_plan(semantic_meta)
            
            # Refine the LazyFrame with the casting plan
            refined_df = base_df
            schema = base_df.collect_schema()

            for col, target_type in casting_plan.items():
                if col not in schema.names():
                    continue
                
                try:
                    # Special handling for dates if they are currently strings
                    if target_type == pl.Date and schema[col] in [pl.String, pl.Utf8]:
                        refined_df = refined_df.with_columns(
                            pl.col(col).str.to_date(strict=False)
                        )
                    # Special handling for numeric casting from strings (handles commas/etc)
                    elif target_type in [pl.Float64, pl.Int64] and schema[col] in [pl.String, pl.Utf8]:
                         # Clean numeric strings before casting if needed
                         refined_df = refined_df.with_columns(
                             pl.col(col).str.replace_all(",", "").cast(target_type, strict=False)
                         )
                    else:
                        refined_df = refined_df.with_columns(
                            pl.col(col).cast(target_type, strict=False)
                        )
                except Exception as e:
                    print(f"Warning: Could not cast column {col} to {target_type}: {e}")

            self.df = refined_df
            
            # 4. Store enriched metadata
            self.metadata = {
                "columns": self.df.collect_schema().names(),
                "technical_dtypes": {k: str(v) for k, v in self.df.collect_schema().items()},
                "semantic_types": {col: meta["semantic_type"] for col, meta in semantic_meta.items()},
                "ambiguities": {col: meta["ambiguity_reason"] for col, meta in semantic_meta.items() if meta["is_ambiguous"]},
                "source": file_path
            }
            
            return True
        except Exception as e:
            print(f"Error loading data: {e}")
            import traceback
            traceback.print_exc()
            return False

    def execute_query(self, query: str) -> Optional[pl.DataFrame]:
        """
        Placeholder for executing SQL-like or Polars queries.
        For now, just returns head.
        """
        if self.df is None:
            return None
        return self.df.limit(5).collect()

    def get_summary(self) -> Dict[str, Any]:
        if self.df is None:
            return {"status": "no_data"}
        
        schema = self.df.collect_schema()
        # Collect only a few rows for preview and count for summary
        try:
            preview = self.df.limit(5).collect().to_dicts()
            row_count = self.df.select(pl.len()).collect().item()
        except Exception as e:
            preview = []
            row_count = "Error collecting count"

        return {
            "status": "loaded",
            "columns": schema.names(),
            "technical_dtypes": {k: str(v) for k, v in schema.items()},
            "semantic_types": self.metadata.get("semantic_types", {}),
            "ambiguities": self.metadata.get("ambiguities", {}),
            "preview": preview,
            "row_count": row_count
        }
