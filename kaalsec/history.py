"""Shell history integration for KaalSec"""

import os
from pathlib import Path
from typing import List, Optional


class HistoryManager:
    """Manages shell history for context"""
    
    def __init__(self, history_lines: int = 25):
        self.history_lines = history_lines
    
    def get_shell_history(self, lines: Optional[int] = None) -> List[str]:
        """Get recent shell history"""
        if lines is None:
            lines = self.history_lines
        
        history = []
        shell = os.environ.get("SHELL", "/bin/bash")
        
        # Try to read from common history files
        history_files = [
            Path.home() / ".bash_history",
            Path.home() / ".zsh_history",
        ]
        
        for hist_file in history_files:
            if hist_file.exists():
                try:
                    with open(hist_file, "r", encoding="utf-8", errors="ignore") as f:
                        all_lines = f.readlines()
                        # Get last N lines
                        history = [line.strip() for line in all_lines[-lines:] if line.strip()]
                        break
                except Exception:
                    continue
        
        return history
    
    def get_context_for_suggestion(self, lines: int = 5) -> str:
        """Get recent commands as context for suggestions"""
        history = self.get_shell_history(lines)
        if not history:
            return ""
        
        return "\n".join([f"  {i+1}. {cmd}" for i, cmd in enumerate(history)])

