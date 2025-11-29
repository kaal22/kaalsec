# 🛡️ KaalSec — The Ethical AI Copilot for Kali Linux

KaalSec is a CLI-first ethical security assistant built for Kali Linux. It sits next to your terminal, explains complex commands, suggests safer recon/exploitation workflows, and auto-generates documentation — all while keeping everything transparent, permission-based, and legally safe.

## ⚠️ Legal Disclaimer

KaalSec is designed for **ETHICAL security testing ONLY**:
- Only use on systems you own or have explicit permission to test
- Unauthorized access is ILLEGAL and may result in criminal prosecution
- You are responsible for all actions taken with this tool
- KaalSec logs all executed commands for compliance

## ✨ Features

### 1. Ask Mode
Get natural-language guidance using your configured LLM backend:
```bash
kaalsec ask "How do I safely scan a /24 subnet?"
```

### 2. Explain Mode
Break down commands or tool outputs:
```bash
kaalsec explain "nmap -sCV -p 22,80,443 10.0.0.5"
kaalsec explain -f output.txt
```

Shows:
- What it does
- Why the flags matter
- Potential risks
- Safer alternatives

### 3. Suggest Mode
Generate 2–4 safe, accurate, tool-specific commands:
```bash
kaalsec suggest "enumerate web servers on 10.0.0.0/24"
```

Each suggestion gets an ID so you can manually execute it.

### 4. Run Mode (Human-in-loop)
Execute a suggestion — only after explicit confirmation:
```bash
kaalsec run 2
```

No silent or auto-execution.

### 5. Automatic Logging
Every run command is logged to `~/.kaalsec/logs/`:
- Session command trails
- JSON logs
- Markdown summaries

### 6. Report Builder
Create clean Markdown pentest reports:
```bash
kaalsec report today
```

### 7. Tool Discovery
Discover and list installed Kali Linux pentesting tools:
```bash
kaalsec tools                    # List all tools by category
kaalsec tools --installed        # Show only installed tools
kaalsec tools --category web_application_analysis
```

### 8. Terminal Integration
Integrate KaalSec with your shell for better context:
```bash
kaalsec integrate                 # Install shell hooks
kaalsec integrate --uninstall    # Remove integration
```

This enables KaalSec to access your last executed command for better suggestions and explanations.

## 🚀 Installation

### Quick Install (Kali Linux)

```bash
chmod +x install.sh
./install.sh
```

### Manual Installation

1. **Clone the repository:**
```bash
git clone https://github.com/kaal22/kaalsec.git
cd kaalsec
```

2. **Create virtual environment:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -e .
```

4. **Set up configuration:**
```bash
mkdir -p ~/.kaalsec/logs ~/.kaalsec/plugins
cp plugins/* ~/.kaalsec/plugins/
```

5. **Install and set up Ollama:**
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama service
ollama serve

# Pull the default model (in another terminal)
ollama pull qwen2.5
```

6. **Optional: Performance tuning for VMs**
Add to `~/.bashrc` for better performance on CPU-only VMs:
```bash
export OLLAMA_NUM_THREADS=$(nproc)
export OLLAMA_MAX_LOADED_MODELS=1
```
Then reload: `source ~/.bashrc`

7. **Create config file** (`~/.kaalsec/config.toml`):
```toml
[core]
legal_banner = true
history_lines = 25
log_level = "info"

[backend]
provider = "ollama"  # Local LLM - no API key needed!
model = "qwen2.5"
timeout_seconds = 60

[backend.openai]
api_key_env = "OPENAI_API_KEY"

[backend.ollama]
host = "http://localhost:11434"
model = "qwen2.5"

[policy]
red_team_mode = false
anonymise_ips = false
```

**Note:** KaalSec uses Ollama with Qwen2.5 (local LLM) by default. No API keys required! To use OpenAI instead, change `provider = "openai"` and set `OPENAI_API_KEY` environment variable.

## 📖 Usage Examples

### Ask a Question
```bash
kaalsec ask "How do I scan a subnet safely?"
kaalsec ask "fix 'E: Unable to correct problems, you have held broken packages' in kali"
kaalsec ask "write a bash script to run nmap then gobuster on a target domain"
kaalsec ask "show steps to put wlan0 into monitor mode in a vm and capture handshakes"
```

### Explain a Command
```bash
kaalsec explain "nmap -sS -p- 10.0.0.1"
kaalsec explain -f output.txt
```

### Get Suggestions
```bash
kaalsec suggest "enumerate web servers on 10.0.0.0/24"
kaalsec suggest "generate a basic recon checklist for a new web target"
```

### Execute a Suggestion
```bash
# First, get suggestions
kaalsec suggest "scan for open ports on 10.0.0.1"

# Then execute by ID
kaalsec run 1
```

### Generate Report
```bash
kaalsec report today
kaalsec report 2024-01-15
kaalsec report today -o report.md
```

### Discover Tools
```bash
kaalsec tools                              # List all Kali tools by category
kaalsec tools --installed                  # Show only installed tools
kaalsec tools --category password_attacks  # Tools in specific category
```

### Terminal Integration
```bash
kaalsec integrate                          # Install shell hooks (bash/zsh)
kaalsec integrate --uninstall              # Remove integration
```

## 🔧 Configuration

Edit `~/.kaalsec/config.toml` to customize:

- **Backend**: Default is Ollama (local, no API key). Can switch to OpenAI if needed
- **Model**: Default is qwen2.5. Can use other Ollama models (llama3:instruct, mistral, etc.) or OpenAI models
- **Policy**: Enable/disable red team mode, IP anonymization
- **Logging**: Adjust log levels and history retention

### Using Different Ollama Models

```bash
# Pull a different model
ollama pull mistral
ollama pull llama3:instruct
ollama pull deepseek-coder

# Update config.toml
[backend.ollama]
model = "mistral"  # or your preferred model
```

### Switching to OpenAI (Optional)

If you prefer OpenAI, update `config.toml`:
```toml
[backend]
provider = "openai"
model = "gpt-4o-mini"
```

Then set your API key:
```bash
export OPENAI_API_KEY="your_key_here"
```

## 🧩 Plugins

KaalSec uses YAML plugins to provide tool-specific knowledge. Plugins are located in `~/.kaalsec/plugins/`.

Example plugins included:
- `nmap.yml` - Network mapper
- `nikto.yml` - Web server scanner
- `gobuster.yml` - Directory/file brute-forcer

To add a new plugin, create a YAML file following the format in `plugins/README.md`.

## 🏗️ Architecture

- **Python 3.11+** - Core language
- **Typer** - CLI framework
- **Rich** - Beautiful terminal output
- **TOML** - Configuration format
- **YAML** - Plugin format
- **Pluggable backends** - OpenAI, Ollama, or custom adapters

## 📁 Project Structure

```
kaalsec/
├── kaalsec/
│   ├── cli.py              # CLI commands
│   ├── config.py           # Config loader
│   ├── backend.py          # LLM adapters
│   ├── policy.py           # Ethical filters
│   ├── plugins.py          # Plugin loader
│   ├── history.py          # Shell history
│   ├── store.py            # Suggestion cache
│   ├── reports.py          # Report generation
│   ├── tools.py            # Tool discovery
│   └── shell_integration.py # Shell hooks
├── plugins/                # Tool plugins (YAML)
├── pyproject.toml          # Project config
├── install.sh              # Install script
└── README.md               # This file
```

## 🤝 Contributing

Contributions welcome! Please ensure:
- All code follows ethical security practices
- Tests are included for new features
- Documentation is updated

## 📝 License

[Add your license here]

## 🙏 Acknowledgments

Built for ethical hackers, students, and security professionals who value transparency and responsible security testing.

---

**Remember**: Always test ethically and legally. KaalSec is a tool to assist, not to enable illegal activities.

