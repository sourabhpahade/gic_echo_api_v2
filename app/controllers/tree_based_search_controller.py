
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

@router.post("/get_full_relavent_tree")
async def get_full_relavent_tree(
    user_input: str, # Make sure to type this!
    tree_based_search_service: TreeBasedLLMSerach = Depends(get_tree_based_llm_search_service)
):
    # 1. Start the stopwatch
    start_time = time.perf_counter()

    await tree_based_search_service.initialize_trees()
    result = await tree_based_search_service.execute_phase1_routing(user_input)
    sanitized_result = tree_based_search_service.sanitize_phase1_output(result)

    # FIX: Convert Pydantic model to dictionary, then CALL the extractor method
    phase1_dict = sanitized_result.model_dump() # use .dict() if on older Pydantic v1
    full_relevant_tree = tree_based_search_service.extract_phase2_schema_payload(phase1_dict)

    # 2. Stop the stopwatch
    end_time = time.perf_counter()

    # 3. Calculate and print the elapsed time
    elapsed_time = end_time - start_time
    print(f"Process completed in {elapsed_time:.4f} seconds \n")
    
    # Return the extracted dictionary list
    return full_relevant_tree

@router.post("/get_pruned__db_schema")
async def get_pruned__db_schema(
    user_input: str,
    tree_based_search_service: TreeBasedLLMSerach = Depends(get_tree_based_llm_search_service)
):
    # 1. Start the stopwatch
    start_time = time.perf_counter()
    
    await tree_based_search_service.initialize_trees()
    
    # --- PHASE 1: ROUTING ---
    phase1_result = await tree_based_search_service.execute_phase1_routing(user_input)
    sanitized_phase1 = tree_based_search_service.sanitize_phase1_output(phase1_result)
    
    # --- PHASE 2 PREP: EXTRACTION ---
    phase1_dict = sanitized_phase1.model_dump() # dict() if using Pydantic v1
    extracted_schema = tree_based_search_service.extract_phase2_schema_payload(phase1_dict)
    
    # --- PHASE 2: COLUMN PRUNING ---
    phase2_result = await tree_based_search_service.execute_phase2_pruning(
        user_query=user_input,
        extracted_schema=extracted_schema,
        phase1_relationships=sanitized_phase1.selected_relationships
    )
    
    # 2. Stop the stopwatch
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"Process completed in {elapsed_time:.4f} seconds \n")

    # 3. FINAL MERGE: Rebuild the tree in Python using the LLM's chosen IDs
    retained_ids = set(phase2_result.retained_column_node_ids)
    final_pruned_tree = []
    
    for db in extracted_schema:
        new_db = {
            "node_id": db.get("node_id"), 
            "title": db.get("title"), 
            "tables": []
        }
        for tbl in db.get("nodes", []):
            new_tbl = {
                "node_id": tbl.get("node_id"), 
                "title": tbl.get("title"), 
                "columns": []
            }
            # The columns are stored in the "nodes" key of the table
            for col in tbl.get("nodes", []):
                if col.get("node_id") in retained_ids:
                    new_tbl["columns"].append(col)
            
            # We append the table even if the LLM pruned all its columns, 
            # guaranteeing no tables are ever dropped!
            new_db["tables"].append(new_tbl)
            
        final_pruned_tree.append(new_db)

    # 4. Attach the Phase 1 relationships
    final_output = {
        "pruning_reason": phase2_result.pruning_reason,
        "pruned_schema_tree": final_pruned_tree,
        "selected_relationships": [
            rel.model_dump() for rel in sanitized_phase1.selected_relationships
        ]
    }
    
    return final_output