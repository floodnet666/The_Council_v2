from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class PolarsOperation(BaseModel):
    operation_type: Literal[
        "aggregation", 
        "group_by", 
        "top_n", 
        "top_n_per_group", 
        "filter", 
        "describe", 
        "correlation", 
        "time_series", 
        "unknown"
    ] = Field(
        description="The exact deterministic operation required to answer the user's query."
    )
    target_columns: List[str] = Field(
        description="The precise numerical or categorical column names from the dataset schema to calculate metrics on."
    )
    group_column: Optional[str] = Field(
        default=None,
        description="The primary categorical column used to segment data if the query implies a grouping, breakdown, or 'per category'."
    )
    group_column_secondary: Optional[str] = Field(
        default=None,
        description="Secondary categorical column if grouping involves multiple dimensions."
    )
    limit: Optional[int] = Field(
        default=10,
        description="The number of rows to return if the query asks for top, bottom, highest, or lowest."
    )
    sort_descending: Optional[bool] = Field(
        default=True,
        description="True if asking for 'top', 'highest', 'best', 'most'. False if 'bottom', 'lowest', 'worst', 'least'."
    )
    filter_condition: Optional[str] = Field(
        default=None,
        description="A clear textual description of any required data filters, e.g., 'only city DES MOINES' or 'after 2015'."
    )
