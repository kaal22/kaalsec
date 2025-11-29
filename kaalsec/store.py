"""Store for caching suggestions and command history"""

import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime


class SuggestionStore:
    """Stores and retrieves command suggestions"""
    
    def __init__(self, store_dir: Optional[Path] = None):
        if store_dir is None:
            store_dir = Path.home() / ".kaalsec"
        
        self.store_dir = store_dir
        self.store_dir.mkdir(parents=True, exist_ok=True)
        self.suggestions_file = store_dir / "suggestions.json"
        self._suggestions: List[Dict] = []
        self._load()
    
    def _load(self) -> None:
        """Load suggestions from disk"""
        if self.suggestions_file.exists():
            try:
                with open(self.suggestions_file, "r") as f:
                    self._suggestions = json.load(f)
            except Exception:
                self._suggestions = []
        else:
            self._suggestions = []
    
    def _save(self) -> None:
        """Save suggestions to disk"""
        try:
            with open(self.suggestions_file, "w") as f:
                json.dump(self._suggestions, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save suggestions: {e}")
    
    def add_suggestion(self, command: str, description: str, tool: Optional[str] = None) -> int:
        """Add a new suggestion and return its ID"""
        suggestion_id = len(self._suggestions) + 1
        suggestion = {
            "id": suggestion_id,
            "command": command,
            "description": description,
            "tool": tool,
            "created_at": datetime.now().isoformat(),
            "executed": False,
        }
        self._suggestions.append(suggestion)
        self._save()
        return suggestion_id
    
    def get_suggestion(self, suggestion_id: int) -> Optional[Dict]:
        """Get a suggestion by ID"""
        for suggestion in self._suggestions:
            if suggestion.get("id") == suggestion_id:
                return suggestion
        return None
    
    def mark_executed(self, suggestion_id: int) -> None:
        """Mark a suggestion as executed"""
        suggestion = self.get_suggestion(suggestion_id)
        if suggestion:
            suggestion["executed"] = True
            suggestion["executed_at"] = datetime.now().isoformat()
            self._save()
    
    def get_recent_suggestions(self, limit: int = 10) -> List[Dict]:
        """Get recent suggestions"""
        return self._suggestions[-limit:]
    
    def clear(self) -> None:
        """Clear all suggestions"""
        self._suggestions = []
        self._save()

