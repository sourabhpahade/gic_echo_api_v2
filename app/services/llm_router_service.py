# app/services/llm_router_service.py
import json
from typing import List
from fastapi import HTTPException
from openai import AsyncOpenAI, OpenAIError

class LLMRouterService:

    def __init__(self, base_url: str, model_name: str):
        formatted_url = base_url.rstrip("/")

        if not formatted_url.endswith("/v1"):
            formatted_url += "/v1"

        # Initialize AsyncOpenAI client pointing to local Ollama
        self.client = AsyncOpenAI(
            base_url=formatted_url,
            api_key="ollama"  # Required by OpenAI SDK, ignored by local Ollama
        )
        self.model_name = model_name

    async def execute_routing_pass(self, user_query: str, index_content: str) -> List[str]:

        #Executes a deterministic routing pass against the local router model.
        #Works for both Tier 1 (Global) and Tier 2 (Table) indexes.
    
        system_prompt = (
            "You are a highly precise database routing agent for an enterprise Text-to-SQL system.\n"
            "Your task is to analyze a User Query and a provided Database Index, and determine which file paths or folders contain the necessary data.\n\n"
            "Rules for Output:\n"
            "1. Output ONLY a valid JSON array of the absolute paths. Example: [\"/mdms_master_db/index.md\"]\n"
            "2. Do NOT output markdown formatting (such as ```json), conversational text, or explanations.\n"
            "3. Rely strictly on the Keywords, Synonyms, and Cross-Database Joins provided in the index to make your decision."
        )

        user_content = f"Index:\n{index_content}\n\nUser Query: {user_query}"

        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                temperature=0.0
            )

            result_text = response.choices[0].message.content or ""

        except OpenAIError as exc:
            raise HTTPException(
                status_code=503, 
                detail=f"Ollama local service error: {exc}"
            )

        try:
            clean_text = result_text.strip().strip("`").removeprefix("json").strip()
            parsed_result = json.loads(clean_text)

            if not isinstance(parsed_result, list):
                raise ValueError("LLM response is not a valid JSON list.")

            return parsed_result

        except (json.JSONDecodeError, ValueError) as err:
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to parse LLM router JSON output: {err}. Raw output: {result_text}"
            )