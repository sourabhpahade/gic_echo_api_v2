import json
from typing import List, Dict, Any
from openai import AsyncOpenAI
from core.config import settings

class DataAnalysisService:

    """
    MVP Data Analysis Service.
    Takes a JSON-serializable list of database records and a user query,
    and returns a narrative executive summary using Phi-4.
    """

    SYSTEM_PROMPT = (
        "You are an executive data analyst. You will be given a user's question and a "
        "JSON array of database results. Your job is to analyze the data and provide a high-level, "
        "human-readable summary in sentence form.\n\n"
        "CRITICAL RULES:\n"
        "1. NARRATIVE ONLY: Write a flowing, professional paragraph (2-4 sentences). Answer the user's question immediately.\n"
        "2. NO ROW DUMPS: NEVER list, regurgitate, or print individual rows, names, or IDs.\n"
        "3. AGGREGATE THE DATA: Group the data conceptually. Mention the total count of the provided rows, date ranges, and major geographic/categorical trends instead of individual records.\n"
        "4. STRICT GROUNDING: Answer using ONLY the numbers provided in the data. Do not invent metrics.\n"
        "5. NO LISTS: Do not use numbered lists, bullet points, or markdown tables."
    )

    def __init__(self) -> None:
        formatted_url = settings.ollama_base_url.rstrip("/")
        if not formatted_url.endswith("/v1"):
            formatted_url += "/v1"

        self.client = AsyncOpenAI(base_url=formatted_url, api_key="ollama")
        self.model_name = settings.data_analysis_model_name

    async def analyze(self, user_query: str, data: List[Dict[str, Any]]) -> str:
        """
        Runs the analysis pipeline against a list of database records.
        """
        # 1. Zero-Row Guardrail
        if not data:
            return "No records were found in the database matching your criteria."

        # 2. Data Formatting
        # Convert the Python list of dicts directly into a compact JSON string
        data_json_string = json.dumps(data, default=str)

        # 3. Prompt Construction
        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {
                "role": "user", 
                "content": (
                    f"Question: {user_query}\n\n"
                    f"Database Results (Max {settings.DB_FETCH_LIMIT} rows shown):\n"
                    f"{data_json_string}"
                )
            },
        ]

        # 4. LLM Inference
        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.2,  # Low temperature for analytical consistency
                max_tokens=500,   # Shorter max output to enforce brevity
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )
            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"Error during Data Analysis LLM text generation: {e}")
            return "Analysis is temporarily unavailable due to a model generation error."