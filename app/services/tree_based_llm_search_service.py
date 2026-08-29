import os
import json
import logging
import copy
from typing import Dict, Any, Optional, Set, List
from core.config import settings
from pageindex.page_index_md import md_to_tree
from models.index_tree_model import Phase1RoutingResult, Phase2PruningResult 
from openai import AsyncOpenAI
import re

class TreeBasedLLMSerach:

    def __init__(self):
        self.markdown_file_path = settings.page_index_bundle

        self.db_schema_path = settings.db_schema_path
        self.db_relationship_path = settings.db_relationship_path

        self.db_schema_tree: Optional[Dict[str, Any]] = None
        self.db_relationship_tree: Optional[Dict[str, Any]] = None
    
        formatted_url = settings.ollama_base_url.rstrip("/")
        if not formatted_url.endswith("/v1"):
            formatted_url += "/v1"

        self.client = AsyncOpenAI(base_url=formatted_url, api_key="ollama")
        self.model_name = settings.router_model_name

    # test method for generate tree index.
    async def generate_tree_index(self) -> dict:
        result = await md_to_tree(self.markdown_file_path)
        print(result['doc_name'])
        print(result['structure'])
        return result['structure']

    #-----------------------------------------------------------------------------------------------------------
    # creating tree index for db_schema and db_relationships.
    async def initialize_trees(self) -> None:
        """Parses both markdown files and stores the resulting JSON trees in memory."""
        if not os.path.exists(self.db_schema_path):
            raise FileNotFoundError(f"Schema markdown not found at: {self.db_schema_path}")
            
        if not os.path.exists(self.db_relationship_path):
            raise FileNotFoundError(f"Relationships markdown not found at: {self.db_relationship_path}")

        # 1. Parse DB -> Tables -> Columns tree
        self.db_schema_tree = await md_to_tree(
            self.db_schema_path ,
            if_add_node_summary='no',
            summary_token_threshold=500
        )

        # 2. Parse Relationships -> Tables -> Joins tree
        self.db_relationship_tree = await md_to_tree(
            self.db_relationship_path,
            if_add_node_summary='no',
            summary_token_threshold=500
        )
    
    def prune_schema_to_level2(self) -> list[dict]:
        tree_list = self.db_schema_tree if isinstance(self.db_schema_tree, list) else self.db_schema_tree.get("structure", [])
        pruned_tree = []

        for db_node in tree_list:
            db_title_full = db_node.get("title", "")
            db_name = db_title_full.split(":")[0].strip() 

            db_copy = {
                "title": db_title_full,
                "node_id": db_node.get("node_id"),
                "nodes": []
            }
            
            # Level 2 traversal (Tables)
            for table_node in db_node.get("nodes", []):
                # INJECT THE DB NAME DIRECTLY INTO THE TABLE TITLE
                original_table_title = table_node.get("title", "")
                table_copy = {
                    "title": f"[DB: {db_name}] {original_table_title}",
                    "node_id": table_node.get("node_id")
                }
                db_copy["nodes"].append(table_copy)

            pruned_tree.append(db_copy)
        
        return pruned_tree
    
    def _collect_valid_node_ids(self, tree: Any) -> Set[str]:
        """Helper to recursively collect all valid node_ids from an index tree."""
        valid_ids = set()
        nodes = tree if isinstance(tree, list) else tree.get("structure", [])
        
        def traverse(node_list):
            for n in node_list:
                if "node_id" in n:
                    valid_ids.add(str(n["node_id"]))
                if n.get("nodes"):
                    traverse(n["nodes"])
                    
        traverse(nodes)
        return valid_ids

    async def execute_phase1_routing(self, user_query: str) -> Phase1RoutingResult:
        """
        Pass 1: Identifies relevant tables and relationship joins,
        and generates the Master Plan explanation.
        """
        # 1. Prune schema to Level 1 & Level 2
        pruned_schema = self.prune_schema_to_level2()
        rel_structure = self.db_relationship_tree if isinstance(self.db_relationship_tree, list) else self.db_relationship_tree.get("structure", [])

        # 2. Build system instructions and payload for FLAT LIST extraction
        system_prompt = (
            "You are an expert MS SQL Database Architect and Semantic Router.\n"
            "Your task is to analyze a user query and determine the exact tables "
            "and join paths required to satisfy the request.\n\n"
            "Input Context Information:\n"
            "1. DATABASE SCHEMA TREE (Pruned): Level 1 nodes are Databases. Level 2 nodes are Tables. Note: Each table title begins with a tag like '[DB: mdms_master]' indicating its exact parent database.\n"
            "2. RELATIONSHIP TREE: Defines join paths. Level 1 is Root. Level 2 nodes are Source Tables. Level 3 nodes are specific Join Logic.\n\n"
            "CRITICAL ROUTING RULES (Strictly Enforced):\n"
            "- LOOKUP-ONLY INQUIRIES: If a user asks for a list of available types, categories, or statuses (e.g., 'What are the categories?'), select ONLY the relevant master lookup table (e.g., m_connection_category). Do NOT select or join the main entity tables (like l_consumer_lookup) unless the user explicitly asks for metrics or counts associated with them.\n"
            "- ZERO SPECULATION (AGGREGATES): If the query asks for a general summary, total, or count (e.g., 'summary of consumption') WITHOUT specifying groupings, select ONLY the primary fact table (e.g., t_dailyconsumption). Do NOT join dimension tables (like l_consumer_lookup or m_connection_category) unless the user explicitly asks to filter or group by their specific attributes.\n"
            "- MINIMALIST JOINS & BRIDGES: First, determine the absolute minimum core tables needed. If the core tables you selected do NOT have a direct relationship, you MUST use the RELATIONSHIP TREE to find and include the necessary bridge tables (e.g., linking consumers to organizations requires l_meter_lookup). Do NOT add joins just because they exist; only add them to close the loop between your chosen core tables. \n"
            "- ONLY OUTPUT IDs: In the arrays for selected tables and joins, you MUST ONLY output the exact alphanumeric 'node_id' (e.g., '0001'). DO NOT add the table name, description, or [DB: ] tag inside the arrays.\n\n"
            "Output Structure (Valid JSON only):\n"
            "{\n"
            "  \"master_plan\": \"<Step 1: Identify the absolute minimum core tables needed. Step 2: Explain IF joins are strictly necessary based on the query. Do NOT add joins just because they exist in the schema.>\",\n"
            "  \"selected_table_node_ids\": [\n"
            "    \"<exact_table_node_id_1>\",\n"
            "    \"<exact_table_node_id_2>\"\n"
            "  ],\n"
            "  \"selected_join_node_ids\": [\n"
            "    \"<Level_3_join_node_id_1>\"\n"
            "  ]\n"
            "}"
        )

        """
        system_prompt = (
            "You are an expert MS SQL Database Architect and Semantic Router.\n"
            "Your task is to analyze a user query and determine the exact tables "
            "and join paths required to satisfy the request.\n\n"
            "Input Context Information:\n"
            "1. DATABASE SCHEMA TREE (Pruned): Level 1 nodes are Databases. Level 2 nodes are Tables. Note: Each table title begins with a tag like '[DB: mdms_master]' indicating its exact parent database.\n"
            "2. RELATIONSHIP TREE: Defines join paths. Level 1 is Root. Level 2 nodes are Source Tables. Level 3 nodes are specific Join Logic.\n\n"
            "CRITICAL ROUTING RULES (Strictly Enforced):\n"
            "- LOOKUP-ONLY INQUIRIES: If a user asks for a list of available types, categories, or statuses (e.g., 'What are the categories?'), select ONLY the relevant master lookup table (e.g., m_connection_category). Do NOT select or join the main entity tables (like l_consumer_lookup) unless the user explicitly asks for metrics or counts associated with them.\n"
            "- ZERO SPECULATION: Do NOT select lookup tables unless the user asks for their specific attributes. For a simple 'count of consumers', you only need the primary lookup tables.\n"
            "- ONLY OUTPUT IDs: In the arrays for selected tables and joins, you MUST ONLY output the exact alphanumeric 'node_id' (e.g., '0001'). DO NOT add the table name, description, or [DB: ] tag inside the arrays.\n\n"
            "Output Structure (Valid JSON only):\n"
            "{\n"
            "  \"master_plan\": \"<Explain which tables you need and how they join>\",\n"
            "  \"selected_table_node_ids\": [\n"
            "    \"<exact_table_node_id_1>\",\n"
            "    \"<exact_table_node_id_2>\"\n"
            "  ],\n"
            "  \"selected_join_node_ids\": [\n"
            "    \"<Level_3_join_node_id_1>\"\n"
            "  ]\n"
            "}"
        )
        """

        """
        system_prompt = (
            "You are an expert MS SQL Database Architect and Semantic Router.\n"
            "Your task is to analyze a user query and determine the exact tables "
            "and join paths required to satisfy the request.\n\n"
            "Input Context Information:\n"
            "1. DATABASE SCHEMA TREE (Pruned): Level 1 nodes are Databases. Level 2 nodes are Tables. Note: Each table title begins with a tag like '[DB: mdms_master]' indicating its exact parent database.\n"
            "2. RELATIONSHIP TREE: Defines join paths. Level 1 is Root. Level 2 nodes are Source Tables. Level 3 nodes are specific Join Logic.\n\n"
            "CRITICAL ROUTING RULES (Strictly Enforced):\n"
            "- ZERO SPECULATION: Do NOT select lookup tables unless the user asks for their specific attributes. For a simple 'count of consumers', you only need the primary lookup tables.\n"
            "- ONLY OUTPUT IDs: In the arrays for selected tables and joins, you MUST ONLY output the exact alphanumeric 'node_id' (e.g., '0001'). DO NOT add the table name, description, or [DB: ] tag inside the arrays.\n\n"
            "Output Structure (Valid JSON only):\n"
            "{\n"
            "  \"master_plan\": \"<Explain which tables you need and how they join>\",\n"
            "  \"selected_table_node_ids\": [\n"
            "    \"<exact_table_node_id_1>\",\n"
            "    \"<exact_table_node_id_2>\"\n"
            "  ],\n"
            "  \"selected_join_node_ids\": [\n"
            "    \"<Level_3_join_node_id_1>\"\n"
            "  ]\n"
            "}"
        )
        """

        user_content = {
            "user_query": user_query,
            "pruned_database_schema": pruned_schema,
            "relationship_tree": rel_structure
        }

        # 3. Call local LLM with structured output
        print(f"Dispatching Phase 1 Semantic Routing for query: '{user_query}' \n")
        
        response = await self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(user_content, indent=2)}
            ],
            response_format={"type": "json_object"},
            temperature=0.0
        )

        raw_content = response.choices[0].message.content or "{}"
        print(f"llm pass 1 raw response : \n {raw_content} \n\n ")

        parsed_json = json.loads(raw_content)
        routing_result = Phase1RoutingResult.model_validate(parsed_json)

        # 4. Validate output against in-memory node IDs
        valid_schema_ids = self._collect_valid_node_ids(self.db_schema_tree)
        valid_rel_ids = self._collect_valid_node_ids(self.db_relationship_tree)

        for tbl_id in routing_result.selected_table_node_ids:
            if tbl_id not in valid_schema_ids:
                print(f"Pass 1 returned unrecognized Table node_id: {tbl_id} \n")

        for join_id in routing_result.selected_join_node_ids:
            if join_id not in valid_rel_ids:
                print(f"Pass 1 returned unrecognized Join node_id: {join_id} \n")

        print(f"Phase 1 complete. Selected {len(routing_result.selected_table_node_ids)} table(s) and {len(routing_result.selected_join_node_ids)} join(s).\n")
        return routing_result

    def sanitize_phase1_output(self, routing_result: Phase1RoutingResult) -> Phase1RoutingResult:
        """
        Enforces the Closed-Loop Join rule in Python based on the flattened IDs.
        """
        # Rule 1: Single table -> No joins allowed
        if len(routing_result.selected_table_node_ids) <= 1:
            routing_result.selected_join_node_ids = []
            return routing_result

        # Rule 2: Multi-table -> Only keep joins targeting an active selected table
        # Fetch the actual extracted table names
        phase1_dict = routing_result.model_dump()
        extracted_schema = self.extract_phase2_schema_payload(phase1_dict)
        
        selected_table_names = set()
        for db in extracted_schema:
            for tbl in db.get("nodes", []):
                # Clean up the name by removing [DB: tag] and descriptions
                name = tbl.get("title", "").split(":")[0]
                name = name.split("]")[-1].strip()
                selected_table_names.add(name)

        # Fetch extracted relationships
        extracted_rels = self.extract_phase1_relationships(phase1_dict)
        valid_joins = []
        
        for source_tbl in extracted_rels:
            for join_obj in source_tbl.get("joins", []):
                join_title = join_obj.get("title", "")
                if any(tbl_name in join_title for tbl_name in selected_table_names):
                    valid_joins.append(join_obj.get("node_id"))

        routing_result.selected_join_node_ids = valid_joins
        return routing_result

    def extract_phase2_schema_payload(self, phase1_result: dict) -> List[Dict[str, Any]]:
        """
        Takes the flat list of table IDs from Phase 1 and constructs 
        the DB -> Table -> Column hierarchical tree dynamically.
        """
        allowed_table_ids = set(phase1_result.get("selected_table_node_ids", []))
        filtered_schema = []

        tree_list = self.db_schema_tree if isinstance(self.db_schema_tree, list) else self.db_schema_tree.get("structure", [])

        for db_node in tree_list:
            db_copy = {
                "node_id": db_node.get("node_id"),
                "title": db_node.get("title"),
                "nodes": [] 
            }
            
            for table_node in db_node.get("nodes", []):
                table_id = str(table_node.get("node_id"))
                if table_id in allowed_table_ids:
                    table_copy = copy.deepcopy(table_node)
                    db_copy["nodes"].append(table_copy)
            
            # Only include the DB if it contains at least one selected table
            if db_copy["nodes"]:
                filtered_schema.append(db_copy)

        return filtered_schema

    def extract_phase1_relationships(self, phase1_result: dict) -> List[Dict[str, Any]]:
        """
        Takes the flat list of join IDs from Phase 1 and constructs 
        the structured Source Table -> Joins relationship tree.
        """
        allowed_join_ids = set(phase1_result.get("selected_join_node_ids", []))
        filtered_rels = []
        
        rel_list = self.db_relationship_tree if isinstance(self.db_relationship_tree, list) else self.db_relationship_tree.get("structure", [])

        for source_table in rel_list:
            src_copy = {
                "node_id": source_table.get("node_id"),
                "title": source_table.get("title"),
                "joins": []
            }
            
            for join_node in source_table.get("nodes", []):
                if str(join_node.get("node_id")) in allowed_join_ids:
                    src_copy["joins"].append(copy.deepcopy(join_node))
                    
            if src_copy["joins"]:
                filtered_rels.append(src_copy)
                
        return filtered_rels

    async def execute_phase2_pruning(
        self, 
        user_query: str, 
        extracted_schema: List[Dict[str, Any]], 
        phase1_relationships: List[Dict[str, Any]]
    ) -> Phase2PruningResult:
        """
        Pass 2:
        Takes the extracted schema (with all columns) and the required joins from Phase 1,
        and prompts the LLM to prune unnecessary columns.
        """

        system_prompt = (
            "You are an Expert MS SQL Database Architect and Schema Optimizer.\n"
            "Your task is to review a subset of a database schema and identify the exact columns "
            "required to answer the user's query.\n\n"
            "Input Context Information:\n"
            "1. EXTRACTED SCHEMA: A JSON array of the selected Databases, Tables, and ALL their Columns.\n"
            "2. REQUIRED JOINS: The specific relationships/join paths determined in Phase 1.\n\n"
            "CRITICAL PRUNING RULES (Strictly Enforced):\n"
            "- KEEP JOIN KEYS (BOTH SIDES): Look closely at the 'Join Logic' provided in the REQUIRED JOINS. You MUST retain the 'node_id' for both columns used in the equation. If you drop a join key, the system will crash.\n"
            "- KEEP ENTITY IDENTIFIERS: Always retain the human-readable identifier columns for the primary entities involved (e.g., RRNumber, MSN, Meter_Serial_Number).\n"
            "- KEEP LOOKUP NAMES: If a lookup or reference table is included, you MUST retain its descriptive text/name column.\n"
            "- KEEP QUERY TARGETS: Retain the 'node_id' of columns explicitly requested by the user (e.g., metrics, dates, amounts).\n"
            "- KEEP STATUS & STATE FLAGS: If the query asks for a 'summary', 'history', or 'activity', you MUST retain columns that indicate the execution status, success/failure state, or current condition of the records (e.g., CommandStatus, IsExecuted, Status_TblRefID).\n"
            "- DROP THE REST (STRICT): If a column does not fall into the above categories, you MUST drop it. Ignore audit columns (created_by, updated_at) unless explicitly requested.\n\n"
            "Output Structure (Valid JSON only):\n"
            "{\n"
            "  \"pruning_reason\": \"<Explain why you kept specific columns for the query, explicitly noting the entity identifiers and join keys>\",\n"
            "  \"retained_column_node_ids\": [\n"
            "    \"<column_node_id_1>\",\n"
            "    \"<column_node_id_2>\"\n"
            "  ]\n"
            "}"
        )
        
        system_prompt1 = (
            "You are an Expert MS SQL Database Architect and Schema Optimizer.\n"
            "Your task is to review a subset of a database schema and identify the exact columns "
            "required to answer the user's query.\n\n"
            "Input Context Information:\n"
            "1. EXTRACTED SCHEMA: A JSON array of the selected Databases, Tables, and ALL their Columns.\n"
            "2. REQUIRED JOINS: The specific relationships/join paths determined in Phase 1.\n\n"
            "CRITICAL PRUNING RULES (Strictly Enforced):\n"
            "- KEEP JOIN KEYS (BOTH SIDES): Look closely at the 'Join Logic' provided in the REQUIRED JOINS (e.g., 'lcl.PaymentContract_TblRefID = mptc.PaymentContract_TblRefID'). You MUST retain the 'node_id' for BOTH columns mentioned in the equation. Never drop the Primary Key from the target lookup table!\n"
            "- KEEP ENTITY IDENTIFIERS: Always retain the human-readable identifier columns for the primary entities involved. Read the column descriptions to find them. For consumers, keep 'rrnumber'; for meters, keep 'meter_serial_number', 'msn', or 'meter_no'; for organizations, keep 'office_name' and 'office_code'; for networks, keep 'network_code' and 'network_name'.\n"
            "- KEEP LOOKUP NAMES: If a lookup or reference table is included, you MUST retain its descriptive text/name column (e.g., 'PaymentContract_Name', 'ConnectionStatus_Name').\n"
            "- KEEP QUERY TARGETS: Retain the 'node_id' of columns explicitly requested by the user (e.g., metrics, dates, amounts).\n"
            "- DROP THE REST (STRICT): If a column is NOT part of the 'Join Logic', NOT a mandatory entity identifier/name, and NOT directly requested by the query, you MUST drop it.\n\n"
            "Output Structure (Valid JSON only):\n"
            "{\n"
            "  \"pruning_reason\": \"<Explain why you kept specific columns for the query, explicitly noting the entity identifiers, lookup names, and BOTH sides of the join keys you preserved>\",\n"
            "  \"retained_column_node_ids\": [\n"
            "    \"<column_node_id_1>\",\n"
            "    \"<column_node_id_2>\"\n"
            "  ]\n"
            "}"
        )

        user_content = {
            "user_query": user_query,
            "required_joins": phase1_relationships,
            "extracted_schema": extracted_schema
        }

        print(f"Dispatching Phase 2 Column Pruning for query: '{user_query}' \n")

        # Call local LLM with structured output
        response = await self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(user_content, indent=2)}
            ],
            response_format={"type": "json_object"},
            temperature=0.0 
        )

        raw_content = response.choices[0].message.content or "{}"
        print(f"LLM Pass 2 raw response: \n {raw_content} \n\n ")

        parsed_json = json.loads(raw_content)
        pruning_result = Phase2PruningResult.model_validate(parsed_json)
        
        # Count total columns retained for logging
        total_cols = len(pruning_result.retained_column_node_ids)
        print(f"Phase 2 complete. Retained {total_cols} critical columns.\n")

        return pruning_result

    async def execute_phase3_sql_generation(
        self,
        user_query: str,
        pruned_schema: list,
        required_joins: list
    ) -> str:
        """
        Phase 3: Takes the pruned schema and required joins, and prompts the LLM to generate the final MS SQL query.
        """

        """
        system_prompt = (
            "You are an Expert MS SQL Database Developer.\n"
            "Your task is to translate a user's natural language query into a syntactically correct, highly optimized MS SQL query.\n\n"
            "Input Context Information:\n"
            "You will receive a JSON object containing:\n"
            "1. 'user_query': The natural language request.\n"
            "2. 'pruned_schema_tree': The exact databases, tables, and columns available to you.\n"
            "3. 'required_joins': The mandatory join paths and table aliases.\n\n"
            "CRITICAL SQL RULES (Strictly Enforced):\n"
            "- READ-ONLY (SELECT ONLY): You are strictly forbidden from writing INSERT, UPDATE, DELETE, DROP, or ALTER statements. You must ONLY write SELECT queries.\n"
            "- MS SQL SYNTAX ONLY: You must write strictly valid Microsoft SQL Server syntax (e.g., use TOP instead of LIMIT).\n"
            "- FULLY QUALIFIED TABLE NAMES: You MUST write every table name in the format database_name.dbo.table_name using the database and table titles provided in the JSON.\n"
            "- MANDATORY NOLOCK: You MUST append WITH (NOLOCK) immediately after every table alias in your FROM and JOIN clauses (e.g., FROM mdms_master.dbo.l_consumer_lookup lcl WITH (NOLOCK)).\n"
            "- NO HALLUCINATIONS: You MUST ONLY use the tables and columns explicitly listed in the 'pruned_schema_tree'. If a column is not in the JSON, it does not exist.\n"
            "- MANDATORY ALIASES & JOINS: You MUST use the exact 'Join Logic' and table aliases (e.g., 'lcl', 'mcs') provided in the 'required_joins' array.\n"
            "- HUMAN-READABLE OUTPUTS: In your SELECT statement, always select the descriptive name columns (e.g., 'ConnectionStatus_Name') instead of returning raw Foreign Key IDs.\n\n"
            "Output Format:\n"
            "Return ONLY the executable SQL query wrapped in a markdown code block. Do not include any conversational text, pleasantries, or explanations.\n"
            "```sql\n"
            "<Write MS SQL here query your>\n"
            "```"
        )
        """
        system_prompt = (
            "You are an Expert MS SQL Database Developer.\n"
            "Your task is to translate a user's natural language query into a syntactically correct, highly optimized MS SQL query.\n\n"
            "Input Context Information:\n"
            "You will receive a JSON object containing:\n"
            "1. 'user_query': The natural language request.\n"
            "2. 'pruned_schema_tree': The exact databases, tables, and columns available to you.\n"
            "3. 'required_joins': The mandatory join paths and table aliases.\n\n"
            "CRITICAL SQL RULES (Strictly Enforced):\n"
            "- READ-ONLY (SELECT ONLY): You are strictly forbidden from writing INSERT, UPDATE, DELETE, DROP, or ALTER statements. You must ONLY write SELECT queries.\n"
            "- MS SQL SYNTAX ONLY: You must write strictly valid Microsoft SQL Server syntax (e.g., use TOP instead of LIMIT).\n"
            "- FULLY QUALIFIED TABLE NAMES: You MUST write every table name in the format database_name.dbo.table_name using the database and table titles provided in the JSON.\n"
            "- MANDATORY NOLOCK: You MUST append WITH (NOLOCK) immediately after every table alias in your FROM and JOIN clauses.\n"
            "- NO HALLUCINATIONS: You MUST ONLY use the tables and columns explicitly listed in the 'pruned_schema_tree'. If a column is not in the JSON, it does not exist.\n"
            "- MANDATORY ALIASES & JOINS: You MUST use the exact 'Join Logic' and table aliases (e.g., 'lcl', 'mcs') provided in the 'required_joins' array.\n"
            "- HUMAN-READABLE OUTPUTS: In your SELECT statement, always select the descriptive name columns (e.g., 'ConnectionStatus_Name') instead of returning raw Foreign Key IDs.\n"
            "- EXPLICIT AGGREGATES: If the query involves grouping, counting, summing, or finding the 'highest/lowest', you MUST include the calculated metric (e.g., COUNT(column_name) AS TotalCount) directly in your SELECT clause alongside the grouped entity.\n\n"
            "Output Format:\n"
            "Return ONLY the executable SQL query wrapped in a markdown code block. Do not include any conversational text, pleasantries, or explanations.\n"
            "```sql\n"
            "<Write MS SQL here query your>\n"
            "```"
        )

        user_content = {
            "user_query": user_query,
            "pruned_schema_tree": pruned_schema,
            "required_joins": required_joins
        }

        print(f"Dispatching Phase 3 SQL Generation for query: '{user_query}' \n")

        # Call the local LLM
        response = await self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(user_content, indent=2)}
            ],
            temperature=0.0 # Strict determinism for SQL generation
        )

        raw_content = response.choices[0].message.content or ""
        print(f"LLM Pass 3 raw response: \n {raw_content} \n\n")
        
        # Safely extract the SQL string
        clean_sql = self.extract_sql_from_markdown(raw_content)
        return clean_sql

    @staticmethod
    def extract_sql_from_markdown(raw_response: str) -> str:
        """
        Safely extracts the SQL query from the LLM's markdown output using regex.
        """
        # Match anything between ```sql and ```
        match = re.search(r'```sql\s*(.*?)\s*```', raw_response, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        
        # Fallback: if it dropped the 'sql' tag, check for bare markdown blocks
        match = re.search(r'```\s*(.*?)\s*```', raw_response, re.DOTALL)
        if match:
            return match.group(1).strip()
            
        # Absolute fallback if it forgot markdown entirely (strips leading/trailing whitespace)
        return raw_response.strip()