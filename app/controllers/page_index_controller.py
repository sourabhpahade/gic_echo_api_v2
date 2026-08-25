from pathlib import Path
from typing import Set, List
from fastapi import APIRouter, Depends, HTTPException
from core.config import settings
from services.pageindex_service import PageIndexService
from core.dependencies import get_page_index_service

router = APIRouter(prefix="/test", tags=["Page Index Endpoints"])

# global variables
base_dir = Path(settings.okf_bundles_dir).resolve()

#LLM Pass 1: Selecting Relevant Databases
@router.get("/get_processed_pageindex")
async def get_relevant_databases(
    page_index_service: PageIndexService = Depends(get_page_index_service)
) :

    result = await page_index_service.inspect_pageindex_tree()

    return result
