import re
from pathlib import Path
from typing import Dict, List, Set,Any

class OKFDependencyService:

    def get_candidate_schemas(self, base_dir: Path, seed_table_paths: List[str]) -> Dict[str, List[str]]:
        """Gathers seed tables and their 1-level deep direct joins."""
        candidates = {}
        tables_to_process = set(seed_table_paths)
        
        # Gather direct joins (1 level deep)
        for seed_path in seed_table_paths:
            joins = self._extract_direct_joins(base_dir, seed_path)
            tables_to_process.update(joins)
        
        for rel_path in tables_to_process:
            clean_path = rel_path.lstrip("/")
            file_path = (base_dir / clean_path).resolve()
            if file_path.exists():
                table_name = file_path.stem
                candidates[table_name] = self._extract_columns(file_path)
                
        return candidates

    def build_trimmed_sqlcoder_prompt(self, pruned_schema: Dict[str, Any], user_query: str, base_dir: Path = None)-> str:
        prompt_blocks = []

        for table_name, selected_cols in pruned_schema.items():
            if not selected_cols or not isinstance(selected_cols, list):
                continue

            table_lines = [f"Table: {table_name}", "Columns:"]

            for col_info in selected_cols:
                # Handles dictionary items: {"column_name": "...", "description": "..."}
                if isinstance(col_info, dict):
                    col_name = col_info.get("column_name", "").strip()
                    desc = col_info.get("description", "").strip()
                    if col_name:
                        table_lines.append(f"  - `{col_name}` : {desc}" if desc else f"  - `{col_name}`")

                # Handles string items fallback: "column_name"
                elif isinstance(col_info, str):
                    col_name = col_info.strip()
                    if col_name:
                        table_lines.append(f"  - `{col_name}`")

            if len(table_lines) > 2:
                prompt_blocks.append("\n".join(table_lines))

        schema_text = "\n\n".join(prompt_blocks)

        return (
            f"### Task\nGenerate a SQL query to answer [QUESTION]{user_query}[/QUESTION]\n\n"
            f"### Instructions\n- If you cannot answer the question with the available database schema, return 'I do not know'\n"
            f"- Use standard SQL syntax.\n- Write strict, executable SQL without any markdown formatting or explanations.\n\n"
            f"### Database Schema\nThe query will run on a database with the following schema:\n{schema_text}\n\n"
            f"### Answer\nGiven the database schema, here is the SQL query that answers [QUESTION]{user_query}[/QUESTION]\n"
            f"[SQL]\n"
        )

    def _extract_direct_joins(self, base_dir: Path, rel_path: str) -> Set[str]:
        joins = set()
        clean_path = rel_path.lstrip("/")
        file_path = (base_dir / clean_path).resolve()
        if not file_path.exists():
            return joins
        
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        if "## Joins" in content:
            joins_section = content.split("## Joins")[1].split("##")[0]
            matches = re.findall(r'\[.*?\]\((.*?\.md)\)', joins_section)
            for raw_link in matches:
                joins.add(raw_link.lstrip("/"))
        return joins

    def _extract_columns(self, file_path: Path) -> List[str]:
        cols = []
        with open(file_path, "r", encoding="utf-8") as f:
            in_schema = False
            for line in f.readlines():
                if line.startswith("## Schema"):
                    in_schema = True
                    continue
                if in_schema and line.startswith("## "):
                    break
                if in_schema and line.strip().startswith("* `"):
                    cols.append(line.strip())
        return cols