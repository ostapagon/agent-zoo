import sys
from pathlib import Path
import logging

# Add the project root to Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
import uvicorn

from core.config import Config
from agents.agent_factory import AgentFactory
from agents.orchestrator.orchestrator_agent import OrchestratorAgent
from models.schemas import QuestionRequest, QuestionResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Text2SQL Chatbot API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize configuration and agents
logger.info("Initializing configuration and agents...")
config = Config()
agent_factory = AgentFactory(config)
orchestrator = OrchestratorAgent(config)

@app.on_event("startup")
async def startup_event():
    """Initialize the orchestrator on startup."""
    logger.info("Initializing orchestrator...")
    await orchestrator.initialize(agent_factory.get_all_agents())
    logger.info("Orchestrator initialized successfully")

@app.post("/api/process", response_model=QuestionResponse)
async def process_request(request: QuestionRequest) -> QuestionResponse:
    """Process a question through the orchestrator"""
    try:
        logger.info(f"Received request: {request}")
        
        # Convert question request to agent request
        agent_request = {
            "question": request.question
        }
        logger.info(f"Converted to agent request: {agent_request}")
        
        # Process through orchestrator
        logger.info("Sending request to orchestrator...")
        agent_response = await orchestrator.process(agent_request)
        logger.info(f"Received result from orchestrator: {agent_response}")
        
        if not agent_response["success"]:
            logger.error(f"Agent returned error: {agent_response['error']}")
            raise HTTPException(status_code=400, detail=agent_response["error"])
        
        # Convert agent response to question response
        response = QuestionResponse(
            answer=agent_response["data"],
        )
        logger.info(f"Sending response: {response}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/agents")
async def get_available_agents():
    """Get list of available agents and their capabilities"""
    try:
        logger.info("Getting available agents...")
        agents_info = []
        for agent in agent_factory.get_all_agents():
            capabilities = await agent.get_capabilities()
            agents_info.append({
                "name": capabilities["name"],
                "description": capabilities["description"],
                "supported_tasks": capabilities["supported_tasks"]
            })
        logger.info(f"Found {len(agents_info)} agents")
        return {"agents": agents_info}
    except Exception as e:
        logger.error(f"Error getting agents: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    try:
        logger.info("Health check requested")
        return {"status": "healthy", "agents": list(orchestrator.agents.keys())}
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 