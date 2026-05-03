# 🛠️ IDE Setup Guide - Cursor on Desktop

**For VIF Trading System - Running Cursor Identically on Desktop**

**Updated**: 2026-04-30  
**IDE**: Cursor (VS Code based)  
**Difficulty**: Beginner-Friendly

---

## Quick Answer: Cursor Setup Flow

When Cursor asks you to choose a setup flow, here's what to select:

### **Choose: "Import from VS Code"** ⭐ (Recommended)

**Why?**
- Your laptop has VS Code with your project settings
- This will copy all your extensions, settings, and keybindings
- Fastest way to replicate your laptop environment
- Takes 2 minutes, copies everything automatically

**If you don't have VS Code on laptop:**
- Choose "Import Fresh"
- Manually configure settings (see below)

---

## Step-by-Step Cursor Setup

### Step 1: Cursor Setup Flow (When You First Launch)

**Screen 1: Choose Setup Flow**
```
○ Import from VS Code (CHOOSE THIS)
○ Import from Cursor
○ Import Fresh
```

**Select**: "Import from VS Code" → Click **Next**

**What it does**: 
- Copies all VS Code settings, extensions, keybindings
- Brings over your project configuration
- Syncs your preferences from laptop

⏳ **Wait 1–2 minutes** while Cursor imports settings.

✅ **Success**: Cursor restarts with your settings applied.

---

### Step 2: Verify Project is Loaded

After Cursor opens:

1. **Check the File Explorer** (left side)
   - You should see your `vif-trading-system` folder
   - All files visible (agents/, config/, scripts/, etc.)

2. **Open a Terminal**
   - Press: `Ctrl + `` (backtick)
   - Terminal opens at bottom of screen

3. **Verify Python & Virtual Environment**
   ```bash
   python --version
   # Should show: Python 3.14.x
   
   venv\Scripts\activate
   # Terminal should show: (venv) prompt
   ```

✅ **Success**: Python and venv are working.

---

### Step 3: IDE Configuration Files to Understand

Your project has special IDE configuration files:

#### **File 1: .vscode/settings.json** (Your Custom Settings)

This file configures:
- ✅ Python virtual environment path
- ✅ Python formatter settings
- ✅ Antigravity (Cursor AI) settings
- ✅ Terminal integration
- ✅ UTF-8 encoding for Python

**What was imported from laptop:**
- All these settings were copied when you chose "Import from VS Code"

**If settings didn't import, manually copy:**
1. Open on laptop: `.vscode/settings.json`
2. Copy the entire content
3. On desktop in Cursor: 
   - Press `Ctrl+Shift+P`
   - Type: "Preferences: Open Settings (JSON)"
   - Paste the settings

#### **File 2: .claude/settings.json** (Claude Code Permissions)

This file configures:
- ✅ What bash commands are allowed (python, git, npm, etc.)
- ✅ Which tools Claude can use (Read, Write, Edit, etc.)
- ✅ Auto-approval settings for file changes

**Location**: `.claude/settings.json` in your project root

**You don't need to do anything** - this file is already in your project and will work automatically.

---

### Step 4: Check Extensions

**Cursor should have installed:**

- ✅ **Cursor** (built-in, comes with Cursor)
- ✅ **Python** (Microsoft) - auto-installed
- ✅ **Claude Code** (Anthropic) - imported from VS Code

**To verify:**

1. Press: `Ctrl+Shift+X` (Extensions panel)
2. Look for:
   - ✅ "Python" by Microsoft
   - ✅ "Claude Code" by Anthropic (if missing, search and install)

**If Claude Code is missing:**
```
1. Search: "Claude Code" in Extensions
2. Click: Install
3. Restart Cursor
```

---

## What's Configured in Your Project

### Python Environment

Your project settings automatically configure:

- ✅ **Python Interpreter**: Points to your venv
- ✅ **Venv Location**: `C:\Users\marti\vif-trading-system\venv`
- ✅ **Terminal Activation**: Automatically activates venv in terminal
- ✅ **Auto-completion**: Knows about all installed packages
- ✅ **Formatting**: Python files auto-format on save

### Cursor (Antigravity) Settings

Your project settings automatically configure:

- ✅ **Workspace Trust**: Enabled (so Cursor works without security warnings)
- ✅ **Auto-approve File Edits**: Yes (so Cursor can modify files)
- ✅ **Auto-approve Commands**: Yes (so Cursor can run Python scripts)

### Claude Code Settings

Your project settings define:

- ✅ **Allowed Commands**: Python, Git, pip, PowerShell
- ✅ **Allowed Tools**: Read, Write, Edit, Bash
- ✅ **Auto-approval**: Set for efficiency

---

## Verification Checklist

After Cursor setup, verify everything works:

### ✅ Python Environment

```bash
# In Cursor terminal
python --version        # Should show Python 3.14.x
pip list               # Should show your packages
```

### ✅ Virtual Environment

```bash
venv\Scripts\activate  # Should activate without error
deactivate            # Should deactivate
```

### ✅ Project Access

```bash
# In terminal, all these should work:
python agents/watchlist_watcher.py --watchlist vantage_portfolio
python scripts/check_usage.py
python tests/test_api_key.py
```

### ✅ Claude Code Integration

1. Open any Python file (e.g., `agents/watchlist_watcher.py`)
2. Press: `Ctrl+Shift+P`
3. Type: "Claude Code: Open Chat"
4. Chat panel should open on right side

✅ **All checks pass?** You're ready!

---

## IDE Features You Get

With Cursor + Claude Code on desktop, you have:

### 🤖 **AI-Powered Coding**
- Natural language to code generation
- Code completion with AI context
- Refactoring suggestions
- Bug detection and fixes

### 🔧 **Python Tools**
- Syntax highlighting
- Auto-completion
- Debugging
- Testing integration
- Linting (if you add)

### 💬 **Claude Code Integration**
- Chat with Claude about your code
- Ask questions about VIF framework
- Generate documentation
- Refactor code with AI guidance
- Explain existing code

### 📁 **Project Navigation**
- File search (`Ctrl+P`)
- Symbol search (`Ctrl+Shift+O`)
- Workspace overview

### 🖥️ **Terminal Integration**
- Integrated terminal with Python ready
- venv auto-activated
- Run scripts directly from Cursor
- No need to open separate Command Prompt

---

## Keyboard Shortcuts (Cursor/VS Code Standard)

| Action | Shortcut |
|--------|----------|
| Command Palette | `Ctrl+Shift+P` |
| File Search | `Ctrl+P` |
| Symbol Search | `Ctrl+Shift+O` |
| Terminal | `Ctrl+`` (backtick) |
| Claude Code Chat | `Ctrl+K` |
| Find in File | `Ctrl+F` |
| Find & Replace | `Ctrl+H` |
| Format Document | `Shift+Alt+F` |
| Go to Definition | `F12` |
| Rename Symbol | `F2` |

---

## Troubleshooting IDE Setup

### Problem: Python Extension Shows "No Python Found"

**Solution:**
1. Press: `Ctrl+Shift+P`
2. Type: "Python: Select Interpreter"
3. Choose: `./venv/Scripts/python.exe`
4. Terminal should activate venv automatically

### Problem: Claude Code Not Available

**Solution:**
1. Open Extensions (`Ctrl+Shift+X`)
2. Search: "Claude Code"
3. Install from Anthropic
4. Reload Cursor

### Problem: Terminal Not Activating Virtual Environment

**Solution:**
```bash
# Manually activate in terminal
venv\Scripts\activate

# Or check settings:
# Ctrl+Shift+P → Preferences: Open Settings (JSON)
# Ensure: "python.terminal.activateEnvironment": true
```

### Problem: Can't Run Python Scripts

**Solution:**
1. Verify venv is activated (see `(venv)` in terminal)
2. Run: `python agents/watchlist_watcher.py --help`
3. If it fails, check Python path:
   ```bash
   which python
   # Should show: C:\Users\marti\vif-trading-system\venv\Scripts\python.exe
   ```

---

## Syncing Settings Between Laptop & Desktop

If you update VS Code settings on laptop, here's how to sync to desktop:

### **Easy Way: Use VS Code Cloud Sync** (Recommended)

1. **On Laptop**:
   - Sign in to VS Code (click icon, top right)
   - Account: Microsoft or GitHub
   - Settings auto-sync

2. **On Desktop**:
   - Open Cursor
   - Sign in with same account
   - Settings auto-sync within 1 minute

### **Manual Way: Copy Settings File**

1. **On Laptop**:
   ```
   Copy: C:\Users\marti\vif-trading-system\.vscode\settings.json
   ```

2. **On Desktop**:
   ```
   Paste: C:\Users\YourUsername\vif-trading-system\.vscode\settings.json
   Restart Cursor
   ```

---

## Your IDE is Ready!

✅ **You now have**:
- Cursor installed and configured
- Python environment detected and working
- Claude Code integrated for AI assistance
- All project settings synchronized
- Keyboard shortcuts ready
- Terminal with venv auto-activated

**Next steps:**
1. Open a Python file in your project
2. Press `Ctrl+K` to chat with Claude Code
3. Start asking Claude to help with your code!

---

## Quick Reference: First 5 Commands

After Cursor is set up, try these to verify everything works:

```bash
# 1. Activate virtual environment (if not auto-activated)
venv\Scripts\activate

# 2. Check Python version
python --version

# 3. Check installed packages
pip list | grep anthropic

# 4. Run your first analysis
python tests/test_api_key.py

# 5. Check your costs
python scripts/check_usage.py
```

All should work without errors!

---

## Related Documentation

- **Project Architecture**: See `CLAUDE.md`
- **Usage Tracking**: See `QUICK_START_USAGE_TRACKING.md`
- **Desktop Python Setup**: See `DESKTOP_SETUP_GUIDE.md`

---

**You're all set! Your desktop IDE is ready.** 🚀

For Cursor help, see: https://www.cursor.sh/docs
