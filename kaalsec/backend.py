"""LLM backend adapters for KaalSec"""

import os
import json
from typing import Optional, Dict, Any
import requests
from abc import ABC, abstractmethod


class LLMBackend(ABC):
    """Abstract base class for LLM backends"""
    
    @abstractmethod
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate response from LLM"""
        pass


class OpenAIBackend(LLMBackend):
    """OpenAI API backend"""
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini", timeout: int = 30):
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.base_url = "https://api.openai.com/v1"
        
        if not api_key:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate response using OpenAI API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 2000,
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"OpenAI API error: {e}")


class OllamaBackend(LLMBackend):
    """Ollama local backend"""
    
    def __init__(self, host: str = "http://localhost:11434", model: str = "qwen2.5", timeout: int = 120):
        self.host = host.rstrip("/")
        self.model = model
        self.timeout = timeout
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate response using Ollama API"""
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        
        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False,
        }
        
        try:
            response = requests.post(
                f"{self.host}/api/generate",
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()
            data = response.json()
            return data.get("response", "").strip()
        except requests.exceptions.ConnectionError:
            raise RuntimeError(
                f"Could not connect to Ollama at {self.host}. "
                "Make sure Ollama is running: 'ollama serve'"
            )
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Ollama API error: {e}")


def create_backend(config: Dict[str, Any]) -> LLMBackend:
    """Factory function to create appropriate backend"""
    provider = config.get("provider", "ollama")
    
    if provider == "openai":
        return OpenAIBackend(
            api_key=config.get("api_key", ""),
            model=config.get("model", "gpt-4o-mini"),
            timeout=config.get("timeout", 30),
        )
    elif provider == "ollama":
        return OllamaBackend(
            host=config.get("host", "http://localhost:11434"),
            model=config.get("model", "qwen2.5"),
            timeout=config.get("timeout", 120),  # Longer timeout for slower systems/VMs
        )
    else:
        raise ValueError(f"Unknown backend provider: {provider}")

