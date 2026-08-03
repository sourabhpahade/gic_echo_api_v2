from pathlib import Path
from typing import Set
from fastapi import APIRouter, Depends, HTTPException
from models.query_model import QueryRequest, QueryResponse
from services.llm_router_service import LLMRouterService
from services.okf_dependency_service import OKFDependencyService
from core.dependencies import get_llm_router_service, get_okf_dependency_service
from core.config import settings

router = APIRouter(prefix="/query", tags=["Text-to-SQL Routing"])

@router.post("/user_query")
async def user_query(query: QueryRequest):
    print(f"The user asked: {query.user_input}")   
     
    return {
        "status":"success",
        "user_question": query.user_input
    }


@router.post("/assemble-context", response_model=QueryResponse)
async def assemble_sql_context(
    request: QueryRequest,
    llm_router: LLMRouterService = Depends(get_llm_router_service),
    dependency_service: OKFDependencyService = Depends(get_okf_dependency_service)
):
    base_dir = Path(settings.okf_bundles_dir).resolve()
    print(f"Using OKF Bundles Directory: {base_dir}")

    # --- Tier 1: Global Index Pass ---
    global_index_path = base_dir / "index.md"
    print(f"Global index.md path: {global_index_path}")

    if not global_index_path.exists():
        raise HTTPException(
            status_code=500, 
            detail=f"Global index.md not found at {global_index_path}"
        )
        
    with open(global_index_path, "r", encoding="utf-8") as f:
        global_index_content = f.read()

    selected_databases = await llm_router.execute_routing_pass(
        user_query=request.user_input,
        index_content=global_index_content
    )

    if not selected_databases:
        raise HTTPException(status_code=400, detail="Could not route query to any database.")

   
    # --- Tier 2: Table Index Pass ---
    seed_tables: Set[str] = set()
    for db_path in selected_databases:
        clean_db_dir = db_path.lstrip("/")
        print(f"Routing for database: {clean_db_dir}")
        db_index_path = base_dir / clean_db_dir
        print(f"Database index.md path: {db_index_path}")
        
        if db_index_path.exists():
            with open(db_index_path, "r", encoding="utf-8") as f:
                db_index_content = f.read()
                
            tables = await llm_router.execute_routing_pass(
                user_query=request.user_input,
                index_content=db_index_content
            )
            for t in tables:
                seed_tables.add(t.lstrip("/"))

    if not seed_tables:
        raise HTTPException(status_code=400, detail="Could not route query to any table files.")

    
    # --- Tier 3: Programmatic Dependency Expansion ---
    all_resolved_table_paths: Set[str] = set()
    for seed_table in seed_tables:
        deps = dependency_service.extract_table_dependencies(base_dir, seed_table)
        all_resolved_table_paths.update(deps)
    
    print(f"All resolved table paths: {all_resolved_table_paths}")

    # --- Context Assembly Pass ---
    context_blocks = []
    for rel_table_path in sorted(all_resolved_table_paths):
        full_table_path = base_dir / rel_table_path
        print(f"Adding context from: {full_table_path}")
        if full_table_path.exists():
            with open(full_table_path, "r", encoding="utf-8") as f:
                context_blocks.append(f"--- START SCHEMA: {rel_table_path} ---\n" + f.read())

    final_assembled_context = "\n\n".join(context_blocks)
    
    return QueryResponse(
        status="success",
        selected_databases=selected_databases,
        #seed_tables=[],  # Placeholder since Tier 2 is commented out
        #all_resolved_tables=[],  # Placeholder since Tier 3 is commented out
        #assembled_context="",  # Placeholder since context assembly is commented out
        seed_tables=list(seed_tables),
        all_resolved_tables=list(all_resolved_table_paths),
        assembled_context=final_assembled_context
    )