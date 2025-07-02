from typing import Dict, Any
import logging
from sqlalchemy import text, inspect
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)

class SQLAlchemyConnection:
    """Database connection using SQLAlchemy."""
    
    def __init__(self):
        self.async_engine = None
        self.session_factory = None
        self.db_type = None
        
    async def connect(self, config: Dict[str, Any]):
        """Initialize SQLAlchemy connection."""
        database_url = config.get("url")
        if not database_url:
            raise ValueError("Database URL not found in configuration")
        
        # Convert to async URL
        async_url = self._convert_to_async_url(database_url)
        self.db_type = self._get_database_type(async_url)
        
        # Create async engine
        self.async_engine = create_async_engine(
            async_url,
            echo=config.get("echo", False),
            pool_size=config.get("max_connections", 10)
        )
        
        # Create session factory
        self.session_factory = async_sessionmaker(
            self.async_engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        # Test connection
        async with self.async_engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
    
    def _convert_to_async_url(self, url: str) -> str:
        """Convert standard database URL to async URL."""
        if url.startswith("postgresql://") and "+asyncpg" not in url:
            return url.replace("postgresql://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgres://") and "+asyncpg" not in url:
            return url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif url.startswith("mysql://") and "+aiomysql" not in url:
            return url.replace("mysql://", "mysql+aiomysql://", 1)
        elif url.startswith("sqlite://") and "+aiosqlite" not in url:
            return url.replace("sqlite://", "sqlite+aiosqlite://", 1)
        return url
    
    def _get_database_type(self, url: str) -> str:
        """Extract database type from connection URL."""
        if (url.startswith("postgresql://") or url.startswith("postgres://") or 
            url.startswith("postgresql+asyncpg://")):
            return "postgresql"
        elif (url.startswith("mysql://") or url.startswith("mysql+aiomysql://")):
            return "mysql"
        elif (url.startswith("sqlite://") or url.startswith("sqlite+aiosqlite://")):
            return "sqlite"
        else:
            raise ValueError(f"Unsupported database URL format: {url}")
    
    async def execute_query(self, query: str) -> Dict[str, Any]:
        """Execute a SQL query and return the results."""
        if not self.async_engine:
            raise RuntimeError("Database connection not initialized")
        
        try:
            async with self.session_factory() as session:
                is_select = query.strip().upper().startswith("SELECT")
                
                if is_select:
                    result = await session.execute(text(query))
                    rows = result.fetchall()
                    columns = result.keys()
                    data = [dict(zip(columns, row)) for row in rows]
                    
                    return {
                        "success": True,
                        "data": data,
                        "error": None
                    }
                else:
                    result = await session.execute(text(query))
                    await session.commit()
                    
                    return {
                        "success": True,
                        "data": f"Query executed successfully. Rows affected: {result.rowcount}",
                        "error": None
                    }
                    
        except SQLAlchemyError as e:
            return {
                "success": False,
                "data": None,
                "error": str(e)
            }
    
    async def get_schema_info(self) -> Dict[str, Any]:
        """Get database schema information using SQLAlchemy inspector."""
        if not self.async_engine:
            raise RuntimeError("Database connection not initialized")

        async with self.async_engine.connect() as conn:
            def get_info(sync_conn):
                inspector = inspect(sync_conn)
                table_names = inspector.get_table_names()
                tables_data = []
                foreign_keys_data = []
                
                for table_name in table_names:
                    columns = inspector.get_columns(table_name)
                    for column in columns:
                        tables_data.append({
                            "table_name": table_name,
                            "column_name": column["name"],
                            "data_type": column["type"].__class__.__name__,
                            "is_nullable": "YES" if column.get("nullable", True) else "NO",
                            "column_default": str(column.get("default", ""))
                        })
                    
                    foreign_keys = inspector.get_foreign_keys(table_name)
                    for fk in foreign_keys:
                        for column in fk.get("constrained_columns", []):
                            foreign_keys_data.append({
                                "table_name": table_name,
                                "column_name": column,
                                "foreign_table_name": fk.get("referred_table"),
                                "foreign_column_name": fk.get("referred_columns", [None])[0]
                            })
                
                return {
                    "tables": tables_data,
                    "foreign_keys": foreign_keys_data
                }
            
            return await conn.run_sync(get_info)
    
    async def close(self):
        """Close SQLAlchemy connection."""
        if self.async_engine:
            await self.async_engine.dispose()
    
    def get_database_type(self) -> str:
        """Get the database type."""
        return self.db_type or "unknown" 