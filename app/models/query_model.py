from typing import List

from pydantic import BaseModel

class UserQueryRequest(BaseModel):
    question: str

class UserQueryResponse(BaseModel):
    status: str
    user_question: str
    tables_found_in_folder: List[str]
    generated_sql: str
   # pruned_schemas: List[str]