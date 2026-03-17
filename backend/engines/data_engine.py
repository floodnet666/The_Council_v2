import polars as pl
from typing import Optional, List, Dict, Any
from engines.semantic_engine import SemanticEngine
from utils.logging_config import logger
import os
from opentelemetry import trace
import time

tracer = trace.get_tracer(__name__)

import pandas as pd
import json
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import MinMaxScaler

class PandasSyntaxDetectedError(Exception):
    """Exception raised when Pandas syntax is detected in a code block intended for Polars."""
    pass

class DataEngine:
    # Global Caches to avoid re-reading large CSVs across isolated Session IDs
    _global_lazy_df: Optional[pl.LazyFrame] = None
    _global_scanned_file: Optional[str] = None
    _global_ctx: Optional[pl.SQLContext] = None
    
    def __init__(self):
        self.df: Optional[pl.LazyFrame] = None
        self.ctx: Optional[pl.SQLContext] = None
        self.metadata: Dict[str, Any] = {}
        self.semantic_engine = SemanticEngine()

    def validate_polars_syntax(self, code: str) -> bool:
        """
        Detects prohibited Pandas patterns using Regex.
        Raises PandasSyntaxDetectedError if found.
        """
        prohibited_patterns = [
            r'\.loc\b',
            r'\.iloc\b',
            r'\.apply\(lambda',
            r'\.iterrows\(\)',
            r'\bpd\.',
            r'\[df\[',  # Common pandas filtering: df[df['col'] > 0]
            r'\.groupby\(.*\)\.apply\('
        ]
        
        for pattern in prohibited_patterns:
            if re.search(pattern, code):
                match = re.search(pattern, code).group()
                logger.warning(f"Pandas syntax detected: {match}")
                raise PandasSyntaxDetectedError(f"Pandas syntax detected: '{match}'. Use pure Polars (e.g., pl.col, df.filter, df.group_by).")
        
        return True

    def _detect_date_format(self, values: List[Any]) -> Optional[str]:
        """Detects the date format on a small sample list using datetime.strptime."""
        from datetime import datetime
        formats = ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d"]
        
        non_empty = [str(v).strip() for v in values if v is not None and str(v).strip()]
        if not non_empty:
            return None
            
        test_val = non_empty[0]
        for fmt in formats:
            try:
                datetime.strptime(test_val, fmt)
                return fmt
            except ValueError:
                continue
        return None

    def _parse_date_expr(self, col_name: str, values: List[Any]):
        """Retorna expressão estática para parsed de data baseado no formato detectado."""
        fmt = self._detect_date_format(values)
        if fmt:
            logger.info(f"Detected Date format for {col_name}: {fmt}")
            return pl.col(col_name).str.to_date(fmt, strict=False)
        else:
            # Fallback seguro para auto-parse se o formato for indefinido
            return pl.col(col_name).str.to_date(strict=False)

    def load_data(self, file_path: str):
        """
        Loads data into a LazyFrame with semantic type detection.
        Uses infer_schema_length=0 to prevent early inference crashes.
        """
        # Singleton Check
        if DataEngine._global_lazy_df is not None and DataEngine._global_scanned_file == file_path:
            logger.info(f"Using Static Global Cache for: {file_path}")
            self.df = DataEngine._global_lazy_df
            self.ctx = DataEngine._global_ctx
            return self.df
            
        with tracer.start_as_current_span("load_data") as span:
            span.set_attribute("file_path", file_path)
            file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
            span.set_attribute("file_size_bytes", file_size)
            
            start_time = time.time()
            logger.info(f"Loading data from: {file_path} ({file_size / 1e6:.2f} MB)")
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
                                self._parse_date_expr(col, sample_df[col].to_list()).alias(col)
                            )
                        # Special handling for numeric casting from strings (handles commas/etc)
                        elif target_type in [pl.Float64, pl.Int64] and schema[col] in [pl.String, pl.Utf8]:
                             # Clean numeric strings before casting if needed
                             refined_df = refined_df.with_columns(
                                 pl.col(col).str.replace_all(",", "").str.replace_all("$", "").cast(target_type, strict=False)
                             )
                        else:
                            refined_df = refined_df.with_columns(
                                pl.col(col).cast(target_type, strict=False)
                            )
                    except Exception as e:
                        logger.warning(f"Could not cast column {col} to {target_type}: {e}")

                # 4. Automatic Column Derivation (from V1)
                derived_ops = []
                cols = refined_df.collect_schema().names()
                
                # Check for first available date column for time derivation
                date_cols = [c for c, t in refined_df.collect_schema().items() if t == pl.Date or t == pl.Datetime]
                if date_cols:
                    base_date = pl.col(date_cols[0])
                    derived_ops.extend([
                        base_date.dt.year().alias("ano"),
                        base_date.dt.strftime("%Y-%m").alias("mes_ano"),
                        base_date.dt.weekday().alias("dia_semana_idx"),
                    ])
                    # Add sales derivation if quantity and price are detected
                    q_col = next((c for c in cols if any(word in c.lower() for word in ["qty", "quantity", "quantidade"])), None)
                    p_col = next((c for c in cols if any(word in c.lower() for word in ["price", "valor", "preço"])), None)
                    if q_col and p_col:
                        derived_ops.append(
                            (pl.col(q_col).cast(pl.Float64) * pl.col(p_col).cast(pl.Float64)).alias("vendas")
                        )

                if derived_ops:
                    refined_df = refined_df.with_columns(derived_ops)

                self.df = refined_df
                self.ctx = pl.SQLContext(frames={"data": self.df})
                
                # Update Static Global Cache
                DataEngine._global_lazy_df = self.df
                DataEngine._global_ctx = self.ctx
                DataEngine._global_scanned_file = file_path
                logger.info(f"Saved Static Global Cache for: {file_path}")
                
                self.metadata = {
                    "columns": self.df.collect_schema().names(),
                    "technical_dtypes": {k: str(v) for k, v in self.df.collect_schema().items()},
                    "semantic_types": {col: meta["semantic_type"] for col, meta in semantic_meta.items()},
                    "ambiguities": {col: meta["ambiguity_reason"] for col, meta in semantic_meta.items() if meta["is_ambiguous"]},
                    "source": file_path,
                    "file_size": file_size
                }
                
                duration = time.time() - start_time
                logger.info(f"Data loading complete. Columns: {len(self.metadata['columns'])}, Time: {duration:.4f}s")
                span.set_attribute("duration_s", duration)
                return True
            except Exception as e:
                logger.error(f"Error loading data: {e}")
                return False

    def execute_query(self, query: str) -> Optional[pl.DataFrame]:
        """
        Placeholder for executing SQL-like or Polars queries.
        For now, just returns head.
        """
        with tracer.start_as_current_span("execute_query") as span:
            span.set_attribute("query", query)
            if self.df is None:
                logger.warning("Query execution attempted without loaded data")
                return None
            
            start_time = time.time()
            result = self.df.limit(5).collect()
            duration = time.time() - start_time
            
            logger.info(f"Query executed in {duration:.4f}s")
            span.set_attribute("duration_s", duration)
            return result

    def execute_sql(self, query: str):
        try:
            logger.info(f"[SQL] Executing: {query[:100]}...")
            if not self.ctx:
                 self.ctx = pl.SQLContext(frames={"data": self.df})
            
            res = self.ctx.execute(query).limit(5000).collect(streaming=True)
            return {"data": json.loads(res.to_pandas().to_json(orient="records")), "columns": res.columns}
        except Exception as e:
            logger.error(f"[SQL ERROR] {e}")
            return {"error": str(e)}

    def execute_python(self, code: str):
        logger.info(f"[PYTHON] Executing code block...")
        
        # Sandbox setup (from V1)
        loc = {
            "pl": pl,
            "np": np,
            "lf": self.df,
            "result": None,
            "LinearRegression": LinearRegression,
            "KMeans": KMeans,
            "IsolationForest": IsolationForest,
            "MinMaxScaler": MinMaxScaler,
        }

        try:
            # Clean and execute
            code = code.replace("```python", "").replace("```", "").strip()
            # Prevent re-assignment of 'lf' if the agent tries it
            code = re.sub(r"(^\s*lf\s*=.*)", r"# \1", code, flags=re.MULTILINE)

            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                exec(code, {}, loc)

            res = loc.get("result")

            if res is None:
                # Fallback: find any generated LazyFrame/DataFrame
                c = [v for k, v in loc.items() if isinstance(v, (pl.DataFrame, pl.LazyFrame)) and k != "lf"]
                if c:
                    res = c[-1]
                else:
                    return {"error": "O código rodou mas não gerou variável 'result' nem DataFrame."}

            if isinstance(res, pl.LazyFrame):
                res = res.limit(5000).collect(streaming=True)

            if isinstance(res, (pl.DataFrame, pl.Series)):
                if isinstance(res, pl.Series):
                    res = res.to_frame()
                return {"data": json.loads(res.to_pandas().to_json(orient="records"))}

            return {"text": str(res)}

        except Exception as e:
            logger.error(f"[PYTHON ERROR] {e}")
            return {"error": f"Erro na execução Python: {str(e)}"}

    def get_summary(self) -> Dict[str, Any]:
        if self.df is None:
            return {"status": "no_data"}
        
        schema = self.df.collect_schema()
        # Collect only a few rows for preview and count for summary
        try:
            preview = self.df.limit(5).collect().to_dicts()
            
            # Row count is expensive for massive CSVs. Skip if > 500MB
            file_size = self.metadata.get("file_size", 0)
            if file_size > 500 * 1024 * 1024: # 500 MB
                row_count = "Large Dataset (>500MB) - Total count skipped for performance"
            else:
                row_count = self.df.select(pl.len()).collect().item()
        except Exception as e:
            preview = []
            row_count = f"Error collecting stats: {e}"

        return {
            "status": "loaded",
            "columns": schema.names(),
            "technical_dtypes": {k: str(v) for k, v in schema.items()},
            "semantic_types": self.metadata.get("semantic_types", {}),
            "ambiguities": self.metadata.get("ambiguities", {}),
            "preview": preview,
            "row_count": row_count
        }
