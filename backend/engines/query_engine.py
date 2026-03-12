"""
QueryEngine - Executa análises determinísticas em DataFrames Polars
Detecta tipo de query e executa operações sem depender de LLM
"""
import polars as pl
from typing import Dict, Any, List, Optional, Literal
import json
from utils.json_utils import safe_json_dumps
import re
from datetime import datetime


QueryType = Literal[
    "aggregation",      # sum, count, avg, etc
    "filter",           # filtrar dados
    "group_by",         # agrupar por coluna
    "sort",             # ordenar
    "describe",         # estatísticas descritivas
    "top_n",            # top N valores
    "time_series",      # análise temporal
    "correlation",      # correlação entre colunas
    "unknown"
]


class QueryEngine:
    """Engine para executar queries determinísticas em DataFrames Polars"""
    
    def __init__(self, df: Optional[pl.LazyFrame] = None):
        self.df = df
        self.cache: Dict[str, Any] = {}
        
    def set_dataframe(self, df: pl.LazyFrame):
        """Define o DataFrame para análise"""
        self.df = df
        self.cache.clear()  # Limpa cache quando muda o DataFrame
        
    def detect_query_type(self, query: str) -> QueryType:
        """Detecta o tipo de query baseado em palavras-chave"""
        query_lower = query.lower()
        
        # Padrões para cada tipo de query
        # IMPORTANTE: Ordem importa! Padrões mais específicos primeiro
        patterns = {
            "group_by": [
                r'\b(por categoria|por tipo|group by|agrupar por)\b',
                r'\b(cada|every)\b.*\b(categoria|tipo|grupo|class)\b',
                r'\b(total|soma|média|count).*\b(por categoria|por tipo|por)\b'
            ],
            "describe": [
                r'\b(estatísticas|statistics|describe|resumo|summary|overview)\b'
            ],
            "top_n": [
                r'\b(top \d+|melhores|piores)\b',
                r'\b(\d+ maiores|\d+ menores)\b'
            ],
            "aggregation": [
                r'\b(total|soma|sum|média|average|avg|count|contar|quantos)\b',
                r'\b(máximo|mínimo|max|min)\b'
            ],
            "filter": [
                r'\b(onde|where|filtrar|filter|apenas|only|somente)\b',
                r'\b(maior que|menor que|igual a|greater|less|equal)\b'
            ],
            "sort": [
                r'\b(ordenar|sort|ranking)\b'
            ],
            "time_series": [
                r'\b(ao longo do tempo|over time|temporal|tendência|trend)\b',
                r'\b(por mês|por ano|por dia|monthly|yearly|daily)\b'
            ],
            "correlation": [
                r'\b(correlação|correlation|relação|relationship)\b'
            ]
        }
        
        # Verifica cada padrão
        for query_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                if re.search(pattern, query_lower):
                    return query_type
                    
        return "unknown"
    
    def execute_aggregation(self, query: str, columns: List[str]) -> Dict[str, Any]:
        """Executa agregações (sum, count, avg, etc)"""
        if self.df is None:
            return {"error": "No dataframe loaded"}
            
        query_lower = query.lower()
        results = {}
        
        # Detecta operação
        if any(word in query_lower for word in ["total", "soma", "sum"]):
            operation = "sum"
        elif any(word in query_lower for word in ["média", "average", "avg"]):
            operation = "mean"
        elif any(word in query_lower for word in ["count", "contar", "quantos"]):
            operation = "count"
        elif any(word in query_lower for word in ["máximo", "max"]):
            operation = "max"
        elif any(word in query_lower for word in ["mínimo", "min"]):
            operation = "min"
        else:
            operation = "sum"  # default
            
        # Identifica colunas numéricas
        schema = self.df.collect_schema()
        numeric_cols = [
            col for col, dtype in schema.items() 
            if dtype in [pl.Int64, pl.Int32, pl.Float64, pl.Float32, pl.Int8, pl.Int16]
        ]
        
        # Executa agregação
        try:
            if operation == "count":
                result = self.df.select(pl.len().alias("count")).collect()
                results["count"] = result["count"][0]
            else:
                agg_exprs = []
                for col in numeric_cols:
                    if operation == "sum":
                        agg_exprs.append(pl.col(col).sum().alias(f"{col}_sum"))
                    elif operation == "mean":
                        agg_exprs.append(pl.col(col).mean().alias(f"{col}_mean"))
                    elif operation == "max":
                        agg_exprs.append(pl.col(col).max().alias(f"{col}_max"))
                    elif operation == "min":
                        agg_exprs.append(pl.col(col).min().alias(f"{col}_min"))
                        
                if agg_exprs:
                    result = self.df.select(agg_exprs).collect()
                    results = result.to_dicts()[0]
                    
        except Exception as e:
            return {"error": str(e)}
            
        return {
            "query_type": "aggregation",
            "operation": operation,
            "results": results,
            "columns_analyzed": numeric_cols
        }
    
    def execute_group_by(self, query: str, columns: List[str]) -> Dict[str, Any]:
        """Executa group by em colunas categóricas"""
        if self.df is None:
            return {"error": "No dataframe loaded"}
            
        schema = self.df.collect_schema()
        
        # Identifica coluna de agrupamento (primeira coluna categórica ou string)
        group_col = None
        for col, dtype in schema.items():
            if dtype in [pl.Utf8, pl.Categorical, pl.String]:
                group_col = col
                break
                
        if not group_col:
            return {"error": "No categorical column found for grouping"}
            
        # Identifica colunas numéricas para agregação
        numeric_cols = [
            col for col, dtype in schema.items() 
            if dtype in [pl.Int64, pl.Int32, pl.Float64, pl.Float32, pl.Int8, pl.Int16]
        ]
        
        if not numeric_cols:
            # Se não há colunas numéricas, apenas conta
            try:
                result = (
                    self.df
                    .group_by(group_col)
                    .agg(pl.len().alias("count"))
                    .sort("count", descending=True)
                    .collect()
                )
                return {
                    "query_type": "group_by",
                    "group_column": group_col,
                    "results": result.to_dicts(),
                    "operation": "count"
                }
            except Exception as e:
                return {"error": str(e)}
        
        # Com colunas numéricas, faz agregação
        try:
            agg_exprs = [pl.len().alias("count")]
            
            # Adiciona sum para primeira coluna numérica
            if numeric_cols:
                agg_exprs.append(pl.col(numeric_cols[0]).sum().alias(f"{numeric_cols[0]}_sum"))
                agg_exprs.append(pl.col(numeric_cols[0]).mean().alias(f"{numeric_cols[0]}_mean"))
                
            result = (
                self.df
                .group_by(group_col)
                .agg(agg_exprs)
                .sort("count", descending=True)
                .collect()
            )
            
            return {
                "query_type": "group_by",
                "group_column": group_col,
                "numeric_column": numeric_cols[0] if numeric_cols else None,
                "results": result.to_dicts()
            }
        except Exception as e:
            return {"error": str(e)}
    
    def execute_describe(self) -> Dict[str, Any]:
        """Retorna estatísticas descritivas do DataFrame"""
        if self.df is None:
            return {"error": "No dataframe loaded"}
            
        try:
            # Coleta estatísticas básicas
            df_collected = self.df.collect()
            
            stats = {
                "query_type": "describe",
                "row_count": len(df_collected),
                "column_count": len(df_collected.columns),
                "columns": df_collected.columns,
                "dtypes": {k: str(v) for k, v in df_collected.schema.items()},
                "numeric_stats": {}
            }
            
            # Estatísticas para colunas numéricas
            for col in df_collected.columns:
                if df_collected[col].dtype in [pl.Int64, pl.Int32, pl.Float64, pl.Float32, pl.Int8, pl.Int16]:
                    stats["numeric_stats"][col] = {
                        "mean": float(df_collected[col].mean()),
                        "median": float(df_collected[col].median()),
                        "std": float(df_collected[col].std()),
                        "min": float(df_collected[col].min()),
                        "max": float(df_collected[col].max()),
                        "null_count": int(df_collected[col].null_count())
                    }
                    
            return stats
            
        except Exception as e:
            return {"error": str(e)}
    
    def execute_top_n(self, query: str, n: int = 10) -> Dict[str, Any]:
        """Retorna top N registros"""
        if self.df is None:
            return {"error": "No dataframe loaded"}
            
        # Extrai N da query se possível
        match = re.search(r'\b(\d+)\b', query)
        if match:
            n = int(match.group(1))
            
        # Identifica coluna numérica para ordenar
        schema = self.df.collect_schema()
        numeric_cols = [
            col for col, dtype in schema.items() 
            if dtype in [pl.Int64, pl.Int32, pl.Float64, pl.Float32, pl.Int8, pl.Int16]
        ]
        
        if not numeric_cols:
            return {"error": "No numeric column found for ranking"}
            
        sort_col = numeric_cols[0]
        descending = "maior" in query.lower() or "top" in query.lower()
        
        try:
            result = (
                self.df
                .sort(sort_col, descending=descending)
                .limit(n)
                .collect()
            )
            
            return {
                "query_type": "top_n",
                "n": n,
                "sort_column": sort_col,
                "descending": descending,
                "results": result.to_dicts()
            }
        except Exception as e:
            return {"error": str(e)}
    
    def execute_query(self, query: str) -> Dict[str, Any]:
        """
        Executa query detectando automaticamente o tipo
        Retorna resultado estruturado em JSON
        """
        # Verifica cache
        cache_key = f"{query}_{id(self.df)}"
        if cache_key in self.cache:
            return self.cache[cache_key]
            
        if self.df is None:
            return {"error": "No dataframe loaded"}
            
        # Detecta tipo de query
        query_type = self.detect_query_type(query)
        schema = self.df.collect_schema()
        columns = schema.names()
        
        # Executa baseado no tipo
        result = None
        
        if query_type == "aggregation":
            result = self.execute_aggregation(query, columns)
        elif query_type == "group_by":
            result = self.execute_group_by(query, columns)
        elif query_type == "describe":
            result = self.execute_describe()
        elif query_type == "top_n":
            result = self.execute_top_n(query)
        else:
            # Fallback: retorna estatísticas gerais
            result = self.execute_describe()
            
        # Adiciona metadata
        if result and "error" not in result:
            result["timestamp"] = datetime.now().isoformat()
            result["original_query"] = query
            
        # Cacheia resultado
        self.cache[cache_key] = result
        
        return result
    
    def format_result_for_llm(self, result: Dict[str, Any]) -> str:
        """
        Formata resultado para ser usado pelo LLM
        Retorna string formatada com dados estruturados
        """
        if "error" in result:
            return f"ERROR: {result['error']}"
            
        # Formato: ANALYSIS_DATA: {json} para parsing fácil
        json_data = safe_json_dumps(result, indent=2)
        return f"ANALYSIS_DATA:\n{json_data}"
