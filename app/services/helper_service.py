import re

class HelperService:

    def extract_relevant_relationships(self, selected_tables: list, full_relationships_text: str) -> str:
        """
        Scans the master relationships file and returns only the lines 
        that contain at least one of the selected tables.
        """
        relevant_lines = []
        
        # Clean up the table names (e.g., remove paths/extensions if they exist in the list)
        import pathlib
        clean_tables = [pathlib.Path(t).stem for t in selected_tables]
        
        # Split the relationships file into individual lines
        lines = full_relationships_text.strip().split('\n')
        
        for line in lines:
            # Skip empty lines or markdown headers/comments
            if not line.strip() or line.strip().startswith('#'):
                continue
                
            # Check if any of our exact table names appear in this line
            for table in clean_tables:
                # \b ensures we match "User" but not "User_Log"
                if re.search(rf'\b{re.escape(table)}\b', line, re.IGNORECASE):
                    relevant_lines.append(line.strip())
                    break  # Found a match! Add line and move to the next one
                    
        # If no relationships were found (e.g., a single-table query), return a fallback message
        if not relevant_lines:
            return "No explicit relationships found for the selected tables."
            
        return "\n".join(relevant_lines)