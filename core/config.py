from typing import Dict, Any
import os
from pathlib import Path
import yaml
from dotenv import load_dotenv

class Config:
    def __init__(self):
        self.config: Dict[str, Any] = {}
        load_dotenv()  # Load environment variables
        self._load_config()

    def _load_config(self):
        """Load configuration from environment variables and config files"""
        # Load YAML config
        config_path = Path("config/agents_config.yaml")
        if config_path.exists():
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)

        # Override with environment variables
        self._override_from_env()

    def _override_from_env(self):
        """Override config values from environment variables"""
        # Google AI settings
        if os.getenv("GOOGLE_AI_API_KEY"):
            self.config.setdefault("google_ai", {})["api_key"] = os.getenv("GOOGLE_AI_API_KEY")
        if os.getenv("GOOGLE_AI_MODEL"):
            self.config.setdefault("google_ai", {})["model_name"] = os.getenv("GOOGLE_AI_MODEL")
        if os.getenv("GOOGLE_AI_TEMPERATURE"):
            self.config.setdefault("google_ai", {})["temperature"] = float(os.getenv("GOOGLE_AI_TEMPERATURE"))

        # Agent-specific settings
        for agent_name in self.config.get("agents", {}).keys():
            prefix = agent_name.upper()
            if os.getenv(f"{prefix}_MODEL"):
                self.config["agents"][agent_name]["model"] = os.getenv(f"{prefix}_MODEL")
            if os.getenv(f"{prefix}_TEMPERATURE"):
                self.config["agents"][agent_name]["temperature"] = float(os.getenv(f"{prefix}_TEMPERATURE"))

        # Database settings
        if os.getenv("DATABASE_URL"):
            self.config.setdefault("database", {})["url"] = os.getenv("DATABASE_URL")

        # Logging settings
        if os.getenv("LOG_LEVEL"):
            self.config["log_level"] = os.getenv("LOG_LEVEL")

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value"""
        return self.config.get(key, default)

    def __getitem__(self, key: str) -> Any:
        """Get a configuration value using bracket notation"""
        return self.config[key]

    def __contains__(self, key: str) -> bool:
        """Check if a configuration key exists"""
        return key in self.config 