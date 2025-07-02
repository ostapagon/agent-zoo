from typing import Dict, Any
import logging
from agents.base.base_agent import BaseAgent
from agents.base.agent_interface import AgentResponse, AgentStatus
from agents.text2sql.langchain_processor import Text2SQLProcessor

logger = logging.getLogger(__name__)

class Text2SQLAgent(BaseAgent):
    def __init__(self, config: Dict[str, Any]):
        """Initialize the Text2SQL agent with configuration."""
        super().__init__(config)
        logger.info("Initializing Text2SQL agent")
        self.processor = Text2SQLProcessor(config)
        self.status = AgentStatus.IDLE
        logger.info("Text2SQL agent initialized successfully")

    async def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process a question and return an answer."""
        try:
            logger.info(f"Processing request: {request}")
            self.status = AgentStatus.PROCESSING
            
            # Process the text using the processor
            logger.info("Processing text with Text2SQL processor")
            result = await self.processor.process_text(request["question"])
            logger.info(f"Received result from processor: {result}")
            
            self.status = AgentStatus.COMPLETED
            return AgentResponse(
                success=True,
                data={
                    "answer": result["answer"],
                    "sql_query": result["sql_query"]
                }
            )

        except Exception as e:
            logger.error(f"Error in Text2SQL agent: {str(e)}", exc_info=True)
            self.status = AgentStatus.ERROR
            return AgentResponse(
                success=False,
                data=None,
                error=str(e)
            )

    async def get_capabilities(self) -> Dict[str, Any]:
        """Get agent capabilities."""
        capabilities = {
            "name": "text2sql",
            "description": "Converts natural language questions to SQL queries and executes them",
            "supported_tasks": ["sql", "query", "database"],
            "input_format": {
                "question": "Natural language question"
            },
            "output_format": {
                "answer": "Natural language answer",
                "sql_query": "SQL query used to generate the answer"
            }
        }
        logger.info(f"Returning capabilities: {capabilities}")
        return capabilities 