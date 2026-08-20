import asyncio
import json
import re
from typing import List, Dict, Any
from fastapi import HTTPException, Path
from openai import AsyncOpenAI, OpenAIError
from pydantic_core import ValidationError
from models.query_model import PrunedTableSchema, RelaventDatabasesResponse, RelaventTablesResponse
from core.config import settings
import pathlib


class LLMRouterService :

    def __init__ (self, base_url: str, model_name: str):
        formatted_url = base_url.rstrip("/")

        if not formatted_url.endswith("/v1"):
            formatted_url += "/v1"

        self.client = AsyncOpenAI(base_url=formatted_url, api_key="ollama")
        self.model_name = model_name
        self.sql_model_name = settings.sqlcoder_model_name or "sqlcoder"

    # llm call helper to retrieve relavent data for each phi 4 llm call.
    async def _call_llm_json(self, system_prompt: str, user_content: str) -> Any:
    
        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                temperature=0.0,
                max_tokens=1500,
                response_format={"type": "json_object"}
            )

            result_text = response.choices[0].message.content or ""

        except OpenAIError as exc:
            raise HTTPException(status_code=503, detail=f"Ollama local service error: {exc}")   
        
        return result_text

    # llm call helper to retrieve sql query from sqlcoder 4 llm call.
    async def _call_llm_text(self, system_prompt: str, user_content: str) -> str:
        """
        Calls the SQLCoder LLM and returns the raw text response.
        Strictly configured for deterministic code generation.
        """
        try:
            response = await self.client.chat.completions.create(
                model=self.sql_model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                # CRITICAL: Temperature MUST be 0.0 for SQL generation to prevent hallucinations.
                temperature=0.0,
                # Give it enough tokens to write complex JOINs, but prevent infinite loops
                max_tokens=1500, 
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error during SQLCoder LLM text generation: {e}")
            # Depending on your error handling, you might want to raise an HTTPException here
            raise Exception(f"SQL Generation failed: {str(e)}")
        
    # llm pass 1: Selecting Relevant Databases
    async def execute_database_routing_pass(self, user_query: str, global_index_path : str) -> List[str] :

        print(f"Global index path: {global_index_path}")
                    
        if not global_index_path.exists():
            raise HTTPException(status_code=500, detail=f"Global index.md not found at {global_index_path}")
            
        with open(global_index_path, "r", encoding="utf-8") as f:
            global_index_content = f.read()

        
        user_content = f"Global Index:\n{global_index_content}\n\nUser Query: {user_query}"
         
        system_prompt = (
            "You are a strict database routing agent for an enterprise Text-to-SQL system.\n"
            "Your task is to analyze a User Query and a provided Global Index, and determine which database folders contain the relevant data.\n\n"
            "CRITICAL RULES:\n"
            "1. Evaluate the User Query against the 'Keywords & Synonyms' in the index.\n"
            "2. If the query is gibberish (e.g., 'string', 'test') or unrelated, the database list MUST be empty.\n"
            "3. You MUST return ONLY a valid JSON object matching the exact schema below.\n\n"
            "REQUIRED JSON SCHEMA:\n"
            "{\n"
            "  \"reasoning\": \"Step 1: Write a 1-sentence explanation of why the query matches or fails to match the index.\",\n"
            "  \"relevant_databases\": [\"Step 2: List the exact file paths here, or leave empty [] if no match.\"]\n"
            "}\n\n"
            "EXAMPLES:\n"
            "User Query: 'How many smart meters are disconnected?'\n"
            "Output:\n"
            "{\n"
            "  \"reasoning\": \"The query asks about smart meters, which matches the keywords for mdms_master_db.\",\n"
            "  \"relevant_databases\": [\"./mdms_master_db/index.md\"]\n"
            "}\n\n"
            "User Query: 'string'\n"
            "Output:\n"
            "{\n"
            "  \"reasoning\": \"The query 'string' is generic and does not match any database keywords.\",\n"
            "  \"relevant_databases\": []\n"
            "}"
        )

        relavent_databases = await self._call_llm_json(system_prompt, user_content)

        print(f"LLM Output for Database Routing Pass: {relavent_databases}")

        try:
            # Pydantic v2 method to directly parse a JSON string
            parsed_response = RelaventDatabasesResponse.model_validate_json(relavent_databases)
            return parsed_response
        except ValidationError as e:
            # Happens if the JSON is valid, but the keys/types don't match your model
            print(f"Pydantic Validation Error: {e}")

            raise HTTPException(
                status_code=500,
                detail=f"Database Routing pass returned an invalid structure: {relavent_databases}"
            )
        
        except ValueError as e:
            # Happens if the LLM output is not valid JSON (e.g., has markdown tags)
            print(f"JSON Decode Error: {e}")
            # Fallback or raise exception
            raise HTTPException(
                status_code=500,
                detail=f"Database Routing pass returned an invalid structure: {relavent_databases}"
            )
            
    # llm pass 2 : Selecting Relevant Tables
    async def execute_table_routing_pass(self, user_query: str, selected_databases: list, base_path: pathlib.Path):

        combined_indexes = ""
        combined_relationships = ""     

        # 1. Stitch all selected databases together
        for db_path in selected_databases:
            clean_db_dir = db_path.lstrip("./\\")
            db_folder = pathlib.Path(clean_db_dir).parent  # e.g., 'mdms_master_db'

            # Append Index
            db_index_path = base_path / clean_db_dir
            if db_index_path.exists():
                with open(db_index_path, "r", encoding="utf-8") as f:
                    combined_indexes += f"\n=== Index for {db_folder.name} ===\n"
                    combined_indexes += f.read() + "\n"     

            # Append Relationships
            relationships_path = base_path / db_folder / "relationships.md"
            if relationships_path.exists():
                with open(relationships_path, "r", encoding="utf-8") as f:
                    combined_relationships += f"\n=== Relationships for {db_folder.name} ===\n"
                    combined_relationships += f.read() + "\n"    

        # 2. Build the unified payload
        user_content = (
            f"Combined Database Indexes:\n{combined_indexes}\n\n"
            f"Combined Relationships:\n{combined_relationships}\n\n"
            f"User Query: {user_query}"
        )   


        # 3. System Prompt requiring a "Master Plan"
        """
        system_prompt = (
             "You are a highly precise database table routing agent for an enterprise Text-to-SQL system.\n"
             "Your task is to analyze a User Query, combined Database Indexes, and Relationships files from one or more databases.\n"
             "You must determine WHICH specific table markdown files contain the data necessary to answer the query.\n\n"
             "CRITICAL RULES:\n"
             "1. Base your decision ONLY on the table descriptions, keywords, and relations provided.\n"
             "2. If the query is gibberish or does not map to ANY table, return an empty list.\n"
             "3. You MUST return ONLY a valid JSON object matching the exact schema below.\n\n"
             "REQUIRED JSON SCHEMA:\n"
             "{\n"
             "  \"reasoning\": \"Step 1: Write a detailed Master Plan. Explain why these tables are needed. CRITICAL: If you select more than one table, you MUST explicitly state the relationship/join logic between them based on the Relationships file.\",\n"
             "  \"relevant_tables\": [\"Step 2: List the exact file paths here, or leave empty [] if no match.\"]\n"
             "}\n\n"
             "EXAMPLES:\n"
             "User Query: 'what is the count of total prepaid consumers?'\n"
             "Output:\n"
             "{\n"
             "  \"reasoning\": \"We need l_consumer_lookup for consumer counts, which joins to M_PaymentType_Contract via the Payment Contract Status to identify prepaid users.\",\n"
             "  \"relevant_tables\": [\"./mdms_master/l_consumer_lookup.md\", \"./mdms_master/M_PaymentType_Contract.md\"]\n"
             "}\n\n"
             "User Query: 'string'\n"
             "Output:\n"
             "{\n"
             "  \"reasoning\": \"The query 'string' is a generic test input and does not match any table descriptions.\",\n"
             "  \"relevant_tables\": []\n"
             "}"
        )
        """

        system_prompt = (
            "You are a highly capable database table routing agent for an enterprise Text-to-SQL system.\n"
            "Your task is to analyze a User Query, combined Database Indexes, and Relationships files from one or more databases.\n"
            "You must determine WHICH specific table markdown files contain the data necessary to answer the query.\n\n"
            "CRITICAL RULES:\n"
            "1. CONCEPTUAL MATCHING: The user query may use domain terms (e.g., 'installed', 'billed', 'units', 'metered') that live in related entity tables (e.g., meter lookup, device, consumer lookup). Select all candidate tables likely to contain relevant attributes or join keys.\n"
            "2. RELATIONSHIP TRAVERSAL: If the query requires entities that must be joined (e.g., consumer details + meter installation), select all intermediate tables required to complete the join path as defined in the Relationships file.\n"
            "3. EMPTY LIST ONLY FOR IRRELEVANT QUERIES: Return an empty list `[]` ONLY if the query is complete gibberish (e.g., 'test', 'asdf') or completely outside the domain of the database.\n"
            "4. Output ONLY a valid JSON object matching the exact schema below.\n\n"
            "REQUIRED JSON SCHEMA:\n"
            "{\n"
            "  \"reasoning\": \"Step 1: Write a detailed Master Plan explaining which tables and joins will satisfy the query.\",\n"
            "  \"relevant_tables\": [\"Step 2: List the exact file paths here, or leave empty [] if completely unrelated.\"]\n"
            "}\n"
            "EXAMPLES:\n"
             "User Query: 'what is the count of total prepaid consumers?'\n"
             "Output:\n"
             "{\n"
             "  \"reasoning\": \"We need l_consumer_lookup for consumer counts, which joins to M_PaymentType_Contract via the Payment Contract Status to identify prepaid users.\",\n"
             "  \"relevant_tables\": [\"./mdms_master_db/l_consumer_lookup.md\", \"./mdms_master_db/M_PaymentType_Contract.md\"]\n"
             "}\n\n"
             "User Query: 'string'\n"
             "Output:\n"
             "{\n"
             "  \"reasoning\": \"The query 'string' is a generic test input and does not match any table descriptions.\",\n"
             "  \"relevant_tables\": []\n"
             "}"
)


        # 4. Make a SINGLE LLM Call
        raw_llm_output = await self._call_llm_json(system_prompt, user_content)  

        # 5. Parse, Validate, and Return the FULL Object
        try:
            parsed_response = RelaventTablesResponse.model_validate_json(raw_llm_output)

            # We return the ENTIRE parsed object, not just the list.
            # This allows the controller to pass `parsed_response.reasoning` to Step 3 as the Master Plan!
            return parsed_response

        except ValidationError as e:
            print(f"Pydantic Validation Error in Table Routing: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Table Routing pass returned an invalid structure: {raw_llm_output}"
            )
        except ValueError as e:
            print(f"JSON Decode Error in Table Routing: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Table Routing pass returned invalid JSON: {raw_llm_output}"
            )  

    # llm pass 3 : Prune Schema and Columns
    async def execute_column_pruning_pass(self, user_query: str, master_plan: str, selected_tables: list, base_path: pathlib.Path) -> list:

        combined_relationships = ""
        processed_dbs = set()

        # 1. Gather combined relationships so the LLM knows how to join everything
        for table_path in selected_tables:
            clean_table_path = table_path.lstrip("./\\")
            db_folder = pathlib.Path(clean_table_path).parts[0] # e.g., 'mdms_master_db'

            if db_folder not in processed_dbs:
                relationships_path = base_path / db_folder / "relationships.md"
                if relationships_path.exists():
                    with open(relationships_path, "r", encoding="utf-8") as f:
                        combined_relationships += f"\n=== Relationships for {db_folder} ===\n"
                        combined_relationships += f.read() + "\n"
                processed_dbs.add(db_folder)

        # 2. Prepare the concurrent tasks
        tasks = []

        for table_path in selected_tables:
            clean_table_path = table_path.lstrip("./\\")
            full_table_path = base_path / clean_table_path

            table_markdown_content = ""
            if full_table_path.exists():
                with open(full_table_path, "r", encoding="utf-8") as f:
                    table_markdown_content = f.read()
            else:
                print(f"Warning: Table file not found at {full_table_path}")
                continue

            # Build the Prompt for THIS specific table
            """
            system_prompt = (
                "You are an expert database schema architect. Your job is to prune a single table's schema down to ONLY the essential columns needed for a specific user query.\n\n"
                "CRITICAL RULES:\n"
                "1. You MUST select columns that contain the data requested in the User Query.\n"
                "2. You MUST ALSO select any Primary Keys or Foreign Keys required to join this table to the 'Other Selected Tables', based on the provided Master Plan and Relationships file.\n"
                "3. Output ONLY a valid JSON object matching the exact schema below.\n\n"
                "REQUIRED JSON SCHEMA:\n"
                "{\n"
                "  \"reasoning\": \"Explain which data columns you selected, and which key columns you selected to join to the other tables.\",\n"
                "  \"pruned_columns\": [\n"
                "       {\n"
                "           \"column_name\": \"Exact name of the column\",\n"
                "           \"description\": \"The description and data type of the column exactly as written in the markdown\"\n"
                "       }\n"
                "   ]\n"
                "}"
            )
           

            system_prompt = (
                "You are an expert data extraction agent. Your job is to prune a single table's schema down to ONLY the essential columns needed for a specific user query.\n\n"
                "CRITICAL RULES:\n"
                "1. You MUST select columns that contain the data requested in the User Query.\n"
                "2. You MUST ALSO select any Primary Keys or Foreign Keys required to join this table to the 'Other Selected Tables', based on the provided Master Plan and Relationships file.\n"
                "3. VERBATIM EXTRACTION: When providing the column name and description, you MUST COPY AND PASTE the exact text from the provided table markdown. DO NOT paraphrase, DO NOT summarize, and DO NOT add your own notes.\n"
                "4. Output ONLY a valid JSON object matching the exact schema below.\n\n"
                "REQUIRED JSON SCHEMA:\n"
                "{\n"
                "  \"reasoning\": \"Explain which data columns you selected, and which key columns you selected to join to the other tables.\",\n"
                "  \"pruned_columns\": [\n"
                "       {\n"
                "           \"column_name\": \"Exact name of the column as written in the markdown.\",\n"
                "           \"description\": \"COPY AND PASTE the exact description and data type from the markdown. DO NOT alter a single word.\"\n"
                "       }\n"
                "   ]\n"
                "}"
            )
            """

            system_prompt = (
                "You are an expert data extraction agent. Your job is to prune a single table's schema down to ONLY the essential columns needed for a specific user query.\n\n"
                "CRITICAL RULES:\n"
                "1. You MUST select columns that contain the data requested in the User Query.\n"
                "2. You MUST ALSO select any Primary Keys or Foreign Keys required to join this table to the 'Other Selected Tables', based on the provided Master Plan and Relationships file.\n"
                "3. Output ONLY a valid JSON object matching the exact schema below.\n"
                "4. STRICT EXTRACTION ONLY: You may ONLY select columns that explicitly appear in the \"AVAILABLE COLUMNS\" list below.\n"
                "5. NEVER INVENT COLUMNS: Do not guess, assume, or fabricate columns. If a concept from the User Query (e.g., 'Prepaid') is NOT in this specific table, IGNORE IT. Trust that another table in the Master Plan will provide it.\n"
                "6. PERFECT SCHEMA: Output ONLY valid JSON. Do not add keys, notes, or comments outside of the exact schema provided. Put ALL your assumptions solely in the 'selection_reason' string.\n\n"
                "REQUIRED JSON SCHEMA:\n"
                "{\n"
                "  \"reasoning\": \"Explain your overall strategy for this table.\",\n"
                "  \"pruned_columns\": [\n"
                "       {\n"
                "           \"column_name\": \"Exact name of the column as written in the markdown.\",\n"
                "           \"description\": \"CRITICAL: COPY AND PASTE the description EXACTLY as it appears in the markdown.\",\n"
                "           \"selection_reason\": \"Explain why you selected this column. PUT ALL ASSUMPTIONS OR LOGIC HERE.\"\n"
                "       }\n"
                "   ]\n"
                "}"
            )

            user_content = (
                f"User Query: {user_query}\n\n"
                f"Master Plan (Global Context from routing): {master_plan}\n\n"
                f"All Tables Involved in this Query: {selected_tables}\n\n"
                f"Relationships Map:\n{combined_relationships}\n\n"
                f"=========================================\n"
                f"YOUR TASK: Prune the following table to support the Master Plan:\n"
                f"Table File: {table_path}\n\n"
                f"{table_markdown_content}"
            )

            # Append the LLM call as a tuple with its table_path so we know which result is which
            tasks.append((table_path, self._call_llm_json(system_prompt, user_content)))

        # 3. Execute all LLM calls CONCURRENTLY
        # asyncio.gather requires a list of awaitables. We unzip our tuples to await just the LLM calls.
        table_paths, awaitables = zip(*tasks) if tasks else ([], [])
        raw_results = await asyncio.gather(*awaitables)

        # 4. Parse and assemble the final pruned schemas
        final_pruned_schemas = []

        for path, raw_llm_output in zip(table_paths, raw_results):

            print(f"Raw LLM Output for Column Pruning of {path}:\n{raw_llm_output}\n\n")
            try:
                parsed_schema = PrunedTableSchema.model_validate_json(raw_llm_output)
                # Inject the table path so Step 4 knows the table name
                parsed_schema.table_path = path 
                final_pruned_schemas.append(parsed_schema)

            except ValidationError as e:
                print(f"Pydantic Validation Error in Column Pruning for {path}: {e}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Column Pruning pass returned an invalid structure for {path}."
                )
            except ValueError as e:
                print(f"JSON Decode Error in Column Pruning for {path}: {e}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Column Pruning pass returned invalid JSON for {path}."
                )

        return final_pruned_schemas

    # sqlcoder prompt generation
    def build_sqlcoder_ddl(self, pruned_schemas: list) -> str:
        ddl_lines = []

        for schema in pruned_schemas:
            # 1. Skip if no columns were selected
            if not schema.pruned_columns:
                continue

            # Extract DB Name and Table Name dynamically from the path
            # Example: "./mdms_master/l_consumer_lookup.md"

            path_obj = pathlib.Path(schema.table_path)
            table_name = path_obj.stem                # Extracts: "l_consumer_lookup"
            db_name = path_obj.parent.name            # Extracts: "mdms_master"

            table_name = pathlib.Path(schema.table_path).stem
            ddl_lines.append(f"CREATE TABLE {db_name}.dbo.{table_name} (")

            seen_columns = set()
            formatted_columns = []

            # 2. Process and sanitize columns
            for col in schema.pruned_columns:
                clean_col_name = col.column_name.split('.')[-1].strip()

                if clean_col_name.lower() in seen_columns:
                    continue
                seen_columns.add(clean_col_name.lower())

                clean_desc = col.description.replace('\n', ' ').strip()

                # Store them temporarily without commas
                formatted_columns.append(f"  {clean_col_name}") 
                # We'll attach the comment separately to manage the comma
                formatted_columns.append(f" -- {clean_desc}")

            # 3. Assemble columns with correct comma placement
            for i in range(0, len(formatted_columns), 2):
                col_str = formatted_columns[i]
                desc_str = formatted_columns[i+1]

                # If it's the last column, NO comma. Otherwise, add a comma.
                if i == len(formatted_columns) - 2:
                    ddl_lines.append(f"{col_str}{desc_str}")
                else:
                    ddl_lines.append(f"{col_str},{desc_str}")

            ddl_lines.append(");\n")

        return "\n".join(ddl_lines)

    # SQL Coder Pass 4: Generate SQL Query
    async def execute_sql_generation_pass(self, user_query: str, pruned_schemas: list) -> str:

        # 1. Build the schema string using our sanitizing helper
        schema_ddl = self.build_sqlcoder_ddl(pruned_schemas)

        # 2. System Prompt: STATIC rules, persona, and constraints.
        """
        system_prompt = (
            "You are an expert Microsoft SQL Server (T-SQL) developer. "
            "You write highly optimized, accurate, and safe T-SQL queries.\n\n"
            "### Instructions\n"
            "- If you cannot answer the question with the available database schema, return 'I do not know'.\n"
            "- Use standard Microsoft SQL Server (T-SQL) syntax exclusively (e.g., use TOP instead of LIMIT, correct date functions, etc.).\n"
            "- STRICT RULE: You must ONLY generate READ-ONLY 'SELECT' statements. Never generate INSERT, UPDATE, DELETE, DROP, or EXEC queries.\n"
            "- STRICT RULE: You MUST append the `WITH (NOLOCK)` table hint to EVERY table referenced in the FROM and JOIN clauses. (Example: `FROM l_consumer_lookup lcl WITH (NOLOCK) JOIN M_PaymentType_Contract mptc WITH (NOLOCK) ON...`).\n"
            "- Output ONLY the raw executable SQL query. Do not include markdown formatting (like ```sql), conversational text, or explanations."
        )
        """

        system_prompt = (
            "You are an expert MS SQL Server (T-SQL) developer. "
            "Your task is to write a highly optimized SQL query to answer the user's question based ONLY on the provided database schema.\n\n"
            "CRITICAL T-SQL RULES:\n"
            "1. FULL TABLE NAMES: You MUST use the exact, fully qualified table names as provided in the CREATE TABLE statements (e.g., db_name.dbo.table_name).\n"
            "2. NOLOCK REQUIREMENT (MANDATORY): You MUST append the `WITH (NOLOCK)` table hint to EVERY table referenced in a `FROM` or `JOIN` clause. "
            "Failure to do this will crash the production system.\n"
            "   CORRECT Example: \n"
            "   FROM mdms_master.dbo.l_consumer_lookup a WITH (NOLOCK)\n"
            "   JOIN mdms_master.dbo.M_PaymentType_Contract b WITH (NOLOCK) ON a.PaymentContract_TblRefID = b.PaymentContract_TblRefID\n"
            "3. ALIASES: Use short, clean table aliases (e.g., a, b, c) in your FROM and JOIN clauses. Place the WITH (NOLOCK) hint IMMEDIATELY AFTER the alias.\n"
            "4. READ ONLY: Generate a SELECT statement only. NO INSERT, UPDATE, DELETE, or DROP allowed.\n"
            "5. OUTPUT FORMAT: Return ONLY the raw SQL query. Do not provide any explanations, apologies, or conversational text. Do not wrap it in markdown blocks (```sql) unless necessary for the parser."
        )

        # 3. User Content: DYNAMIC schema context and the specific task.
        user_content = (
            f"### Database Schema\n"
            f"The query will run on a database with the following schema:\n"
            f"{schema_ddl}\n\n"
            f"### Task\n"
            f"Generate a Microsoft SQL Server (T-SQL) query to answer [QUESTION]{user_query}[/QUESTION]\n\n"
            f"### Answer\n"
            f"Given the database schema, here is the T-SQL query that answers the question:\n"
        )

        # 4. Call the LLM (Standard text generation)
        raw_response = await self._call_llm_text(system_prompt, user_content)
        print(f"Raw SQLCoder Output:\n{raw_response} \n\n")

        # 5. Clean the output
        sql_match = re.search(r"```(?:sql)?\n(.*?)```", raw_response, re.DOTALL | re.IGNORECASE)
        if sql_match:
            final_sql = sql_match.group(1).strip()
        else:
            final_sql = raw_response.strip()

        # Optional: Hard-coded safety check before returning
        if not final_sql.strip().upper().startswith("SELECT"):
            print("WARNING: Generated SQL does not start with SELECT.")

        return final_sql