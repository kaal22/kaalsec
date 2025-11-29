"""Configuration loader for KaalSec"""

import os
import toml
from pathlib import Path
from typing import Optional, Dict, Any


class Config:
    """Loads and manages KaalSec configuration from TOML file"""
    
    def __init__(self, config_path: Optional[Path] = None):
        if config_path is None:
            config_path = Path.home() / ".kaalsec" / "config.toml"
        
        self.config_path = config_path
        self._config: Dict[str, Any] = {}
        self.load()
    
    def load(self) -> None:
        """Load configuration from TOML file"""
        if not self.config_path.exists():
            self._config = self._default_config()
            return
        
        try:
            with open(self.config_path, "r") as f:
                self._config = toml.load(f)
        except Exception as e:
            print(f"Warning: Could not load config: {e}. Using defaults.")
            self._config = self._default_config()
    
    def _default_config(self) -> Dict[str, Any]:
        """Returns default configuration"""
        return {
            "core": {
                "legal_banner": True,
                "history_lines": 25,
                "log_level": "info",
            },
            "backend": {
                "provider": "ollama",
                "model": "qwen2.5",
                "timeout_seconds": 60,
            },
            "backend.openai": {
                "api_key_env": "OPENAI_API_KEY",
            },
            "backend.ollama": {
                "host": "http://localhost:11434",
                "model": "qwen2.5",
            },
            "policy": {
                "red_team_mode": False,
                "anonymise_ips": False,
            },
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation (e.g., 'core.legal_banner')"""
        keys = key.split(".")
        value = self._config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        
        return value
    
    def get_backend_config(self) -> Dict[str, Any]:
        """Get backend-specific configuration"""
        provider = self.get("backend.provider", "ollama")
        
        if provider == "openai":
            api_key = os.getenv(self.get("backend.openai.api_key_env", "OPENAI_API_KEY"))
            return {
                "provider": "openai",
                "api_key": api_key,
                "model": self.get("backend.model", "gpt-4o-mini"),
                "timeout": self.get("backend.timeout_seconds", 30),
            }
        elif provider == "ollama":
            return {
                "provider": "ollama",
                "host": self.get("backend.ollama.host", "http://localhost:11434"),
                "model": self.get("backend.ollama.model", "qwen2.5"),
                "timeout": self.get("backend.timeout_seconds", 60),
            }
        else:
            raise ValueError(f"Unknown backend provider: {provider}")
    
    @property
    def log_dir(self) -> Path:
        """Get log directory path"""
        return Path.home() / ".kaalsec" / "logs"
    
    @property
    def plugins_dir(self) -> Path:
        """Get plugins directory path"""
        return Path.home() / ".kaalsec" / "plugins"

