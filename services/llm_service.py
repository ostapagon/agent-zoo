from typing import Dict, Any, Optional, List
import logging
from langchain_google_genai import ChatGoogleGenerativeAI
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
            # Get Google AI configuration
            google_config = self.config.get("google_ai", {})
            if not google_config:
                raise ValueError("Google AI configuration not found")

            # Initialize Google AI
            llm = ChatGoogleGenerativeAI(
                model=google_config.get("model_name", "gemini-2.5-flash"),
                google_api_key=google_config.get("api_key"),
                temperature=google_config.get("temperature", 0.5),
                convert_system_message_to_human=True,
            )
            logger.info(f"Initialized Google AI with model: {google_config.get('model_name')}")
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
                generation_kwargs["max_output_tokens"] = max_tokens
            
            # Generate response
            response = await self.llm.ainvoke(
                messages,
                **generation_kwargs
            )
            
            return response.content

        except Exception as e:
            logger.error(f"Error generating response: {str(e)}", exc_info=True)
            raise