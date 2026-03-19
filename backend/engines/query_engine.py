"""
QueryEngine - Executa análises determinísticas em DataFrames Polars
"""
import polars as pl
from typing import Dict, Any, Optional
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
        Executa cegamente a operação definida pela AST (PolarsOperation), 
        garantindo 100% de determinismo matemático.
        """
        if self.df is None:
            return {"error": "No dataframe loaded"}
            
        try:
            # Padrão 1: Group By com Agregação
            if operation.operation_type == "group_by":
                if not operation.group_column:
                    return {"error": "group_column is required for group_by operation"}
                    
                # Se target_columns estiver vazio, tenta inferir colunas numéricas
                target = operation.target_columns
                if not target:
                    # Coleta dtypes para inferência (LazyFrame -> collect .schema)
                    schema = self.df.schema
                    target = [col for col, dtype in schema.items() if dtype in [pl.Int64, pl.Float64, pl.Int32, pl.Float32]]
                
                agg_exprs = []
                for col in target:
                    agg_exprs.append(pl.col(col).sum().alias(f"{col}_sum"))
                    
                if not agg_exprs:
                    agg_exprs = [pl.len().alias("count")]
                    
                sort_col = f"{target[0]}_sum" if target else "count"

                
                result = (
                    self.df
                    .group_by(operation.group_column)
                    .agg(agg_exprs)
                    .sort(sort_col, descending=operation.sort_descending)
                    .limit(operation.limit)
                    .collect()
                )
                return {
                    "query_type": "group_by",
                    "operation": operation.model_dump(),
                    "data": result.to_dicts()
                }
                
            # Padrão 2: Top N
            elif operation.operation_type == "top_n":
                if not operation.target_columns:
                    return {"error": "target_columns is required for top_n sorting"}
                    
                sort_col = operation.target_columns[0]
                result = (
                    self.df
                    .sort(sort_col, descending=operation.sort_descending)
                    .limit(operation.limit)
                    .collect()
                )
                return {
                    "query_type": "top_n",
                    "operation": operation.model_dump(),
                    "data": result.to_dicts()
                }
                
            # Adicione aqui os blocos para "aggregation", "filter" e "describe" de forma similar...
            # (Para esta iteração, garanta que pelo menos group_by e top_n estejam implementados conforme acima)

            return {"error": f"Operation {operation.operation_type} not fully implemented yet."}
            
        except Exception as e:
            return {"error": str(e)}
