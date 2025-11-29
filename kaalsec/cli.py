"""Main CLI interface for KaalSec"""

import os
import sys
import subprocess
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional

import typer
from typer import Context
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Confirm

from kaalsec.config import Config
from kaalsec.backend import create_backend
from kaalsec.policy import PolicyFilter
from kaalsec.plugins import PluginLoader
from kaalsec.store import SuggestionStore
from kaalsec.history import HistoryManager
from kaalsec.reports import ReportGenerator
from kaalsec.tools import ToolDiscovery
from kaalsec.shell_integration import ShellIntegration

app = typer.Typer(help="KaalSec - Ethical AI Copilot for Kali Linux", no_args_is_help=False)
console = Console()


@app.callback(invoke_without_command=True)
def main(
    ctx: Context,
):
    """
    KaalSec - Ethical AI Copilot for Kali Linux
    
    Use without subcommands for quick questions:
      kaalsec give me an nmap scan of 192.168.1.1
    
    Or use subcommands for specific features:
      kaalsec ask your question
      kaalsec suggest task description
      kaalsec explain command
    """
    # If a subcommand was invoked, don't do anything here
    if ctx.invoked_subcommand is not None:
        return
    
    # Get remaining arguments from sys.argv (only when no subcommand)
    import sys
    args = sys.argv[1:]  # Skip script name
    
    # Filter out options/flags and known subcommands
    known_commands = ['ask', 'suggest', 'explain', 'run', 'report', 'version', 'update', 'tools', 'integrate']
    question_words = []
    skip_next = False
    
    for i, arg in enumerate(args):
        if skip_next:
            skip_next = False
            continue
        if arg.startswith('-'):
            # Skip options and their values
            if '=' in arg:
                continue
            # Check if next arg is a value (for options like --file path)
            if i + 1 < len(args) and not args[i + 1].startswith('-'):
                skip_next = True
            continue
        if arg in known_commands:
            # This shouldn't happen if no subcommand was invoked, but if it does,
            # it means Typer didn't recognize it as a subcommand, so treat it as part of question
            # Actually, if it's a known command, we should skip it to avoid confusion
            # But wait - if ctx.invoked_subcommand is None, then these shouldn't be commands
            # So we can include them in the question
            pass  # Include all words as part of the question
        question_words.append(arg)
    
    # If no question provided, show help
    if not question_words:
        console.print("[bold cyan]KaalSec[/bold cyan] - Ethical AI Copilot for Kali Linux\n")
        console.print("Usage examples:")
        console.print("  [green]kaalsec[/green] give me an nmap scan of 192.168.1.1")
        console.print("  [green]kaalsec ask[/green] your question")
        console.print("  [green]kaalsec suggest[/green] task description")
        console.print("  [green]kaalsec explain[/green] command")
        console.print("\nRun [cyan]kaalsec --help[/cyan] for all commands")
        return
    
    # Join all words into a single question
    question = " ".join(question_words)
    _ask_question(question, show_banner=True)


def run_cli():
    """Entry point for CLI"""
    import sys
    from click.exceptions import UsageError, BadParameter
    import click
    
    # Check if this looks like a direct question (not a known command)
    args = sys.argv[1:] if len(sys.argv) > 1 else []
    known_commands = ['ask', 'suggest', 'explain', 'run', 'report', 'version', 'update', 'tools', 'integrate', '--help', '-h', 'help']
    
    # If first arg is not a known command and not an option, treat as question
    if args and not args[0].startswith('-') and args[0] not in known_commands:
        # This is likely a direct question
        question_words = []
        skip_next = False
        for i, arg in enumerate(args):
            if skip_next:
                skip_next = False
                continue
            if arg.startswith('-'):
                if '=' in arg:
                    continue
                if i + 1 < len(args) and not args[i + 1].startswith('-'):
                    skip_next = True
                continue
            question_words.append(arg)
        
        if question_words:
            question = " ".join(question_words)
            _ask_question(question, show_banner=True)
            return
    
    # Otherwise, try normal Typer command handling
    try:
        app()
    except typer.Exit:
        # Typer exit (normal exit, e.g., --help)
        raise
    except (UsageError, BadParameter, SystemExit) as e:
        # Check if it's an unknown command error
        error_str = str(e).lower() if hasattr(e, '__str__') else ''
        error_code = getattr(e, 'exit_code', None)
        
        # SystemExit with code 2 usually means usage error
        if isinstance(e, SystemExit) and error_code == 2:
            # Try to treat as question
            args = sys.argv[1:] if len(sys.argv) > 1 else []
            if args and args[0] not in known_commands and not args[0].startswith('-'):
                question_words = [arg for arg in args if not arg.startswith('-')]
                if question_words:
                    question = " ".join(question_words)
                    _ask_question(question, show_banner=True)
                    return
        
        # Check error message for unknown command or unexpected arguments
        if any(phrase in error_str for phrase in ["no such command", "got unexpected extra arguments", "missing argument"]):
            args = sys.argv[1:] if len(sys.argv) > 1 else []
            if args and len(args) > 1:
                # Special handling for suggest/ask/explain commands with extra args
                if args[0] == 'suggest':
                    # Parse task from args manually and call _perform_suggest
                    try:
                        task_words = []
                        skip_next = False
                        tool_option = None
                        for i, arg in enumerate(args[1:], 1):  # Skip 'suggest'
                            if skip_next:
                                skip_next = False
                                continue
                            if arg.startswith('-'):
                                if arg == '--tool' or arg.startswith('--tool='):
                                    if '=' in arg:
                                        tool_option = arg.split('=', 1)[1]
                                    elif i + 1 < len(args):
                                        tool_option = args[i + 1]
                                        skip_next = True
                                    continue
                                break
                            task_words.append(arg)
                        
                        if task_words:
                            _perform_suggest(" ".join(task_words), tool_option)
                            return
                    except Exception as e:
                        # If that fails, fall through to question handling
                        pass
                elif args[0] == 'ask':
                    # Parse question from args manually and call _ask_question
                    try:
                        question_words = []
                        skip_next = False
                        for i, arg in enumerate(args[1:], 1):  # Skip 'ask'
                            if skip_next:
                                skip_next = False
                                continue
                            if arg.startswith('-'):
                                if arg == '--banner' or arg == '--no-banner':
                                    continue
                                break
                            question_words.append(arg)
                        
                        if question_words:
                            _ask_question(" ".join(question_words), show_banner=True)
                            return
                    except Exception as e:
                        pass
                elif args[0] == 'explain':
                    # Parse command from args manually and call explain logic
                    try:
                        command_words = []
                        file_path = None
                        skip_next = False
                        for i, arg in enumerate(args[1:], 1):  # Skip 'explain'
                            if skip_next:
                                skip_next = False
                                continue
                            if arg.startswith('-'):
                                if arg == '-f' or arg == '--file':
                                    if i + 1 < len(args):
                                        file_path = Path(args[i + 1])
                                        skip_next = True
                                    continue
                                break
                            command_words.append(arg)
                        
                        if command_words or file_path:
                            # Call explain logic directly
                            _perform_explain(" ".join(command_words) if command_words else None, file_path)
                            return
                    except Exception as e:
                        pass
                elif args[0] == 'ask':
                    try:
                        from typer import Context
                        mock_ctx = Context(None, None, None, None)
                        ask(mock_ctx, show_banner=True)
                        return
                    except Exception as e:
                        pass
                elif args[0] == 'explain':
                    try:
                        from typer import Context
                        mock_ctx = Context(None, None, None, None)
                        explain(mock_ctx, file=None)
                        return
                    except Exception as e:
                        pass
                
                # Otherwise treat as question
                question_words = [arg for arg in args if not arg.startswith('-') and arg not in known_commands]
                if question_words:
                    question = " ".join(question_words)
                    _ask_question(question, show_banner=True)
                    return
        
        # Re-raise if we can't handle it
        raise
    except Exception as e:
        # Last resort - if any other exception and we have args, try as question
        args = sys.argv[1:] if len(sys.argv) > 1 else []
        if args and args[0] not in known_commands and not args[0].startswith('-'):
            question_words = [arg for arg in args if not arg.startswith('-')]
            if question_words:
                question = " ".join(question_words)
                _ask_question(question, show_banner=True)
                return
        raise


def _ask_question(question: str, show_banner: bool = True):
    """Internal function to handle asking questions"""
    config = Config()
    policy = PolicyFilter(
        red_team_mode=config.get("policy.red_team_mode", False),
        anonymise_ips=config.get("policy.anonymise_ips", False),
    )
    
    if show_banner and config.get("core.legal_banner", True):
        console.print(Panel(policy.inject_legal_banner(), style="yellow"))
    
    try:
        backend_config = config.get_backend_config()
        backend = create_backend(backend_config)
        
        system_prompt = """You are KAALSEC — an elite Kali Linux and offensive security assistant.
You specialise in WiFi attacks, OSINT, exploit development, scripting, fixing Kali/Parrot errors,
and automated recon workflows.

You respond with:
- Direct, copy-pasteable Linux commands
- Short, practical explanations

Avoid placeholders where possible (use realistic examples)."""
        
        console.print(f"[bold cyan]Asking:[/bold cyan] {question}\n")
        console.print("[yellow]Thinking...[/yellow]")
        
        response = backend.generate(question, system_prompt=system_prompt)
        
        console.print(Panel(response, title="KaalSec Response", border_style="green"))
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)


@app.command()
def ask(
    ctx: Context,
    show_banner: bool = typer.Option(True, "--banner/--no-banner", help="Show legal banner"),
):
    """Ask KaalSec a question about ethical security testing
    
    You can provide the question as multiple words without quotes:
      kaalsec ask how do i scan my local network
    """
    # Get all remaining arguments from sys.argv
    import sys
    args = sys.argv[1:]  # Skip script name
    
    # Find where 'ask' appears and get everything after it
    question_words = []
    found_ask = False
    skip_next = False
    
    for i, arg in enumerate(args):
        if skip_next:
            skip_next = False
            continue
        if arg == 'ask':
            found_ask = True
            continue
        if found_ask:
            if arg.startswith('-'):
                # Stop at options
                if arg == '--banner' or arg == '--no-banner':
                    continue
                break
            question_words.append(arg)
    
    if not question_words:
        console.print("[bold red]Error:[/bold red] Question is required")
        console.print("Usage: kaalsec ask <your question>")
        console.print("Example: kaalsec ask how do i scan my local network")
        sys.exit(1)
    
    question = " ".join(question_words)
    _ask_question(question, show_banner)


@app.command()
def explain(
    ctx: Context,
    file: Optional[Path] = typer.Option(None, "-f", "--file", help="File containing command/output to explain"),
):
    """Explain what a command does, its flags, risks, and safer alternatives
    
    You can provide the command as multiple words without quotes:
      kaalsec explain nmap -sCV -p 22,80,443 target
    """
    config = Config()
    policy = PolicyFilter(
        red_team_mode=config.get("policy.red_team_mode", False),
        anonymise_ips=config.get("policy.anonymise_ips", False),
    )
    
    # Get all remaining arguments from sys.argv
    import sys
    args = sys.argv[1:]  # Skip script name
    
    # Find where 'explain' appears and get everything after it
    command_words = []
    found_explain = False
    skip_next = False
    
    for i, arg in enumerate(args):
        if skip_next:
            skip_next = False
            continue
        if arg == 'explain':
            found_explain = True
            continue
        if found_explain:
            if arg.startswith('-'):
                # Stop at options
                if arg == '-f' or arg == '--file':
                    if i + 1 < len(args):
                        skip_next = True
                    continue
                break
            command_words.append(arg)
    
    command = " ".join(command_words) if command_words else None
    _perform_explain(command, file)


def _perform_explain(command: Optional[str], file: Optional[Path]):
    """Internal function to perform explain logic"""
    if not command and not file:
        console.print("[bold red]Error:[/bold red] Provide either a command or --file option")
        sys.exit(1)
    
    content = command
    if file:
        if not file.exists():
            console.print(f"[bold red]Error:[/bold red] File not found: {file}")
            sys.exit(1)
        with open(file, "r") as f:
            content = f.read()
    
    config = Config()
    policy = PolicyFilter(
        red_team_mode=config.get("policy.red_team_mode", False),
        anonymise_ips=config.get("policy.anonymise_ips", False),
    )
    
    try:
        backend_config = config.get_backend_config()
        backend = create_backend(backend_config)
        
        system_prompt = """You are KAALSEC — an elite Kali Linux and offensive security assistant.
You specialise in WiFi attacks, OSINT, exploit development, scripting, fixing Kali/Parrot errors,
and automated recon workflows.

For this command/output, provide:
- Direct, copy-pasteable Linux commands
- Short, practical explanations
- What it does and what the flags mean
- Potential risks or safer alternatives if applicable

Avoid placeholders where possible (use realistic examples)."""
        
        prompt = f"Explain this command/output in detail:\n\n{content}"
        
        console.print(f"[bold cyan]Explaining:[/bold cyan] {content[:100]}...\n")
        console.print("[yellow]Analyzing...[/yellow]")
        
        response = backend.generate(prompt, system_prompt=system_prompt)
        
        console.print(Panel(response, title="Command Explanation", border_style="blue"))
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)


@app.command()
def suggest(
    ctx: Context,
    tool: Optional[str] = typer.Option(None, "--tool", help="Specific tool to use (e.g., nmap, nikto)"),
):
    """Suggest safe, accurate commands for a security testing task
    
    You can provide the task as multiple words without quotes:
      kaalsec suggest scan my local network
    """
    # Get all remaining arguments from sys.argv
    import sys
    args = sys.argv[1:]  # Skip script name
    
    # Find where 'suggest' appears and get everything after it
    task_words = []
    found_suggest = False
    skip_next = False
    
    for i, arg in enumerate(args):
        if skip_next:
            skip_next = False
            continue
        if arg == 'suggest':
            found_suggest = True
            continue
        if found_suggest:
            if arg.startswith('-'):
                # Stop at options
                if arg == '--tool' or arg.startswith('--tool='):
                    if '=' not in arg and i + 1 < len(args):
                        skip_next = True
                    continue
                break
            task_words.append(arg)
    
    if not task_words:
        console.print("[bold red]Error:[/bold red] Task description is required")
        console.print("Usage: kaalsec suggest <task description>")
        console.print("Example: kaalsec suggest scan my local network")
        sys.exit(1)
    
    # Use tool from option if provided, otherwise from parsed args
    final_tool = tool if tool else None
    _perform_suggest(" ".join(task_words), final_tool)


def _perform_suggest(task: str, tool: Optional[str] = None):
    """Internal function to perform suggestion logic"""
    config = Config()
    policy = PolicyFilter(
        red_team_mode=config.get("policy.red_team_mode", False),
        anonymise_ips=config.get("policy.anonymise_ips", False),
    )
    
    try:
        backend_config = config.get_backend_config()
        backend = create_backend(backend_config)
        plugin_loader = PluginLoader(config.plugins_dir)
        store = SuggestionStore()
        history = HistoryManager(config.get("core.history_lines", 25))
        
        # Get context from recent history
        context = history.get_context_for_suggestion(5)
        
        # Discover installed tools for better suggestions
        discovery = ToolDiscovery()
        installed_tools = discovery.get_installed_tools()
        
        # Build prompt
        system_prompt = """You are KAALSEC — an elite Kali Linux and offensive security assistant.
You specialise in WiFi attacks, OSINT, exploit development, scripting, fixing Kali/Parrot errors,
and automated recon workflows.

Generate 2-4 direct, copy-pasteable Linux commands for the given task.
For each command, provide:
- The exact command (use realistic examples, avoid placeholders)
- A brief description
- The tool name

Format as JSON array:
[{"tool": "nmap", "command": "nmap -sCV -p 22,80,443 10.0.0.5", "description": "..."}, ...]"""
        
        prompt = f"Task: {task}\n\n"
        
        # Add installed tools context
        if installed_tools:
            tools_list = ", ".join(installed_tools[:20])  # Limit to first 20
            prompt += f"Available installed Kali tools: {tools_list}"
            if len(installed_tools) > 20:
                prompt += f" (and {len(installed_tools) - 20} more)"
            prompt += "\n\n"
        
        if context:
            prompt += f"Recent commands for context:\n{context}\n\n"
        prompt += "Suggest 2-4 safe commands for this task. Prefer tools that are installed."
        
        if tool:
            plugin = plugin_loader.get_plugin(tool)
            if plugin:
                examples = plugin.get_all_examples()
                if examples:
                    prompt += f"\n\nTool-specific examples for {tool}:\n"
                    for ex in examples[:3]:
                        prompt += f"- {ex.get('cmd')}: {ex.get('desc')}\n"
        
        console.print(f"[bold cyan]Task:[/bold cyan] {task}\n")
        console.print("[yellow]Generating suggestions...[/yellow]")
        
        response = backend.generate(prompt, system_prompt=system_prompt)
        
        # Try to parse JSON from response
        try:
            # Extract JSON from response if it's wrapped in markdown
            import re
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                suggestions_data = json.loads(json_match.group(0))
            else:
                suggestions_data = json.loads(response)
        except json.JSONDecodeError:
            # Fallback: parse manually or show raw response
            console.print("[yellow]Could not parse structured suggestions. Showing raw response:[/yellow]")
            console.print(Panel(response, title="Suggestions", border_style="green"))
            return
        
        # Display suggestions in a table
        table = Table(title="Suggested Commands", show_header=True, header_style="bold magenta")
        table.add_column("ID", style="cyan", width=6)
        table.add_column("Tool", style="yellow")
        table.add_column("Command", style="green")
        table.add_column("Description", style="white")
        
        suggestion_ids = []
        for suggestion in suggestions_data:
            cmd = suggestion.get("command", "")
            desc = suggestion.get("description", "")
            tool_name = suggestion.get("tool", "unknown")
            
            # Check if command is safe
            is_safe, warning = policy.check_command(cmd)
            if not is_safe:
                desc = f"[red]⚠️ {warning}[/red] {desc}"
            
            suggestion_id = store.add_suggestion(cmd, desc, tool_name)
            suggestion_ids.append(suggestion_id)
            
            table.add_row(
                str(suggestion_id),
                tool_name,
                cmd,
                desc,
            )
        
        console.print("\n")
        console.print(table)
        console.print("\n[bold]To execute a suggestion:[/bold] [cyan]kaalsec run <ID>[/cyan]")
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)


@app.command()
def run(
    suggestion_id: int = typer.Argument(..., help="ID of suggestion to execute"),
    confirm: bool = typer.Option(True, "--yes/--no", help="Skip confirmation prompt"),
):
    """Execute a suggested command (with confirmation)"""
    config = Config()
    store = SuggestionStore()
    policy = PolicyFilter(
        red_team_mode=config.get("policy.red_team_mode", False),
        anonymise_ips=config.get("policy.anonymise_ips", False),
    )
    
    suggestion = store.get_suggestion(suggestion_id)
    if not suggestion:
        console.print(f"[bold red]Error:[/bold red] Suggestion ID {suggestion_id} not found")
        sys.exit(1)
    
    command = suggestion["command"]
    description = suggestion["description"]
    
    # Check if command is safe
    is_safe, warning = policy.check_command(command)
    if not is_safe:
        console.print(f"[bold red]⚠️ WARNING:[/bold red] {warning}")
        if not Confirm.ask("Do you still want to proceed?"):
            console.print("[yellow]Command cancelled.[/yellow]")
            sys.exit(0)
    
    # Show command details
    console.print(f"[bold cyan]Command:[/bold cyan] {command}")
    console.print(f"[bold cyan]Description:[/bold cyan] {description}\n")
    
    # Confirm execution
    if confirm:
        if not Confirm.ask("[bold yellow]Execute this command?[/bold yellow]"):
            console.print("[yellow]Command cancelled.[/yellow]")
            sys.exit(0)
    
    # Execute command
    console.print("[yellow]Executing...[/yellow]\n")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
        )
        
        # Log the execution
        log_dir = config.log_dir
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "command": command,
            "description": description,
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "output": result.stdout + result.stderr,
        }
        
        log_file = log_dir / f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(log_file, "w") as f:
            json.dump(log_entry, f, indent=2)
        
        # Mark suggestion as executed
        store.mark_executed(suggestion_id)
        
        # Display output
        if result.stdout:
            console.print(Panel(result.stdout, title="Output", border_style="green"))
        if result.stderr:
            console.print(Panel(result.stderr, title="Errors", border_style="red"))
        
        console.print(f"\n[bold green]✓ Command executed (exit code: {result.returncode})[/bold green]")
        console.print(f"[dim]Logged to: {log_file}[/dim]")
        
    except subprocess.TimeoutExpired:
        console.print("[bold red]Error:[/bold red] Command timed out after 5 minutes")
        sys.exit(1)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)


@app.command()
def report(
    date: str = typer.Argument("today", help="Date filter (e.g., 'today', '2024-01-15')"),
    output: Optional[Path] = typer.Option(None, "-o", "--output", help="Output file path"),
):
    """Generate a markdown report from command logs"""
    config = Config()
    generator = ReportGenerator(config.log_dir)
    
    # Parse date filter
    if date.lower() == "today":
        date_filter = datetime.now().strftime("%Y-%m-%d")
    else:
        date_filter = date
    
    console.print(f"[bold cyan]Generating report for:[/bold cyan] {date_filter}\n")
    
    try:
        if output:
            report_content = generator.generate_report(date_filter, output)
            console.print(f"[bold green]✓ Report saved to:[/bold green] {output}")
        else:
            report_content = generator.generate_report(date_filter)
            console.print(Panel(report_content, title="Report", border_style="blue"))
            
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)


@app.command()
def version():
    """Show KaalSec version"""
    from kaalsec import __version__
    console.print(f"[bold cyan]KaalSec[/bold cyan] version [bold]{__version__}[/bold]")


@app.command()
def update(
    force: bool = typer.Option(False, "--force", "-f", help="Force update even if already up to date"),
):
    """Update KaalSec to the latest version from GitHub"""
    console.print("[bold cyan]Updating KaalSec...[/bold cyan]\n")
    
    # Find the installation directory
    # Try common locations
    possible_dirs = [
        Path.home() / "kaalsec",
        Path(__file__).parent.parent,  # If installed in repo
    ]
    
    install_dir = None
    for dir_path in possible_dirs:
        if (dir_path / ".git").exists():
            install_dir = dir_path
            break
    
    if not install_dir:
        console.print("[bold red]Error:[/bold red] Could not find KaalSec installation directory.")
        console.print("Make sure KaalSec was installed from GitHub using the install script.")
        console.print("\nTo update manually:")
        console.print("  cd ~/kaalsec")
        console.print("  git pull")
        console.print("  source .venv/bin/activate")
        console.print("  pip install -e .")
        sys.exit(1)
    
    console.print(f"[bold]Installation directory:[/bold] {install_dir}\n")
    
    try:
        # Check current status
        result = subprocess.run(
            ["git", "fetch", "origin"],
            cwd=install_dir,
            capture_output=True,
            text=True,
            timeout=30,
        )
        
        # Check if there are updates
        result = subprocess.run(
            ["git", "status", "-uno"],
            cwd=install_dir,
            capture_output=True,
            text=True,
            timeout=10,
        )
        
        if "Your branch is up to date" in result.stdout and not force:
            console.print("[bold green]✓ KaalSec is already up to date![/bold green]")
            console.print("Use --force to reinstall anyway.")
            return
        
        # Show what will be updated
        result = subprocess.run(
            ["git", "log", "HEAD..origin/main", "--oneline"],
            cwd=install_dir,
            capture_output=True,
            text=True,
            timeout=10,
        )
        
        if result.stdout.strip():
            console.print("[bold]New updates available:[/bold]")
            console.print(result.stdout)
            console.print()
        
        # Check for local changes before pulling
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=install_dir,
            capture_output=True,
            text=True,
            timeout=10,
        )
        
        has_local_changes = bool(result.stdout.strip())
        
        if has_local_changes:
            console.print("[yellow]⚠️  Local changes detected in repository[/yellow]")
            console.print("Files with changes:")
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    console.print(f"  {line}")
            console.print()
            
            # Try to stash changes automatically
            console.print("[yellow]Stashing local changes...[/yellow]")
            stash_result = subprocess.run(
                ["git", "stash", "push", "-m", "KaalSec auto-stash before update"],
                cwd=install_dir,
                capture_output=True,
                text=True,
                timeout=10,
            )
            
            if stash_result.returncode == 0:
                console.print("[bold green]✓ Local changes stashed[/bold green]")
                console.print("[dim]You can restore them later with: git stash pop[/dim]\n")
            else:
                console.print("[bold yellow]⚠️  Could not stash changes automatically[/bold yellow]")
                console.print("[bold]Please resolve manually:[/bold]")
                console.print("  1. Commit your changes: git add . && git commit -m 'Your changes'")
                console.print("  2. Or stash them: git stash")
                console.print("  3. Then run: kaalsec update")
                console.print("\nOr update manually:")
                console.print("  cd ~/kaalsec")
                console.print("  git pull")
                console.print("  source .venv/bin/activate")
                console.print("  pip install -e .")
                sys.exit(1)
        
        # Pull latest changes
        console.print("[yellow]Pulling latest changes...[/yellow]")
        result = subprocess.run(
            ["git", "pull", "origin", "main"],
            cwd=install_dir,
            capture_output=True,
            text=True,
            timeout=60,
        )
        
        if result.returncode != 0:
            console.print(f"[bold red]Error:[/bold red] Failed to pull updates")
            console.print(result.stderr)
            
            # If we stashed, try to restore
            if has_local_changes:
                console.print("\n[yellow]Attempting to restore stashed changes...[/yellow]")
                subprocess.run(
                    ["git", "stash", "pop"],
                    cwd=install_dir,
                    capture_output=True,
                )
            
            console.print("\n[bold]To update manually:[/bold]")
            console.print("  cd ~/kaalsec")
            console.print("  git pull")
            console.print("  source .venv/bin/activate")
            console.print("  pip install -e .")
            sys.exit(1)
        
        console.print("[bold green]✓ Code updated[/bold green]\n")
        
        # Reinstall dependencies
        console.print("[yellow]Updating dependencies...[/yellow]")
        venv_python = install_dir / ".venv" / "bin" / "python"
        
        if not venv_python.exists():
            console.print("[yellow]Virtual environment not found, creating...[/yellow]")
            subprocess.run(
                ["python3", "-m", "venv", ".venv"],
                cwd=install_dir,
                check=True,
            )
            venv_python = install_dir / ".venv" / "bin" / "python"
        
        # Upgrade pip
        subprocess.run(
            [str(venv_python), "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"],
            cwd=install_dir,
            capture_output=True,
        )
        
        # Reinstall package
        result = subprocess.run(
            [str(venv_python), "-m", "pip", "install", "-e", "."],
            cwd=install_dir,
            capture_output=True,
            text=True,
        )
        
        if result.returncode != 0:
            console.print("[bold yellow]Warning:[/bold yellow] Some dependencies may have failed to update")
            console.print(result.stderr)
        else:
            console.print("[bold green]✓ Dependencies updated[/bold green]\n")
        
        # Update plugins
        console.print("[yellow]Updating plugins...[/yellow]")
        plugins_source = install_dir / "plugins"
        plugins_dest = Path.home() / ".kaalsec" / "plugins"
        
        if plugins_source.exists() and plugins_dest.exists():
            # Copy new/updated plugins
            for plugin_file in plugins_source.glob("*.yml"):
                shutil.copy2(plugin_file, plugins_dest / plugin_file.name)
            console.print("[bold green]✓ Plugins updated[/bold green]\n")
        
        # Show new version
        from kaalsec import __version__
        console.print("=" * 50)
        console.print("[bold green]✓ KaalSec updated successfully![/bold green]")
        console.print(f"[bold]Current version:[/bold] {__version__}")
        console.print("=" * 50)
        console.print("\n[bold]Note:[/bold] If you encounter any issues, restart your terminal.")
        
    except subprocess.TimeoutExpired:
        console.print("[bold red]Error:[/bold red] Update timed out. Check your internet connection.")
        sys.exit(1)
    except FileNotFoundError:
        console.print("[bold red]Error:[/bold red] Git not found. Please install git:")
        console.print("  sudo apt install git")
        sys.exit(1)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)


@app.command()
def tools(
    category: Optional[str] = typer.Option(None, "--category", "-c", help="Filter by category"),
    installed_only: bool = typer.Option(False, "--installed", "-i", help="Show only installed tools"),
):
    """List available Kali Linux pentesting tools"""
    discovery = ToolDiscovery()
    
    if category:
        if category not in discovery.get_all_categories():
            console.print(f"[bold red]Error:[/bold red] Unknown category: {category}")
            console.print(f"Available categories: {', '.join(discovery.get_all_categories())}")
            sys.exit(1)
        
        tools_list = discovery.get_tools_by_category(category)
        console.print(f"[bold cyan]Tools in category '{category}':[/bold cyan]\n")
    else:
        if installed_only:
            tools_list = discovery.get_installed_tools()
            console.print(f"[bold cyan]Installed Kali tools:[/bold cyan]\n")
        else:
            # Show all tools grouped by category
            table = Table(title="Kali Linux Tools by Category", show_header=True, header_style="bold magenta")
            table.add_column("Category", style="yellow")
            table.add_column("Installed Tools", style="green")
            table.add_column("Count", style="cyan", justify="right")
            
            for cat in discovery.get_all_categories():
                installed = discovery.get_tools_by_category(cat)
                if installed or not installed_only:
                    table.add_row(
                        cat.replace("_", " ").title(),
                        ", ".join(installed[:5]) + ("..." if len(installed) > 5 else ""),
                        str(len(installed))
                    )
            
            console.print(table)
            return
    
    # Display tools list
    if tools_list:
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Tool", style="green")
        table.add_column("Status", style="cyan")
        table.add_column("Path", style="white")
        
        for tool in sorted(tools_list):
            info = discovery.get_tool_info(tool)
            status = "✓ Installed" if info["installed"] else "✗ Not installed"
            path = info["path"] or "N/A"
            table.add_row(tool, status, path)
        
        console.print(table)
    else:
        console.print("[yellow]No tools found.[/yellow]")


@app.command()
def integrate(
    uninstall: bool = typer.Option(False, "--uninstall", help="Remove shell integration"),
):
    """Install shell integration hooks for terminal integration"""
    integration = ShellIntegration()
    
    if uninstall:
        if integration.uninstall_hook():
            console.print("[bold green]✓ Shell integration removed[/bold green]")
            console.print("Restart your terminal or run: source ~/.bashrc (or ~/.zshrc)")
        else:
            console.print("[bold red]Error:[/bold red] Could not remove shell integration")
            sys.exit(1)
    else:
        if integration.is_installed():
            console.print("[yellow]Shell integration is already installed.[/yellow]")
            return
        
        if integration.install_hook():
            console.print("[bold green]✓ Shell integration installed successfully![/bold green]")
            console.print("\n[bold]What this enables:[/bold]")
            console.print("  • KaalSec can access your last executed command")
            console.print("  • Better context for suggestions and explanations")
            console.print("\n[bold]To activate:[/bold]")
            console.print("  Restart your terminal or run:")
            if integration.shell_name == "bash":
                console.print("    source ~/.bashrc")
            elif integration.shell_name == "zsh":
                console.print("    source ~/.zshrc")
        else:
            console.print("[bold red]Error:[/bold red] Could not install shell integration")
            console.print(f"Unsupported shell: {integration.shell_name}")
            console.print("Supported shells: bash, zsh")
            sys.exit(1)

