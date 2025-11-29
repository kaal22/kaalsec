"""Shell integration hooks for KaalSec"""

import os
from pathlib import Path
from typing import Optional


class ShellIntegration:
    """Manages shell integration for KaalSec"""
    
    def __init__(self):
        self.shell = os.environ.get("SHELL", "/bin/bash")
        self.shell_name = Path(self.shell).name
    
    def get_shell_config_file(self) -> Optional[Path]:
        """Get the shell configuration file path"""
        home = Path.home()
        
        if self.shell_name == "bash":
            return home / ".bashrc"
        elif self.shell_name == "zsh":
            return home / ".zshrc"
        elif self.shell_name == "fish":
            return home / ".config" / "fish" / "config.fish"
        else:
            return None
    
    def install_bash_hook(self) -> bool:
        """Install PROMPT_COMMAND hook for bash"""
        config_file = self.get_shell_config_file()
        if not config_file or self.shell_name != "bash":
            return False
        
        hook_code = """
# KaalSec shell integration
_kaalsec_last_cmd() {
    if [ -n "$BASH_COMMAND" ] && [ "$BASH_COMMAND" != "$PROMPT_COMMAND" ]; then
        export KAALSEC_LAST_CMD="$BASH_COMMAND"
    fi
}
PROMPT_COMMAND="_kaalsec_last_cmd;$PROMPT_COMMAND"
"""
        
        try:
            with open(config_file, "r") as f:
                content = f.read()
            
            if "KAALSEC_LAST_CMD" in content:
                return True  # Already installed
            
            with open(config_file, "a") as f:
                f.write(hook_code)
            
            return True
        except Exception:
            return False
    
    def install_zsh_hook(self) -> bool:
        """Install precmd hook for zsh"""
        config_file = self.get_shell_config_file()
        if not config_file or self.shell_name != "zsh":
            return False
        
        hook_code = """
# KaalSec shell integration
_kaalsec_precmd() {
    export KAALSEC_LAST_CMD="$history[$[HISTCMD-1]]"
}
precmd_functions+=(_kaalsec_precmd)
"""
        
        try:
            with open(config_file, "r") as f:
                content = f.read()
            
            if "KAALSEC_LAST_CMD" in content:
                return True  # Already installed
            
            with open(config_file, "a") as f:
                f.write(hook_code)
            
            return True
        except Exception:
            return False
    
    def install_hook(self) -> bool:
        """Install appropriate hook for current shell"""
        if self.shell_name == "bash":
            return self.install_bash_hook()
        elif self.shell_name == "zsh":
            return self.install_zsh_hook()
        else:
            return False
    
    def uninstall_hook(self) -> bool:
        """Remove shell integration hooks"""
        config_file = self.get_shell_config_file()
        if not config_file:
            return False
        
        try:
            with open(config_file, "r") as f:
                lines = f.readlines()
            
            # Remove KaalSec hook lines
            filtered_lines = []
            skip_next = False
            for i, line in enumerate(lines):
                if "KaalSec shell integration" in line:
                    skip_next = True
                    continue
                if skip_next and (line.strip().startswith("#") or line.strip() == "" or "KAALSEC" in line):
                    continue
                skip_next = False
                filtered_lines.append(line)
            
            with open(config_file, "w") as f:
                f.writelines(filtered_lines)
            
            return True
        except Exception:
            return False
    
    def is_installed(self) -> bool:
        """Check if shell integration is installed"""
        config_file = self.get_shell_config_file()
        if not config_file:
            return False
        
        try:
            with open(config_file, "r") as f:
                return "KAALSEC_LAST_CMD" in f.read()
        except Exception:
            return False
    
    def get_last_command(self) -> Optional[str]:
        """Get the last executed command from shell integration"""
        return os.environ.get("KAALSEC_LAST_CMD")

