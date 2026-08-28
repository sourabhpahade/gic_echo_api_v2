import typing

# --- PYTHON 3.10 COMPATIBILITY PATCH ---
# litellm requires 'NotRequired', which doesn't exist in Python 3.10's native typing module.
# We fetch it from typing_extensions and inject it into the standard typing module in memory.
try:
    from typing import NotRequired
except ImportError:
    from typing_extensions import NotRequired
    typing.NotRequired = NotRequired

import sys
print(f"--- RUNNING PYTHON ENV: {sys.executable} ---")

# Force the raw import to expose the true hidden error
import litellm

import os
import json
from pageindex.page_index_md import md_to_tree
from pageindex import PageIndexClient
from core.config import settings

# Force local API routing for Ollama
os.environ["OPENAI_API_BASE"] = settings.ollama_base_url
os.environ["OPENAI_API_KEY"] = "local"

class PageIndexService:
    def __init__(self):
        # 1. Safely resolve absolute paths for Windows compatibility
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        safe_storage_name = settings.page_index_storage.strip('/\\')
        self.storage_dir = os.path.normpath(os.path.join(self.base_dir, safe_storage_name))
        self.markdown_path = os.path.normpath(settings.page_index_bundle)

        # 2. Force PageIndex to use our specific local working directory
        os.environ["PAGEINDEX_WORK_DIR"] = self.storage_dir

        # 3. Initialize client strictly in Local Mode (no api_key parameter)
        self.client = PageIndexClient(
            index_model=settings.router_model_name, 
            chat_model=settings.router_model_name,
            storage_path=self.storage_dir
        )

    async def build_database_index(self) -> str:
        """
        STEP 1: Parse the Markdown file and register it natively into DocStore.
        """
        from datetime import datetime, timezone
        
        print(f"\n--- [Step 1] Indexing Markdown: {self.markdown_path} ---")
        
        # 1. Parse the Markdown into a structure
        tree = await md_to_tree(
            self.markdown_path, 
            if_add_node_summary='no', 
            summary_token_threshold=500 
        )
        
        target_filename = os.path.basename(self.markdown_path)
        doc_id = tree.get("doc_name") or target_filename.replace('.md', '')
        structure = tree.get("structure", [])

        # 2. Read the raw Markdown text to spoof a "PDF Page"
        with open(self.markdown_path, 'r', encoding='utf-8') as f:
            raw_markdown = f.read()

        # 3. Create the exact Metadata schema expected by LocalAPI
        now_iso = datetime.now(timezone.utc).replace(tzinfo=None).isoformat()
        meta = {
            "id": doc_id,
            "name": doc_id,
            "description": "Database Schema via Markdown",
            "status": "completed",
            "createdAt": now_iso,
            "pageNum": 1,
            "folderId": None,
            "metadata": {"owner": "local", "status": "ready"},
            "mode": "flash",
        }
        
        # 4. Create the exact Pages schema expected by LocalAPI
        pages = [{"page_index": 1, "markdown": raw_markdown}]

        # 5. NATIVELY REGISTER the document into the client's internal DocStore!
        print("Registering document into internal DocStore ledger...")
        store = self.client._api._store
        
        # Acquire the thread lock to safely write to the registry (just like the source code)
        with store.lock():
            store.save_document(doc_id, meta, structure, pages)
            
        print(f"✅ Tree officially registered in PageIndex for ID: {doc_id}")
        return doc_id

    def extract_relevant_schema(self, user_query: str, active_doc_ids: list) -> dict:
        """
        STEP 2: Traverse the Tree and output the pruned JSON Schema.
        """
        print(f"\n--- [Step 2] Agent Retrieval for Docs: {active_doc_ids} ---")
        
        # Double curly braces {{ }} escape the JSON format so the f-string works natively
        extraction_prompt = f"""
        User Query: "{user_query}"
        
        Task: Navigate the database documentation to find the exact tables, columns, and relationships needed to answer the user's query. 
        
        Rules:
        1. DO NOT write the SQL query.
        2. First, EXPAND the "Tables" node to find the required tables.
        3. If your query requires data from more than one table, you MUST EXPAND the "Relationships" node.
        4. Inside the Relationships node, find the specific join that connects your chosen tables and issue a READ command on it.
        5. If only one table is needed, leave the "relationships" array empty.
        6. Output ONLY valid JSON in the exact structure below, with no conversational text.
        
        Required JSON Structure:
        {{
            "tables": {{
                "table_name": [
                    {{
                        "columnname": "name of the column", 
                        "columndescription": "description, data type, and enum mappings"
                    }}
                ]
            }},
            "relationships": [
                {{
                    "target": "target table name",
                    "join_logic": "the exact SQL join logic provided in the docs",
                    "purpose": "why these tables are joined"
                }}
            ]
        }}
        """
        
        raw_response = self.client.chat(extraction_prompt, doc_id=active_doc_ids)
        cleaned_response = self._clean_json_output(raw_response)
        
        try:
            pruned_schema = json.loads(cleaned_response)
            print("✅ Successfully extracted pruned schema!")
            return pruned_schema
        except json.JSONDecodeError:
            print("❌ Agent failed to output valid JSON.")
            print(f"Raw Output:\n{raw_response}")
            return {"error": "Failed to parse schema JSON", "raw_output": raw_response}

    def _clean_json_output(self, text: str) -> str:
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return text.strip()