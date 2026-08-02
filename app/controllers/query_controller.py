from models.query_model import UserQueryRequest, UserQueryResponse;
from fastapi import APIRouter


router = APIRouter(prefix="/query", tags=["OKF Query"])

@router.post("/user_query")
async def user_query(query: UserQueryRequest):
    print(f"The user asked: {query.question}")   
     
    return {
        "status":"success",
        "user_question": query.question
    }
