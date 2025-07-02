from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseAgent(ABC):
    def __init__(self, config: Dict[str, Any]):
        self.config = config

    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process the input and return the result"""
        pass

    @abstractmethod
    async def get_capabilities(self) -> Dict[str, Any]:
        """Return the capabilities of this agent"""
        pass 