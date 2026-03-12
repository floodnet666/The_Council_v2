from typing import Dict, Any, List, Optional
import json
from utils.json_utils import safe_json_dumps


class VisualizationEngine:
    """
    Engine para gerar visualizações baseadas em dados estruturados
    Integrado com QueryEngine para criar gráficos automaticamente
    """
    
    def __init__(self):
        pass
    
    def detect_chart_type_from_query_result(self, query_result: Dict[str, Any]) -> str:
        """
        Detecta o tipo de gráfico mais adequado baseado no resultado do QueryEngine
        """
        query_type = query_result.get("query_type", "unknown")
        
        # Mapeamento: tipo de query → tipo de gráfico
        chart_mapping = {
            "aggregation": "bar",      # Agregações → gráfico de barras
            "group_by": "bar",         # Group by → gráfico de barras
            "top_n": "bar",            # Top N → gráfico de barras horizontal
            "describe": "box",         # Estatísticas → box plot
            "time_series": "line",     # Temporal → linha
            "correlation": "scatter"   # Correlação → scatter
        }
        
        return chart_mapping.get(query_type, "bar")
    
    def create_chart_from_query_result(self, query_result: Dict[str, Any], title: str = None) -> str:
        """
        Cria especificação Plotly baseada no resultado do QueryEngine
        Detecta automaticamente o tipo de gráfico e formata os dados
        """
        query_type = query_result.get("query_type", "unknown")
        
        if query_type == "aggregation":
            return self._create_aggregation_chart(query_result, title)
        elif query_type == "group_by":
            return self._create_group_by_chart(query_result, title)
        elif query_type == "top_n":
            return self._create_top_n_chart(query_result, title)
        elif query_type == "describe":
            return self._create_describe_chart(query_result, title)
        else:
            # Fallback para gráfico genérico
            return self._create_generic_chart(query_result, title)
    
    def _create_aggregation_chart(self, result: Dict[str, Any], title: str = None) -> str:
        """Cria gráfico de barras para agregações"""
        operation = result.get("operation", "sum")
        results = result.get("results", {})
        
        # Extrai labels e valores
        labels = list(results.keys())
        values = list(results.values())
        
        # Remove sufixos (_sum, _mean, etc) dos labels
        clean_labels = [label.replace(f"_{operation}", "") for label in labels]
        
        spec = {
            "data": [
                {
                    "x": clean_labels,
                    "y": values,
                    "type": "bar",
                    "marker": {
                        "color": "#00f0ff",  # Neon Blue
                        "line": {"color": "#7000ff", "width": 1}
                    },
                    "text": values,
                    "textposition": "auto",
                    "texttemplate": "%{y:.2f}"
                }
            ],
            "layout": {
                "title": title or f"{operation.capitalize()} por Coluna",
                "template": "plotly_dark",
                "paper_bgcolor": "rgba(0,0,0,0)",
                "plot_bgcolor": "rgba(0,0,0,0)",
                "font": {"color": "#ededed", "size": 12},
                "xaxis": {"title": "Coluna"},
                "yaxis": {"title": operation.capitalize()},
                "showlegend": False,
                "margin": {"l": 50, "r": 50, "t": 80, "b": 50}
            }
        }
        
        return safe_json_dumps(spec)
    
    def _create_group_by_chart(self, result: Dict[str, Any], title: str = None) -> str:
        """Cria gráfico de barras para group by"""
        group_column = result.get("group_column", "categoria")
        numeric_column = result.get("numeric_column")
        results_list = result.get("results", [])
        
        if not results_list:
            return self._create_empty_chart("Sem dados para visualizar")
        
        # Extrai categorias e valores
        categories = [row.get(group_column, "Unknown") for row in results_list]
        
        # Tenta usar coluna numérica com _sum, senão usa count
        if numeric_column:
            values = [row.get(f"{numeric_column}_sum", row.get("count", 0)) for row in results_list]
            y_label = f"{numeric_column} (Total)"
        else:
            values = [row.get("count", 0) for row in results_list]
            y_label = "Contagem"
        
        spec = {
            "data": [
                {
                    "x": categories,
                    "y": values,
                    "type": "bar",
                    "marker": {
                        "color": "#00f0ff",
                        "line": {"color": "#7000ff", "width": 1}
                    },
                    "text": values,
                    "textposition": "auto",
                    "texttemplate": "%{y:.2f}"
                }
            ],
            "layout": {
                "title": title or f"{y_label} por {group_column.capitalize()}",
                "template": "plotly_dark",
                "paper_bgcolor": "rgba(0,0,0,0)",
                "plot_bgcolor": "rgba(0,0,0,0)",
                "font": {"color": "#ededed", "size": 12},
                "xaxis": {"title": group_column.capitalize()},
                "yaxis": {"title": y_label},
                "showlegend": False,
                "margin": {"l": 50, "r": 50, "t": 80, "b": 50}
            }
        }
        
        return safe_json_dumps(spec)
    
    def _create_top_n_chart(self, result: Dict[str, Any], title: str = None) -> str:
        """Cria gráfico de barras horizontais para top N"""
        n = result.get("n", 10)
        sort_column = result.get("sort_column", "valor")
        results_list = result.get("results", [])
        
        if not results_list:
            return self._create_empty_chart("Sem dados para visualizar")
        
        # Extrai labels (primeira coluna não numérica) e valores
        first_row = results_list[0]
        label_column = None
        
        for key in first_row.keys():
            if key != sort_column and not isinstance(first_row[key], (int, float)):
                label_column = key
                break
        
        if label_column:
            labels = [row.get(label_column, f"Item {i}") for i, row in enumerate(results_list)]
        else:
            labels = [f"Item {i+1}" for i in range(len(results_list))]
        
        values = [row.get(sort_column, 0) for row in results_list]
        
        # Inverte ordem para barras horizontais (maior no topo)
        labels = labels[::-1]
        values = values[::-1]
        
        spec = {
            "data": [
                {
                    "y": labels,
                    "x": values,
                    "type": "bar",
                    "orientation": "h",
                    "marker": {
                        "color": "#00f0ff",
                        "line": {"color": "#7000ff", "width": 1}
                    },
                    "text": values,
                    "textposition": "auto",
                    "texttemplate": "%{x:.2f}"
                }
            ],
            "layout": {
                "title": title or f"Top {n} - {sort_column.capitalize()}",
                "template": "plotly_dark",
                "paper_bgcolor": "rgba(0,0,0,0)",
                "plot_bgcolor": "rgba(0,0,0,0)",
                "font": {"color": "#ededed", "size": 12},
                "xaxis": {"title": sort_column.capitalize()},
                "yaxis": {"title": ""},
                "showlegend": False,
                "margin": {"l": 150, "r": 50, "t": 80, "b": 50}
            }
        }
        
        return safe_json_dumps(spec)
    
    def _create_describe_chart(self, result: Dict[str, Any], title: str = None) -> str:
        """Cria gráfico de estatísticas (box plot ou barras)"""
        numeric_stats = result.get("numeric_stats", {})
        
        if not numeric_stats:
            return self._create_empty_chart("Sem estatísticas numéricas")
        
        # Cria gráfico de barras comparando médias
        columns = list(numeric_stats.keys())
        means = [stats.get("mean", 0) for stats in numeric_stats.values()]
        
        spec = {
            "data": [
                {
                    "x": columns,
                    "y": means,
                    "type": "bar",
                    "marker": {
                        "color": "#00f0ff",
                        "line": {"color": "#7000ff", "width": 1}
                    },
                    "text": means,
                    "textposition": "auto",
                    "texttemplate": "%{y:.2f}"
                }
            ],
            "layout": {
                "title": title or "Médias por Coluna",
                "template": "plotly_dark",
                "paper_bgcolor": "rgba(0,0,0,0)",
                "plot_bgcolor": "rgba(0,0,0,0)",
                "font": {"color": "#ededed", "size": 12},
                "xaxis": {"title": "Coluna"},
                "yaxis": {"title": "Média"},
                "showlegend": False,
                "margin": {"l": 50, "r": 50, "t": 80, "b": 50}
            }
        }
        
        return safe_json_dumps(spec)
    
    def _create_generic_chart(self, result: Dict[str, Any], title: str = None) -> str:
        """Cria gráfico genérico quando tipo não é reconhecido"""
        return self._create_empty_chart(title or "Tipo de visualização não suportado")
    
    def _create_empty_chart(self, message: str) -> str:
        """Cria gráfico vazio com mensagem"""
        spec = {
            "data": [],
            "layout": {
                "title": message,
                "template": "plotly_dark",
                "paper_bgcolor": "rgba(0,0,0,0)",
                "plot_bgcolor": "rgba(0,0,0,0)",
                "font": {"color": "#ededed", "size": 14},
                "annotations": [
                    {
                        "text": message,
                        "xref": "paper",
                        "yref": "paper",
                        "x": 0.5,
                        "y": 0.5,
                        "showarrow": False,
                        "font": {"size": 16, "color": "#ededed"}
                    }
                ]
            }
        }
        
        return safe_json_dumps(spec)
    
    def create_chart_spec(self, data: List[Dict[str, Any]], chart_type: str = "bar", 
                         x_col: str = "x", y_col: str = "y") -> str:
        """
        Método legado para compatibilidade
        Gera especificação Plotly básica
        """
        x_vals = [row.get(x_col) for row in data]
        y_vals = [row.get(y_col) for row in data]
        
        spec = {
            "data": [
                {
                    "x": x_vals,
                    "y": y_vals,
                    "type": chart_type,
                    "marker": {"color": "#00f0ff"}
                }
            ],
            "layout": {
                "title": f"{y_col} vs {x_col}",
                "template": "plotly_dark",
                "paper_bgcolor": "rgba(0,0,0,0)",
                "plot_bgcolor": "rgba(0,0,0,0)",
                "font": {"color": "#ededed"}
            }
        }
        return safe_json_dumps(spec)

