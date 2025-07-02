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
        # Azure OpenAI settings
        if os.getenv("AZURE_OPENAI_API_KEY"):
            self.config.setdefault("azure_openai", {})["api_key"] = os.getenv("AZURE_OPENAI_API_KEY")
        if os.getenv("AZURE_OPENAI_ENDPOINT"):
            self.config.setdefault("azure_openai", {})["endpoint"] = os.getenv("AZURE_OPENAI_ENDPOINT")
        if os.getenv("AZURE_OPENAI_API_VERSION"):
            self.config.setdefault("azure_openai", {})["api_version"] = os.getenv("AZURE_OPENAI_API_VERSION")
        if os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"):
            self.config.setdefault("azure_openai", {})["deployment_name"] = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

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
            self.config.setdefault("logging", {})["level"] = os.getenv("LOG_LEVEL")
        if os.getenv("LOG_FILE"):
            self.config.setdefault("logging", {})["file"] = os.getenv("LOG_FILE")

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key"""
        keys = key.split(".")
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, default)
            else:
                return default
        return value

    def set(self, key: str, value: Any):
        """Set configuration value by key"""
        keys = key.split(".")
        config = self.config
        for k in keys[:-1]:
            config = config.setdefault(k, {})
        config[keys[-1]] = value 