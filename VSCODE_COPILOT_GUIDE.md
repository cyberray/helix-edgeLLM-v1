# VS Code + GitHub Copilot Deployment Guide 🚀

## Quick Setup for VS Code Users

This guide is optimized for developers using Visual Studio Code with GitHub Copilot.

---

## 📋 Prerequisites

### Required
- ✅ **VS Code** installed (latest version)
- ✅ **GitHub Copilot** subscription active
- ✅ **Python 3.9+** installed
- ✅ **Git** installed

### Verify Setup
```bash
# Check VS Code is installed
code --version

# Check Python version
python3 --version

# Check Git
git --version
```

---

## 🎯 Step-by-Step Deployment in VS Code

### Step 1: Set Up Project in VS Code

```bash
# Create project directory
mkdir edge-llm-project
cd edge-llm-project

# Initialize Git repository
git init

# Open in VS Code
code .
```

### Step 2: Install Recommended Extensions

**Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac) → "Extensions: Show Recommended Extensions"**

Install these extensions:
1. **Python** (by Microsoft)
2. **Pylance** (Python language server)
3. **GitHub Copilot** (already have it!)
4. **GitHub Copilot Chat** (for inline assistance)
5. **Error Lens** (inline error messages)
6. **Code Spell Checker** (optional but helpful)

### Step 3: Copy All System Files

Place all the downloaded files in your `edge-llm-project` folder:

```
edge-llm-project/
├── .vscode/                    (create this - we'll configure below)
├── llm_edge_router.py
├── download_models.py
├── example_integration.py
├── edge-llm-cli.py
├── requirements.txt
├── test_edge_llm.py
├── quickstart.sh
├── README.md
├── STEP_BY_STEP_DEPLOYMENT.md
├── GET_STARTED.md
├── QUICK_REFERENCE.md
├── platform_implementations.md
└── ... (all other files)
```

---

## ⚙️ VS Code Workspace Configuration

### Create `.vscode/settings.json`

In VS Code, create `.vscode/settings.json`:

```json
{
    // Python Settings
    "python.defaultInterpreterPath": "${workspaceFolder}\\.venv\\Scripts\\python.exe",
    "python.terminal.activateEnvironment": true,
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    
    // Copilot Settings
    "github.copilot.enable": {
        "*": true,
        "python": true,
        "markdown": true,
        "javascript": true,
        "typescript": true
    },
    
    // Editor Settings
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    },
    
    // File Associations
    "files.associations": {
        "*.md": "markdown",
        "*.py": "python"
    },
    
    // Files to Exclude from Search
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        "**/.venv": true,
        "**/.pytest_cache": true
    },
    
    // Terminal Settings
    "terminal.integrated.env.osx": {
        "PYTHONPATH": "${workspaceFolder}"
    },
    "terminal.integrated.env.linux": {
        "PYTHONPATH": "${workspaceFolder}"
    }
}
```

### Create `.vscode/launch.json` (for debugging)

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Example Integration",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/example_integration.py",
            "console": "integratedTerminal",
            "justMyCode": true
        },
        {
            "name": "Python: CLI Chat",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/edge-llm-cli.py",
            "args": ["chat"],
            "console": "integratedTerminal",
            "justMyCode": true
        },
        {
            "name": "Python: Download Models",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/download_models.py",
            "args": ["--platform", "desktop"],
            "console": "integratedTerminal",
            "justMyCode": true
        },
        {
            "name": "Python: Current File",
            "type": "python",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal",
            "justMyCode": true
        }
    ]
}
```

### Create `.vscode/tasks.json` (for common tasks)

```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Install Dependencies",
            "type": "shell",
            "command": ".\\.venv\\Scripts\\python.exe -m pip install -r requirements.txt",
            "group": "build",
            "presentation": {
                "reveal": "always",
                "panel": "new"
            }
        },
        {
            "label": "Download Models (Desktop)",
            "type": "shell",
            "command": ".\\.venv\\Scripts\\python.exe download_models.py --platform desktop",
            "group": "build",
            "presentation": {
                "reveal": "always",
                "panel": "new"
            }
        },
        {
            "label": "Run Tests",
            "type": "shell",
            "command": "pytest test_edge_llm.py -v",
            "group": "test",
            "presentation": {
                "reveal": "always",
                "panel": "new"
            }
        },
        {
            "label": "Start CLI Chat",
            "type": "shell",
            "command": ".\\.venv\\Scripts\\python.exe edge-llm-cli.py chat",
            "group": "none",
            "presentation": {
                "reveal": "always",
                "panel": "new"
            }
        },
        {
            "label": "Quick Start",
            "type": "shell",
            "command": ".\\vscode-setup.sh",
            "group": "build",
            "presentation": {
                "reveal": "always",
                "panel": "new"
            }
        }
    ]
}
```

### Create `.vscode/extensions.json` (recommended extensions)

```json
{
    "recommendations": [
        "ms-python.python",
        "ms-python.vscode-pylance",
        "github.copilot",
        "github.copilot-chat",
        "usernamehw.errorlens",
        "streetsidesoftware.code-spell-checker",
        "ms-python.black-formatter",
        "ms-toolsai.jupyter"
    ]
}
```

---

## 🎯 Using VS Code Integrated Terminal

### Step 1: Create Virtual Environment

**In VS Code Terminal (Ctrl+`):**

```bash
# Create virtual environment
python -m venv .venv

# Activate it
# On Windows (PowerShell):
.\.venv\Scripts\Activate.ps1

# On macOS/Linux:
# source .venv/bin/activate

# VS Code should detect it and ask to use it - click "Yes"
```

### Step 2: Install Dependencies

```bash
# Install from requirements.txt
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

# This takes 5-10 minutes
```

### Step 3: Download Models

```bash
# Interactive mode
.\.venv\Scripts\python.exe download_models.py

# Or specific platform
.\.venv\Scripts\python.exe download_models.py --platform desktop
```

---

## 🤖 Using GitHub Copilot Effectively

### Copilot Tips for This Project

#### 1. Ask Copilot to Explain Code

**In Copilot Chat (Ctrl+Shift+I):**

```
Explain how the LLMEdgeRouter class works in llm_edge_router.py
```

#### 2. Generate Custom Routing Logic

**In your Python file, type comment:**

```python
# Create a custom router that prefers Qwen for Python code
# and Phi-3.5 for everything else
```

**Press Tab** - Copilot will suggest implementation!

#### 3. Create Custom Integration

**Type comment:**

```python
# Create a function that uses the LLM to analyze code quality
# and return a score from 1-10 with detailed feedback
```

#### 4. Debug with Copilot

**Select error text → Right-click → "Copilot: Explain This"**

---

## 🚀 VS Code Tasks Integration

### Run Tasks with Keyboard Shortcuts

**Press `Ctrl+Shift+B` (or `Cmd+Shift+B` on Mac)**

Select:
- **Install Dependencies** - Install all packages
- **Download Models (Desktop)** - Download models
- **Run Tests** - Run test suite
- **Start CLI Chat** - Start interactive chat
- **Quick Start** - Run automated setup

### Or use Command Palette

**Press `Ctrl+Shift+P` → "Tasks: Run Task"**

---

## 🐛 Debugging in VS Code

### Debug Your Code

1. **Set breakpoints** (click left of line numbers)
2. **Press F5** or click "Run and Debug"
3. **Select configuration:**
   - "Python: Example Integration" - Run demos
   - "Python: CLI Chat" - Debug CLI
   - "Python: Current File" - Debug any file

### Debug with Copilot Help

While debugging:
- **Hover over variables** - See values
- **Ask Copilot:** "Why is this variable None?"
- **Ask Copilot:** "How can I fix this TypeError?"

---

## 📁 Recommended Folder Structure

```
edge-llm-project/
├── .vscode/                    # VS Code configuration
│   ├── settings.json
│   ├── launch.json
│   ├── tasks.json
│   └── extensions.json
├── models/                     # Downloaded models (gitignored)
├── .venv/                      # Virtual environment (gitignored)
├── llm_edge_router.py         # Core system
├── download_models.py          # Model downloader
├── example_integration.py      # Examples
├── edge-llm-cli.py            # CLI tool
├── test_edge_llm.py           # Tests
├── requirements.txt            # Dependencies
├── .env                        # API keys (gitignored)
├── .gitignore                  # Git ignore file
└── README.md                   # Documentation
```

---

## 📝 Create `.gitignore`

**Create `.gitignore` in project root:**

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
.venv/
env/
ENV/
.pytest_cache/

# Models (too large for git)
models/
*.gguf
*.bin

# Environment variables
.env
.env.local

# VS Code
.vscode/settings.json  # Optional: remove if you want to share settings

# System
.DS_Store
Thumbs.db

# Logs
*.log
metrics.jsonl

# Distribution
dist/
build/
*.egg-info/
```

---

## 🔄 Git Workflow in VS Code

### Initial Setup

**In VS Code Source Control (Ctrl+Shift+G):**

```bash
# In terminal
git add .
git commit -m "Initial commit: Edge LLM System"

# Create GitHub repo (optional)
gh repo create edge-llm-project --private

# Push
git push -u origin main
```

### Use Copilot for Commit Messages

1. Stage changes in Source Control
2. Click commit message box
3. **Type `/` and select "Generate Commit Message"**
4. Copilot generates descriptive commit!

---

## 🎨 Copilot Prompts for Common Tasks

### 1. Create Custom Model

**In Python file, type:**

```python
# Add a new model configuration for Mistral 7B
# with 32K context window and Q4 quantization
# optimized for creative writing tasks
```

### 2. Implement Feature

```python
# Create a function that streams LLM responses
# word by word with a typing animation effect
# for better user experience
```

### 3. Add Error Handling

```python
# Add comprehensive error handling to this function
# including network errors, timeout, and invalid responses
# with user-friendly error messages
```

### 4. Write Tests

```python
# Write pytest tests for the route_request method
# covering simple, medium, and complex task scenarios
# including edge cases and error conditions
```

### 5. Create API Endpoint

```python
# Create a FastAPI endpoint that accepts a prompt
# routes it through the LLM system, and returns
# the response with metadata (model used, latency, tier)
```

---

## 🚀 Quick Deployment Workflows

### Desktop Development (VS Code Terminal)

```bash
# Terminal 1: Development
.\.venv\Scripts\python.exe example_integration.py

# Terminal 2: Testing
pytest test_edge_llm.py --watch

# Terminal 3: CLI
.\.venv\Scripts\python.exe edge-llm-cli.py chat
```

### iOS Development (with Xcode)

```bash
# In VS Code: Prepare models
.\.venv\Scripts\python.exe download_models.py --platform ios

# Then open Xcode
open EdgeLLMApp.xcodeproj
```

### Web Development

```bash
# Create web project in VS Code
mkdir edge-llm-web && cd edge-llm-web
npm init -y

# Let Copilot help!
# Comment: "Setup a Vite project with Transformers.js"
```

---

## 💡 Copilot Best Practices for This Project

### 1. Ask Specific Questions

**Good:**
```
How do I modify llm_edge_router.py to add custom scoring 
for technical documentation tasks?
```

**Less Good:**
```
How to change router?
```

### 2. Use Comments as Prompts

**Type:**
```python
# Create a function that:
# 1. Takes a code file as input
# 2. Uses the LLM to analyze code quality
# 3. Returns scores for: readability, performance, security
# 4. Provides actionable recommendations
```

**Press Enter** - Copilot generates!

### 3. Ask for Explanations

**Select code → Copilot Chat:**
```
Explain this routing decision logic and suggest improvements
for battery-constrained devices
```

### 4. Request Optimizations

```
Optimize this model loading function to reduce memory usage
and startup time on mobile devices
```

---

## 🎯 VS Code Shortcuts for This Project

| Shortcut | Action |
|----------|--------|
| `Ctrl+Shift+P` | Command Palette |
| `Ctrl+`` | Toggle Terminal |
| `F5` | Start Debugging |
| `Ctrl+Shift+B` | Run Build Task |
| `Ctrl+Shift+G` | Source Control |
| `Ctrl+Shift+I` | Copilot Chat |
| `Alt+\` | Inline Copilot |
| `Ctrl+Shift+T` | Reopen Closed Terminal |

---

## 📊 VS Code Development Workflow

### Typical Development Session

```
1. Open VS Code → Open project folder
2. Activate virtual environment (automatic if configured)
3. Open Copilot Chat (Ctrl+Shift+I)
4. Ask: "Help me understand the routing logic"
5. Make changes with Copilot suggestions
6. Run tests (F5 or task)
7. Debug if needed (F5)
8. Commit changes (Source Control)
9. Push to GitHub
```

---

## 🔧 Troubleshooting in VS Code

### Python Interpreter Not Found

1. `Ctrl+Shift+P` → "Python: Select Interpreter"
2. Choose: `.\\.venv\\Scripts\\python.exe` (Windows)
    or `./.venv/bin/python` (macOS/Linux)

### Copilot Not Working

1. `Ctrl+Shift+P` → "GitHub Copilot: Check Status"
2. Sign in if needed
3. Restart VS Code

### Import Errors

1. Check virtual environment is activated
2. Verify `PYTHONPATH` in settings.json
3. Run: `.\.venv\Scripts\python.exe -m pip install -r requirements.txt`

### Terminal Issues

1. Click trash icon to kill terminal
2. Open new terminal
3. Activate virtual environment

---

## 🎓 Learning Resources

### Ask Copilot These Questions

1. "Explain the three-tier routing strategy"
2. "How does offline mode work?"
3. "What's the best model for coding tasks?"
4. "How can I reduce memory usage?"
5. "Show me how to add a custom model"

### Use Copilot Chat for:

- Code explanations
- Debugging assistance
- Feature implementation
- Test writing
- Documentation generation
- Performance optimization

---

## ✅ Your Action Checklist

### Today (30 minutes)

- [ ] Open project in VS Code
- [ ] Copy all files to project folder
- [ ] Create `.vscode/` configuration files
- [ ] Install recommended extensions
- [ ] Create virtual environment
- [ ] Install dependencies: `.\.venv\Scripts\python.exe -m pip install -r requirements.txt`
- [ ] Run quick start: `.\quickstart.sh` (Windows PowerShell)

### This Week (2-3 hours)

- [ ] Download models for your platform
- [ ] Run example_integration.py
- [ ] Try CLI chat
- [ ] Debug with breakpoints
- [ ] Ask Copilot questions about the code
- [ ] Customize for your use case
- [ ] Deploy to your platform

---

## 🚀 Ready to Start!

**Open VS Code and run:**

```bash
# 1. Open project
code edge-llm-project

# 2. Open integrated terminal (Ctrl+`)
.\.venv\Scripts\Activate.ps1

# 3. Run setup
.\quickstart.sh

# 4. Start building!
.\.venv\Scripts\python.exe edge-llm-cli.py chat
```

**Ask Copilot anything along the way! It knows this codebase well.**

---

## 💬 Example Copilot Conversations

### Getting Started

**You:** "How do I use this LLM system in my own app?"

**Copilot will suggest:** Import and usage examples

### Customization

**You:** "Add a model that specializes in SQL queries"

**Copilot will suggest:** Configuration and routing changes

### Debugging

**You:** "Why is my model selection always choosing the cloud API?"

**Copilot will:** Analyze routing logic and suggest fixes

---

**Happy coding with VS Code + Copilot! 🎉**

Use Copilot as your pair programmer throughout deployment!
