#!/bin/bash

echo "=========================================="
echo "     Installing KaalSec — Ethical AI       "
echo "=========================================="
sleep 1

# Detect shell and set config file
detect_shell_config() {
    local shell_name=$(basename "$SHELL" 2>/dev/null || echo "bash")
    local config_file=""
    
    case "$shell_name" in
        zsh)
            config_file="$HOME/.zshrc"
            ;;
        bash|sh)
            config_file="$HOME/.bashrc"
            ;;
        *)
            # Default to bashrc, but also check zshrc
            if [ -f "$HOME/.zshrc" ]; then
                config_file="$HOME/.zshrc"
            else
                config_file="$HOME/.bashrc"
            fi
            ;;
    esac
    
    # If config file doesn't exist, create it
    if [ ! -f "$config_file" ]; then
        touch "$config_file"
    fi
    
    echo "$config_file"
}

# Get the shell config file
SHELL_CONFIG=$(detect_shell_config)
SHELL_NAME=$(basename "$SHELL" 2>/dev/null || echo "bash")
echo "[Shell detected: $SHELL_NAME, using config: $SHELL_CONFIG]"
echo ""

# Ensure system is up to date
echo "[1/9] Updating apt packages..."
sudo apt update -y

# Install Python + pip
echo "[2/9] Installing Python dependencies..."
sudo apt install -y python3 python3-pip python3-venv git curl

# Install Ollama
echo "[3/9] Installing Ollama..."
if ! command -v ollama &> /dev/null; then
    echo "Downloading and installing Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
    echo "Ollama installed successfully!"
else
    echo "Ollama is already installed."
fi

# Start Ollama service and pull default model
echo "[3.5/9] Setting up Ollama model..."
if ! pgrep -x "ollama" > /dev/null; then
    echo "Starting Ollama service..."
    ollama serve &
    sleep 3
fi

# Pull qwen2.5 model if not already present
echo "Pulling qwen2.5 model (this may take a while)..."
ollama pull qwen2.5 || echo "Warning: Could not pull model. You can run 'ollama pull qwen2.5' manually later."

# Performance tuning for VMs (optional)
echo "[3.6/9] Setting up performance tuning (optional)..."
if ! grep -q "OLLAMA_NUM_THREADS" "$SHELL_CONFIG" 2>/dev/null; then
    echo "" >> "$SHELL_CONFIG"
    echo "# KaalSec performance tuning for Ollama" >> "$SHELL_CONFIG"
    echo "export OLLAMA_NUM_THREADS=\$(nproc)" >> "$SHELL_CONFIG"
    echo "export OLLAMA_MAX_LOADED_MODELS=1" >> "$SHELL_CONFIG"
    echo "Performance tuning added to $SHELL_CONFIG (reload with: source $SHELL_CONFIG)"
else
    echo "Performance tuning already configured in $SHELL_CONFIG"
fi

# Create install directory
echo "[4/9] Creating ~/.kaalsec directory..."
mkdir -p ~/.kaalsec
mkdir -p ~/.kaalsec/logs
mkdir -p ~/.kaalsec/plugins

# Clone repo or use current directory
echo "[5/9] Setting up KaalSec..."
SAFE_INSTALL_DIR="$HOME/kaalsec"

if [ -f "pyproject.toml" ] && [ -d "kaalsec" ]; then
    # We're in the repo directory
    CURRENT_DIR=$(pwd)
    
    # Check if we're already in the safe location
    if [ "$CURRENT_DIR" != "$SAFE_INSTALL_DIR" ] && [ "$CURRENT_DIR" != "$(realpath $SAFE_INSTALL_DIR 2>/dev/null)" ]; then
        echo "Repository found in: $CURRENT_DIR"
        echo "Moving to safe installation location: $SAFE_INSTALL_DIR"
        
        # Remove old installation if it exists
        if [ -d "$SAFE_INSTALL_DIR" ]; then
            echo "Removing old installation at $SAFE_INSTALL_DIR..."
            rm -rf "$SAFE_INSTALL_DIR"
        fi
        
        # Create the safe installation directory
        mkdir -p "$SAFE_INSTALL_DIR"
        
        # Copy to safe location (preserve git history)
        echo "Copying repository to $SAFE_INSTALL_DIR..."
        # Copy everything including hidden files (.git, etc.)
        cp -r "$CURRENT_DIR"/. "$SAFE_INSTALL_DIR" 2>/dev/null || cp -r "$CURRENT_DIR" "$SAFE_INSTALL_DIR"
        
        # Remove .venv if it exists (we'll create a fresh one)
        if [ -d "$SAFE_INSTALL_DIR/.venv" ]; then
            rm -rf "$SAFE_INSTALL_DIR/.venv"
        fi
        
        INSTALL_DIR="$SAFE_INSTALL_DIR"
        echo "✓ Repository moved to safe location: $INSTALL_DIR"
        echo "  You can safely delete the original folder: $CURRENT_DIR"
    else
        # Already in safe location
        INSTALL_DIR="$CURRENT_DIR"
        echo "Using installation directory: $INSTALL_DIR"
    fi
else
    # Clone from GitHub
    if [ ! -d "$SAFE_INSTALL_DIR" ]; then
        git clone https://github.com/kaal22/kaalsec.git "$SAFE_INSTALL_DIR"
    else
        echo "Installation directory already exists, pulling latest..."
        cd "$SAFE_INSTALL_DIR" && git pull
    fi
    INSTALL_DIR="$SAFE_INSTALL_DIR"
fi

# Create virtual environment
echo "[6/9] Creating Python virtual environment..."
cd "$INSTALL_DIR"
python3 -m venv .venv

# Activate venv + upgrade pip and setuptools
echo "[7/9] Installing Python dependencies..."
source .venv/bin/activate

# Upgrade pip, setuptools, and wheel first
echo "Upgrading pip, setuptools, and wheel..."
pip install --upgrade pip setuptools wheel

# Install all project dependencies
echo "Installing KaalSec and all dependencies..."
pip install -e .

# Verify installation
echo "Verifying installation..."
if ! python3 -c "import kaalsec" 2>/dev/null; then
    echo "Warning: KaalSec module not found. Installation may have failed."
else
    echo "✓ KaalSec Python package installed successfully"
fi

# Copy plugins to user directory
echo "[7.5/9] Copying plugins to ~/.kaalsec/plugins/..."
if [ -d "$INSTALL_DIR/plugins" ]; then
    # Copy all plugin files
    cp -r "$INSTALL_DIR/plugins"/* ~/.kaalsec/plugins/ 2>/dev/null || true
    PLUGIN_COUNT=$(ls -1 ~/.kaalsec/plugins/*.yml 2>/dev/null | wc -l)
    echo "  ✓ Plugin files copied: $PLUGIN_COUNT"
else
    echo "Warning: Plugins directory not found at $INSTALL_DIR/plugins"
fi

# Create config file if missing
echo "[8/9] Creating default config file..."
CONFIG_PATH=~/.kaalsec/config.toml

if [ ! -f "$CONFIG_PATH" ]; then
cat <<EOF > $CONFIG_PATH
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
EOF
    echo "✓ Config file created at $CONFIG_PATH"
else
    echo "Config already exists at $CONFIG_PATH, skipping."
fi

# Make kaalsec command available globally
echo "[8.5/9] Setting up global kaalsec command..."
VENV_BIN="$INSTALL_DIR/.venv/bin/kaalsec"

# Check if kaalsec is already in PATH
if command -v kaalsec &> /dev/null; then
    echo "✓ kaalsec command already available"
else
    if [ -f "$VENV_BIN" ]; then
        # Try method 1: Create symlink in /usr/local/bin (requires sudo)
        if sudo ln -sf "$VENV_BIN" /usr/local/bin/kaalsec 2>/dev/null; then
            echo "✓ Global kaalsec command created at /usr/local/bin/kaalsec"
        else
            # Method 2: Add alias to shell config (no sudo needed)
            echo "Creating alias in $SHELL_CONFIG..."
            if ! grep -q "alias kaalsec=" "$SHELL_CONFIG" 2>/dev/null; then
                echo "" >> "$SHELL_CONFIG"
                echo "# KaalSec alias" >> "$SHELL_CONFIG"
                echo "alias kaalsec=\"$VENV_BIN\"" >> "$SHELL_CONFIG"
                echo "✓ Alias added to $SHELL_CONFIG"
                echo "  Run 'source $SHELL_CONFIG' or restart terminal to use 'kaalsec' command"
            else
                echo "✓ Alias already exists in $SHELL_CONFIG"
            fi
            
            # Method 3: Also add venv bin to PATH as backup
            if ! grep -q "$INSTALL_DIR/.venv/bin" "$SHELL_CONFIG" 2>/dev/null; then
                echo "" >> "$SHELL_CONFIG"
                echo "# KaalSec PATH" >> "$SHELL_CONFIG"
                echo "export PATH=\"$INSTALL_DIR/.venv/bin:\$PATH\"" >> "$SHELL_CONFIG"
                echo "✓ Added KaalSec to PATH in $SHELL_CONFIG"
            fi
        fi
    else
        echo "Warning: kaalsec binary not found at $VENV_BIN"
    fi
fi

# Offer shell integration
echo "[8.6/9] Setting up shell integration (optional)..."
echo "To enable terminal integration (access to last command), run after installation:"
echo "  kaalsec integrate"

# Verify all dependencies are installed
echo "[8.7/9] Verifying all dependencies..."
source "$INSTALL_DIR/.venv/bin/activate"
MISSING_DEPS=0

# Check each dependency with correct import name
check_dep() {
    local pkg=$1
    local import=$2
    if python3 -c "import $import" 2>/dev/null; then
        echo "  ✓ $pkg"
        return 0
    else
        echo "  ✗ Missing: $pkg"
        return 1
    fi
}

check_dep "typer" "typer" || MISSING_DEPS=1
check_dep "pyyaml" "yaml" || MISSING_DEPS=1
check_dep "toml" "toml" || MISSING_DEPS=1
check_dep "requests" "requests" || MISSING_DEPS=1
check_dep "rich" "rich" || MISSING_DEPS=1

if [ $MISSING_DEPS -eq 0 ]; then
    echo "✓ All dependencies verified"
else
    echo "Warning: Some dependencies may be missing. Try: pip install -e ."
fi

# Final verification
echo "[9/9] Final verification..."
echo "=========================================="
echo "Installation Summary:"
echo "  ✓ KaalSec directory: $INSTALL_DIR"
echo "  ✓ Config location: ~/.kaalsec/config.toml"
echo "  ✓ Plugins location: ~/.kaalsec/plugins/"
echo "  ✓ Logs location: ~/.kaalsec/logs/"
echo "  ✓ Virtual environment: $INSTALL_DIR/.venv"

# Test kaalsec command
if command -v kaalsec &> /dev/null; then
    echo "  ✓ kaalsec command: $(which kaalsec)"
    # Test if command actually works
    if kaalsec version &>/dev/null; then
        echo "  ✓ kaalsec command verified working"
    else
        echo "  ⚠ kaalsec command found but may not be working correctly"
    fi
else
    # Test using venv path directly
    VENV_KAALSEC="$INSTALL_DIR/.venv/bin/kaalsec"
    if [ -f "$VENV_KAALSEC" ]; then
        echo "  ✓ kaalsec binary: $VENV_KAALSEC"
        if source "$INSTALL_DIR/.venv/bin/activate" && kaalsec version &>/dev/null; then
            echo "  ✓ kaalsec command verified working (in venv)"
        fi
    else
        echo "  ⚠ kaalsec command: Not found"
    fi
    echo "     To use: source $INSTALL_DIR/.venv/bin/activate"
    echo "     Or add alias to $SHELL_CONFIG: alias kaalsec='$VENV_KAALSEC'"
fi

# Verify file locations
echo ""
echo "File Locations Verification:"
[ -f ~/.kaalsec/config.toml ] && echo "  ✓ Config file exists" || echo "  ✗ Config file missing"
[ -d ~/.kaalsec/plugins ] && echo "  ✓ Plugins directory exists" || echo "  ✗ Plugins directory missing"
[ -d ~/.kaalsec/logs ] && echo "  ✓ Logs directory exists" || echo "  ✗ Logs directory missing"
[ -d "$INSTALL_DIR/.venv" ] && echo "  ✓ Virtual environment exists" || echo "  ✗ Virtual environment missing"

echo "=========================================="
echo "✔ KaalSec Installed Successfully!"
echo
echo "Ollama Configuration:"
echo "  ✓ Default model: qwen2.5"
echo "  ✓ Performance tuning: Added to $SHELL_CONFIG"
echo
echo "Quick Start:"
if command -v kaalsec &> /dev/null; then
    echo "  kaalsec ask \"How do I scan a subnet safely?\""
    echo "  kaalsec fix 'E: Unable to correct problems, you have held broken packages'"
    echo "  kaalsec write a bash script to run nmap then gobuster on a target domain"
else
    echo "  source $INSTALL_DIR/.venv/bin/activate"
    echo "  kaalsec ask \"How do I scan a subnet safely?\""
fi
echo
echo "Important Notes:"
echo "  • Make sure Ollama is running: ollama serve"
echo "  • Reload shell to use kaalsec command: source $SHELL_CONFIG (or restart terminal)"
echo "  • To use different model: ollama pull <model> && nano ~/.kaalsec/config.toml"
echo "  • Enable terminal integration: kaalsec integrate"
echo "  • List available Kali tools: kaalsec tools"
echo ""
echo "To use KaalSec now (without restarting terminal):"
if command -v kaalsec &> /dev/null; then
    echo "  kaalsec ask \"test question\""
else
    echo "  source $SHELL_CONFIG"
    echo "  kaalsec ask \"test question\""
fi
echo ""
echo "Shell Configuration:"
echo "  • Detected shell: $SHELL_NAME"
echo "  • Config file: $SHELL_CONFIG"
echo "  • After reloading config, 'kaalsec' command will work from anywhere"
echo "=========================================="

