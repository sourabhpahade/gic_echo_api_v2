from pathlib import Path
from fastapi import APIRouter, Depends
from services.tree_based_llm_search_service import TreeBasedLLMSerach
from core.dependencies import get_tree_based_llm_search_service
import json
from fastapi.responses import Response
import time


router = APIRouter(prefix="/test", tags=["Index Tree Based Search Endpoints"])

@router.get("/get_index_tree")
async def get_index_tree(
    tree_based_search_service: TreeBasedLLMSerach = Depends(get_tree_based_llm_search_service)
):
    index_tree = await tree_based_search_service.generate_tree_index() 

    # Manually dump to string with indentation
    pretty_json = json.dumps(index_tree, indent=2)
    
    # Return via a raw Response object with the proper header
    return Response(content=pretty_json, media_type="application/json")

@router.get("/get_db_table_tree")
async def get_db_table_tree(
    tree_based_search_service: TreeBasedLLMSerach = Depends(get_tree_based_llm_search_service)
):
    await tree_based_search_service.initialize_trees()

    pruned_tree = tree_based_search_service.prune_schema_to_level2()

    # Manually dump to string with indentation
    pretty_json = json.dumps(pruned_tree, indent=2)
    
    # Return via a raw Response object with the proper header
    return Response(content=pretty_json, media_type="application/json")

@router.post("/get_relevant_db_tbl_rel")
async def get_relevant_db_tbl_rel(
    user_input: str,
    tree_based_search_service: TreeBasedLLMSerach = Depends(get_tree_based_llm_search_service)
):
    # 1. Start the stopwatch
    start_time = time.perf_counter()

    await tree_based_search_service.initialize_trees()

    # --- Run Phase 1 Routing ---
    result = await tree_based_search_service.execute_phase1_routing(user_input)
    sanitized_result = tree_based_search_service.sanitize_phase1_output(result)

    # --- Reconstruct Relevant DB -> Table Tree (No Columns) ---
    # Get the base Level 1 & Level 2 schema
    level2_schema = tree_based_search_service.prune_schema_to_level2()
    
    selected_table_ids = set(sanitized_result.selected_table_node_ids)
    relevant_db_tbl_tree = []
    
    # Filter the base schema using the LLM's selected IDs
    for db in level2_schema:
        new_db = {
            "title": db.get("title"),
            "node_id": db.get("node_id"),
            "nodes": []
        }
        for tbl in db.get("nodes", []):
            if str(tbl.get("node_id")) in selected_table_ids:
                new_db["nodes"].append(tbl)
        
        # Only append the database if it contains selected tables
        if new_db["nodes"]:
            relevant_db_tbl_tree.append(new_db)

    # --- Reconstruct Relationships ---
    phase1_dict = sanitized_result.model_dump()
    extracted_relationships = tree_based_search_service.extract_phase1_relationships(phase1_dict)

    # 2. Stop the stopwatch
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"Process completed in {elapsed_time:.4f} seconds \n")
    
    # Return the clean, column-free tree and the relationships
    return {
        "master_plan": sanitized_result.master_plan,
        "relevant_db_table_tree": relevant_db_tbl_tree,
        "relevant_relationships": extracted_relationships
    }

@router.post("/get_full_relavent_tree")
async def get_full_relavent_tree(
    user_input: str, 
    tree_based_search_service: TreeBasedLLMSerach = Depends(get_tree_based_llm_search_service)
):
    # 1. Start the stopwatch
    start_time = time.perf_counter()

    await tree_based_search_service.initialize_trees()
    result = await tree_based_search_service.execute_phase1_routing(user_input)
    sanitized_result = tree_based_search_service.sanitize_phase1_output(result)

    # Convert Pydantic model to dictionary
    phase1_dict = sanitized_result.model_dump()
    
    # Dynamically build both the Schema and Relationship trees from the flat IDs
    extracted_schema = tree_based_search_service.extract_phase2_schema_payload(phase1_dict)
    extracted_relationships = tree_based_search_service.extract_phase1_relationships(phase1_dict)

    # 2. Stop the stopwatch
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"Process completed in {elapsed_time:.4f} seconds \n")
    
    # Return both reconstructed trees for debugging/validation
    return {
        "extracted_schema": extracted_schema,
        "extracted_relationships": extracted_relationships
    }

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
    
    # --- PHASE 2 PREP: EXTRACTION IN PYTHON ---
    phase1_dict = sanitized_phase1.model_dump() 
    
    # We must extract BOTH the schema and the relationships from the flat IDs here
    extracted_schema = tree_based_search_service.extract_phase2_schema_payload(phase1_dict)
    extracted_relationships = tree_based_search_service.extract_phase1_relationships(phase1_dict)
    
    # --- PHASE 2: COLUMN PRUNING ---
    phase2_result = await tree_based_search_service.execute_phase2_pruning(
        user_query=user_input,
        extracted_schema=extracted_schema,
        phase1_relationships=extracted_relationships # Pass the Python-extracted dicts directly
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

    # 4. Attach the Python-extracted Phase 1 relationships to the final output
    final_output = {
        "pruning_reason": phase2_result.pruning_reason,
        "pruned_schema_tree": final_pruned_tree,
        "selected_relationships": extracted_relationships
    }
    
    return final_output

import time
import json
from fastapi import APIRouter, Depends
from fastapi.responses import Response

@router.post("/generate_sql")
async def generate_sql(
    user_input: str,
    tree_based_search_service: TreeBasedLLMSerach = Depends(get_tree_based_llm_search_service)
):
    # 1. Start the stopwatch
    start_time = time.perf_counter()
    await tree_based_search_service.initialize_trees()

    # --- PHASE 1: ROUTING ---
    phase1_result = await tree_based_search_service.execute_phase1_routing(user_input)
    sanitized_phase1 = tree_based_search_service.sanitize_phase1_output(phase1_result)

    # --- PHASE 2 PREP: EXTRACTION IN PYTHON ---
    phase1_dict = sanitized_phase1.model_dump()
    extracted_schema = tree_based_search_service.extract_phase2_schema_payload(phase1_dict)
    extracted_relationships = tree_based_search_service.extract_phase1_relationships(phase1_dict)

    # PRINT LLM PASS 1 FULL TREE
    print("========================================")
    print("       LLM PASS 1: EXTRACTED TREE       ")
    print("========================================")
    pass1_print_payload = {
        "extracted_schema": extracted_schema,
        "extracted_relationships": extracted_relationships
    }
    print(json.dumps(pass1_print_payload, indent=2))
    print("\n")

    # --- PHASE 2: COLUMN PRUNING ---
    phase2_result = await tree_based_search_service.execute_phase2_pruning(
        user_query=user_input,
        extracted_schema=extracted_schema,
        phase1_relationships=extracted_relationships
    )

    # Rebuild the perfectly pruned tree in Python using the LLM's chosen IDs
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
            
            new_db["tables"].append(new_tbl)
        final_pruned_tree.append(new_db)

    # PRINT LLM PASS 2 FULL TREE
    print("========================================")
    print("        LLM PASS 2: PRUNED TREE         ")
    print("========================================")
    pass2_print_payload = {
        "pruning_reason": phase2_result.pruning_reason,
        "pruned_schema_tree": final_pruned_tree,
        "required_joins": extracted_relationships
    }
    print(json.dumps(pass2_print_payload, indent=2))
    print("\n")

    # --- PHASE 3: SQL GENERATION ---
    final_sql = await tree_based_search_service.execute_phase3_sql_generation(
        user_query=user_input,
        pruned_schema=final_pruned_tree,
        required_joins=extracted_relationships
    )

    # 2. Stop the stopwatch
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"Full Text-to-SQL pipeline completed in {elapsed_time:.4f} seconds \n")

    # Return the clean SQL string as a plain text response
    return Response(content=final_sql, media_type="text/plain")