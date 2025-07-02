"""
Schema formatter module for LLM-friendly database schema representation.

This module provides the mschema functionality that formats database schema information
in various formats optimized for LLMs, inspired by the xiyan server approach.
"""

from typing import Dict, Any, List

class SchemaFormatter:
    """Handles formatting of database schema information for LLMs."""
    
    def __init__(self, db_type: str = "unknown"):
        """Initialize the schema formatter."""
        self.db_type = db_type
    
    def format_schema(self, schema_info: Dict[str, Any], format_type: str = "text") -> str:
        """
        Format schema information in the specified format.
        
        Args:
            schema_info: Raw schema information from database
            format_type: Output format ("text", "json", "markdown")
            
        Returns:
            Formatted schema string
        """
        if format_type == "text":
            return self._format_as_text(schema_info)
        elif format_type == "json":
            return self._format_as_json(schema_info)
        elif format_type == "markdown":
            return self._format_as_markdown(schema_info)
        else:
            raise ValueError(f"Unsupported format type: {format_type}")
    
    def _format_as_text(self, schema_info: Dict[str, Any]) -> str:
        """Format schema information as plain text for LLMs."""
        tables = schema_info.get("tables", [])
        foreign_keys = schema_info.get("foreign_keys", [])
        
        # Group columns by table
        table_schema = {}
        for row in tables:
            table_name = row.get("table_name")
            if table_name not in table_schema:
                table_schema[table_name] = []
            
            if row.get("column_name"):
                table_schema[table_name].append({
                    "name": row.get("column_name"),
                    "type": row.get("data_type"),
                    "nullable": row.get("is_nullable") == "YES",
                    "default": row.get("column_default")
                })
        
        # Build foreign key relationships
        fk_relationships = {}
        for fk in foreign_keys:
            table = fk.get("table_name")
            if table not in fk_relationships:
                fk_relationships[table] = []
            fk_relationships[table].append({
                "column": fk.get("column_name"),
                "references_table": fk.get("foreign_table_name"),
                "references_column": fk.get("foreign_column_name")
            })
        
        # Format as text
        schema_text = f"Database Schema ({self.db_type.upper()}):\n\n"
        
        for table_name, columns in table_schema.items():
            schema_text += f"Table: {table_name}\n"
            schema_text += "-" * (len(table_name) + 7) + "\n"
            
            for col in columns:
                nullable = "NULL" if col["nullable"] else "NOT NULL"
                default = f" DEFAULT {col['default']}" if col["default"] else ""
                schema_text += f"  {col['name']:<20} {col['type']:<15} {nullable}{default}\n"
            
            # Add foreign key information
            if table_name in fk_relationships:
                schema_text += "\n  Foreign Keys:\n"
                for fk in fk_relationships[table_name]:
                    schema_text += f"    {fk['column']} -> {fk['references_table']}.{fk['references_column']}\n"
            
            schema_text += "\n"
        
        return schema_text
    
    def _format_as_json(self, schema_info: Dict[str, Any]) -> str:
        """Format schema information as JSON string."""
        import json
        
        tables = schema_info.get("tables", [])
        foreign_keys = schema_info.get("foreign_keys", [])
        
        # Group columns by table
        table_schema = {}
        for row in tables:
            table_name = row.get("table_name")
            if table_name not in table_schema:
                table_schema[table_name] = {
                    "columns": [],
                    "foreign_keys": []
                }
            
            if row.get("column_name"):
                table_schema[table_name]["columns"].append({
                    "name": row.get("column_name"),
                    "type": row.get("data_type"),
                    "nullable": row.get("is_nullable") == "YES",
                    "default": row.get("column_default")
                })
        
        # Add foreign key relationships
        for fk in foreign_keys:
            table = fk.get("table_name")
            if table in table_schema:
                table_schema[table]["foreign_keys"].append({
                    "column": fk.get("column_name"),
                    "references_table": fk.get("foreign_table_name"),
                    "references_column": fk.get("foreign_column_name")
                })
        
        formatted_schema = {
            "database_type": self.db_type,
            "tables": table_schema
        }
        
        return json.dumps(formatted_schema, indent=2)
    
    def _format_as_markdown(self, schema_info: Dict[str, Any]) -> str:
        """Format schema information as Markdown."""
        tables = schema_info.get("tables", [])
        foreign_keys = schema_info.get("foreign_keys", [])
        
        # Group columns by table
        table_schema = {}
        for row in tables:
            table_name = row.get("table_name")
            if table_name not in table_schema:
                table_schema[table_name] = []
            
            if row.get("column_name"):
                table_schema[table_name].append({
                    "name": row.get("column_name"),
                    "type": row.get("data_type"),
                    "nullable": row.get("is_nullable") == "YES",
                    "default": row.get("column_default")
                })
        
        # Build foreign key relationships
        fk_relationships = {}
        for fk in foreign_keys:
            table = fk.get("table_name")
            if table not in fk_relationships:
                fk_relationships[table] = []
            fk_relationships[table].append({
                "column": fk.get("column_name"),
                "references_table": fk.get("foreign_table_name"),
                "references_column": fk.get("foreign_column_name")
            })
        
        # Format as markdown
        markdown = f"# Database Schema ({self.db_type.upper()})\n\n"
        
        for table_name, columns in table_schema.items():
            markdown += f"## Table: `{table_name}`\n\n"
            
            # Create table header
            markdown += "| Column | Type | Nullable | Default |\n"
            markdown += "|--------|------|----------|--------|\n"
            
            for col in columns:
                nullable = "YES" if col["nullable"] else "NO"
                default = col["default"] or ""
                markdown += f"| `{col['name']}` | `{col['type']}` | {nullable} | {default} |\n"
            
            # Add foreign key information
            if table_name in fk_relationships:
                markdown += "\n**Foreign Keys:**\n\n"
                for fk in fk_relationships[table_name]:
                    markdown += f"- `{fk['column']}` → `{fk['references_table']}.{fk['references_column']}`\n"
            
            markdown += "\n---\n\n"
        
        return markdown
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported format types."""
        return ["text", "json", "markdown"]
    
    def set_database_type(self, db_type: str):
        """Update the database type."""
        self.db_type = db_type 