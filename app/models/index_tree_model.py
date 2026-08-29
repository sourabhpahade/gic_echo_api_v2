from typing import List
from pydantic import BaseModel, Field

# ==========================================
# --- Phase 1: Table & Join Routing ---
# ==========================================

class Phase1RoutingResult(BaseModel):
    master_plan: str = Field(
        ..., 
        description="Write a single paragraph explaining the required tables, their parent databases, and the join strategy."
    )
    selected_table_node_ids: List[str] = Field(
        default_factory=list,
        description="A flat list containing ONLY the exact node_ids of the tables you want to keep."
    )
    selected_join_node_ids: List[str] = Field(
        default_factory=list,
        description="A flat list containing ONLY the Level 3 node_ids of the specific joins required. Return [] if no joins are needed."
    )


# ==========================================
# --- Phase 2: Column Pruning ---
# ==========================================

class Phase2PruningResult(BaseModel):
    pruning_reason: str = Field(
        ..., 
        description="Explain why specific columns were kept, explicitly mentioning join keys and query requirements."
    )
    retained_column_node_ids: List[str] = Field(
        default_factory=list,
        description="A flat list containing ONLY the exact node_ids of the columns you want to keep."
    )