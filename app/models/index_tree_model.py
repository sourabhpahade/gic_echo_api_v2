from typing import List, Optional
from pydantic import BaseModel, Field

# --- Schema Tree Models ---
class SelectedTable(BaseModel):
    node_id: str = Field(..., description="The exact node_id of the table from the schema tree.")
    title: str = Field(..., description="The table name/title from the schema tree.")

class SelectedDatabase(BaseModel):
    node_id: str = Field(..., description="The exact node_id of the database from the schema tree.")
    title: str = Field(..., description="The database name/title from the schema tree.")
    tables: List[SelectedTable] = Field(default_factory=list)

# --- Relationship Tree Models ---
class SelectedJoin(BaseModel):
    node_id: str = Field(..., description="The Level 3 node_id of the specific join logic.")
    title: str = Field(..., description="The specific target join logic string.")

class SelectedRelationshipSource(BaseModel):
    node_id: str = Field(..., description="The Level 2 node_id of the Source Table in the relationship tree.")
    title: str = Field(..., description="The Source Table name/title.")
    joins: List[SelectedJoin] = Field(..., description="List of specific Level 3 joins branching from this source table.")

# --- Final Output Model ---
class Phase1RoutingResult(BaseModel):
    selection_reason: str = Field(..., description="Master Plan: Detailed explanation of the query intent. MUST be generated first.")
    selected_databases: List[SelectedDatabase] = Field(...)
    selected_relationships: Optional[List[SelectedRelationshipSource]] = Field(
        default_factory=list, 
        description="Hierarchical list of Source Tables and their Joins. Return [] if no joins are needed."
    )