from pathlib import Path
from typing import Set, List
from fastapi import APIRouter, Depends, HTTPException
from core.config import settings
from services.pageindex_service import PageIndexService
from core.dependencies import get_page_index_service

router = APIRouter(prefix="/test", tags=["Page Index Endpoints"])

# global variables
base_dir = Path(settings.okf_bundles_dir).resolve()


@router.get("/get_processed_pageindex")
async def get_relevant_databases(
    page_index_service: PageIndexService = Depends(get_page_index_service)
) :

    # 1. Build the tree AND get the string identifier (e.g., "mdms_master")
    active_id = await page_index_service.build_database_index()
    
    # 2. Pass that exact string into the chat client. 
    # The client will silently go to .pageindex_storage/mdms_master.json to run the search.
    #schema = page_index_service.extract_relevant_schema(user_query, active_doc_ids=[active_id])
    
    return active_id


@router.post("/get_schema")
async def get_relevant_databases(
    user_query,
    page_index_service: PageIndexService = Depends(get_page_index_service)
) :

    # 1. Build the tree AND get the string identifier (e.g., "mdms_master")
    active_id = await page_index_service.build_database_index()
    
    # 2. Pass that exact string into the chat client. 
    # The client will silently go to .pageindex_storage/mdms_master.json to run the search.
    schema = page_index_service.extract_relevant_schema(user_query, active_doc_ids=[active_id])
    
    return schema
