"""Ethical filters and legal banners for KaalSec"""

from typing import List, Optional
import re


LEGAL_BANNER = """
╔═══════════════════════════════════════════════════════════════╗
║                    ⚠️  LEGAL DISCLAIMER  ⚠️                    ║
╠═══════════════════════════════════════════════════════════════╣
║ KaalSec is designed for ETHICAL security testing ONLY.        ║
║                                                               ║
║ • Only use on systems you own or have explicit permission    ║
║ • Unauthorized access is ILLEGAL and may result in criminal   ║
║   prosecution                                                 ║
║ • You are responsible for all actions taken with this tool    ║
║ • KaalSec logs all executed commands for compliance           ║
║                                                               ║
║ By using KaalSec, you agree to use it ethically and legally. ║
╚═══════════════════════════════════════════════════════════════╝
"""


class PolicyFilter:
    """Filters and validates commands for ethical use"""
    
    def __init__(self, red_team_mode: bool = False, anonymise_ips: bool = False):
        self.red_team_mode = red_team_mode
        self.anonymise_ips = anonymise_ips
        
        # Dangerous patterns that should trigger warnings
        self.dangerous_patterns = [
            (r"rm\s+-rf\s+/", "DANGEROUS: Attempting to delete root filesystem"),
            (r"dd\s+if=/dev/", "DANGEROUS: Direct disk manipulation"),
            (r">\s*/dev/sd[a-z]", "DANGEROUS: Writing to block devices"),
            (r":\(\)\s*\{\s*:\s*\|\s*:\s*&\s*\}", "DANGEROUS: Fork bomb pattern"),
            (r"mkfs\.", "DANGEROUS: Filesystem creation"),
        ]
        
        # Illegal activity patterns
        self.illegal_patterns = [
            (r"crack|brute.*force|password.*dump", "POTENTIALLY ILLEGAL: Unauthorized access attempts"),
            (r"exploit.*production|prod.*exploit", "POTENTIALLY ILLEGAL: Production system exploitation"),
        ]
    
    def check_command(self, command: str) -> tuple[bool, Optional[str]]:
        """
        Check if command is safe to suggest/execute.
        Returns (is_safe, warning_message)
        """
        command_lower = command.lower()
        
        # Check for dangerous patterns
        for pattern, warning in self.dangerous_patterns:
            if re.search(pattern, command_lower):
                return False, warning
        
        # Check for illegal patterns (unless in red team mode)
        if not self.red_team_mode:
            for pattern, warning in self.illegal_patterns:
                if re.search(pattern, command_lower):
                    return False, warning
        
        return True, None
    
    def anonymize_ips(self, text: str) -> str:
        """Anonymize IP addresses in text if enabled"""
        if not self.anonymise_ips:
            return text
        
        # Simple IP anonymization (replace last octet with X)
        ip_pattern = r"\b(\d{1,3}\.){3}\d{1,3}\b"
        
        def anonymize_ip(match):
            ip = match.group(0)
            parts = ip.split(".")
            parts[-1] = "X"
            return ".".join(parts)
        
        return re.sub(ip_pattern, anonymize_ip, text)
    
    def inject_legal_banner(self) -> str:
        """Returns legal banner if enabled"""
        return LEGAL_BANNER

