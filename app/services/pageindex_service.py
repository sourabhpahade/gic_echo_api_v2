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
from pageindex import PageIndexClient
from pageindex.page_index_md import md_to_tree
import os

# 1. MUST HAVE THESE for local LLM routing
os.environ["OPENAI_API_BASE"] = "http://localhost:11434/v1"
os.environ["OPENAI_API_KEY"] = "local"

class PageIndexService :

    def __init__(self):
        formatted_url = settings.ollama_base_url.rstrip("/")

        if not formatted_url.endswith("/v1"):
            formatted_url += "/v1"

        self.page_index_okf = settings.page_index_bundle

        self.storage_dir =  settings.page_index_storage

        self.client = PageIndexClient(
            index_model=settings.router_model_name, 
            chat_model=settings.router_model_name,
            storage_path=settings.page_index_storage
)


    async def inspect_pageindex_tree(self):
        file_path = self.page_index_okf 
        
        print(f"Parsing Markdown structure from: {file_path}")
        
        # 1. Run the async md_to_tree function
        # if_add_node_summary='no' disables the LLM API key requirement
        tree = await md_to_tree(
            file_path, 
            if_add_node_summary='no' 
        )
        
        print(f"✅ Markdown indexed successfully!")
        
        # 3. Output the result
        print("\n--- PROCESSED PAGEINDEX TREE ---")
        print(json.dumps(tree, indent=2))
        
        return tree