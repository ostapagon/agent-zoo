from typing import Dict, Any, List, Optional
import logging
from agents.base.base_agent import BaseAgent
from agents.text2sql.text2sql_agent import Text2SQLAgent
from core.config import Config

logger = logging.getLogger(__name__)

class AgentFactory:
    def __init__(self, config: Config):
        self.config = config
        self.agents: Dict[str, BaseAgent] = {}
        self._initialize_agents()

    def _initialize_agents(self):
        """Initialize all enabled agents from config"""
        logger.info("Initializing agents...")
        
        self.agents["text2sql"] = Text2SQLAgent(self.config)

        logger.info(f"Initialized {len(self.agents)} agents: {list(self.agents.keys())}")

    def get_agent(self, agent_name: str) -> Optional[BaseAgent]:
        """Get an agent by name"""
        agent = self.agents.get(agent_name)
        if agent is None:
            logger.warning(f"Agent not found: {agent_name}")
        return agent

    def get_all_agents(self) -> List[BaseAgent]:
        """Get all initialized agents"""
        return list(self.agents.values())
