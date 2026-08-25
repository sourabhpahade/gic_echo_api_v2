import re
import pyodbc
import asyncio
from typing import List, Dict, Any
from core.config import settings

class SQLExecutionError(Exception):
    """Custom exception raised when SQL sanitization or execution fails."""
    pass


class SQLExecutionService:

    def __init__(self):

        """
        Initializes the Database Execution Service.
        connection_string: ODBC connection string for MS SQL Server.
        """
        self.connection_string = settings.DB_CONNECTION_STRING
        self.connection_timeout = settings.DB_CONNECTION_TIMEOUT
        self.query_timeout = settings.DB_QUERY_TIMEOUT
        self.fetch_limit = settings.DB_FETCH_LIMIT

        # Prohibited keywords/patterns (checked with word boundaries where appropriate)
        self._blocked_keywords = [
            r"\bINSERT\b",
            r"\bUPDATE\b",
            r"\bDELETE\b",
            r"\bDROP\b",
            r"\bTRUNCATE\b",
            r"\bALTER\b",
            r"\bCREATE\b",
            r"\bEXEC\b",
            r"\bEXECUTE\b",
            r"\bGRANT\b",
            r"\bREVOKE\b",
            r"\bMERGE\b",
            r"\bSHUTDOWN\b",
            r"\bBACKUP\b",
            r"\bRESTORE\b",
            r"--",          # SQL single-line comment injection
            r"/\*",         # SQL multi-line comment injection
        ]

    def sanitize_query(self, raw_llm_output: str) -> str:

        """
        Cleans and sanitizes raw LLM output into a safe, executable T-SQL SELECT query.
        Raises SQLExecutionError if a dangerous command is detected or format is invalid.
        """

        if not raw_llm_output or not raw_llm_output.strip():
            raise SQLExecutionError("Received empty query from LLM.")

        cleaned = raw_llm_output.strip()

        # 1. Strip Markdown code fences if present (```sql ... ``` or ``` ...)
        markdown_match = re.search(r"```(?:sql)?\s*([\s\S]*?)\s*```", cleaned, re.IGNORECASE)
        if markdown_match:
            cleaned = markdown_match.group(1).strip()

        # 2. Strip trailing semicolons or whitespace
        cleaned = cleaned.rstrip(";").strip()

        # 3. Check against blocklisted destructive keywords/patterns
        for pattern in self._blocked_keywords:
            if re.search(pattern, cleaned, re.IGNORECASE):
                raise SQLExecutionError(
                    f"Security Alert: Query rejected due to forbidden keyword/pattern: {pattern}"
                )

        # 4. Check that the statement strictly begins with SELECT or WITH (for CTEs)
        # Strips leading whitespace/newlines before checking
        first_word_match = re.match(r"^\s*([A-Za-z]+)", cleaned)
        if not first_word_match:
            raise SQLExecutionError("Unable to identify SQL command type.")

        first_word = first_word_match.group(1).upper()
        if first_word not in ("SELECT", "WITH"):
            raise SQLExecutionError(
                f"Invalid query type '{first_word}'. Only SELECT and WITH (CTE) queries are permitted."
            )

        return cleaned

    async def execute_query(self, sql_query: str) -> List[Dict[str, Any]]:
        """
        Executes a sanitized SQL query asynchronously using env configurations.
        """
        if not self.connection_string:
            raise SQLExecutionError("Database connection string is missing or not configured in .env.")

        def _run_sync_query() -> List[Dict[str, Any]]:
            try:
                # 1. Connection Timeout applied here
                with pyodbc.connect(self.connection_string, timeout=self.connection_timeout) as conn:
                    cursor = conn.cursor()
                    
                    # 2. Query Execution Timeout applied here
                    conn.timeout = self.query_timeout 
                    
                    cursor.execute(sql_query)
                    
                    # 3. Fetch Logic: Handle -1 for all records, otherwise enforce the limit
                    if self.fetch_limit == -1:
                        rows = cursor.fetchall()
                    else:
                        rows = cursor.fetchmany(self.fetch_limit)

                    print(f"raw DB data : {rows} \n\n")
                    columns = [column[0] for column in cursor.description]

                
                    if not rows:
                        return []

                    # 4. Serialization
                    columns = [column[0] for column in cursor.description]

                    #return [dict(zip(columns, row)) for row in rows]
  
                    json_friendly_results = []
     
                    for row in rows:
                        row_dict = {}
                        for i, col_name in enumerate(columns):
                            row_dict[col_name] = row[i]
                        json_friendly_results.append(row_dict)

                    return json_friendly_results
                    
                    
            except pyodbc.OperationalError as e:
                raise SQLExecutionError(f"Database connectivity or timeout error: {str(e)}")
            except pyodbc.ProgrammingError as e:
                raise SQLExecutionError(f"SQL Syntax or Schema error: {str(e)}")
            except pyodbc.Error as e:
                raise SQLExecutionError(f"Database execution failed: {str(e)}")

        return await asyncio.to_thread(_run_sync_query)


    async def process_user_query(self, raw_llm_sql: str):

        # =========================================================
        # Step : Database Execution & Sanitization (MVP)
        # =========================================================
        try:
            # Sanitize
            sanitized_sql = self.sanitize_query(raw_llm_sql)
            print(f"sanitized SQL : {sanitized_sql} \n\n")

            # Execute
            query_results = await self.execute_query(sanitized_sql)

            # Return Success
            return {
                "status": "success",
                "message": "Query executed successfully.",
                "generated_sql": sanitized_sql,
                "row_count": len(query_results),
                "data": query_results
            }

        except SQLExecutionError as e:
            # Returns the exact database error so you can debug the AI's logic
            return {
                "status": "error",
                "message": f"Database Execution Failed: {str(e)}",
                "generated_sql": raw_llm_sql,
                "data": []
            }
        except Exception as e:
            return {
                "status": "critical_error",
                "message": f"An unexpected system error occurred: {str(e)}",
                "data": []
            }
