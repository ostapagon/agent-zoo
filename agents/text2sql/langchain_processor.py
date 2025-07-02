from typing import Dict, Any
import logging
from services.llm_service import LLMService
from services.database import DatabaseService

logger = logging.getLogger(__name__)

SQL_GEN_PROMPT_TEMPLATE = """
Given the following database schema:
{schema}

Convert the following natural language question into a SQL query.

Question: {question}

Please provide a SQL query that would answer this question.
The query should be valid SQL and should be the complete query needed to get the answer.
"""

ANSWER_FORMAT_PROMPT_TEMPLATE = """
Given the following database schema:
{schema}

Original question: {question}
SQL query: {sql_query}
Query results: {query_results}

Please provide a natural language answer that directly addresses the original question.
The answer should be clear, concise, and easy to understand.
Do not mention SQL or technical details in the response.
"""

class Text2SQLProcessor:
    def __init__(self, config: Dict[str, Any]):
        """Initialize the Text2SQL processor with configuration."""
        self.config = config
        self.llm_service = LLMService(config)
        self.db_service = DatabaseService(config)
        logger.info("Text2SQL processor initialized")

    async def process_text(self, text: str) -> Dict[str, Any]:
        """Process the input text and generate a SQL query."""
        try:
            logger.info(f"Processing text: {text}")
            await self.db_service.initialize()
            schema_result = await self.db_service.mschema(format_type="text")
            if not schema_result["success"]:
                logger.error(f"Failed to get schema: {schema_result['error']}")
                return {"sql_query": None, "answer": f"Error getting schema: {schema_result['error']}"}
            schema_text = schema_result["schema"]

            # Use the SQL generation prompt template
            prompt = SQL_GEN_PROMPT_TEMPLATE.format(schema=schema_text, question=text)
            logger.info(f"SQL generation prompt: {prompt}")
            sql_query = await self.llm_service.generate_response(
                prompt=prompt,
                system_message="""You are a SQL expert that converts natural language questions into SQL queries.\nYour response should be a valid SQL query only, with no additional text or explanation.\nThe query should be complete and ready to execute.""",
                temperature=0.3
            )
            sql_query = sql_query.strip()
            if sql_query.startswith("```sql"):
                sql_query = sql_query[6:]
            if sql_query.endswith("```"):
                sql_query = sql_query[:-3]
            sql_query = sql_query.strip()
            logger.info(f"Generated SQL query: {sql_query}")

            # Execute the SQL query
            query_result = await self.db_service.execute_query(sql_query)
            if not query_result["success"]:
                logger.error(f"Query execution failed: {query_result['error']}")
                return {"sql_query": sql_query, "answer": f"Error executing query: {query_result['error']}"}

            # Use the answer formatting prompt template
            format_prompt = ANSWER_FORMAT_PROMPT_TEMPLATE.format(
                schema=schema_text,
                question=text,
                sql_query=sql_query,
                query_results=query_result['data']
            )
            response = await self.llm_service.generate_response(
                prompt=format_prompt,
                system_message="""You are a helpful assistant that explains database query results in natural language.\nYour response should be clear, concise, and directly answer the user's question.\nDo not mention SQL queries or technical details.\nFocus on providing the information the user asked for in a natural way.""",
                temperature=0.7
            )
            return {"sql_query": sql_query, "answer": response.strip()}
        except Exception as e:
            logger.error(f"Error in Text2SQL processor: {str(e)}", exc_info=True)
            raise 