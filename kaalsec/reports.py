"""Report generation for KaalSec"""

import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime


class ReportGenerator:
    """Generates markdown reports from command logs"""
    
    def __init__(self, log_dir: Optional[Path] = None):
        if log_dir is None:
            log_dir = Path.home() / ".kaalsec" / "logs"
        
        self.log_dir = log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)
    
    def load_session_logs(self, date_filter: Optional[str] = None) -> List[Dict]:
        """Load logs from session files"""
        logs = []
        
        if not self.log_dir.exists():
            return logs
        
        # Load all JSON log files
        for log_file in self.log_dir.glob("*.json"):
            try:
                with open(log_file, "r") as f:
                    log_data = json.load(f)
                    
                    # Filter by date if specified
                    if date_filter:
                        log_date = log_data.get("date", "")
                        if date_filter not in log_date:
                            continue
                    
                    logs.append(log_data)
            except Exception:
                continue
        
        return logs
    
    def generate_report(self, date_filter: Optional[str] = None, output_path: Optional[Path] = None) -> str:
        """Generate a markdown report from logs"""
        logs = self.load_session_logs(date_filter)
        
        if not logs:
            return "# KaalSec Report\n\nNo activity found for the specified period.\n"
        
        # Group by date
        by_date: Dict[str, List[Dict]] = {}
        for log in logs:
            date = log.get("date", "Unknown")
            if date not in by_date:
                by_date[date] = []
            by_date[date].append(log)
        
        # Generate markdown
        report_lines = [
            "# KaalSec Security Testing Report",
            "",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "---",
            "",
        ]
        
        for date in sorted(by_date.keys(), reverse=True):
            report_lines.append(f"## {date}")
            report_lines.append("")
            
            for log in by_date[date]:
                command = log.get("command", "Unknown")
                timestamp = log.get("timestamp", "")
                output = log.get("output", "")
                notes = log.get("notes", "")
                
                report_lines.append(f"### Command: `{command}`")
                report_lines.append(f"**Time:** {timestamp}")
                report_lines.append("")
                
                if notes:
                    report_lines.append(f"**Notes:** {notes}")
                    report_lines.append("")
                
                if output:
                    report_lines.append("**Output:**")
                    report_lines.append("```")
                    report_lines.append(output[:500])  # Limit output length
                    if len(output) > 500:
                        report_lines.append("... (truncated)")
                    report_lines.append("```")
                    report_lines.append("")
                
                report_lines.append("---")
                report_lines.append("")
        
        report_content = "\n".join(report_lines)
        
        # Save to file if path provided
        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as f:
                f.write(report_content)
        
        return report_content

