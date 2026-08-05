import json
import re
from typing import List, Dict, Any
from fastapi import HTTPException
from openai import AsyncOpenAI, OpenAIError


class LLMRouterService:

    def __init__(self, base_url: str, model_name: str):
        formatted_url = base_url.rstrip("/")
        if not formatted_url.endswith("/v1"):
            formatted_url += "/v1"

        self.client = AsyncOpenAI(base_url=formatted_url, api_key="ollama")
        self.model_name = model_name

    async def execute_routing_pass(self, user_query: str, index_content: str) -> List[str]:
        """Tier 1 & 2: Route query to database folders and seed tables.
        
        Expected LLM output shape:
        { "result": ["/mdms_master_db/l_consumer_lookup.md", ...] }
        """
        system_prompt = (
            "You are a highly precise database routing agent for an enterprise Text-to-SQL system.\n"
            "Your task is to analyze a User Query and a provided Database Index, and determine which file paths or folders contain the necessary data.\n\n"
            "Rules for Output:\n"
            '1. Output ONLY a valid JSON object containing a single key "result" mapped to an array of absolute paths. Example: {"result": ["/mdms_master_db/index.md"]}\n'
            "2. Do NOT output markdown formatting (such as ```json), conversational text, or explanations.\n"
            "3. Rely strictly on the Keywords, Synonyms, and Cross-Database Joins provided in the index to make your decision."
        )
        user_content = f"Index:\n{index_content}\n\nUser Query: {user_query}"
        
        parsed_data = await self._call_llm_json(system_prompt, user_content)

        # Handle Object format: {"result": ["path1", "path2"]}
        if isinstance(parsed_data, dict):
            result_list = parsed_data.get("result") or parsed_data.get("results")
            if isinstance(result_list, list):
                return result_list
            raise HTTPException(
                status_code=500,
                detail=f"Expected 'result' key with a list of paths, but got: {parsed_data}"
            )

        # Fallback for bare list: ["path1", "path2"]
        elif isinstance(parsed_data, list):
            return parsed_data

        raise HTTPException(
            status_code=500,
            detail=f"Routing pass returned an invalid structure: {parsed_data}"
        )

    async def prune_schema_and_columns(self, user_query: str, candidate_schemas: Dict[str, Any]) -> Dict[str, Any]:
        """Tier 3: Prune candidate tables and extract only necessary columns with descriptions."""
        system_prompt = (
            "You are an expert SQL schema pruner.\n"
            "Your task is to analyze a User Query and a list of Candidate Database Tables with their available columns.\n"
            "Select ONLY the tables and specific columns required to construct the SQL query (including columns needed for SELECT, WHERE, JOIN, GROUP BY, ORDER BY).\n\n"
            "Rules:\n"
            "1. Include Primary Keys and Foreign Keys required to JOIN selected tables.\n"
            "2. Do NOT include unneeded tables or unneeded columns.\n"
            "3. Output ONLY a valid JSON object where keys are table names and values are arrays of objects, each with 'column_name' and 'description'.\n"
            '   Example Output: {"l_consumer_table": [{"column_name": "Consumer_Name", "description": "Name of the consumer"}, {"column_name": "ConnectionStatus_TblRefID", "description": "Foreign key to connection status"}]}\n'
            "4. Do NOT output markdown code blocks, explanations, or conversational text."
        )
        user_content = f"Candidate Schemas:\n{json.dumps(candidate_schemas, indent=2)}\n\nUser Query: {user_query}"

        parsed_data = await self._call_llm_json(system_prompt, user_content)

        # Directly return the dictionary returned by json.loads()
        if isinstance(parsed_data, dict):
            return parsed_data

        raise HTTPException(
            status_code=500,
            detail=f"Prune schema pass expected a JSON dictionary, but got: {parsed_data}"
        )

   
        """
        Tier 4: Send the strict prompt to SQLCoder and extract the query.
        """
        try:
            # Note: We do NOT use JSON mode here, as we want raw SQL text
            response = await self.client.chat.completions.create(
                model=sql_model_name,
                messages=[
                    # We pass the entire crafted template as a single user message
                    {"role": "user", "content": sqlcoder_prompt}
                ],
                temperature=0.0 # Keep at 0 for deterministic SQL generation
            )
            raw_sql = response.choices[0].message.content or ""
            print(f"Raw SQLCoder Output:\n{raw_sql}")
            
            return self._clean_sql_output(raw_sql)
            
        except OpenAIError as exc:
            raise HTTPException(status_code=503, detail=f"SQLCoder inference error: {exc}")
        
    async def _call_llm_json(self, system_prompt: str, user_content: str) -> Any:
        """Low-level helper to execute LLM request and return raw parsed JSON (dict or list)."""
        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                temperature=0.0,
                response_format={"type": "json_object"}
            )
            result_text = response.choices[0].message.content or ""
            print(f"LLM raw output: {result_text}")
        except OpenAIError as exc:
            raise HTTPException(status_code=503, detail=f"Ollama local service error: {exc}")

        try:
            # Strip markdown code blocks if the LLM included them
            clean_text = re.sub(r"```(?:json)?", "", result_text, flags=re.IGNORECASE).replace("```", "").strip()
            print(f"LLM cleaned output: {clean_text}")

            parsed_data = json.loads(clean_text)
            return parsed_data

        except (json.JSONDecodeError, ValueError) as err:
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to parse LLM JSON output. Error: {err}. Raw output: {result_text}"
            )

    async def generate_sql(self, sqlcoder_prompt: str, sql_model_name: str) -> str:
        """
        Tier 4: Send the strict prompt to SQLCoder and extract the query.
        """
        try:
            # Note: We do NOT use JSON mode here, as we want raw SQL text
            response = await self.client.chat.completions.create(
                model=sql_model_name,
                messages=[
                    # We pass the entire crafted template as a single user message
                    {"role": "user", "content": sqlcoder_prompt}
                ],
                temperature=0.0 # Keep at 0 for deterministic SQL generation
            )
            raw_sql = response.choices[0].message.content or ""
            print(f"Raw SQLCoder Output:\n{raw_sql}")
            
            return raw_sql
            
        except OpenAIError as exc:
            raise HTTPException(status_code=503, detail=f"SQLCoder inference error: {exc}")