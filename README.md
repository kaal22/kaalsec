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

### Prerequisites

- **Kali Linux** (or compatible Debian-based Linux distribution)
- **Internet connection** (for downloading dependencies and the AI model)
- **sudo/root access** (for installing system packages)

### Method 1: Automated Installation (Recommended for Beginners)

This is the easiest method - the install script handles everything automatically.

#### Step 1: Clone the Repository

Open a terminal and run:

```bash
git clone https://github.com/kaal22/kaalsec.git
cd kaalsec
```

**Note:** You can clone to any location (Downloads, Desktop, etc.). The install script will automatically move everything to `~/kaalsec` (a safe location in your home directory) so you can safely delete the original folder after installation.

#### Step 2: Run the Install Script

```bash
# Make the script executable
chmod +x install.sh

# Run the installation
./install.sh
```

**What happens during installation:**
- If you cloned to Downloads/Desktop/etc., the script will **automatically move** the repository to `~/kaalsec`
- All installation files (code, virtual environment, etc.) will be in `~/kaalsec`
- You can safely delete the original clone location after installation
- The installation is now in a permanent, safe location

**What the install script does:**
- ✅ Updates your system packages
- ✅ Installs Python and required dependencies
- ✅ Installs Ollama (local AI model server)
- ✅ Downloads the Qwen2.5 AI model (~4GB, may take a few minutes)
- ✅ Sets up KaalSec with all plugins and configuration
- ✅ Creates the `kaalsec` command for easy access
- ✅ Configures performance settings for VMs

#### Step 3: Start Ollama Service

After installation, you need to start Ollama in a terminal:

```bash
ollama serve
```

**Keep this terminal open** - Ollama needs to be running for KaalSec to work.

#### Step 4: Test the Installation

Open a **new terminal** and test KaalSec:

```bash
kaalsec ask "What is KaalSec?"
```

If you see a response, installation was successful! 🎉

---

### Method 2: Manual Installation (Advanced Users)

If you prefer to install manually or the automated script doesn't work:

#### Step 1: Clone the Repository

```bash
git clone https://github.com/kaal22/kaalsec.git
cd kaalsec
```

**Note:** The install script will move the repository to `~/kaalsec` automatically, so you can clone to any temporary location.

#### Step 2: Install System Dependencies

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git curl
```

#### Step 3: Install Ollama

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

#### Step 4: Start Ollama and Download Model

```bash
# Start Ollama (keep this terminal open)
ollama serve
```

In a **new terminal**:

```bash
# Download the AI model (this may take several minutes)
ollama pull qwen2.5
```

#### Step 5: Set Up Python Environment

```bash
# Create virtual environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate

# Install KaalSec
pip install -e .
```

#### Step 6: Set Up Configuration

```bash
# Create directories
mkdir -p ~/.kaalsec/logs ~/.kaalsec/plugins

# Copy plugins
cp plugins/* ~/.kaalsec/plugins/

# Create config file
cat > ~/.kaalsec/config.toml << 'EOF'
[core]
legal_banner = true
history_lines = 25
log_level = "info"

[backend]
provider = "ollama"
model = "qwen2.5"
timeout_seconds = 60

[backend.ollama]
host = "http://localhost:11434"
model = "qwen2.5"

[policy]
red_team_mode = false
anonymise_ips = false
EOF
```

#### Step 7: Make kaalsec Available Globally

```bash
# Create symlink (requires sudo)
sudo ln -s $(pwd)/.venv/bin/kaalsec /usr/local/bin/kaalsec
```

Or add to your `~/.bashrc`:

```bash
echo 'alias kaalsec="$(pwd)/.venv/bin/kaalsec"' >> ~/.bashrc
source ~/.bashrc
```

---

### Post-Installation Setup

#### Enable Terminal Integration (Optional but Recommended)

This allows KaalSec to access your command history for better suggestions:

```bash
kaalsec integrate
```

Then restart your terminal or run:
```bash
source ~/.bashrc
```

#### Performance Tuning for VMs (Optional)

If running on a VM with limited resources, add to `~/.bashrc`:

```bash
echo 'export OLLAMA_NUM_THREADS=$(nproc)' >> ~/.bashrc
echo 'export OLLAMA_MAX_LOADED_MODELS=1' >> ~/.bashrc
source ~/.bashrc
```

---

### Troubleshooting

#### "kaalsec: command not found"

If the command isn't found after installation:

```bash
# Option 1: Activate the virtual environment
source ~/kaalsec/.venv/bin/activate
kaalsec --version

# Option 2: Use full path
~/kaalsec/.venv/bin/kaalsec --version

# Option 3: Add alias to ~/.bashrc
echo 'alias kaalsec="~/kaalsec/.venv/bin/kaalsec"' >> ~/.bashrc
source ~/.bashrc
```

#### "Could not connect to Ollama"

Make sure Ollama is running:

```bash
# Check if Ollama is running
pgrep ollama

# If not, start it
ollama serve
```

#### Model Not Found

If you get errors about the model:

```bash
# Pull the model again
ollama pull qwen2.5

# Verify it's available
ollama list
```

#### Installation Script Fails

If the automated install fails:

1. Check you have internet connection
2. Ensure you have sudo/root access
3. Try the manual installation method
4. Check error messages for specific issues

---

### Updating KaalSec

To update KaalSec to the latest version, simply run:

```bash
kaalsec update
```

This command will:
- ✅ Pull the latest code from GitHub
- ✅ Update all Python dependencies
- ✅ Update plugins
- ✅ Show you what changed

**Note:** Make sure you have an internet connection for the update to work.

#### Manual Update (if update command doesn't work)

If the `kaalsec update` command fails, you can update manually:

```bash
# Navigate to installation directory
cd ~/kaalsec

# Pull latest changes
git pull origin main

# Activate virtual environment
source .venv/bin/activate

# Reinstall dependencies
pip install -e .
```

#### Check for Updates

To see if updates are available without installing:

```bash
cd ~/kaalsec
git fetch origin
git status
```

---

### Quick Start After Installation

Once installed, try these commands:

```bash
# Ask a question
kaalsec ask "How do I scan for open ports safely?"

# List available Kali tools
kaalsec tools --installed

# Get command suggestions
kaalsec suggest "enumerate web servers on 10.0.0.0/24"

# Explain a command
kaalsec explain "nmap -sCV -p 22,80,443 10.0.0.5"
```

**Note:** KaalSec uses Ollama with Qwen2.5 (local LLM) by default. No API keys required! Everything runs locally and offline after the initial setup.

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

### Update KaalSec
```bash
kaalsec update                             # Update to latest version
kaalsec update --force                     # Force update even if up to date
kaalsec version                            # Check current version
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

