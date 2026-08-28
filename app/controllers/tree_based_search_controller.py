
from pathlib import Path
from fastapi import APIRouter, Depends
from services.tree_based_llm_search_service import TreeBasedLLMSerach
from core.dependencies import get_tree_based_llm_search_service
import json
from fastapi.responses import Response
import time;

router = APIRouter(prefix="/test", tags=["Index Tree Based Search Endpoints"])

@router.get("/get_index_tree")
async def get_index_tree(
    tree_based_search_service: TreeBasedLLMSerach = Depends(get_tree_based_llm_search_service)
) :

    index_tree = await tree_based_search_service.generate_tree_index() 

    # Manually dump to string with indentation
    pretty_json = json.dumps(index_tree, indent=2)
    
    # Return via a raw Response object with the proper header
    return Response(content=pretty_json, media_type="application/json")

@router.get("/get_db_table_tree")
async def get_db_table_tree(
    tree_based_search_service: TreeBasedLLMSerach = Depends(get_tree_based_llm_search_service)
) :

    await tree_based_search_service.initialize_trees()

    pruned_tree = tree_based_search_service.prune_schema_to_level2()

    index_tree = pruned_tree

    # Manually dump to string with indentation
    pretty_json = json.dumps(index_tree, indent=2)
    
    # Return via a raw Response object with the proper header
    return Response(content=pretty_json, media_type="application/json")

@router.post("/get_relevant_db_tbl_rel")
async def get_relevant_db_tbl_rel(
    user_input,
    tree_based_search_service: TreeBasedLLMSerach = Depends(get_tree_based_llm_search_service)
) :

    # 1. Start the stopwatch
    start_time = time.perf_counter()

    await tree_based_search_service.initialize_trees()

    result = await tree_based_search_service.execute_phase1_routing(user_input)

    sanitized_result = tree_based_search_service.sanitize_phase1_output(result)

    # 2. Stop the stopwatch
    end_time = time.perf_counter()

    # 3. Calculate and print the elapsed time
    elapsed_time = end_time - start_time
    print(f"Process completed in {elapsed_time:.4f} seconds \n")
    
    # Return via a raw Response object with the proper header
    return sanitized_result