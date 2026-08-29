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
    master_plan: str = Field(..., description="Write a single paragraph explaining the required tables, their parent databases, and the join strategy.")
    selected_databases: List[SelectedDatabase] = Field(...)
    # The Arrays
    selected_databases: List[SelectedDatabase] = Field(..., description="Hierarchical list of databases and their selected tables.")
    selected_relationships: Optional[List[SelectedRelationshipSource]] = Field(
        default_factory=list, 
        description="Hierarchical list of Source Tables and their Joins. Return [] if no joins are needed."
    )

# --- Phase 2 Column Pruning Models ---

class PrunedColumn(BaseModel):
    node_id: str = Field(..., description="The exact node_id of the column.")
    title: str = Field(..., description="The exact title/string of the column.")

class PrunedTable(BaseModel):
    node_id: str = Field(..., description="The exact node_id of the table.")
    title: str = Field(..., description="The exact title of the table.")
    columns: List[PrunedColumn] = Field(..., description="List of retained columns required for the query or joins.")

class PrunedDatabase(BaseModel):
    node_id: str = Field(..., description="The exact node_id of the database.")
    title: str = Field(..., description="The exact title of the database.")
    tables: List[PrunedTable] = Field(..., description="List of tables containing the pruned columns.")

# --- Phase 2 Column Pruning Models ---

class Phase2PruningResult(BaseModel):
    pruning_reason: str = Field(
        ..., 
        description="Explain why specific columns were kept, explicitly mentioning join keys and query requirements."
    )
    retained_column_node_ids: List[str] = Field(
        ..., 
        description="A flat list containing ONLY the exact node_ids of the columns you want to keep."
    )