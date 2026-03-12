import polars as pl
import re
from typing import Dict, Any, List, Optional, Tuple, Literal

SemanticType = Literal["DATE", "ID", "MEASURE", "CATEGORY", "TEXT", "UNKNOWN"]

class SemanticEngine:
    """
    Engine to detect the semantic meaning of data columns.
    Uses name heuristics and sample data validation.
    """
    
    PATTERNS = {
        "DATE": [r'date', r'data', r'ts', r'timestamp', r'created', r'updated', r'ano', r'mes', r'dia', r'year', r'month', r'day', r'prazo'],
        "ID": [r'id$', r'code', r'key', r'pk$', r'sku', r'uuid', r'cnpj', r'cpf', r'matricula', r'identificador', r'zip', r'postal'],
        "MEASURE": [r'price', r'valor', r'total', r'amount', r'qty', r'quantity', r'preco', r'soma', r'mean', r'avg', r'venda', r'lucro', r'custo'],
        "CATEGORY": [r'type', r'tipo', r'cat', r'categoria', r'group', r'grupo', r'status', r'state', r'uf', r'genero', r'gender', r'setor']
    }

    def detect_semantic_types(self, df_sample: pl.DataFrame) -> Dict[str, Dict[str, Any]]:
        """
        Analyzes a sample DataFrame and returns semantic metadata for each column.
        """
        semantic_metadata = {}
        schema = df_sample.schema

        for col in df_sample.columns:
            dtype = str(schema[col])
            values = df_sample[col].to_list()
            
            # Remove nulls for analysis
            clean_values = [v for v in values if v is not None]
            
            # If everything is String (loaded with infer_schema_length=0), 
            # we check if it LOOKS numeric or date
            is_effectively_numeric = False
            is_effectively_date = False
            
            if "String" in dtype or "Utf8" in dtype:
                non_empty = [str(v) for v in clean_values if str(v).strip()]
                if non_empty:
                    # Check for numeric strings
                    if all(re.match(r'^-?\d*\.?\d+$', s) for s in non_empty):
                        is_effectively_numeric = True
                    # Check for date strings
                    if any(re.search(r'\d{2,4}[-/]\d{2}[-/]\d{2,4}', s) for s in non_empty):
                        is_effectively_date = True

            s_type, is_ambiguous, reason = self._infer_single_column(col, clean_values, dtype, is_effectively_numeric, is_effectively_date)
            
            semantic_metadata[col] = {
                "semantic_type": s_type,
                "is_ambiguous": is_ambiguous,
                "ambiguity_reason": reason if is_ambiguous else None,
                "suggested_dtype": self._map_to_technical_type(s_type, dtype, clean_values, is_effectively_numeric)
            }
            
        return semantic_metadata

    def _infer_single_column(self, name: str, values: List[Any], dtype: str, is_eff_numeric: bool = False, is_eff_date: bool = False) -> Tuple[SemanticType, bool, str]:
        name_lower = name.lower()
        
        # 1. Initial clues from name
        clues = []
        for s_type, patterns in self.PATTERNS.items():
            if any(re.search(p, name_lower) for p in patterns):
                clues.append(s_type)

        # 2. Data stats
        unique_count = len(set(values)) if values else 0
        total_count = len(values)
        cardinality_ratio = unique_count / total_count if total_count > 0 else 0
        
        is_numeric = any(t in dtype for t in ["Int", "Float", "Decimal"]) or is_eff_numeric
        is_string = any(t in dtype for t in ["Utf8", "String"]) and not is_eff_numeric
        is_bool = "Bool" in dtype
        
        # Decision Logic
        final_type: SemanticType = "UNKNOWN"
        ambiguous = False
        reason = ""

        # Check for DATE
        if "DATE" in clues or is_eff_date:
            if is_numeric:
                # Might be year/month
                if all(isinstance(v, (int, float)) and 1900 <= v <= 2100 for v in values if v):
                    final_type = "DATE"
                else:
                    final_type = "MEASURE"
                    ambiguous = True
                    reason = f"Column name suggests DATE but values are numeric outside typical year range."
            elif is_string:
                # Check for date pattern in string
                if any(re.search(r'\d{2,4}[-/]\d{2}[-/]\d{2,4}', str(v)) for v in values if v):
                    final_type = "DATE"
                else:
                    final_type = "TEXT"
                    ambiguous = True
                    reason = f"Column name suggests DATE but string values don't match date patterns."
            else:
                final_type = "DATE"
        
        # Check for ID
        elif "ID" in clues:
            if is_numeric:
                # Highly unique or integers
                if cardinality_ratio > 0.9 or unique_count > 100:
                    final_type = "ID"
                else:
                    final_type = "CATEGORY" # Low cardinality ID is usually a category (e.g. status_id)
                    ambiguous = True
                    reason = f"Numeric ID with low cardinality ({unique_count} uniques) behaves more like a CATEGORY."
            else:
                final_type = "ID"

        # Check for MEASURE
        elif "MEASURE" in clues:
            if is_numeric:
                final_type = "MEASURE"
            else:
                final_type = "TEXT"
                ambiguous = True
                reason = f"Name suggests MEASURE but data is non-numeric."

        # Check for CATEGORY
        elif "CATEGORY" in clues:
            final_type = "CATEGORY"
            if is_numeric and unique_count > (total_count * 0.5) and total_count > 10:
                ambiguous = True
                reason = f"Name suggests CATEGORY but numeric data has very high cardinality."

        # Default fallback by data characteristics
        else:
            if is_numeric:
                if unique_count < 10 and total_count > 20:
                    final_type = "CATEGORY" # Inferred category
                    ambiguous = True
                    reason = f"Numeric column with very low cardinality ({unique_count} uniques)."
                else:
                    final_type = "MEASURE"
            elif is_bool:
                final_type = "CATEGORY"
            elif is_string:
                avg_len = sum(len(str(v)) for v in values) / total_count if total_count > 0 else 0
                if unique_count < 20 and cardinality_ratio < 0.3:
                    final_type = "CATEGORY"
                elif "ID" in clues and cardinality_ratio > 0.8 and avg_len < 50:
                    final_type = "ID"
                elif cardinality_ratio > 0.9 and avg_len < 15: # Highly unique but very short might be an ID code
                    final_type = "ID"
                    ambiguous = True
                    reason = "Inferred ID from short unique strings, but no name clue found."
                else:
                    final_type = "TEXT"

        # Final check: Conflict between clues
        if len(clues) > 1:
            ambiguous = True
            reason = f"Conflicting name clues: {clues}"

        return final_type, ambiguous, reason

    def _map_to_technical_type(self, semantic_type: SemanticType, current_dtype: str, sample_values: List[Any], is_eff_numeric: bool = False) -> str:
        """Suggests the best technical Polars type."""
        if semantic_type == "DATE":
            return "Date"
        if semantic_type == "CATEGORY":
            return "Categorical"
        if semantic_type == "MEASURE":
            # If it's effectively numeric but currently String, check if it's float or int
            if is_eff_numeric:
                non_empty = [str(v) for v in sample_values if str(v).strip()]
                if any("." in s for s in non_empty):
                    return "Float64"
                return "Int64"
            return "Float64" if "Float" in current_dtype or "Decimal" in current_dtype else "Int64"
        if semantic_type == "ID":
            return "String" 
        return current_dtype

    def get_casting_plan(self, semantic_metadata: Dict[str, Dict[str, Any]]) -> Dict[str, pl.DataType]:
        """Returns a dictionary of columns and the Polars types they should be cast to."""
        plan = {}
        type_map = {
            "Date": pl.Date,
            "Categorical": pl.Categorical,
            "Float64": pl.Float64,
            "Int64": pl.Int64,
            "String": pl.String,
            "Boolean": pl.Boolean
        }
        
        for col, meta in semantic_metadata.items():
            suggested = meta["suggested_dtype"]
            if suggested in type_map:
                plan[col] = type_map[suggested]
                
        return plan
