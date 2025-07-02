from typing import TypedDict, List, Optional
from enum import Enum

class AgentCapability(TypedDict):
    name: str
    description: str
    supported_operations: List[str]

class AgentResponse(TypedDict):
    success: bool
    response: Optional[str]
    error: Optional[str]

class AgentStatus(Enum):
    IDLE = "idle"
    PROCESSING = "processing"
    ERROR = "error"
    COMPLETED = "completed" 