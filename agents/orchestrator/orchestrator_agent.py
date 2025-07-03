"""
Orchestrator Agent - A simple implementation using LangGraph for agent coordination
"""

from typing import Dict, List, Any, Optional, TypedDict, Annotated
import logging
import asyncio
from datetime import datetime
import json

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from agents.base.base_agent import BaseAgent
from agents.base.agent_interface import AgentStatus

logger = logging.getLogger(__name__)


class OrchestratorState(TypedDict):
    """Simple state for the orchestrator workflow"""
    messages: Annotated[List[BaseMessage], "Chat messages"]
    agents: Annotated[Dict[str, BaseAgent], "Available agents"]
    current_task: Annotated[str, "Current task being processed"]
    orchestration_plan: Annotated[Optional[Dict[str, Any]], "LLM-generated orchestration plan"]
    subtask_results: Annotated[List[Dict[str, Any]], "Results from subtask execution"]
    final_result: Annotated[Optional[str], "Final natural language response"]


ORCHESTRATION_TEMPLATE_PROMPT = """
You are an intelligent orchestrator that analyzes user requests and coordinates multiple agents to complete complex tasks.

Available Agents:
{agent_descriptions}

User Request: {user_request}

Your job is to:
1. Break down the request into subtasks
2. Assign each subtask to the most appropriate agent
3. Coordinate the execution
4. Synthesize the results

Return a JSON object with the following structure:
{{
    "subtasks": [
        {{
            "id": "subtask_1",
            "description": "What needs to be done",
            "assigned_agent": "agent_name",
        }}
    ],
    "coordination_plan": "Brief description of how to coordinate these subtasks"
}}
"""


class SubtaskExecutionTool(BaseTool):
    """Tool for executing subtasks with agents"""
    
    name: str = "execute_subtask"
    description: str = "Execute a subtask with a specific agent"
    agents: Dict[str, BaseAgent] = Field(default_factory=dict)
    
    async def _run(self, subtask_id: str, description: str, assigned_agent: str) -> Dict[str, Any]:
        """Execute a subtask with the assigned agent"""
        if assigned_agent in self.agents:
            process_result = await self.agents[assigned_agent].process({"question": description})
            
            if assigned_agent == "text2sql":
                actual_response = process_result['data']['answer']
            else:
                actual_response = process_result['data']
            
            return {
                "subtask_id": subtask_id,
                "description": description,
                "agent": assigned_agent,
                "status": "completed",
                "result": actual_response
            }
        else:
            return {
                "subtask_id": subtask_id,
                "description": description,
                "agent": assigned_agent,
                "status": "failed",
                "error": f"Agent {assigned_agent} not found"
            }


class OrchestratorAgent(BaseAgent):
    """Simple orchestrator agent using LangGraph for agent coordination"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.agents = {}
        self.status = AgentStatus.IDLE
        
        google_config = config.get("google_ai")
        self.llm = ChatGoogleGenerativeAI(
            model=google_config.get("model_name", "gemini-2.5-flash"),
            google_api_key=google_config.get("api_key"),
            temperature=google_config.get("temperature", 0.1),
            convert_system_message_to_human=True,
        )
        
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow with multiple nodes"""
        workflow = StateGraph(OrchestratorState)
        
        workflow.add_node("plan_orchestration", self._plan_orchestration)
        workflow.add_node("execute_subtasks", self._execute_subtasks)
        workflow.add_node("synthesize_results", self._synthesize_results)
        
        workflow.set_entry_point("plan_orchestration")
        workflow.add_edge("plan_orchestration", "execute_subtasks")
        workflow.add_edge("execute_subtasks", "synthesize_results")
        workflow.add_edge("synthesize_results", END)
        
        return workflow.compile()
    
    async def initialize(self, agents: List[BaseAgent]):
        """Initialize the orchestrator by getting agent capabilities."""
        logger.info("Initializing orchestrator agent...")
        for agent in agents:
            capabilities = await agent.get_capabilities()
            self.agents[capabilities["name"]] = agent
        logger.info(f"Initialized agents: {list(self.agents.keys())}")
    
    def _format_agent_descriptions(self) -> str:
        """Format agent descriptions for the orchestration prompt."""
        descriptions = []
        for name, agent in self.agents.items():
            agent_class = agent.__class__.__name__
            supported_tasks = agent.supported_tasks if hasattr(agent, 'supported_tasks') else ['various tasks']
            descriptions.append(f"- {name} ({agent_class}): {', '.join(supported_tasks)}")
        return "\n".join(descriptions)
    
    def _plan_orchestration(self, state: OrchestratorState) -> OrchestratorState:
        """Plan the orchestration using LLM"""
        try:
            user_request = state["current_task"]
            agent_descriptions = self._format_agent_descriptions()
            
            logger.info(f"Planning orchestration for: {user_request}")
            
            # Use LangChain to create orchestration plan
            orchestration_prompt = ChatPromptTemplate.from_template(ORCHESTRATION_TEMPLATE_PROMPT)
            orchestration_chain = (
                {"agent_descriptions": RunnablePassthrough(), "user_request": RunnablePassthrough()}
                | orchestration_prompt
                | self.llm
                | JsonOutputParser()
            )
            
            orchestration_plan = orchestration_chain.invoke({
                "agent_descriptions": agent_descriptions,
                "user_request": user_request
            })
            
            logger.info(f"Orchestration plan created: {orchestration_plan}")
            state["orchestration_plan"] = orchestration_plan
            
        except Exception as e:
            logger.error(f"Error in orchestration planning: {str(e)}", exc_info=True)
            # Fallback plan
            state["orchestration_plan"] = {
                "subtasks": [{
                    "id": "subtask_1",
                    "description": user_request,
                    "assigned_agent": list(self.agents.keys())[0] if self.agents else "unknown",
                }],
                "coordination_plan": "Simple fallback execution"
            }
        
        return state
    
    async def _execute_subtasks(self, state: OrchestratorState) -> OrchestratorState:
        """Execute all subtasks using LangGraph's ToolNode pattern"""
        try:
            orchestration_plan = state["orchestration_plan"]
            subtasks = orchestration_plan.get("subtasks", [])
            
            logger.info(f"Executing {len(subtasks)} subtasks")
            
            # Create tool for subtask execution
            subtask_tool = SubtaskExecutionTool(agents=state["agents"])
            
            results = []
            for subtask in subtasks:
                result = await subtask_tool._run(
                    subtask["id"],
                    subtask["description"],
                    subtask["assigned_agent"]
                )
                results.append(result)
            
            state["subtask_results"] = results
            logger.info(f"Completed {len(results)} subtasks")
            
        except Exception as e:
            logger.error(f"Error in subtask execution: {str(e)}", exc_info=True)
            state["subtask_results"] = []
        
        return state
    
    def _synthesize_results(self, state: OrchestratorState) -> OrchestratorState:
        """Synthesize results into a singular natural language response"""
        try:
            subtask_results = state["subtask_results"]
            original_task = state["current_task"]
            
            # Extract actual agent responses
            agent_responses = []
            for result in subtask_results:
                if result["status"] == "completed":
                    # Extract the actual response from the agent
                    agent_response = result.get("result", "")
                    agent_responses.append(f"**{result['agent']}**: {agent_response}")
                else:
                    agent_responses.append(f"**{result['agent']}**: Failed to process - {result.get('error', 'Unknown error')}")
            
            # Create a natural language synthesis prompt
            synthesis_prompt = ChatPromptTemplate.from_messages([
                ("system", """You are an expert at synthesizing information from multiple sources into a concise, 
                direct response. Your job is to take the original question and the responses from different 
                specialized agents, and create a single, focused answer that directly addresses the user's question.
                
                Guidelines:
                - Be concise and to the point
                - Focus on the actual data and information, not on how to retrieve it
                - Do not include SQL queries or technical instructions
                - Present the information in a clear, readable format
                - If multiple agents provide information about the same topic, combine them intelligently
                - Use bullet points or numbered lists when appropriate for clarity
                - Keep the response conversational but informative
                """),
                ("user", """Original Question: {task}

Agent Responses:
{responses}

Please provide a concise answer that directly addresses the original question using the information from the agents.""")
            ])
            
            synthesis_chain = synthesis_prompt | self.llm.with_config({"temperature": 0.3})
            
            # Get the natural language response
            final_response = synthesis_chain.invoke({
                "task": original_task,
                "responses": "\n\n".join(agent_responses) if agent_responses else "No agent responses available."
            })
            
            # Extract the content from the AIMessage
            if hasattr(final_response, 'content'):
                final_text = final_response.content
            else:
                final_text = str(final_response)
            
            state["final_result"] = final_text
            
        except Exception as e:
            logger.error(f"Error in result synthesis: {str(e)}", exc_info=True)
            # Fallback: create a simple response from available results
            if subtask_results:
                fallback_responses = []
                for result in subtask_results:
                    if result["status"] == "completed":
                        response = result.get("result", "")
                        fallback_responses.append(f"{result['agent']}: {response}")
                    else:
                        fallback_responses.append(f"{result['agent']}: Failed to process")
                
                state["final_result"] = "\n\n".join(fallback_responses)
            else:
                state["final_result"] = "I was unable to process your request with the available agents."
        
        return state
    
    async def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process the request through orchestration workflow."""
        try:
            logger.info(f"Processing request with orchestrator: {request}")
            self.status = AgentStatus.PROCESSING
            
            user_request = request.get('question', '')
            
            # Initialize state
            initial_state: OrchestratorState = {
                "messages": [HumanMessage(content=user_request)],
                "agents": self.agents,
                "current_task": user_request,
                "orchestration_plan": None,
                "subtask_results": [],
                "final_result": None
            }
            
            # Execute workflow
            final_state = await self.graph.ainvoke(initial_state)
            
            result = final_state["final_result"]
            logger.info(f"Result: {result}")
            
            if result and isinstance(result, str):
                self.status = AgentStatus.COMPLETED
                return {
                    "success": True,
                    "data": result,
                    "error": None
                }
            else:
                self.status = AgentStatus.ERROR
                return {
                    "success": False,
                    "data": result,
                    "error": "Orchestration failed to produce a valid response"
                }
                
        except Exception as e:
            logger.error(f"Error in orchestrator agent: {str(e)}", exc_info=True)
            self.status = AgentStatus.ERROR
            return {
                "success": False,
                "data": None,
                "error": str(e)
            }
    
    async def get_capabilities(self) -> Dict[str, Any]:
        """Get orchestrator agent capabilities."""
        capabilities = {
            "name": "orchestrator",
            "description": "Intelligent orchestrator that coordinates multiple agents to complete complex tasks",
            "supported_tasks": ["task_decomposition", "agent_coordination", "result_synthesis"],
            "input_format": {
                "question": "Natural language question or complex task request"
            },
            "output_format": {
                "response": "Comprehensive natural language answer that synthesizes responses from multiple agents"
            },
            "available_agents": list(self.agents.keys()) if self.agents else []
        }
        logger.info(f"Returning orchestrator capabilities: {capabilities}")
        return capabilities
    
    async def get_orchestration_stats(self) -> Dict[str, Any]:
        """Get statistics about orchestration."""
        return {
            "total_agents": len(self.agents),
            "available_agents": list(self.agents.keys()),
            "orchestration_method": "langgraph_multi_node",
            "status": self.status.value if hasattr(self.status, 'value') else str(self.status)
        }