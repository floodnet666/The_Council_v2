from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class PolarsOperation(BaseModel):
    operation_type: Literal["aggregation", "group_by", "top_n", "filter", "describe"] = Field(
        description="The exact deterministic operation required to answer the user's query."
    )
    target_columns: List[str] = Field(
        default_factory=list,
        description="The precise column names from the dataset schema to calculate metrics on."
    )
    group_column: Optional[str] = Field(
        default=None,
        description="The categorical column used to segment data if the query implies a grouping or breakdown."
    )
    limit: Optional[int] = Field(
        default=10,
        description="The number of rows to return if the query asks for top, bottom, highest, or lowest."
    )
    sort_descending: Optional[bool] = Field(
        default=True,
        description="True if asking for 'top', 'highest', 'best'. False if 'bottom', 'lowest', 'worst'."
    )
class DualSqlOperation(BaseModel):
    visual_query: str = Field(
        description="A query SQL em dialeto PostgreSQL (compatível com Polars SQLContext) a ser executada na tabela 'data' para retornar a granularidade visual bruta (os dados que irão para o Gráfico ou Tabela)."
    )
    analytical_query: str = Field(
        description="A query SQL em dialeto PostgreSQL focada puramente na agregação global (MIN, MAX, AVG, CORR, SUM). Ela retorna os Contornos, Padrões e Correlações resumidos (1 linha estatística) para que o Analista possa discursar sobre causalidade."
    )

class ChartSchema(BaseModel):
    chart_type: Literal["bar", "line", "pie", "scatter"] = Field(description="Tipo de gráfico")
    x_axis: str = Field(description="Nome da coluna para o eixo X")
    y_axis: str = Field(description="Nome da coluna para o eixo Y")
    title: Optional[str] = Field(default=None, description="Título do gráfico")
