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
