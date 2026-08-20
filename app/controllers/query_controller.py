from pathlib import Path
from typing import Set, List
from fastapi import APIRouter, Depends, HTTPException
from models.query_model import QueryRequest, RelaventDatabasesResponse, RelaventDatabasesResponse,RelaventTablesResponse,DatabaseRequest
from services.llm_router_service import LLMRouterService
from services.sql_execution_service import SQLExecutionService
from services.data_analysis_service import DataAnalysisService
from core.dependencies import get_llm_router_service,get_sql_execution_service,get_data_analysis_service
from core.config import settings

router = APIRouter(prefix="/test", tags=["Test Endpoints"])

# global variables
base_dir = Path(settings.okf_bundles_dir).resolve()

#LLM Pass 1: Selecting Relevant Databases
@router.post("/get_relevant_databases", response_model=RelaventDatabasesResponse)
async def get_relevant_databases(
    request : QueryRequest,
    llm_router: LLMRouterService = Depends(get_llm_router_service)
) :

    global_index_path = base_dir / "index.md"

    selected_databases = await llm_router.execute_database_routing_pass(
            request.user_input, global_index_path
    )
     
    print(f"Selected databases: {selected_databases} \n")

    if not selected_databases:
        raise HTTPException(status_code=400, detail="Could not route query to any database.")

    return RelaventDatabasesResponse(
            relevant_databases=selected_databases.relevant_databases,
            reasoning=selected_databases.reasoning
        ) 

#LLM Pass 2: Selecting relavent tables.
@router.post("/get_relevant_tables" , response_model=RelaventTablesResponse)
async def get_relevant_tables(
    request : QueryRequest,
    llm_router: LLMRouterService = Depends(get_llm_router_service)
) :

    global_index_path = base_dir / "index.md"
    
    selected_databases = await llm_router.execute_database_routing_pass(
            request.user_input, global_index_path
    )

    print(f"Selected databases: {selected_databases} \n")

    if not selected_databases:
        raise HTTPException(status_code=400, detail="Could not route query to any database.")
    
    relevant_tables = await llm_router.execute_table_routing_pass(
            request.user_input, selected_databases.relevant_databases, base_dir
    )

    print(f"Relevant tables: {relevant_tables} \n")

    if not relevant_tables:
        raise HTTPException(status_code=400, detail="Could not route query to any tables.")

    return RelaventTablesResponse(
        relevant_tables= relevant_tables.relevant_tables,
        reasoning= relevant_tables.reasoning
    )

#LLM Pass 3: Pruning table schemas.
@router.post("/get_pruned_schema")
async def get_pruned_schema(
    request : QueryRequest,
    llm_router: LLMRouterService = Depends(get_llm_router_service)
) :

    global_index_path = base_dir / "index.md"
    
    selected_databases = await llm_router.execute_database_routing_pass(
            request.user_input, global_index_path
    )

    print(f"Selected databases: {selected_databases} \n")

    if not selected_databases:
        raise HTTPException(status_code=400, detail="Could not route query to any database.")
    
    relevant_tables = await llm_router.execute_table_routing_pass(
            request.user_input, selected_databases.relevant_databases, base_dir
    )

    print(f"Relevant tables: {relevant_tables} \n")

    if not relevant_tables:
        raise HTTPException(status_code=400, detail="Could not route query to any tables.")


    tables_list = relevant_tables.relevant_tables
    master_plan = relevant_tables.reasoning

    # --- STEP 3: COLUMN PRUNING ---
    pruned_schemas = await llm_router.execute_column_pruning_pass(
        user_query=request.user_input,
        master_plan=master_plan,
        selected_tables=tables_list,
        base_path=base_dir
    )

    print(f"Pruned schemas: {pruned_schemas} \n")
    return pruned_schemas

# SQL Coder Prompt Generation
@router.post("/generate_sqlcoder_prompt")
async def generate_sqlcoder_prompt(
    request: QueryRequest,
    llm_router: LLMRouterService = Depends(get_llm_router_service)
):
    global_index_path = base_dir / "index.md"
    
    selected_databases = await llm_router.execute_database_routing_pass(
            request.user_input, global_index_path
    )

    print(f"Selected databases: {selected_databases} \n\n")

    if not selected_databases:
        raise HTTPException(status_code=400, detail="Could not route query to any database.")
    
    relevant_tables = await llm_router.execute_table_routing_pass(
            request.user_input, selected_databases.relevant_databases, base_dir
    )

    print(f"Relevant tables: {relevant_tables} \n\n")

    if not relevant_tables:
        raise HTTPException(status_code=400, detail="Could not route query to any tables.")

    tables_list = relevant_tables.relevant_tables
    master_plan = relevant_tables.reasoning

    # --- STEP 3: COLUMN PRUNING ---
    pruned_schemas = await llm_router.execute_column_pruning_pass(
        user_query=request.user_input,
        master_plan=master_plan,
        selected_tables=tables_list,
        base_path=base_dir
    )

    print(f"Pruned schemas: {pruned_schemas} \n\n")

    # Generate SQLCoder prompt based on pruned schemas
    sqlcoder_prompt = llm_router.build_sqlcoder_ddl(
        pruned_schemas=pruned_schemas
    )

    print(f"Generated SQLCoder prompt: {sqlcoder_prompt} \n")

    return {"sqlcoder_prompt": sqlcoder_prompt}

# SQL Coder Pass 4: Generate SQL Query
@router.post("/generate_sql_query")
async def generate_sql_query(
    request: QueryRequest,
    llm_router: LLMRouterService = Depends(get_llm_router_service)
):
    global_index_path = base_dir / "index.md"
    
    selected_databases = await llm_router.execute_database_routing_pass(
            request.user_input, global_index_path
    )

    print(f"Selected databases: {selected_databases} \n\n")

    if not selected_databases:
        raise HTTPException(status_code=400, detail="Could not route query to any database.")
    
    relevant_tables = await llm_router.execute_table_routing_pass(
            request.user_input, selected_databases.relevant_databases, base_dir
    )

    print(f"Relevant tables: {relevant_tables} \n\n")

    if not relevant_tables:
        raise HTTPException(status_code=400, detail="Could not route query to any tables.")

    tables_list = relevant_tables.relevant_tables
    master_plan = relevant_tables.reasoning

    # --- STEP 3: COLUMN PRUNING ---
    pruned_schemas = await llm_router.execute_column_pruning_pass(
        user_query=request.user_input,
        master_plan=master_plan,
        selected_tables=tables_list,
        base_path=base_dir
    )

    print(f"Pruned schemas: {pruned_schemas} \n\n")

    # Generate SQLCoder prompt based on pruned schemas
    sqlcoder_prompt = llm_router.build_sqlcoder_ddl(
        pruned_schemas=pruned_schemas
    )

    print(f"Generated SQLCoder prompt: {sqlcoder_prompt} \n")

    # --- STEP 4: SQL Generation ---
    generated_sql = await llm_router.execute_sql_generation_pass(
        user_query=request.user_input,
        pruned_schemas=pruned_schemas
    )

    print(f"Generated SQL: {generated_sql} \n")

    return {"generated_sql": generated_sql} 

# DB Call
@router.post("/db_call_")
async def generate_sql_query(
    request: QueryRequest,
    llm_router: LLMRouterService = Depends(get_llm_router_service),
    sql_service : SQLExecutionService = Depends(get_sql_execution_service)
):
    global_index_path = base_dir / "index.md"
    
    selected_databases = await llm_router.execute_database_routing_pass(
            request.user_input, global_index_path
    )

    print(f"Selected databases: {selected_databases} \n\n")

    if not selected_databases:
        raise HTTPException(status_code=400, detail="Could not route query to any database.")
    
    relevant_tables = await llm_router.execute_table_routing_pass(
            request.user_input, selected_databases.relevant_databases, base_dir
    )

    print(f"Relevant tables: {relevant_tables} \n\n")

    if not relevant_tables:
        raise HTTPException(status_code=400, detail="Could not route query to any tables.")

    tables_list = relevant_tables.relevant_tables
    master_plan = relevant_tables.reasoning

    # --- STEP 3: COLUMN PRUNING ---
    pruned_schemas = await llm_router.execute_column_pruning_pass(
        user_query=request.user_input,
        master_plan=master_plan,
        selected_tables=tables_list,
        base_path=base_dir
    )

    print(f"Pruned schemas: {pruned_schemas} \n\n")

    # Generate SQLCoder prompt based on pruned schemas
    sqlcoder_prompt = llm_router.build_sqlcoder_ddl(
        pruned_schemas=pruned_schemas
    )

    print(f"Generated SQLCoder prompt: {sqlcoder_prompt} \n")

    # --- STEP 4: SQL Generation ---
    generated_sql = await llm_router.execute_sql_generation_pass(
        user_query=request.user_input,
        pruned_schemas=pruned_schemas
    )

    print(f"Generated SQL: {generated_sql} \n")

    sql_data = await sql_service.process_user_query(generated_sql)

    return sql_data

# DB cal Test endpoint
@router.post("/get_data")
async def generate_sql_query(
    request: QueryRequest,
    sql_service : SQLExecutionService = Depends(get_sql_execution_service)
):

    sql_data = await sql_service.process_user_query(request.user_input)

    return sql_data

# Data Analyisi Test Endpoint
@router.post("/get_summary")
async def generate_sql_query(
    request: DatabaseRequest,
    sql_service : SQLExecutionService = Depends(get_sql_execution_service),
    data_analysis_service : DataAnalysisService = Depends(get_data_analysis_service)
):

    sql_data = await sql_service.execute_query(request.sql_query)
    print(f"sql data get_summary call : {sql_data} \n\n")
    result = await data_analysis_service.analyze(request.user_input,sql_data)
    print(f"analysis result get_summary call : {result} \n\n")

    return {"summary" : result}

# End to End flow
@router.post("/get_query_response")
async def generate_sql_query(
    request: QueryRequest,
    llm_router: LLMRouterService = Depends(get_llm_router_service),
    sql_service : SQLExecutionService = Depends(get_sql_execution_service),
    data_analysis_service : DataAnalysisService = Depends(get_data_analysis_service)
):
    global_index_path = base_dir / "index.md"
    
    selected_databases = await llm_router.execute_database_routing_pass(
            request.user_input, global_index_path
    )

    print(f"Selected databases: {selected_databases} \n\n")

    if not selected_databases:
        raise HTTPException(status_code=400, detail="Could not route query to any database.")
    
    relevant_tables = await llm_router.execute_table_routing_pass(
            request.user_input, selected_databases.relevant_databases, base_dir
    )

    print(f"Relevant tables: {relevant_tables} \n\n")

    if not relevant_tables:
        raise HTTPException(status_code=400, detail="Could not route query to any tables.")

    tables_list = relevant_tables.relevant_tables
    master_plan = relevant_tables.reasoning

    # --- STEP 3: COLUMN PRUNING ---
    pruned_schemas = await llm_router.execute_column_pruning_pass(
        user_query=request.user_input,
        master_plan=master_plan,
        selected_tables=tables_list,
        base_path=base_dir
    )

    print(f"Pruned schemas: {pruned_schemas} \n\n")

    # Generate SQLCoder prompt based on pruned schemas
    sqlcoder_prompt = llm_router.build_sqlcoder_ddl(
        pruned_schemas=pruned_schemas
    )

    print(f"Generated SQLCoder prompt: {sqlcoder_prompt} \n")

    # --- STEP 4: SQL Generation ---
    generated_sql = await llm_router.execute_sql_generation_pass(
        user_query=request.user_input,
        pruned_schemas=pruned_schemas
    )

    print(f"Generated SQL: {generated_sql} \n")

    #sql_data = await sql_service.process_user_query(generated_sql)

    sanitized_sql = sql_service.sanitize_query(generated_sql)

    sql_data = await sql_service.execute_query(sanitized_sql)
    print(f"sql data get_summary call : {sql_data} \n\n")

    result = await data_analysis_service.analyze(request.user_input,sql_data)
    print(f"analysis result get_summary call : {result} \n\n")
    
    return {"summary" : result}
