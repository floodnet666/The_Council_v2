"""
QueryEngine - Executa análises determinísticas em DataFrames Polars
Execução estrita baseada na AST (Abstract Syntax Tree) do PolarsOperation.
Sem Regex. Sem Heurísticas de Texto. 100% Matemática.
"""
import polars as pl
from typing import Dict, Any, Optional
from datetime import datetime
from utils.logging_config import logger
from schemas.operations import PolarsOperation

class QueryEngine:
    """Engine para executar queries determinísticas em DataFrames Polars"""
    
    def __init__(self, df: Optional[pl.LazyFrame] = None):
        self.df = df
        
    def set_dataframe(self, df: pl.LazyFrame):
        """Define o DataFrame para análise"""
        self.df = df
        
    def execute_deterministic_operation(self, operation: PolarsOperation) -> Dict[str, Any]:
        """
        Executa cegamente o que a AST determinou, garantindo 100% de determinismo matemático.
        """
        if self.df is None:
            return {"error": "No dataframe loaded"}
            
        try:
            # 1. Aplicar filtro inicial (simplificado - em produção complexa o LLM passaria Expr real ou SQL)
            # Para manter a estabilidade desta refatoração, deixamos filtros complexos a cargo do SQL Engine
            # ou delegamos agregados puros para o determinístico.
            
            # Executa operação
            if operation.operation_type == "group_by":
                if not operation.group_column:
                    return {"error": "Missing group_column for group_by operation"}
                    
                target_cols = operation.target_columns if operation.target_columns else ["vendas" if "vendas" in self.df.collect_schema().names() else "count"]
                
                # Default para sum/count se "count" for o target
                agg_exprs = []
                for c in target_cols:
                    if c == "count":
                        agg_exprs.append(pl.len().alias("count"))
                    else:
                        agg_exprs.append(pl.col(c).sum().alias(f"{c}_sum"))
                
                sort_col = f"{target_cols[0]}_sum" if target_cols[0] != "count" else "count"
                
                group_cols = [operation.group_column]
                if operation.group_column_secondary:
                    group_cols.append(operation.group_column_secondary)
                    
                result = (
                    self.df
                    .group_by(group_cols)
                    .agg(agg_exprs)
                    .sort(sort_col, descending=operation.sort_descending)
                    .limit(operation.limit)
                    .collect()
                )
                
                return {
                    "status": "success",
                    "operation": "group_by",
                    "data": result.to_dicts()
                }
                
            elif operation.operation_type == "aggregation":
                agg_exprs = []
                target_cols = operation.target_columns if operation.target_columns else ["count"]
                for c in target_cols:
                    if c == "count" or c not in self.df.collect_schema().names():
                        agg_exprs.append(pl.len().alias("count"))
                    else:
                        agg_exprs.extend([
                            pl.col(c).sum().alias(f"{c}_sum"),
                            pl.col(c).mean().alias(f"{c}_mean"),
                            pl.col(c).max().alias(f"{c}_max"),
                            pl.col(c).min().alias(f"{c}_min")
                        ])
                        
                result = self.df.select(agg_exprs).collect()
                return {
                    "status": "success", 
                    "operation": "aggregation",
                    "data": result.to_dicts()
                }
                
            elif operation.operation_type == "top_n":
                if not operation.target_columns:
                    return {"error": "Missing target_columns for top_n sort"}
                    
                sort_col = operation.target_columns[0]
                result = (
                    self.df
                    .sort(sort_col, descending=operation.sort_descending)
                    .limit(operation.limit)
                    .collect()
                )
                return {
                    "status": "success",
                    "operation": "top_n", 
                    "data": result.to_dicts()
                }
                
            elif operation.operation_type == "describe":
                schema = self.df.collect_schema()
                numeric_cols = [c for c, t in schema.items() if t in [pl.Int64, pl.Int32, pl.Float64, pl.Float32]]
                
                agg_exprs = [pl.len().alias("row_count")]
                for col in numeric_cols:
                    agg_exprs.extend([
                        pl.col(col).mean().alias(f"{col}_mean"),
                        pl.col(col).min().alias(f"{col}_min"),
                        pl.col(col).max().alias(f"{col}_max")
                    ])
                
                result = self.df.select(agg_exprs).collect()
                return {
                    "status": "success",
                    "operation": "describe",
                    "data": result.to_dicts()
                }
                
            elif operation.operation_type == "top_n_per_group":
                if not operation.group_column or not operation.target_columns:
                    return {"error": "Missing group or target for top_n_per_group"}
                    
                gcol = operation.group_column
                tcol = operation.target_columns[0]
                
                # Check if tcol is numeric/aggregation target or categorical entity
                schema = self.df.collect_schema()
                is_numeric = schema.get(tcol) in [pl.Int64, pl.Float64, pl.Int32]
                
                if is_numeric:
                    # Simple sort within group
                    res = (
                        self.df
                        .sort([gcol, tcol], descending=[False, operation.sort_descending])
                        .with_columns(pl.col(tcol).rank("desc").over(gcol).alias("rank"))
                        .filter(pl.col("rank") <= (operation.limit or 5))
                        .limit(100)
                        .collect()
                    )
                else:
                    # Group -> Count -> Rank
                    agg_expr = pl.len().alias("count")
                    sort_col = "count"
                    if "vendas" in schema.names():
                        agg_expr = pl.col("vendas").sum().alias("vendas_sum")
                        sort_col = "vendas_sum"
                        
                    res = (
                         self.df
                         .group_by([gcol, tcol])
                         .agg(agg_expr)
                         .with_columns(pl.col(sort_col).rank("desc").over(gcol).alias("rank"))
                         .filter(pl.col("rank") <= (operation.limit or 5))
                         .sort([gcol, "rank"])
                         .limit(100)
                         .collect()
                     )
                     
                return {
                    "status": "success",
                    "operation": "top_n_per_group",
                    "data": res.to_dicts()
                }

            else:
                 return {"error": f"Operation '{operation.operation_type}' not natively supported in AST mapping. Use SQL/Python engine."}
                 
        except Exception as e:
            logger.error(f"Error in execute_deterministic_operation: {e}")
            return {"error": str(e)}
