#!/bin/bash

################################################################################
# Edge LLM System - VS Code Quick Setup
# One-command setup optimized for VS Code + GitHub Copilot users
################################################################################

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'
BOLD='\033[1m'

echo -e "${BOLD}${BLUE}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║     Edge LLM System - VS Code Setup                      ║
║     Optimized for GitHub Copilot Users                   ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}\n"

# Check if VS Code is installed
if ! command -v code &> /dev/null; then
    echo -e "${RED}✗ VS Code not found${NC}"
    echo -e "${YELLOW}Please install VS Code from: https://code.visualstudio.com/${NC}\n"
    exit 1
fi
echo -e "${GREEN}✓ VS Code detected${NC}"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 not found${NC}"
    exit 1
fi
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✓ Python ${PYTHON_VERSION} detected${NC}"

echo ""
echo -e "${BOLD}${BLUE}Step 1: Creating VS Code Configuration${NC}"
echo ""

# Create .vscode directory
mkdir -p .vscode

# Create settings.json
cat > .vscode/settings.json << 'VSCODE_SETTINGS'
{
    "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
    "python.terminal.activateEnvironment": true,
    "github.copilot.enable": {
        "*": true,
        "python": true,
        "markdown": true
    },
    "editor.formatOnSave": true,
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        "**/venv": true
    },
    "python.testing.pytestEnabled": true
}
VSCODE_SETTINGS

echo -e "${GREEN}✓ Created .vscode/settings.json${NC}"

# Create launch.json
cat > .vscode/launch.json << 'LAUNCH_JSON'
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "🚀 Run Demo",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/example_integration.py",
            "console": "integratedTerminal"
        },
        {
            "name": "💬 CLI Chat",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/edge-llm-cli.py",
            "args": ["chat"],
            "console": "integratedTerminal"
        }
    ]
}
LAUNCH_JSON

echo -e "${GREEN}✓ Created .vscode/launch.json${NC}"

# Create tasks.json
cat > .vscode/tasks.json << 'TASKS_JSON'
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Install Dependencies",
            "type": "shell",
            "command": "pip install -r requirements.txt",
            "group": "build"
        },
        {
            "label": "Start Chat",
            "type": "shell",
            "command": "python edge-llm-cli.py chat",
            "group": "none"
        }
    ]
}
TASKS_JSON

echo -e "${GREEN}✓ Created .vscode/tasks.json${NC}"

# Create extensions.json
cat > .vscode/extensions.json << 'EXTENSIONS_JSON'
{
    "recommendations": [
        "ms-python.python",
        "ms-python.vscode-pylance",
        "github.copilot",
        "github.copilot-chat",
        "usernamehw.errorlens"
    ]
}
EXTENSIONS_JSON

echo -e "${GREEN}✓ Created .vscode/extensions.json${NC}"

echo ""
echo -e "${BOLD}${BLUE}Step 2: Setting Up Python Environment${NC}"
echo ""

# Create virtual environment
if [ -d "venv" ]; then
    echo -e "${YELLOW}Virtual environment exists, skipping...${NC}"
else
    echo -e "${BLUE}Creating virtual environment...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

# Activate virtual environment
echo -e "${BLUE}Activating virtual environment...${NC}"
source venv/bin/activate

echo ""
echo -e "${BOLD}${BLUE}Step 3: Installing Dependencies${NC}"
echo ""

if [ -f "requirements.txt" ]; then
    echo -e "${BLUE}Installing Python packages...${NC}"
    pip install --upgrade pip --quiet
    pip install -r requirements.txt --quiet
    echo -e "${GREEN}✓ Dependencies installed${NC}"
else
    echo -e "${RED}✗ requirements.txt not found${NC}"
    echo -e "${YELLOW}Make sure all project files are in this directory${NC}"
    exit 1
fi

echo ""
echo -e "${BOLD}${BLUE}Step 4: Creating .gitignore${NC}"
echo ""

cat > .gitignore << 'GITIGNORE'
# Python
__pycache__/
*.py[cod]
venv/
.pytest_cache/

# Models
models/
*.gguf
*.bin

# Environment
.env

# VS Code (optional)
.vscode/settings.json

# System
.DS_Store

# Logs
*.log
metrics.jsonl
GITIGNORE

echo -e "${GREEN}✓ Created .gitignore${NC}"

echo ""
echo -e "${BOLD}${BLUE}Step 5: Verification${NC}"
echo ""

# Test import
if python -c "from llm_edge_router import LLMEdgeRouter" 2>/dev/null; then
    echo -e "${GREEN}✓ Core modules working${NC}"
else
    echo -e "${RED}✗ Module import failed${NC}"
    echo -e "${YELLOW}Check that all Python files are in the directory${NC}"
fi

# Create quick reference file
cat > VSCODE_QUICKSTART.md << 'QUICKSTART'
# VS Code Quick Start

## Just Set Up - What Now?

### Open in VS Code
```bash
code .
```

### Recommended Extensions
VS Code will prompt you to install recommended extensions:
- Python
- Pylance
- GitHub Copilot
- GitHub Copilot Chat
- Error Lens

Click "Install All" when prompted.

### Run Your First Command

**Option 1: Use Tasks (Easy)**
- Press `Ctrl+Shift+B` (or `Cmd+Shift+B` on Mac)
- Select "Start Chat"

**Option 2: Use Terminal**
- Press `Ctrl+`` to open terminal
- Run: `python edge-llm-cli.py chat`

**Option 3: Use Debug (F5)**
- Press F5
- Select "💬 CLI Chat"

### Download Models

In terminal:
```bash
python download_models.py --platform desktop
```

Or use task: `Ctrl+Shift+P` → "Tasks: Run Task" → "Install Dependencies"

### Try Examples

Press F5 → Select "🚀 Run Demo"

### Ask Copilot for Help!

Press `Ctrl+Shift+I` to open Copilot Chat and ask:
- "How do I use the LLM router?"
- "Show me how to generate code"
- "Explain the routing logic"

## Next Steps

1. Read: VSCODE_COPILOT_GUIDE.md
2. Try: ./edge-llm-cli.py chat
3. Explore: Example demos with F5

Happy coding! 🚀
QUICKSTART

echo -e "${GREEN}✓ Created VSCODE_QUICKSTART.md${NC}"

echo ""
echo -e "${BOLD}${GREEN}╔═══════════════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}${GREEN}║                                                       ║${NC}"
echo -e "${BOLD}${GREEN}║           Setup Complete! 🎉                         ║${NC}"
echo -e "${BOLD}${GREEN}║                                                       ║${NC}"
echo -e "${BOLD}${GREEN}╚═══════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${BOLD}Next Steps:${NC}\n"
echo -e "  1. Open in VS Code:"
echo -e "     ${BLUE}code .${NC}\n"
echo -e "  2. Install recommended extensions when prompted\n"
echo -e "  3. Download models:"
echo -e "     ${BLUE}python download_models.py --platform desktop${NC}\n"
echo -e "  4. Start chatting:"
echo -e "     ${BLUE}python edge-llm-cli.py chat${NC}\n"
echo -e "  ${YELLOW}Or press F5 in VS Code to run demos!${NC}\n"

echo -e "${BOLD}Quick Reference:${NC}"
echo -e "  • Read: ${BLUE}VSCODE_QUICKSTART.md${NC}"
echo -e "  • Guide: ${BLUE}VSCODE_COPILOT_GUIDE.md${NC}"
echo -e "  • Help: Ask GitHub Copilot anything!\n"

echo -e "${BOLD}Keyboard Shortcuts:${NC}"
echo -e "  • ${BLUE}F5${NC}         - Run/Debug"
echo -e "  • ${BLUE}Ctrl+Shift+B${NC} - Run Task"
echo -e "  • ${BLUE}Ctrl+Shift+I${NC} - Copilot Chat"
echo -e "  • ${BLUE}Ctrl+\`${NC}       - Terminal\n"

echo -e "${GREEN}Happy coding! 🚀${NC}\n"
