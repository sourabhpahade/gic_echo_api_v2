import os
import logging
from typing import Dict, Any, Optional,Set
from core.config import settings
from pageindex.page_index_md import md_to_tree
from models.index_tree_model import Phase1RoutingResult
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
        """
        Creates a lightweight copy of the schema tree containing only:
        - Level 1: Databases
        - Level 2: Tables (with descriptions)
        All Level 3 (Columns) nodes are stripped.
        """

        tree_list = self.db_schema_tree if isinstance(self.db_schema_tree, list) else self.db_schema_tree.get("structure", [])
        pruned_tree = []

        for db_node in tree_list:
            db_copy = {
                "title": db_node.get("title"),
                "node_id": db_node.get("node_id"),
                "nodes": []
            }
            
            # Level 2 traversal (Tables)
            for table_node in db_node.get("nodes", []):
                table_copy = {
                    "title": table_node.get("title"),
                    "node_id": table_node.get("node_id")
                    # Intentionally omit or empty "nodes" (Columns)
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
        """
        system_prompt = (
            "You are an expert MS SQL Database Architect and Semantic Router.\n"
            "Your task is to analyze a user query and determine the exact databases, tables, "
            "and join paths required to satisfy the request.\n\n"
            "Input Context Information:\n"
            "1. DATABASE SCHEMA TREE (Pruned): Level 1 nodes are Databases. Level 2 nodes are Tables with descriptions.\n"
            "2. RELATIONSHIP TREE: Defines join paths. Level 1 is Root. Level 2 nodes are the Source Tables. Level 3 nodes are the specific Join Logic to Target Tables.\n\n"
            "CRITICAL ROUTING RULES (Strictly Enforced):\n"
            "- ZERO SPECULATION: Do NOT select lookup tables (like payment contracts, categories, or status) unless the user query explicitly filters by them or asks for their labels. For a simple 'count of consumers', only the consumer table is needed.\n"
            "- RELATIONSHIP NAVIGATION: To pick a join, find the Source Table at Level 2 of the Relationship Tree, then select the exact Target Join Logic at Level 3. \n"
            "- ONLY SELECT JOINS (LEVEL 3): Never include a Level 1 or Level 2 parent node from the Relationship Tree in your 'selected_relationships' array. Only include the Level 3 nodes that contain the actual 'Join Logic'.\n"
            "- SELF-CORRECTION: If your 'selection_reason' concludes that no joins are necessary, you MUST set 'selected_relationships' exactly to [] or null.\n"
            "- CLOSED-LOOP JOINS: Every join in 'selected_relationships' MUST connect two tables that are BOTH explicitly listed in your 'selected_databases -> tables' array.\n\n"
            "Output Structure (Valid JSON only - 'selection_reason' MUST be the first key):\n"
            "{\n"
            '  "selection_reason": "<Analyze the query and plan your join strategy HERE first>",\n'
            '  "selected_databases": [\n'
            "    {\n"
            '      "node_id": "<database_node_id>",\n'
            '      "title": "<database_title>",\n'
            '      "tables": [\n'
            "        {\n"
            '          "node_id": "<table_node_id>",\n'
            '          "title": "<table_title>"\n'
            "        }\n"
            "      ]\n"
            "    }\n"
            "  ],\n"
            '  "selected_relationships": [\n'
            "    {\n"
            '      "node_id": "<Level_3_relationship_node_id>",\n'
            '      "title": "<Level_3_relationship_title>"\n'
            "    }\n"
            "  ]\n"
            "}"
        )
        """

        system_prompt = (
            "You are an expert MS SQL Database Architect and Semantic Router.\n"
            "Your task is to analyze a user query and determine the exact databases, tables, "
            "and join paths required to satisfy the request.\n\n"
            "Input Context Information:\n"
            "1. DATABASE SCHEMA TREE (Pruned): Level 1 nodes are Databases. Level 2 nodes are Tables with descriptions/keywords.\n"
            "2. RELATIONSHIP TREE: Defines join paths. Level 1 is Root. Level 2 nodes are Source Tables. Level 3 nodes are specific Join Logic.\n\n"
            "CRITICAL ROUTING RULES (Strictly Enforced):\n"
            "- ZERO SPECULATION: Do NOT select lookup tables unless the user query explicitly filters by them or asks for their labels.\n"
            "- NO ATTRIBUTE GUESSING: Do not add tables just to search for dates, statuses, or IDs if those concepts are already covered by the keywords in the primary tables.\n"
            "- EXACT MATCH STRINGS: When outputting a 'title', you MUST copy the EXACT, full string provided in the schema tree. Do not abbreviate or remove the descriptions.\n"
            "- HIERARCHICAL RELATIONSHIPS: If a join is required, nest the Level 3 'Join Logic' under its corresponding Level 2 'Source Table'.\n"
            "- SELF-CORRECTION: If your 'selection_reason' concludes no joins are necessary, set 'selected_relationships' exactly to [] or null.\n"
            "- CLOSED-LOOP JOINS: Every join target MUST connect to a table explicitly listed in 'selected_databases -> tables'.\n\n"
            "Output Structure (Valid JSON only - 'selection_reason' MUST be the first key):\n"
            "{\n"
            '  "selection_reason": "<Analyze the query and plan your join strategy HERE first>",\n'
            '  "selected_databases": [\n'
            "    {\n"
            '      "node_id": "<exact_database_node_id>",\n'
            '      "title": "<EXACT_full_database_string>",\n'
            '      "tables": [\n'
            "        {\n"
            '          "node_id": "<exact_table_node_id>",\n'
            '          "title": "<EXACT_full_table_string>"\n'
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

        print(f"llm pass 1 parsed response : \n {parsed_json} \n\n ")

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