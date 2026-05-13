# VS Code + Copilot Quick Start

## Start Here

This guide is optimized for your current setup:

- Windows
- VS Code + GitHub Copilot
- Python virtual environment at `.venv`

---

## 5-Minute Setup

### 1) Project folder

```bash
mkdir edge-llm-project
cd edge-llm-project
```

Copy all project files into this folder.

### 2) Run setup script

```bash
# Windows (PowerShell)
.\vscode-setup.sh

# macOS/Linux
# chmod +x vscode-setup.sh
# ./vscode-setup.sh
```

This configures `.vscode`, dependencies, and debug/tasks.

### 3) Open in VS Code

```bash
code edge-llm-project.code-workspace
# or
code .
```

### 4) Install recommended extensions

When prompted in VS Code, click **Install All**.

Recommended:

- Python
- Pylance
- GitHub Copilot
- GitHub Copilot Chat
- Error Lens

### 5) Download models and run chat

```bash
# Windows (PowerShell)
.\.venv\Scripts\python.exe download_models.py --platform desktop
.\.venv\Scripts\python.exe edge-llm-cli.py chat

# Optional platforms
.\.venv\Scripts\python.exe download_models.py --platform ios
.\.venv\Scripts\python.exe download_models.py --platform android
.\.venv\Scripts\python.exe download_models.py --platform web
```

If your terminal auto-activates `.venv`, plain `python ...` also works.

---

## Most Useful Shortcuts

| Shortcut | Action | Use |
| --- | --- | --- |
| `Ctrl+\`` | Toggle terminal | Open/close terminal |
| `F5` | Start debugging | Run launch config |
| `Ctrl+Shift+B` | Run task | Quick project actions |
| `Ctrl+Shift+I` | Copilot chat | Ask coding questions |
| `Ctrl+Shift+P` | Command palette | Find any command |

---

## Common Workflows

### Start chat

- `F5` and select **Start CLI Chat**
- or `Ctrl+Shift+B` and select **Start CLI Chat**
- or run in terminal:

```bash
.\.venv\Scripts\python.exe edge-llm-cli.py chat
```

### Run demo

```bash
.\.venv\Scripts\python.exe example_integration.py
```

### Download models

```bash
.\.venv\Scripts\python.exe download_models.py --platform desktop
```

### Run tests

```bash
.\.venv\Scripts\python.exe -m pytest test_edge_llm.py -v
```

### Check status

```bash
.\.venv\Scripts\python.exe edge-llm-cli.py status
```

---

## VS Code Workspace Shape

```text
edge-llm-project/
├── .vscode/
│   ├── settings.json
│   ├── launch.json
│   ├── tasks.json
│   └── extensions.json
├── .venv/
├── models/
├── llm_edge_router.py
├── download_models.py
├── example_integration.py
├── edge-llm-cli.py
├── test_edge_llm.py
├── requirements.txt
├── .env
└── *.md
```

---

## Deployment Direction

- Desktop quick test: use `--platform desktop`
- iOS/Android/Web: follow `STEP_BY_STEP_DEPLOYMENT.md`
- Decision help: `DEPLOYMENT_DECISION_GUIDE.md`

---

## Copilot Prompts You Can Paste

```text
Explain the routing logic in llm_edge_router.py with examples.
```

```text
Add a new model configuration optimized for summarization tasks.
```

```text
Write pytest tests for fallback behavior when cloud inference fails.
```

```text
Help me deploy this project for iOS and list the exact next steps.
```

---

## Troubleshooting

### Python interpreter not found

1. `Ctrl+Shift+P`
2. Run **Python: Select Interpreter**
3. Choose `.\.venv\Scripts\python.exe` (Windows)

### Module not found

- Ensure `.venv` is selected in VS Code
- Reinstall dependencies:

```bash
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Copilot not responding

1. `Ctrl+Shift+P`
2. Run **GitHub Copilot: Check Status**
3. Sign in again if needed

### Model download failed

- Check network and disk space
- Retry with smaller model
- Re-run the command

---

## Action Checklist

### Right now

- [ ] Open workspace in VS Code
- [ ] Confirm interpreter is `.venv`
- [ ] Download desktop models
- [ ] Start CLI chat

### This week

- [ ] Run tests
- [ ] Customize routing behavior
- [ ] Deploy to your target platform

---

## You Are Ready

Start here:

```bash
.\.venv\Scripts\python.exe edge-llm-cli.py chat
```

Then use `Ctrl+Shift+I` and ask Copilot to help build your first feature.
