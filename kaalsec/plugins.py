"""Plugin loader for tool knowledge bases"""

import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any


class ToolPlugin:
    """Represents a tool plugin loaded from YAML"""
    
    def __init__(self, tool_name: str, data: Dict[str, Any]):
        self.tool_name = tool_name
        self.data = data
        self.categories = data.get("categories", [])
    
    def get_examples_for_category(self, category_name: str) -> List[Dict[str, str]]:
        """Get example commands for a specific category"""
        for category in self.categories:
            if category.get("name") == category_name:
                return category.get("examples", [])
        return []
    
    def get_all_examples(self) -> List[Dict[str, str]]:
        """Get all example commands from all categories"""
        examples = []
        for category in self.categories:
            examples.extend(category.get("examples", []))
        return examples
    
    def get_description(self) -> str:
        """Get tool description"""
        return self.data.get("description", f"Tool: {self.tool_name}")


class PluginLoader:
    """Loads and manages tool plugins from YAML files"""
    
    def __init__(self, plugins_dir: Optional[Path] = None):
        if plugins_dir is None:
            plugins_dir = Path.home() / ".kaalsec" / "plugins"
        
        self.plugins_dir = plugins_dir
        self.plugins_dir.mkdir(parents=True, exist_ok=True)
        self._plugins: Dict[str, ToolPlugin] = {}
        self._load_all()
    
    def _load_all(self) -> None:
        """Load all YAML plugins from plugins directory"""
        if not self.plugins_dir.exists():
            return
        
        for yaml_file in self.plugins_dir.glob("*.yml"):
            try:
                with open(yaml_file, "r") as f:
                    data = yaml.safe_load(f)
                    if data and "tool" in data:
                        tool_name = data["tool"]
                        self._plugins[tool_name] = ToolPlugin(tool_name, data)
            except Exception as e:
                print(f"Warning: Could not load plugin {yaml_file}: {e}")
    
    def get_plugin(self, tool_name: str) -> Optional[ToolPlugin]:
        """Get a specific plugin by tool name"""
        return self._plugins.get(tool_name)
    
    def get_all_plugins(self) -> Dict[str, ToolPlugin]:
        """Get all loaded plugins"""
        return self._plugins.copy()
    
    def reload(self) -> None:
        """Reload all plugins"""
        self._plugins.clear()
        self._load_all()
    
    def get_tool_suggestions(self, tool_name: str, task: str) -> List[Dict[str, str]]:
        """Get relevant command suggestions for a tool and task"""
        plugin = self.get_plugin(tool_name)
        if not plugin:
            return []
        
        # Simple keyword matching for now
        task_lower = task.lower()
        suggestions = []
        
        for example in plugin.get_all_examples():
            desc = example.get("desc", "").lower()
            cmd = example.get("cmd", "")
            
            # Check if task keywords match description
            if any(keyword in desc for keyword in task_lower.split()):
                suggestions.append(example)
        
        return suggestions[:5]  # Limit to 5 suggestions

