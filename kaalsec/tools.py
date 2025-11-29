"""Kali Linux tool discovery and management"""

import os
import subprocess
from pathlib import Path
from typing import List, Dict, Optional, Set, Any


class ToolDiscovery:
    """Discovers installed Kali Linux pentesting tools"""
    
    # Common Kali Linux tool categories and their tools
    KALI_TOOL_CATEGORIES = {
        "information_gathering": [
            "nmap", "masscan", "zmap", "dnsrecon", "dnsenum", "dnsmap", "dnswalk",
            "fierce", "maltego", "recon-ng", "theharvester", "whatweb", "wafw00f",
            "nikto", "wapiti", "wpscan", "joomscan", "drupwn", "cmsmap"
        ],
        "vulnerability_analysis": [
            "nmap", "openvas", "lynis", "nikto", "skipfish", "w3af", "wapiti",
            "sqlninja", "sqlmap", "commix", "davtest", "deblaze"
        ],
        "web_application_analysis": [
            "burpsuite", "owasp-zap", "nikto", "wapiti", "w3af", "sqlmap",
            "commix", "davtest", "deblaze", "gobuster", "dirb", "dirbuster",
            "wfuzz", "websploit", "whatweb", "wpscan", "joomscan", "drupwn"
        ],
        "password_attacks": [
            "hydra", "medusa", "ncrack", "john", "hashcat", "crunch", "wordlists",
            "cewl", "chntpw", "cmospwd", "fcrackzip", "pdfcrack", "pyrit",
            "rainbowcrack", "rcracki-mt", "rarcrack", "sipcrack", "sucrack"
        ],
        "wireless_attacks": [
            "aircrack-ng", "reaver", "bully", "cowpatty", "eapmd5pass", "fern-wifi-cracker",
            "mdk3", "wifite", "kismet", "wireshark", "tshark", "kismet"
        ],
        "exploitation_tools": [
            "metasploit-framework", "armitage", "beef-xss", "backdoor-factory",
            "cisco-auditing-tool", "cisco-global-exploiter", "cisco-ocs", "cisco-torch",
            "commix", "crackle", "exploitdb", "jboss-autopwn", "linux-exploit-suggester",
            "set", "shellnoob", "sqlmap", "termineter", "yersinia"
        ],
        "forensics": [
            "autopsy", "binwalk", "bulk-extractor", "capstone", "chntpw", "cuckoo",
            "dc3dd", "ddrescue", "dumpzilla", "extundelete", "foremost", "galleta",
            "guymager", "hashdeep", "inetsim", "lbd", "maltego", "missidentify",
            "pasco", "pdfid", "pdf-parser", "pev", "regripper", "volatility", "wireshark"
        ],
        "stress_testing": [
            "dhcpig", "funkload", "iaxflood", "inviteflood", "ipv6-toolkit", "mdk3",
            "reaver", "rtpflood", "slowhttptest", "t50", "termineter", "thc-ipv6",
            "thc-ssl-dos"
        ],
        "sniffing_spoofing": [
            "bettercap", "burpsuite", "driftnet", "ettercap-text-only", "ettercap-graphical",
            "ferret-sidejack", "hamster-sidejack", "hexinject", "iaxflood", "inviteflood",
            "ismtp", "isr-evilgrade", "mitmproxy", "ohrwurm", "protos-sip", "rebind",
            "responder", "rtpbreak", "rtpflood", "rtpinsertsound", "rtpmixsound",
            "sctpscan", "siparmyknife", "sipcrack", "sipp", "sipvicious", "sniffjoke",
            "sslsplit", "sslstrip", "thc-ipv6", "voiphopper", "webscarab", "wireshark",
            "yersinia"
        ],
        "post_exploitation": [
            "backdoor-factory", "cryptcat", "dbd", "http-tunnel", "intersect", "nishang",
            "powersploit", "sbd", "shellter", "u3-pwn", "weevely"
        ],
        "reporting_tools": [
            "casefile", "cherrytree", "dradis", "keepnote", "magic-tree", "maltego",
            "metagoofil", "nipper-ng", "pipal"
        ],
        "social_engineering": [
            "backdoor-factory", "beef-xss", "set", "social-engineer-toolkit"
        ]
    }
    
    def __init__(self):
        self._installed_tools: Optional[Set[str]] = None
        self._tool_paths: Dict[str, str] = {}
    
    def _discover_installed_tools(self) -> Set[str]:
        """Discover which Kali tools are actually installed"""
        if self._installed_tools is not None:
            return self._installed_tools
        
        installed = set()
        path_dirs = os.environ.get("PATH", "").split(os.pathsep)
        
        # Check common Kali tool locations
        kali_paths = [
            "/usr/bin",
            "/usr/sbin",
            "/usr/local/bin",
            "/opt",
            "/usr/share",
        ]
        
        all_paths = path_dirs + kali_paths
        
        # Check all tools from categories
        all_tools = set()
        for category_tools in self.KALI_TOOL_CATEGORIES.values():
            all_tools.update(category_tools)
        
        for tool in all_tools:
            # Try to find tool in PATH
            try:
                result = subprocess.run(
                    ["which", tool],
                    capture_output=True,
                    text=True,
                    timeout=1
                )
                if result.returncode == 0 and result.stdout.strip():
                    installed.add(tool)
                    self._tool_paths[tool] = result.stdout.strip()
                    continue
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass
            
            # Try command -v
            try:
                result = subprocess.run(
                    ["command", "-v", tool],
                    capture_output=True,
                    text=True,
                    timeout=1,
                    shell=True
                )
                if result.returncode == 0 and result.stdout.strip():
                    installed.add(tool)
                    self._tool_paths[tool] = result.stdout.strip()
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass
        
        self._installed_tools = installed
        return installed
    
    def get_installed_tools(self) -> List[str]:
        """Get list of installed Kali tools"""
        return sorted(list(self._discover_installed_tools()))
    
    def is_tool_installed(self, tool_name: str) -> bool:
        """Check if a specific tool is installed"""
        return tool_name in self._discover_installed_tools()
    
    def get_tool_path(self, tool_name: str) -> Optional[str]:
        """Get the full path to a tool"""
        self._discover_installed_tools()
        return self._tool_paths.get(tool_name)
    
    def get_tools_by_category(self, category: str) -> List[str]:
        """Get installed tools in a specific category"""
        installed = self._discover_installed_tools()
        category_tools = self.KALI_TOOL_CATEGORIES.get(category, [])
        return [tool for tool in category_tools if tool in installed]
    
    def get_all_categories(self) -> List[str]:
        """Get all available tool categories"""
        return list(self.KALI_TOOL_CATEGORIES.keys())
    
    def get_tool_info(self, tool_name: str) -> Dict[str, Any]:
        """Get information about a tool"""
        installed = self._discover_installed_tools()
        tool_path = self.get_tool_path(tool_name)
        
        # Find which categories this tool belongs to
        categories = []
        for cat, tools in self.KALI_TOOL_CATEGORIES.items():
            if tool_name in tools:
                categories.append(cat)
        
        return {
            "name": tool_name,
            "installed": tool_name in installed,
            "path": tool_path,
            "categories": categories,
        }

