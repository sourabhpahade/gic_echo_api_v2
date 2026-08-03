import re
from pathlib import Path
from typing import Set

class OKFDependencyService:
    """
    Tier 3: Programmatic Dependency Expansion
    Parses ## Joins in OKF table markdown files deterministically without LLM tokens.
    """

    def extract_table_dependencies(self, base_dir: Path, core_table_rel_path: str) -> Set[str]:
        visited_files: Set[str] = set()
        self._resolve_dependencies_recursive(base_dir, core_table_rel_path, visited_files)
        return visited_files

    def _resolve_dependencies_recursive(self, base_dir: Path, rel_path: str, visited: Set[str]) -> None:

        clean_rel_path = rel_path.lstrip("/")

        if clean_rel_path in visited:
            return

        visited.add(clean_rel_path)
        
        file_path = (base_dir / clean_rel_path).resolve()

        if not file_path.exists():
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            if "## Joins" not in content:
                return

            joins_section = content.split("## Joins")[1].split("##")[0]
            
            # Matches markdown links: [/mdms_master_db/M_Connection_Status.md](/mdms_master_db/M_Connection_Status.md)
            md_link_pattern = r'\[.*?\]\((.*?\.md)\)'
            matches = re.findall(md_link_pattern, joins_section)

            for raw_link in matches:
                dep_rel_path = raw_link.lstrip("/")
                self._resolve_dependencies_recursive(base_dir, dep_rel_path, visited)

        except Exception as e:
            print(f"Error reading dependency {rel_path}: {e}")