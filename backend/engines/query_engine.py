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
from utils.logging_config import logger


QueryType = Literal[
    "aggregation",      # sum, count, avg, etc
    "filter",           # filtrar dados
    "group_by",         # agrupar por coluna
    "sort",             # ordenar
    "describe",         # estatísticas descritivas
    "top_n",            # top N valores
    "top_n_per_group",  # top N valores por grupo (rank over partition)
    "time_series",      # análise temporal
    "correlation",      # correlação entre colunas
    "unknown"
]


class QueryEngine:
    """Engine para executar queries determinísticas em DataFrames Polars"""
    
    def __init__(self, df: Optional[pl.LazyFrame] = None):
        self.df = df
        self.cache: Dict[str, Any] = {}
        
        # Synonyms for mapping Portuguese questions to English column names
        self.column_synonyms = {
            "City": ["cidade", "cidades", "city"],
            "County": ["condado", "condados", "county"],
            "Category Name": ["categoria", "categorias", "category"],
            "Vendor Name": ["vendedor", "fabricante", "vendor"],
            "Store Name": ["loja", "lojas", "store"],
            "Bottles Sold": ["garrafas", "bottles", "garrafas vendidas"],
            "Sale (Dollars)": ["faturamento", "receita", "venda", "vendas", "revenue", "valor"],
            "State Bottle Cost": ["custo", "cost"],
            "State Bottle Retail": ["varejo", "retail", "preço"]
        }
        
    def set_dataframe(self, df: pl.LazyFrame):
        """Define o DataFrame para análise"""
        self.df = df
        self.cache.clear()  # Limpa cache quando muda o DataFrame
        
    def detect_query_type(self, query: str) -> QueryType:
        """Detecta o tipo de query baseado em palavras-chave"""
        query_lower = query.lower()
        
        # Padrões para cada tipo de query (Suporta PT, EN, IT)
        patterns = {
            "top_n_per_group": [
                r"\btop\s*\d+\s*.*(por|by|per|for)\s*(categoria|grupo|tipo|produto|ano|category|group)\b",
                r"\b(melhores|best|migliori)\s*\d+\s*.*(por|by|per)\s*(categoria|grupo|tipo)\b"
            ],
            "group_by": [
                r'\b(por|by|per)\s+(categoria|tipo|grupo|category|type|group)\b',
                r'\b(cada|every|ogni)\b.*\b(categoria|tipo|grupo|category|type)\b',
                r'\b(total|soma|média|count|sum|average|media|vendas|gráfico)\b.*\b(por|by|per)\b'
            ],
            "describe": [
                r'\b(estatísticas|statistics|describe|resumo|summary|overview|statistiche)\b'
            ],
            "top_n": [
                r'\b(top \d+|melhores|piores|maiores|menores|best|worst|migliori|peggiori)\b'
            ],
            "aggregation": [
                r'\b(total|soma|sum|somma|média|average|avg|media|count|contar|conteggio|quantos|how many|quanti)\b',
                r'\b(máximo|mínimo|max|min|mais|menos|more|less|più|meno)\b'
            ],
            "filter": [
                r'\b(onde|where|dove|filtrar|filter|filtra|apenas|only|solo)\b'
            ],
            "sort": [
                r'\b(ordenar|sort|ordina|ranking)\b'
            ],
            "time_series": [
                r'\b(ao longo do tempo|over time|nel tempo|temporal|tendência|trend)\b'
            ],
            "correlation": [
                r'\b(correlação|correlation|correlazione|relação|relationship)\b'
            ]
        }
        
        # Verifica cada padrão
        for query_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                if re.search(pattern, query_lower):
                    return query_type
                    
    def _extract_filter_expr(self, query: str, schema_dict) -> Optional[pl.Expr]:
        """Detecta filtros simples (Datas, Números) por regex de forma determinística."""
        query_lower = query.lower()
        expr = None
        
        # 1. Filtro de Data
        # Padrão: "depois de dd/mm/aaaa", "após dd/mm/aaaa"
        date_match = re.search(r'(depois|após|after|posterior)\s+(?:de\s+)?(\d{2}/\d{2}/\d{4})', query_lower)
        if date_match:
            date_str = date_match.group(2)
            for col in schema_dict.keys():
                if col.lower() in ["date", "data"]:
                     from datetime import datetime
                     try:
                         dt = datetime.strptime(date_str, "%d/%m/%Y")
                         expr = pl.col(col) > pl.lit(dt).cast(pl.Date)
                     except:
                         pass
                     break

        # Padrão: "antes de dd/mm/aaaa"
        if not expr:
            date_match = re.search(r'(antes|before|anterior)\s+(?:de\s+)?(\d{2}/\d{2}/\d{4})', query_lower)
            if date_match:
                date_str = date_match.group(2)
                for col in schema_dict.keys():
                    if col.lower() in ["date", "data"]:
                         from datetime import datetime
                         try:
                             dt = datetime.strptime(date_str, "%d/%m/%Y")
                             expr = pl.col(col) < pl.lit(dt).cast(pl.Date)
                         except:
                             pass
                         break
                         
        return expr

    def _match_column(self, query_lower: str, candidates: List[str]) -> Optional[str]:
        """Tenta encontrar uma coluna pelo nome ou sinônimo determinístico"""
        # 1. Match exato/substring (ordena por tamanho decrescente para priorizar colunas mais longas/específicas)
        sorted_candidates = sorted(candidates, key=len, reverse=True)
        for cand in sorted_candidates:
            if cand.lower() in query_lower:
                return cand
                
        # 2. Match por sinônimos
        for col_name, syns in getattr(self, "column_synonyms", {}).items():
            if col_name in candidates:
                for syn in syns:
                    if re.search(r'\b' + re.escape(syn) + r'\b', query_lower):
                        return col_name
                        
        return None
        
    def execute_aggregation(self, query: str, columns: List[str]) -> Dict[str, Any]:
        """Executa agregações (sum, count, avg, etc)"""
        if self.df is None:
            return {"error": "No dataframe loaded"}
            
        query_lower = query.lower()
        results = {}
        
        # Filtro determinístico
        df = self.df
        schema = df.collect_schema()
        filter_expr = self._extract_filter_expr(query, schema)
        if filter_expr is not None:
            logger.info(f"Deterministic Filter applied: {filter_expr}")
            df = df.filter(filter_expr)
        else:
            # Se fitro determinístico falhou, força fallback se houver indicadores de filtro
            filter_indicators = ["=", ">", "<", "quando", "se", "mês", "mes", "ano", "true", "false", "filtre", "filtrar"]
            if any(word in query_lower for word in filter_indicators):
                return {"error": "Filtro detectado na query mas não suportado determinísticamente pelo QueryEngine. Use SQL."}
            
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
                result = df.select(pl.len().alias("count")).collect()
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
                    result = df.select(agg_exprs).collect(streaming=True)
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
        df = self.df  # Define local df for queries below
        query_lower = query.lower()
        filter_expr = self._extract_filter_expr(query, schema)
        if filter_expr is not None:
            logger.info(f"Deterministic Filter applied in groupby: {filter_expr}")
            df = df.filter(filter_expr)
        else:
            # Se fitro determinístico falhou, força fallback se houver indicadores de filtro
            filter_indicators = ["=", ">", "<", "quando", "se", "mês", "mes", "ano", "true", "false", "filtre", "filtrar"]
            if any(word in query_lower for word in filter_indicators):
                return {"error": "Filtro detectado na query de agrupamento mas não suportado pelo QueryEngine. Use SQL."}
        
        
        if not columns:
            columns = schema.names()
            
        # Tenta encontrar colunas mencionadas na query ou heurística
        group_cols = []
        query_lower = query.lower()
        
        # Heurística: se mencionou "ano", tenta achar coluna de data
        if "ano" in query_lower or "year" in query_lower:
            for col, dtype in schema.items():
                if dtype in [pl.Date, pl.Datetime]:
                    group_cols.append(pl.col(col).dt.year().alias("year"))
                    break
                    
        # Heurística: colunas categóricas mencionadas ou primeiras disponíveis
        candidates = [col for col, dtype in schema.items() if dtype in [pl.Utf8, pl.Categorical, pl.String]]
        matched_cand = self._match_column(query_lower, candidates)
        if matched_cand:
            if matched_cand not in [c.meta.output_name() if hasattr(c, "meta") else str(c) for c in group_cols]:
                group_cols.append(pl.col(matched_cand))
        
        # Fallback: primeira categórica se nada foi achado
        if not group_cols and candidates:
            group_cols.append(pl.col(candidates[0]))
                
        if not group_cols:
            return {"error": "No grouping columns found"}
            
        # Identifica colunas numéricas para agregação
        numeric_cols = [
            col for col, dtype in schema.items() 
            if dtype in [pl.Int64, pl.Int32, pl.Float64, pl.Float32, pl.Int8, pl.Int16]
        ]
        
        # Especial para vendas
        target_col = self._match_column(query_lower, numeric_cols)
        
        if not target_col and numeric_cols:
            target_col = numeric_cols[0]
        
        if not numeric_cols:
            # Se não há colunas numéricas, apenas conta
            try:
                result = (
                    df
                    .group_by(group_cols)
                    .agg(pl.len().alias("count"))
                    .sort("count", descending=True)
                    .limit(100)
                    .collect(streaming=True)
                )
                return {
                    "query_type": "group_by",
                    "group_columns": [str(c) for c in group_cols],
                    "results": result.to_dicts(),
                    "operation": "count"
                }
            except Exception as e:
                return {"error": str(e)}
        
        # Com colunas numéricas, faz agregação
        try:
            agg_exprs = [pl.len().alias("count")]
            agg_exprs.append(pl.col(target_col).sum().alias(f"{target_col}_sum"))
            agg_exprs.append(pl.col(target_col).mean().alias(f"{target_col}_mean"))
                
            result = (
                df
                .group_by(group_cols)
                .agg(agg_exprs)
                .sort(f"{target_col}_sum", descending=True)
                .limit(100)
                .collect(streaming=True)
            )
            
            return {
                "query_type": "group_by",
                "group_columns": [str(c) for c in group_cols],
                "target_column": target_col,
                "results": result.to_dicts()
            }
        except Exception as e:
            return {"error": str(e)}
    
    def execute_describe(self) -> Dict[str, Any]:
        """Retorna estatísticas descritivas do DataFrame de forma preguiçosa (lazy)"""
        if self.df is None:
            return {"error": "No dataframe loaded"}
            
        try:
            # 1. Get Schema and Column Names
            schema = self.df.collect_schema()
            columns = schema.names()
            
            # 2. Identify numeric columns
            numeric_cols = [
                col for col, dtype in schema.items() 
                if dtype in [pl.Int64, pl.Int32, pl.Float64, pl.Float32, pl.Int8, pl.Int16]
            ]
            
            # 3. Build aggregation expressions for all numeric columns
            agg_exprs = [pl.len().alias("row_count")]
            for col in numeric_cols:
                agg_exprs.extend([
                    pl.col(col).mean().alias(f"{col}_mean"),
                    pl.col(col).min().alias(f"{col}_min"),
                    pl.col(col).max().alias(f"{col}_max"),
                    pl.col(col).null_count().alias(f"{col}_null_count")
                ])
            
            # 4. Collect Only Aggregations
            logger.info(f"Describing dataset with {len(numeric_cols)} numeric columns (Lazy)...")
            results_df = self.df.select(agg_exprs).collect()
            results_dict = results_df.to_dicts()[0]
            
            stats = {
                "query_type": "describe",
                "row_count": results_dict.get("row_count"),
                "column_count": len(columns),
                "columns": columns,
                "dtypes": {k: str(v) for k, v in schema.items()},
                "numeric_stats": {}
            }
            
            # 5. Restructure results for frontend
            for col in numeric_cols:
                stats["numeric_stats"][col] = {
                    "mean": results_dict.get(f"{col}_mean"),
                    "min": results_dict.get(f"{col}_min"),
                    "max": results_dict.get(f"{col}_max"),
                    "null_count": results_dict.get(f"{col}_null_count")
                }
                    
            return stats
            
        except Exception as e:
            logger.error(f"Error in execute_describe: {e}")
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
            
        sort_col = self._match_column(query.lower(), numeric_cols)
        if not sort_col:
            sort_col = numeric_cols[0]
            
        descending = "maior" in query.lower() or "top" in query.lower() or "melhores" in query.lower()
        
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

    def execute_top_n_per_group(self, query: str) -> Dict[str, Any]:
        """Executa Top N por grupo (ex: Top 3 produtos por categoria)"""
        if self.df is None:
            return {"error": "No dataframe loaded"}
            
        query_lower = query.lower()
        schema = self.df.collect_schema()
        
        # 1. Extrair N
        n = 5
        match_n = re.search(r'\b(\d+)\b', query)
        if match_n: n = int(match_n.group(1))
        
        # 2. Identificar Grupos e Alvos
        candidates = schema.names()
        group_col = None
        target_col = None
        
        # Heurística para grupo (ex: "por categoria")
        match_group = re.search(r"por\s+(\w+)", query_lower)
        if match_group:
            g_name = match_group.group(1)
            for col in candidates:
                if g_name in col.lower():
                    group_col = col
                    break
                    
        # Heurística para alvo (ex: "top 3 produtos")
        for col in candidates:
            if col.lower() in query_lower and col != group_col:
                target_col = col
                break
        
        # Fallbacks
        if not group_col:
            cat_cols = [c for c, t in schema.items() if t in [pl.Utf8, pl.String, pl.Categorical]]
            group_col = cat_cols[0] if cat_cols else None
            
        if not target_col:
            cat_cols = [c for c, t in schema.items() if t in [pl.Utf8, pl.String, pl.Categorical] and c != group_col]
            target_col = cat_cols[0] if cat_cols else None

        if not group_col or not target_col:
            return {"error": f"Não foi possível identificar grupo ({group_col}) ou alvo ({target_col}) para Ranking."}

        # 3. Execução Window Function (Lazy)
        try:
             # Usamos contagem como métrica de 'mais vendidos' se não houver coluna 'vendas'
             # Se houver 'vendas', usamos soma
             agg_expr = pl.len().alias("count")
             sort_col = "count"
             
             if "vendas" in schema.names():
                  agg_expr = pl.col("vendas").sum().alias("total_vendas")
                  sort_col = "total_vendas"
             
             # Group By + Rank Over Partition
             res = (
                 self.df
                 .group_by([group_col, target_col])
                 .agg(agg_expr)
                 .with_columns(
                     pl.col(sort_col).rank("desc").over(group_col).alias("rank")
                 )
                 .filter(pl.col("rank") <= n)
                 .sort([group_col, "rank"])
                 .limit(100) # Safety limit for result sets
                 .collect()
             )
             
             return {
                 "query_type": "top_n_per_group",
                 "n": n,
                 "group_column": group_col,
                 "target_column": target_col,
                 "metric": sort_col,
                 "results": res.to_dicts()
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
        elif query_type == "top_n_per_group":
            result = self.execute_top_n_per_group(query)
        elif query_type == "group_by":
            result = self.execute_group_by(query, columns)
        elif query_type == "describe":
            result = self.execute_describe()
        elif query_type == "top_n":
            result = self.execute_top_n(query)
        else:
            # Fallback: retorna erro para acionar o fallback SQL no AnalystAgent
            return {"error": f"Tipo de query '{query_type}' não suportado de forma determinística por Regex."}
            
        # Adiciona metadata
        if isinstance(result, dict) and "error" not in result:
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
