# Configuration Reference

**Understanding the settings files that configure your project**

---

## Overview

Your VIF Trading System uses two main configuration files:

1. **`.vscode/settings.json`** — IDE settings (Cursor, Python, Antigravity)
2. **`.claude/settings.json`** — Claude Code permissions and auto-approvals

Both are located in your project root folder.

---

## `.vscode/settings.json` (IDE Configuration)

**Location**: `C:\Users\marti\vif-trading-system\.vscode\settings.json`

**What it does**: Configures how Cursor behaves, where Python lives, and how to format code.

### Key Settings

```json
{
  "python.venvPath": "C:\\Users\\marti\\vif-trading-system\\venv",
  "python.venvFolders": ["venv"],
  "python.terminal.activateEnvironment": true,
  "python.formatting.provider": "black",
  "[python]": {
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "ms-python.python"
  }
}
```

### What Each Setting Means

| Setting | Purpose | Your Value |
|---------|---------|-----------|
| `python.venvPath` | Where Python virtual environment is | Your venv folder path |
| `python.venvFolders` | Folder to search for venv | `["venv"]` |
| `python.terminal.activateEnvironment` | Auto-activate venv in terminal | `true` (recommended) |
| `python.formatting.provider` | Code formatter | `black` |
| `editor.formatOnSave` | Auto-format when saving | `true` |

### When to Modify

**Edit this file if:**
- Python interpreter is not detected automatically
- Virtual environment doesn't auto-activate in terminal
- You want different code formatting
- You're moving the project to a different path

**How to modify:**
1. Open in Cursor: `Ctrl+Shift+P` → "Preferences: Open Settings (JSON)"
2. Find the setting you want to change
3. Modify the value
4. Save: `Ctrl+S`
5. Changes apply immediately

### Example: Change Python Interpreter Path

If your Python is in a different location:

```json
"python.defaultInterpreterPath": "C:\\Users\\YourUsername\\AppData\\Local\\Programs\\Python\\Python314\\python.exe"
```

---

## `.claude/settings.json` (Claude Code Permissions)

**Location**: `C:\Users\marti\vif-trading-system\.claude\settings.json`

**What it does**: Controls what Claude Code can and cannot do (which tools it can use, which commands it can run).

### Key Settings

```json
{
  "bash": {
    "auto_approve": true,
    "allowed_commands": ["python", "git", "pip", "npm"]
  },
  "powershell": {
    "auto_approve": true
  },
  "tools": {
    "Read": {"auto_approve": true},
    "Write": {"auto_approve": true},
    "Edit": {"auto_approve": true},
    "Bash": {"auto_approve": true}
  }
}
```

### What Each Setting Means

| Setting | Purpose | Your Value |
|---------|---------|-----------|
| `bash.auto_approve` | Auto-approve bash commands | `true` |
| `bash.allowed_commands` | Which commands are allowed | `["python", "git", "pip", ...]` |
| `powershell.auto_approve` | Auto-approve PowerShell commands | `true` |
| `tools.*.auto_approve` | Auto-approve tool usage | `true` for all |

### When to Modify

**Edit this file if:**
- You want to restrict Claude Code's permissions
- You want to require approval for certain operations
- You're adding new allowed commands

**Security Note**: These settings are safe as configured. They allow Claude Code to help you work efficiently.

---

## How to Edit These Files

### Option 1: Via Cursor UI (Recommended)

```
Ctrl+Shift+P → Preferences: Open Settings (JSON)
```

This opens `.vscode/settings.json` for editing.

### Option 2: Via File Explorer

1. Open File Explorer
2. Navigate to project folder
3. Look for hidden folders (File → View → Show hidden items)
4. Open `.vscode` or `.claude` folder
5. Edit the `.json` file with Notepad or Cursor

### Option 3: Via Terminal

```bash
# Open .vscode/settings.json in Cursor
code .vscode/settings.json

# Open .claude/settings.json
notepad .claude/settings.json
```

---

## Common Customizations

### Enable Python Linting

Add to `.vscode/settings.json`:

```json
"python.linting.enabled": true,
"python.linting.pylintEnabled": true
```

Then install pylint:
```bash
pip install pylint
```

### Change Code Formatter

Change from Black to autopep8:

```json
"python.formatting.provider": "autopep8",
"[python]": {
  "editor.defaultFormatter": "ms-python.python"
}
```

### Auto-Format on Paste

Add to `.vscode/settings.json`:

```json
"editor.formatOnPaste": true
```

### Restrict Claude Code Permissions

In `.claude/settings.json`, change:

```json
"bash": {
  "auto_approve": false
}
```

Now Claude will ask before running bash commands.

---

## Virtual Environment Configuration

### Understanding the venv Path

Your `.vscode/settings.json` points to:
```json
"python.venvPath": "C:\\Users\\marti\\vif-trading-system\\venv"
```

This tells Cursor:
- Where your Python environment is located
- Which Python interpreter to use
- How to auto-activate in terminal

### If You Move the Project

If you move `vif-trading-system` to a different location:

1. Update the path in `.vscode/settings.json`:
   ```json
   "python.venvPath": "C:\\Users\\YourUsername\\NewLocation\\vif-trading-system\\venv"
   ```

2. Or delete `.vscode/settings.json` and let Cursor auto-detect:
   - Cursor will find `venv` automatically
   - May need to select interpreter: `Ctrl+Shift+P` → "Python: Select Interpreter"

---

## Environment Variables

### Setting via `.env` File

Create `.env` at project root:

```
ANTHROPIC_API_KEY=sk-ant-...
DEBUG=true
LOG_LEVEL=INFO
```

Access in Python:
```python
import os
api_key = os.getenv("ANTHROPIC_API_KEY")
```

### Setting via `.vscode/settings.json`

```json
"terminal.integrated.env.windows": {
  "MY_VAR": "value"
}
```

---

## Troubleshooting Configuration

### "Python interpreter not found"

**Solution:**
1. Open `.vscode/settings.json`
2. Verify `python.venvPath` points to correct location
3. Or delete that line and manually select interpreter:
   - `Ctrl+Shift+P` → "Python: Select Interpreter"
   - Choose `./venv/Scripts/python.exe`

### "Virtual environment not activating"

**Solution:**
1. Check `.vscode/settings.json` has:
   ```json
   "python.terminal.activateEnvironment": true
   ```
2. Close and reopen terminal
3. Or manually activate: `venv\Scripts\activate`

### "Claude Code not working"

**Solution:**
1. Check `.claude/settings.json` exists
2. Verify `auto_approve` settings are `true` for tools you're using
3. Reload Cursor: `Ctrl+Shift+P` → "Reload Window"

---

## Reset to Defaults

### Reset IDE Settings

Delete `.vscode/settings.json` and Cursor will recreate defaults:

```bash
del .vscode\settings.json
```

Then reload Cursor: `Ctrl+Shift+P` → "Reload Window"

### Reset Claude Code Permissions

Delete `.claude/settings.json` and recreate with defaults:

```bash
del .claude\settings.json
```

Then reload Cursor.

---

## Advanced: Custom Python Configuration

### Use Specific Python Version

If you have multiple Python versions, specify which one:

```json
"python.defaultInterpreterPath": "C:\\Python314\\python.exe"
```

### Disable Auto-Format

To manually format instead of auto-format:

```json
"[python]": {
  "editor.formatOnSave": false
}
```

Then manually format with: `Shift+Alt+F`

### Add Custom Python Path

```json
"python.analysis.extraPaths": [
  "${workspaceFolder}/agents",
  "${workspaceFolder}/utils"
]
```

This helps auto-completion find your modules.

---

## Quick Reference: Common Changes

| Need | Change In | What To Do |
|------|-----------|-----------|
| Python not detected | `.vscode/settings.json` | Add `python.defaultInterpreterPath` |
| venv not auto-activating | `.vscode/settings.json` | Set `python.terminal.activateEnvironment: true` |
| Format on save disabled | `.vscode/settings.json` | Set `editor.formatOnSave: true` |
| Require approval for commands | `.claude/settings.json` | Set `auto_approve: false` |
| Add new allowed command | `.claude/settings.json` | Add to `allowed_commands` array |

---

## 📞 Need Help?

- **Settings not working?** See [Troubleshooting Guide](04-troubleshooting.md)
- **Can't find the files?** Use `Ctrl+P` to search for `settings.json`
- **Want to reset?** See "Reset to Defaults" section above

---

## 🔗 Related Documentation

- **Cursor Setup**: [Cursor IDE Setup](01-cursor-desktop-setup.md)
- **Desktop Setup**: [Desktop Python Setup](02-desktop-python-setup.md)
- **Troubleshooting**: [Troubleshooting Guide](04-troubleshooting.md)

---

**Settings configured correctly! Your IDE is ready to work.** ✅
