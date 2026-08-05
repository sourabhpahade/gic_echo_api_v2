from pathlib import Path
from typing import Set, List
from fastapi import APIRouter, Depends, HTTPException

from models.query_model import QueryRequest, QueryResponse
from services.llm_router_service import LLMRouterService
from services.okf_dependency_service import OKFDependencyService
from core.dependencies import get_llm_router_service, get_okf_dependency_service
from core.config import settings

router = APIRouter(prefix="/query", tags=["Text-to-SQL Routing"])

@router.post("/assemble-context", response_model=QueryResponse)
async def assemble_sql_context(
    request: QueryRequest,
    llm_router: LLMRouterService = Depends(get_llm_router_service),
    dependency_service: OKFDependencyService = Depends(get_okf_dependency_service)
):

    # Step 1 : Selecting Relevant Databases (LLM Pass 1)
    print("----------------------------------------------------------------\n # LLM Pass 1: Selecting Relevant Databases \n")
    base_dir = Path(settings.okf_bundles_dir).resolve()
    global_index_path = base_dir / "index.md"

    print(f"Global index path: {global_index_path}")

    if not global_index_path.exists():
        raise HTTPException(status_code=500, detail=f"Global index.md not found at {global_index_path}")
        
    with open(global_index_path, "r", encoding="utf-8") as f:
        global_index_content = f.read()

    selected_databases = await llm_router.execute_routing_pass(
        request.user_input, global_index_content
    )
 
    print(f"Selected databases: {selected_databases}")

    if not selected_databases:
        raise HTTPException(status_code=400, detail="Could not route query to any database.")

    print("----------------------------------------------------------------\n")

    # Step 2 : Selecting Seed Tables (LLM Pass 2)
    print("----------------------------------------------------------------\n # LLM Pass 2: Selecting seed tables \n")
    seed_tables: List[str] = []
    for db_path in selected_databases:
        clean_db_dir = db_path.lstrip("/")

        print(f"Processing database directory: {clean_db_dir}")
        print("----------------------------------------------------------------\n")

        db_index_path = base_dir / clean_db_dir
        print(f"Database index path: {db_index_path}")
        
        if db_index_path.exists():
            with open(db_index_path, "r", encoding="utf-8") as f:
                db_index_content = f.read()
                
            tables = await llm_router.execute_routing_pass(
                request.user_input, db_index_content
            )
            print(f"Tables found in {clean_db_dir}: {tables}")
            seed_tables.extend(tables)

    if not seed_tables:
        raise HTTPException(status_code=400, detail="Could not route query to any table files.")

    print(f"Seed tables: {seed_tables}")
    print("----------------------------------------------------------------\n")

    # Step 3 : Pruning Candidate Schemas (LLM Pass 3)
    print("----------------------------------------------------------------\n # LLM Pass 3: Pruning Candidate Schemas \n")
    candidate_schemas = dependency_service.get_candidate_schemas(base_dir, seed_tables)

    print(f"Candidate schemas: {candidate_schemas.keys()}")
    # print(f"Candidate schemas: {candidate_schemas}")
    print("----------------------------------------------------------------\n")

    pruned_schema = await llm_router.prune_schema_and_columns(
        request.user_input, candidate_schemas
    )

    print(f"Pruned schema: {pruned_schema}")
    print("----------------------------------------------------------------\n")

    # --- Final Assembly: Build SQLCoder Prompt ---
    final_prompt = dependency_service.build_trimmed_sqlcoder_prompt(
         pruned_schema, request.user_input
    )

    print(f"Final SQLCoder prompt: {final_prompt}")
    print("----------------------------------------------------------------\n")

    # --- Tier 4: Generate SQL ---
    generated_sql = await llm_router.generate_sql(
        sqlcoder_prompt=final_prompt,
        sql_model_name=settings.sqlcoder_model_name
    )

    return QueryResponse (
        status="success",
        seed_tables=seed_tables,
        pruned_schema=pruned_schema,
        sqlcoder_prompt=final_prompt,
        generated_sql=generated_sql
    )