import os
import logging
from typing import Dict, Any, Optional,Set,List
from core.config import settings
from pageindex.page_index_md import md_to_tree
from models.index_tree_model import Phase1RoutingResult,Phase2PruningResult 
from openai import AsyncOpenAI
import json

class TreeBasedLLMSerach :

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
    async def generate_tree_index(self) -> dict :

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

        #print(f"db_schema tree : \n {self.db_schema_tree['structure']} \n\n ")

        # 2. Parse Relationships -> Tables -> Joins tree
        self.db_relationship_tree = await md_to_tree(
            self.db_relationship_path,
            if_add_node_summary='no',
            summary_token_threshold=500
        )

        #print(f"relationship tree : \n {self.db_relationship_tree['structure']} \n\n ")

    
    def prune_schema_to_level2(self) -> list[dict]:
        tree_list = self.db_schema_tree if isinstance(self.db_schema_tree, list) else self.db_schema_tree.get("structure", [])
        pruned_tree = []

        for db_node in tree_list:
            db_title_full = db_node.get("title", "")
            # Extract just the DB name (e.g., "mdms_master" from "mdms_master : This database...")
            db_name = db_title_full.split(" :")[0].strip() 

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

        #print(f"prunted db_schema tree : \n {pruned_tree} \n\n ")
        
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

    async def execute_phase1_routing(
        self,
        user_query: str
    ) -> Phase1RoutingResult:
        """
        Pass 1: Identifies relevant databases, tables, and relationship joins,
        and generates the Master Plan explanation.
        """
        # 1. Prune schema to Level 1 & Level 2
        pruned_schema = self.prune_schema_to_level2()
        rel_structure = self.db_relationship_tree if isinstance(self.db_relationship_tree, list) else self.db_relationship_tree.get("structure", [])

        # 2. Build system instructions and payload
        system_prompt = (
            "You are an expert MS SQL Database Architect and Semantic Router.\n"
            "Your task is to analyze a user query and determine the exact databases, tables, "
            "and join paths required to satisfy the request.\n\n"
            "Input Context Information:\n"
            "1. DATABASE SCHEMA TREE (Pruned): Level 1 nodes are Databases. Level 2 nodes are Tables. Note: Each table title begins with a tag like '[DB: mdms_master]' indicating its exact parent database.\n"
            "2. RELATIONSHIP TREE: Defines join paths. Level 1 is Root. Level 2 nodes are Source Tables. Level 3 nodes are specific Join Logic.\n\n"
            "CRITICAL ROUTING RULES (Strictly Enforced):\n"
            "- READ THE DB TAG: You MUST place a table under the database that matches its '[DB: ...]' tag. Never place a table in the wrong database.\n"
            "- MANDATORY TABLES ARRAY: Every database listed in 'selected_databases' MUST contain a populated 'tables' array.\n"
            "- ZERO SPECULATION: Do NOT select tables like 't_dailyconsumption' or 's_meter_commanddetails' unless the user asks for daily usage, billing, or commands. For a simple 'count of consumers', you only need the consumer lookup table and the payment contract lookup.\n"
            "- EXACT MATCH STRINGS: When outputting a 'title', copy the EXACT string provided in the schema tree, including the '[DB: ...]' tag.\n"
            "- CLOSED-LOOP JOINS: Every join target MUST connect to a table explicitly listed in 'selected_databases -> tables'.\n\n"
            "Output Structure (Valid JSON only):\n"
            "{\n"
            '  "master_plan": "<Explain which tables you need, read their [DB: ] tags, and explain how they join>",\n'
            '  "selected_databases": [\n'
            "    {\n"
            '      "node_id": "<exact_database_node_id>",\n'
            '      "title": "<EXACT_full_database_string>",\n'
            '      "tables": [\n'
            "        {\n"
            '          "node_id": "<exact_table_node_id>",\n'
            '          "title": "<EXACT_full_table_string_with_[DB]_tag>"\n'
            "        }\n"
            "      ]\n"
            "    }\n"
            "  ],\n"
            '  "selected_relationships": [\n'
            "    {\n"
            '      "node_id": "<Level_2_source_table_node_id>",\n'
            '      "title": "<EXACT_full_source_table_string>",\n'
            '      "joins": [\n'
            "        {\n"
            '          "node_id": "<Level_3_join_node_id>",\n'
            '          "title": "<EXACT_full_join_logic_string>"\n'
            "        }\n"
            "      ]\n"
            "    }\n"
            "  ]\n"
            "}"
        )

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

        #print(f"llm pass 1 parsed response : \n {parsed_json} \n\n ")

        routing_result = Phase1RoutingResult.model_validate(parsed_json)

        # 4. Validate output against in-memory node IDs
        valid_schema_ids = self._collect_valid_node_ids(self.db_schema_tree)
        valid_rel_ids = self._collect_valid_node_ids(self.db_relationship_tree)

        for db in routing_result.selected_databases:
            if db.node_id not in valid_schema_ids:
                print(f"Pass 1 returned unrecognized DB node_id: {db.node_id} \n")
            for tbl in db.tables:
                if tbl.node_id not in valid_schema_ids:
                    print(f"Pass 1 returned unrecognized Table node_id: {tbl.node_id} \n")

        for rel in routing_result.selected_relationships:
            if rel.node_id not in valid_rel_ids:
                print(f"Pass 1 returned unrecognized Relationship node_id: {rel.node_id} \n")

        print(f"Phase 1 complete. Selected {len(routing_result.selected_databases)} DB(s) and {len(routing_result.selected_relationships)} join(s).\n")
        return routing_result

    @staticmethod
    def sanitize_phase1_output(routing_result: Phase1RoutingResult) -> Phase1RoutingResult:
        """
        Enforces the Closed-Loop Join rule in Python:
        1. If <= 1 table is selected across all databases, wipe relationships to [].
        2. If > 1 table is selected, retain only joins whose target table appears in selected_tables.
        """
        # Extract all selected table names/titles
        selected_table_names = set()
        total_tables_count = 0
        for db in routing_result.selected_databases:
            for tbl in db.tables:
                total_tables_count += 1
                # Extract raw table name (e.g. 'l_consumer_lookup' from title or name)
                table_name = tbl.title.split(":")[0].strip()
                selected_table_names.add(table_name)

        # Rule 1: Single table -> No joins allowed
        if total_tables_count <= 1:
            routing_result.selected_relationships = []
            return routing_result

        # Rule 2: Multi-table -> Only keep joins targeting an active selected table
        if routing_result.selected_relationships:
            valid_joins = []
            for rel in routing_result.selected_relationships:
                # Check if any selected table name appears in the join target title
                if any(tbl_name in rel.title for tbl_name in selected_table_names):
                    valid_joins.append(rel)
            routing_result.selected_relationships = valid_joins

        return routing_result

    def extract_phase2_schema_payload(self, phase1_result: dict) -> List[Dict[str, Any]]:
        """
        Takes the routing result from Phase 1 and extracts the full tables (including columns)
        from the original schema tree.
        """
        selected_map = {}
        for db in phase1_result.get("selected_databases", []):
            db_id = str(db.get("node_id"))
            table_ids = {str(tbl.get("node_id")) for tbl in db.get("tables", [])}
            selected_map[db_id] = table_ids

        filtered_schema = []

        # FIX: Extract the actual list from the dictionary structure
        tree_list = self.db_schema_tree if isinstance(self.db_schema_tree, list) else self.db_schema_tree.get("structure", [])

        # 2. Traverse the list, not the dict
        for db_node in tree_list:
            db_id = str(db_node.get("node_id"))
            
            # If this DB was selected in Phase 1
            if db_id in selected_map:
                db_copy = {
                    "node_id": db_id,
                    "title": db_node.get("title"),
                    "nodes": [] 
                }
                
                allowed_table_ids = selected_map[db_id]
                
                # Check the tables inside this DB
                for table_node in db_node.get("nodes", []):
                    table_id = str(table_node.get("node_id"))
                    
                    if table_id in allowed_table_ids:
                        import copy
                        table_copy = copy.deepcopy(table_node)
                        db_copy["nodes"].append(table_copy)
                
                if db_copy["nodes"]:
                    filtered_schema.append(db_copy)

        return filtered_schema

    async def execute_phase2_pruning(
        self, 
        user_query: str, 
        extracted_schema: List[Dict[str, Any]], 
        phase1_relationships: List[Any]
    ) -> Phase2PruningResult:
        """
        Pass 2:
        Takes the extracted schema (with all columns) and the required joins from Phase 1,
        and prompts the LLM to prune unnecessary columns.
        """
        
        # Convert relationships to a dictionary/list format for the prompt
        # We handle both Pydantic models and dicts just in case
        rel_dump = []
        for rel in phase1_relationships:
            if hasattr(rel, "model_dump"):
                rel_dump.append(rel.model_dump())
            elif hasattr(rel, "dict"):
                rel_dump.append(rel.dict())
            else:
                rel_dump.append(rel)

        system_prompt = (
            "You are an Expert MS SQL Database Architect and Schema Optimizer.\n"
            "Your task is to review a subset of a database schema and identify the exact columns "
            "required to answer the user's query.\n\n"
            "Input Context Information:\n"
            "1. EXTRACTED SCHEMA: A JSON array of the selected Databases, Tables, and ALL their Columns.\n"
            "2. REQUIRED JOINS: The specific relationships/join paths determined in Phase 1.\n\n"
            "CRITICAL PRUNING RULES (Strictly Enforced):\n"
            "- KEEP JOIN KEYS: You MUST retain the 'node_id' of any Primary Keys (PK) and Foreign Keys (FK) needed to "
            "execute the 'REQUIRED JOINS'. If you drop a join key, the system will crash.\n"
            "- KEEP QUERY TARGETS: Retain the 'node_id' of columns explicitly requested by the user (e.g., metrics, dates, statuses).\n"
            "- DROP THE REST: Ignore audit columns (created_by, updated_at) or operational flags UNLESS needed for filtering.\n\n"
            "Output Structure (Valid JSON only):\n"
            "{\n"
            "  \"pruning_reason\": \"<Explain why you kept specific columns for the query, and which join keys you preserved>\",\n"
            "  \"retained_column_node_ids\": [\n"
            "    \"<column_node_id_1>\",\n"
            "    \"<column_node_id_2>\"\n"
            "  ]\n"
            "}"
        )

        user_content = {
            "user_query": user_query,
            "required_joins": rel_dump,
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
