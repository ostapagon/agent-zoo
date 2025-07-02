from typing import Dict, Any, Optional, List
import logging
from langchain_openai import AzureChatOpenAI
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self, config: Dict[str, Any]):
        """Initialize the LLM service with configuration."""
        self.config = config
        self.llm = self._initialize_llm()
        logger.info("LLM service initialized")

    def _initialize_llm(self) -> BaseChatModel:
        """Initialize the LLM based on configuration."""
        try:
            # Get Azure OpenAI configuration
            azure_config = self.config.get("azure_openai", {})
            if not azure_config:
                raise ValueError("Azure OpenAI configuration not found")

            # Initialize Azure OpenAI
            llm = AzureChatOpenAI(
                openai_api_version=azure_config.get("api_version", "2024-02-15-preview"),
                azure_deployment=azure_config.get("deployment_name"),
                azure_endpoint=azure_config.get("endpoint"),
                api_key=azure_config.get("api_key"),
                temperature=azure_config.get("temperature", 0.5),
                model_name=azure_config.get("model_name", "gpt-4o-mini"),
            )
            logger.info(f"Initialized Azure OpenAI with model: {azure_config.get('model_name')}")
            return llm

        except Exception as e:
            logger.error(f"Error initializing LLM: {str(e)}", exc_info=True)
            raise

    async def generate_response(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Generate a response using the LLM.
        
        Args:
            prompt: The user prompt
            system_message: Optional system message to set context
            temperature: Optional temperature override
            max_tokens: Optional max tokens override
            
        Returns:
            The generated response as a string
        """
        try:
            # Prepare messages
            messages: List[BaseMessage] = []
            
            if system_message:
                messages.append(SystemMessage(content=system_message))
            
            messages.append(HumanMessage(content=prompt))
            
            # Set generation parameters
            generation_kwargs = {}
            if temperature is not None:
                generation_kwargs["temperature"] = temperature
            if max_tokens is not None:
                generation_kwargs["max_tokens"] = max_tokens
            
            # Generate response
            response = await self.llm.ainvoke(
                messages,
                **generation_kwargs
            )
            
            return response.content

        except Exception as e:
            logger.error(f"Error generating response: {str(e)}", exc_info=True)
            raise