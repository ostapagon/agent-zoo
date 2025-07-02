from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class QuestionRequest(BaseModel):
    """Request data from UI containing a question."""
    question: str = Field(..., description="Natural language question to be answered")
    
    class Config:
        schema_extra = {
            "example": {
                "question": "Show me all users who made purchases in the last month"
            }
        }

class QuestionResponse(BaseModel):
    """Response data containing the answer to the question."""
    answer: str = Field(..., description="Answer to the question")
    
    class Config:
        schema_extra = {
            "example": {
                "answer": "The following users made purchases in the last month: John Doe, Jane Smith",
            }
        }