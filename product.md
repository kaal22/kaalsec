product.md — KaalSec AI

🛡️ Product Name



KaalSec — The Ethical AI Copilot for Kali Linux



🚀 Overview



KaalSec is a CLI-first ethical security assistant built for Kali Linux.

It sits next to your terminal, explains complex commands, suggests safer recon/exploitation workflows, and auto-generates documentation — all while keeping everything transparent, permission-based, and legally safe.



KaalSec does not silently execute commands, scrape pirated content, or provide illegal guidance.

It’s designed for:



Ethical hackers



Students learning cybersecurity



Sysadmins performing internal audits



Pentesters who want a smarter command assistant



Everything runs locally (Ollama mode) or via a configured cloud LLM (OpenAI, Anthropic, etc.).

Logging, confirmations, and clear warnings keep the workflow safe and compliant.



✨ Core Features (MVP)

1\. Ask Mode

kaalsec ask "How do I safely scan a /24 subnet?"





Natural-language guidance using your configured LLM backend.



2\. Explain Mode

kaalsec explain "nmap -sCV -p 22,80,443 10.0.0.5"

kaalsec explain -f output.txt





Breaks down commands or tool outputs:



What it does



Why the flags matter



Potential risks



Safer alternatives



3\. Suggest Mode

kaalsec suggest "enumerate web servers on 10.0.0.0/24"





Generates 2–4 safe, accurate, tool-specific commands:



Nmap



WhatWeb



Nikto



Gobuster



etc.



Each suggestion gets an ID so the user can manually execute it.



4\. Run Mode (Human-in-loop)

kaalsec run 2





Executes a suggestion — only after explicit confirmation.

No silent or auto-execution.



5\. Automatic Logging



Every run command is logged to:



~/.kaalsec/logs/





This generates:



Session command trails



JSON logs



Markdown summaries



6\. Report Builder

kaalsec report today





Creates a clean Markdown pentest report skeleton from:



Executed commands



Notes



Outputs you marked as important



🧩 Stretch-Goal Features (Later Phases)

Shell Integration



PROMPT\_COMMAND hook (Bash)



precmd() hook (ZSH)



Show last N commands as context for suggestions



TUI Side Panel



Real-time terminal companion showing:



Last command



Explanation



Suggested next steps



Plugin-based tips



Plugin Architecture



Each tool has a YAML file describing:



Common tasks



Example commands



Failure cases



Official docs



Example:



tool: nmap

categories:

&nbsp; - name: "Basic Scans"

&nbsp;   examples:

&nbsp;     - cmd: "nmap -sV <target>"

&nbsp;       desc: "Version detection."



Local-Only AI (Ollama Mode)



Works with:



llama3:instruct



DeepSeek-coder



Mistral



Any local model



Team Mode



Shared logging



Shared plugin library



Organisation policies



🛠️ Architecture

Tech Stack



Python 3.11



Typer CLI



TOML config loader



Pluggable backend system (OpenAI, Ollama, Anthropic, Local Adapter)



YAML plugin loader



Markdown report generator



Local SQLite (optional)



Core Modules

kaalsec/

&nbsp; cli.py           # All CLI commands (ask, explain, suggest, run, report)

&nbsp; config.py        # Load/parse ~/.kaalsec/config.toml

&nbsp; backend.py       # LLM adapters (OpenAI, Ollama, Local)

&nbsp; policy.py        # Ethical filter + legal banner injection

&nbsp; plugins.py       # YAML loader for tool knowledge

&nbsp; history.py       # Optional shell hook support

&nbsp; store.py         # Cache suggestions + lookups for 'run'

&nbsp; reports.py       # Markdown report generation



📂 File/Directory Structure (Cursor-ready)

/kaalsec

&nbsp; /kaalsec

&nbsp;   cli.py

&nbsp;   config.py

&nbsp;   backend.py

&nbsp;   policy.py

&nbsp;   plugins.py

&nbsp;   history.py

&nbsp;   store.py

&nbsp;   reports.py

&nbsp; /plugins

&nbsp;   nmap.yml

&nbsp;   nikto.yml

&nbsp;   gobuster.yml

&nbsp; README.md

&nbsp; pyproject.toml

&nbsp; product.md

&nbsp; install.sh



📦 pyproject.toml



Cursor will scaffold this, but high-level:



\[project]

name = "kaalsec"

version = "0.1.0"

description = "Ethical AI Copilot for Kali Linux"

authors = \[{ name = "Andrew (Kaal)" }]

dependencies = \[

&nbsp; "typer",

&nbsp; "pyyaml",

&nbsp; "toml",

&nbsp; "requests"

]



\[project.scripts]

kaalsec = "kaalsec.cli:run\_cli"



🔥 One-Click Install Script (install.sh)



Beginner-friendly. Tested on Kali Linux.



Copy this entire script into a file called install.sh and run:



chmod +x install.sh

./install.sh



install.sh

\#!/bin/bash



echo "=========================================="

echo "     Installing KaalSec — Ethical AI       "

echo "=========================================="

sleep 1



\# Ensure system is up to date

echo "\[1/8] Updating apt packages..."

sudo apt update -y



\# Install Python + pip

echo "\[2/8] Installing Python dependencies..."

sudo apt install -y python3 python3-pip python3-venv git



\# Create install directory

echo "\[3/8] Creating ~/.kaalsec directory..."

mkdir -p ~/.kaalsec

mkdir -p ~/.kaalsec/logs

mkdir -p ~/.kaalsec/plugins



\# Clone repo

echo "\[4/8] Cloning KaalSec repository..."

if \[ ! -d "$HOME/kaalsec" ]; then

&nbsp;   git clone https://github.com/kaal22/kaalsec.git ~/kaalsec

else

&nbsp;   echo "Repo already exists, pulling latest..."

&nbsp;   cd ~/kaalsec \&\& git pull

fi



\# Create virtual environment

echo "\[5/8] Creating Python virtual environment..."

cd ~/kaalsec

python3 -m venv .venv



\# Activate venv + install

echo "\[6/8] Installing Python dependencies..."

source .venv/bin/activate

pip install -e .



\# Create config file if missing

echo "\[7/8] Creating default config file..."

CONFIG\_PATH=~/.kaalsec/config.toml



if \[ ! -f "$CONFIG\_PATH" ]; then

cat <<EOF > $CONFIG\_PATH

\[core]

legal\_banner = true

history\_lines = 25

log\_level = "info"



\[backend]

provider = "openai"  # or "ollama"

model = "gpt-4.1-mini"

timeout\_seconds = 30



\[backend.openai]

api\_key\_env = "OPENAI\_API\_KEY"



\[backend.ollama]

host = "http://localhost:11434"

model = "llama3:instruct"



\[policy]

red\_team\_mode = false

anonymise\_ips = false

EOF

else

&nbsp;   echo "Config already exists, skipping."

fi



\# Final message

echo "=========================================="

echo "✔ KaalSec Installed Successfully!"

echo

echo "Run it with:"

echo "   kaalsec ask \\"How do I scan a subnet safely?\\""

echo

echo "To change models:"

echo "   nano ~/.kaalsec/config.toml"

echo

echo "Make sure to export your API key:"

echo "   export OPENAI\_API\_KEY=\\"your\_key\_here\\""

echo "=========================================="



🎯 MVP Definition (for Cursor)

Included



CLI with: ask, explain, suggest, run, report



Config loader



Backend adapter (stub or OpenAI first)



Plugin loader (YAML)



Local logs



Installer script



Not included (yet)



TUI



Shell integration



SQLite session store



Team mode



Plugin library expansion

