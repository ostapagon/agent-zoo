"""
Main database service that provides a unified interface for database operations.

This service combines SQLAlchemy connections with LLM-friendly schema formatting
to provide a complete database solution for Text2SQL applications.
"""

from typing import Dict, Any
from .connection import SQLAlchemyConnection
from .schema_formatter import SchemaFormatter

class DatabaseService:
    """Main database service with unified interface and schema functionality."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the database service with configuration."""
        self.config = config
        self.connection = None
        self.schema_formatter = None
        self.db_type = config.get("database", {}).get("type", "postgresql").lower()

    async def initialize(self):
        """Initialize the database connection and schema formatter."""
        db_config = self.config.get("database", {})
        if not db_config:
            raise ValueError("Database configuration not found")

        # Create SQLAlchemy connection
        self.connection = SQLAlchemyConnection()
        await self.connection.connect(db_config)
        
        # Get actual database type from connection
        actual_db_type = self.connection.get_database_type()
        
        # Create schema formatter
        self.schema_formatter = SchemaFormatter(actual_db_type)

    async def execute_query(self, query: str) -> Dict[str, Any]:
        """
        Execute a SQL query and return the results.
        
        Args:
            query: The SQL query to execute
            
        Returns:
            Dictionary containing:
            - success: bool indicating if query executed successfully
            - data: List of results (if SELECT) or number of affected rows (if INSERT/UPDATE/DELETE)
            - error: Error message if query failed
        """
        if not self.connection:
            await self.initialize()

        return await self.connection.execute_query(query)

    async def mschema(self, format_type: str = "text") -> Dict[str, Any]:
        """
        Get database schema in a format optimized for LLMs.
        
        Args:
            format_type: Output format ("text", "json", "markdown")
            
        Returns:
            Dictionary containing:
            - success: bool indicating if schema retrieval was successful
            - schema: Schema information in the requested format
            - error: Error message if schema retrieval failed
        """
        if not self.connection:
            await self.initialize()

        try:
            # Get raw schema information from database
            schema_info = await self.connection.get_schema_info()
            
            # Format schema using the formatter
            formatted_schema = self.schema_formatter.format_schema(schema_info, format_type)

            return {
                "success": True,
                "schema": formatted_schema,
                "error": None
            }

        except Exception as e:
            return {
                "success": False,
                "schema": None,
                "error": str(e)
            }

    def get_supported_schema_formats(self) -> list:
        """Get list of supported schema format types."""
        if self.schema_formatter:
            return self.schema_formatter.get_supported_formats()
        return ["text", "json", "markdown"]

    def get_database_type(self) -> str:
        """Get the current database type."""
        if self.connection:
            return self.connection.get_database_type()
        return self.db_type

    async def close(self):
        """Close the database connection."""
        if self.connection:
            await self.connection.close()

    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close() 