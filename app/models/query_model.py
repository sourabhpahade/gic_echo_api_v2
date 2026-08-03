from pydantic import BaseModel
from typing import List

class QueryRequest(BaseModel):
    user_input: str

class QueryResponse(BaseModel):
    status: str
    selected_databases: List[str]
    seed_tables: List[str]
    all_resolved_tables: List[str]
    assembled_context: str