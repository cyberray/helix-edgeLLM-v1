# 🎨 VS Code Command Reference Card

## ⌨️ Essential Keyboard Shortcuts

### General
| Shortcut | Action | Use For |
|----------|--------|---------|
| `Ctrl+Shift+P` | Command Palette | Access any VS Code command |
| `Ctrl+P` | Quick Open | Open files quickly |
| `Ctrl+,` | Settings | Configure VS Code |
| `Ctrl+B` | Toggle Sidebar | More screen space |
| `Ctrl+J` | Toggle Panel | Show/hide terminal/output |

### Terminal
| Shortcut | Action | Use For |
|----------|--------|---------|
| **`Ctrl+` `** | **Toggle Terminal** | **Most used!** |
| `Ctrl+Shift+` ` | New Terminal | Multiple terminals |
| `Ctrl+Shift+5` | Split Terminal | Side-by-side terminals |
| `Alt+Up/Down` | Switch Terminal | Between terminals |

### Coding
| Shortcut | Action | Use For |
|----------|--------|---------|
| `F5` | **Start Debugging** | **Run your code** |
| `Ctrl+Shift+B` | **Run Task** | **Quick commands** |
| `Ctrl+/` | Toggle Comment | Comment code |
| `Alt+Up/Down` | Move Line | Reorder code |
| `Ctrl+D` | Select Next | Multi-cursor editing |
| `Ctrl+Shift+L` | Select All Occurrences | Rename all |

### GitHub Copilot
| Shortcut | Action | Use For |
|----------|--------|---------|
| **`Ctrl+Shift+I`** | **Copilot Chat** | **Ask questions** |
| `Tab` | Accept Suggestion | Accept Copilot code |
| `Alt+\` | Trigger Copilot | Manual trigger |
| `Alt+]` | Next Suggestion | Cycle suggestions |
| `Alt+[` | Previous Suggestion | Go back |

### Navigation
| Shortcut | Action | Use For |
|----------|--------|---------|
| `Ctrl+Shift+G` | Source Control | Git operations |
| `Ctrl+Shift+E` | Explorer | File browser |
| `Ctrl+Shift+F` | Search | Find in files |
| `Ctrl+Shift+X` | Extensions | Manage extensions |
| `F12` | Go to Definition | Jump to code |

---

## 🚀 Quick Commands (Ctrl+Shift+P)

### Python
```
> Python: Select Interpreter     # Choose venv
> Python: Run Python File        # Run current file
> Python: Create Terminal        # Python terminal
```

### Tasks
```
> Tasks: Run Task                # See all tasks
> Tasks: Run Build Task          # Default task (Ctrl+Shift+B)
```

### Git
```
> Git: Commit                    # Commit changes
> Git: Push                      # Push to remote
> Git: Pull                      # Pull from remote
```

### Copilot
```
> GitHub Copilot: Open Chat      # Chat panel
> GitHub Copilot: Explain This   # Explain selected code
> GitHub Copilot: Fix This       # Fix errors
> GitHub Copilot: Generate Tests # Create tests
```

---

## 🎯 Common Workflows

### 1. First Time Setup
```
1. Open project: code .
2. Install extensions (prompt appears)
3. Select Python interpreter: Ctrl+Shift+P → "Python: Select Interpreter"
4. Open terminal: Ctrl+`
5. Activate venv: .\.venv\Scripts\Activate.ps1
6. You're ready!
```

### 2. Daily Development
```
1. Open VS Code: code .
2. Open terminal: Ctrl+`
3. Activate venv (automatic if configured)
4. Start coding!
5. Run with F5 or Ctrl+Shift+B
```

### 3. Running Tasks
```
Method 1: Ctrl+Shift+B → Select task
Method 2: Ctrl+Shift+P → "Tasks: Run Task"
Method 3: Terminal → Run command directly
```

### 4. Using Copilot
```
1. Type comment: # Create a function that...
2. Press Enter
3. Tab to accept suggestion
4. Or Ctrl+Shift+I to ask in chat
```

### 5. Debugging
```
1. Set breakpoint: Click left of line number
2. Press F5
3. Select configuration (first time)
4. Use debug toolbar (step over, into, out)
5. Check variables in debug panel
```

---

## 📋 Project-Specific Tasks

### Available Tasks (Ctrl+Shift+B)

| Task | What It Does |
|------|-------------|
| **Quick Start** | Automated setup |
| Install Dependencies | .\.venv\Scripts\python.exe -m pip install -r requirements.txt |
| Download Models: Desktop | Download for testing |
| Download Models: iOS | Download for iOS |
| Download Models: Android | Download for Android |
| Start CLI Chat | .\.venv\Scripts\python.exe edge-llm-cli.py chat |
| Run All Tests | pytest test suite |
| Run Benchmarks | Performance tests |
| Show System Status | Check configuration |

### Debug Configurations (F5)

| Configuration | What It Runs |
|--------------|-------------|
| 🚀 Run Demo | example_integration.py |
| 💬 CLI Chat | Interactive chat mode |
| 📦 Download Models | Model downloader |
| 🧪 Run Tests | Full test suite |
| 📄 Current File | Whatever file is open |

---

## 💡 Pro Tips

### Tip 1: Multi-Terminal Layout
```
1. Ctrl+` to open terminal
2. Click "+" for new terminal
3. Drag tabs to split terminals
4. Use one for: venv, another for: git, another for: testing
```

### Tip 2: Quick File Navigation
```
Ctrl+P → Type filename → Enter
Example: Ctrl+P → "router" → Opens llm_edge_router.py
```

### Tip 3: Search & Replace in Files
```
Ctrl+Shift+F → Enter search
Ctrl+Shift+H → Search and replace
Scope to folders with "files to include"
```

### Tip 4: Git in VS Code
```
Ctrl+Shift+G → Source Control
Click "+" to stage changes
Type commit message
Click ✓ to commit
Click "..." → Push
```

### Tip 5: Use Copilot Chat
```
Ctrl+Shift+I → Ask anything:
- "How do I use this router?"
- "Explain this error"
- "Write tests for this function"
- "Optimize this code"
```

---

## 🎨 Customization

### Open Settings
```
File → Preferences → Settings
Or: Ctrl+,
Or: Ctrl+Shift+P → "Preferences: Open Settings"
```

### Useful Settings to Customize
```json
{
    "editor.fontSize": 14,
    "terminal.integrated.fontSize": 13,
    "editor.minimap.enabled": false,
    "workbench.colorTheme": "your-theme",
    "python.defaultInterpreterPath": ".\\.venv\\Scripts\\python.exe"
}
```

### Create Custom Shortcuts
```
File → Preferences → Keyboard Shortcuts
Or: Ctrl+K Ctrl+S
Search for command → Click "+" to add keybinding
```

---

## 🔧 Troubleshooting

### Terminal Won't Activate venv
```
Solution: Ctrl+Shift+P → "Python: Select Interpreter" → Choose venv
Or: Reload window (Ctrl+R)
```

### Import Errors
```
Solution 1: Check interpreter is venv (bottom left)
Solution 2: Ctrl+Shift+P → "Python: Select Interpreter"
Solution 3: Restart VS Code
```

### Copilot Not Working
```
Solution 1: Ctrl+Shift+P → "GitHub Copilot: Check Status"
Solution 2: Sign out and sign in
Solution 3: Restart VS Code
```

### Debugger Won't Start
```
Solution 1: Check launch.json exists
Solution 2: Verify Python interpreter
Solution 3: Check file is saved
```

---

## 📚 Copilot Prompts Library

### For This Project

**Understanding the System:**
```
"Explain the LLMEdgeRouter class architecture"
"How does the routing decision logic work?"
"What's the difference between local and cloud tiers?"
```

**Customization:**
```
"Add a new model configuration for Mistral 7B"
"Modify routing to prefer Qwen for Python code"
"Create a function to benchmark all models"
```

**Debugging:**
```
"Why isn't my model being selected?"
"Fix this import error"
"Optimize this function for memory usage"
```

**Feature Development:**
```
"Add streaming support to the generate function"
"Create an API endpoint for this router"
"Write tests for the offline mode"
```

**Documentation:**
```
"Generate docstrings for this class"
"Create a README section for this feature"
"Write a tutorial for using the router"
```

---

## 🎯 Quick Reference Table

| Want to... | Do this... |
|------------|-----------|
| Open terminal | `Ctrl+` ` |
| Run code | `F5` |
| Run task | `Ctrl+Shift+B` |
| Ask Copilot | `Ctrl+Shift+I` |
| Find file | `Ctrl+P` |
| Find in files | `Ctrl+Shift+F` |
| Git operations | `Ctrl+Shift+G` |
| Run command | `Ctrl+Shift+P` |
| Debug | `F5` |
| Comment code | `Ctrl+/` |
| Save all | `Ctrl+K S` |
| Close file | `Ctrl+W` |
| Split editor | `Ctrl+\` |
| Toggle sidebar | `Ctrl+B` |

---

## 🚀 Common Command Sequences

### Setup Sequence
```
1. code .                                                   # Open VS Code
2. Ctrl+`                                                   # Open terminal
3. .\.venv\Scripts\Activate.ps1                           # Activate venv
4. .\.venv\Scripts\python.exe download_models.py --platform desktop
5. F5 → Run Demo                                           # Test it
```

### Development Sequence
```
1. Ctrl+P → filename               # Open file
2. Edit code
3. Ctrl+S                          # Save
4. F5                              # Run/Debug
5. Fix issues
6. Ctrl+Shift+G                    # Git commit
```

### Testing Sequence
```
1. Ctrl+Shift+B → Run Tests        # Run tests
2. Check output
3. Fix failures
4. Ctrl+Shift+B → Run Tests        # Re-run
5. Commit when green
```

---

## 💾 Save This Reference!

**Print or bookmark this page for quick access.**

**For more details, see:**
- VSCODE_COPILOT_GUIDE.md - Full VS Code guide
- QUICK_REFERENCE.md - Python API reference
- STEP_BY_STEP_DEPLOYMENT.md - Deployment steps

---

**Happy coding in VS Code! 🎉**

_Pro tip: Keep this reference open in a split editor while you code!_
