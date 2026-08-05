from pydantic import BaseModel
from typing import Any, Dict, List

class QueryRequest(BaseModel):
    user_input: str

class QueryResponse(BaseModel):
    status: str 
    seed_tables: List[str]
    pruned_schema: Dict[str, Any]
    sqlcoder_prompt: str