from pydantic import BaseModel
from typing import Any, Dict, List

class QueryRequest(BaseModel):
    user_input: str

class RelaventDatabasesResponse(BaseModel):
    relevant_databases: List[str]
    reasoning: str

class RelaventTablesResponse(BaseModel):
    relevant_tables: List[str]
    reasoning: str

class QueryResponse(BaseModel):
    status: str 
    seed_tables: List[str]
    pruned_schema: Dict[str, Any]
    sqlcoder_prompt: str

class ColumnDetail(BaseModel):
    column_name: str
    description: str
    selection_reason: str  # <-- NEW: The "thought bucket"
    
class PrunedTableSchema(BaseModel):
    table_path: str = "" # We will inject this in Python, not the LLM
    reasoning: str
    pruned_columns: List[ColumnDetail]

class DatabaseRequest(BaseModel):
    user_input: str
    sql_query : str