# Desktop Python Setup

**Getting your Python environment and project ready on desktop**

**Updated**: 2026-04-30  
**Difficulty**: Beginner-Friendly  
**Time Required**: 30–45 minutes (depending on method)

---

## Overview: Two Methods

You have two ways to set up your VIF Trading System on desktop:

| Method | Difficulty | Time | Best For |
|--------|-----------|------|----------|
| **Method A: Simple Copy** | ⭐ Easy | 30 min | Novices, quick setup |
| **Method B: Git Method** | ⭐⭐ Medium | 45 min | Version control, syncing between machines |

**Recommendation**: Start with **Method A** if you're new to git. It's simpler and works great.

---

## Prerequisites (Both Methods)

Before starting, verify you have:

- [ ] **Python 3.14** installed on desktop
  - Check: Open Command Prompt, type `python --version`
  - Should show: `Python 3.14.x`
  - Download from: https://www.python.org/downloads/ (if needed)

- [ ] **Git installed** (only needed for Method B)
  - Check: `git --version`
  - Download from: https://git-scm.com/download/win (if needed)

- [ ] **Your API Key** from laptop
  - Find: `C:\Users\marti\vif-trading-system\.env`
  - Copy: The line `ANTHROPIC_API_KEY=sk-ant-...`

---

## Method A: Simple Copy (Recommended)

**Best for**: Quick setup without git knowledge

### Step 1: Copy Project Folder (5 minutes)

**On your laptop:**
1. Open File Explorer
2. Navigate to: `C:\Users\marti\vif-trading-system`
3. Right-click the folder
4. Click: **Copy**

**On your desktop:**
5. Open File Explorer
6. Navigate to: `C:\Users\YourUsername\` (or Desktop)
7. Right-click in empty space
8. Click: **Paste**

✅ **Result**: `vif-trading-system` folder now on your desktop

---

### Step 2: Open Command Prompt (1 minute)

1. Press: `Windows Key + R`
2. Type: `cmd`
3. Press: `Enter`

A black Command Prompt window opens.

---

### Step 3: Navigate to Project (1 minute)

In Command Prompt, type:

```bash
cd C:\Users\YourUsername\vif-trading-system
```

Replace `YourUsername` with your actual Windows username.

**Example:**
```bash
cd C:\Users\marti\vif-trading-system
```

✅ **Success**: Prompt shows: `C:\Users\marti\vif-trading-system>`

---

### Step 4: Create Virtual Environment (3 minutes)

In Command Prompt, type:

```bash
python -m venv venv
```

This creates a Python environment for this project (separate from system Python).

⏳ **Wait 1–2 minutes** while it installs.

✅ **Result**: New `venv` folder appears in your project directory.

---

### Step 5: Activate Virtual Environment (1 minute)

In Command Prompt, type:

```bash
venv\Scripts\activate
```

✅ **Success**: Prompt now shows: `(venv) C:\Users\marti\vif-trading-system>`

---

### Step 6: Install Dependencies (10 minutes)

In Command Prompt, type:

```bash
pip install -r requirements.txt
```

⏳ **Wait 5–10 minutes** while packages install (you'll see lots of text).

✅ **Success**: Message says something like:
```
Successfully installed anthropic-0.97.0 yfinance-1.0.0 ...
```

---

### Step 7: Add Your API Key (2 minutes)

**On your laptop:**
1. Open: `C:\Users\marti\vif-trading-system\.env`
2. Copy the line: `ANTHROPIC_API_KEY=sk-ant-...`

**On your desktop:**
3. In `vif-trading-system` folder, find: `.env.example`
4. Open with Notepad
5. Replace placeholder with your API key:
   ```
   ANTHROPIC_API_KEY=sk-ant-YOUR_ACTUAL_KEY_HERE
   ```
6. Save the file
7. **Rename** from `.env.example` to `.env`
   - Right-click → Rename
   - Change name to `.env` (remove `.example`)

✅ **Result**: You have a `.env` file with your API key

---

### Step 8: Verify Setup (3 minutes)

In Command Prompt (with `(venv)` active), type:

```bash
python tests/test_api_key.py
```

✅ **Success**: Should show:
```
SUCCESS: key valid, billing active.
```

If you see this, you're done with Method A! ✅

---

## Method B: Git Method (More Professional)

**Best for**: Version control and syncing between machines

### Step 1: Initialize Git on Laptop (2 minutes)

**On your laptop**, open Command Prompt in project folder:

```bash
cd C:\Users\marti\vif-trading-system
git init
git add .
git commit -m "Initial commit: VIF trading system setup"
```

✅ **Result**: Project is now a git repository

---

### Step 2: Create GitHub Repository (5 minutes)

1. Go to: https://github.com/new
2. Name it: `vif-trading-system`
3. **DO NOT** check "Initialize with README"
4. Click: **Create repository**
5. GitHub shows you commands to run

---

### Step 3: Push to GitHub (3 minutes)

**On your laptop**, in Command Prompt:

```bash
git remote add origin https://github.com/YOUR_USERNAME/vif-trading-system.git
git branch -M main
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub username.

✅ **Result**: Project backed up on GitHub

---

### Step 4: Clone on Desktop (10 minutes)

**On your desktop**, open Command Prompt:

```bash
cd C:\Users\YourUsername\
git clone https://github.com/YOUR_USERNAME/vif-trading-system.git
cd vif-trading-system
```

Replace `YOUR_USERNAME` with your GitHub username.

---

### Step 5: Complete Desktop Setup (15 minutes)

Now follow **Steps 4–8 from Method A**:
- Create virtual environment: `python -m venv venv`
- Activate: `venv\Scripts\activate`
- Install dependencies: `pip install -r requirements.txt`
- Add `.env` file with API key
- Verify: `python tests/test_api_key.py`

---

## Syncing Between Laptop & Desktop (Method B Only)

### After Making Changes on Laptop

```bash
cd C:\Users\marti\vif-trading-system
git add .
git commit -m "Description of changes"
git push
```

### On Desktop, Get Latest Changes

```bash
cd C:\Users\YourUsername\vif-trading-system
git pull
```

**Important**: Always commit changes before switching machines.

**DON'T commit these files** (git ignores them automatically):
- `.env` (API key — machine-specific)
- `venv/` (virtual environment — machine-specific)
- `logs/` (log files — machine-specific)
- `data/` (cache files — machine-specific)

These are local to each machine.

---

## ✅ Verification Checklist

After setup, verify:

- [ ] Project folder copied to desktop
- [ ] Virtual environment created (`venv` folder exists)
- [ ] Virtual environment activated (`(venv)` in prompt)
- [ ] Dependencies installed (no errors)
- [ ] `.env` file created with API key
- [ ] `python tests/test_api_key.py` shows SUCCESS
- [ ] `python scripts/check_usage.py` works

---

## 🚀 First Commands to Try

After setup is complete (with `(venv)` active):

```bash
# 1. Test API key
python tests/test_api_key.py

# 2. Check costs
python scripts/check_usage.py

# 3. Run watchlist analysis
python agents/watchlist_watcher.py --watchlist vantage_portfolio

# 4. Check installed packages
pip list | grep anthropic
```

All should work without errors!

---

## 📊 Essential Commands Reference

```bash
# Navigate to project
cd C:\Users\YourUsername\vif-trading-system

# Activate virtual environment
venv\Scripts\activate

# Deactivate virtual environment
deactivate

# Install dependencies
pip install -r requirements.txt

# Run a script
python agents/watchlist_watcher.py --watchlist vantage_portfolio

# Check costs
python scripts/check_usage.py

# Test API key
python tests/test_api_key.py

# Update from GitHub (Method B only)
git pull

# Commit changes (Method B only)
git add .
git commit -m "Description"
git push
```

---

## 📞 Troubleshooting

### "Python is not recognized"
**Cause**: Python not installed or not in PATH

**Solution**:
1. Download Python: https://www.python.org/downloads/
2. During installation, CHECK: "Add Python to PATH"
3. Restart Command Prompt
4. Try again

---

### "pip: command not found"
**Cause**: Virtual environment not activated

**Solution**:
- Make sure you see `(venv)` at start of prompt
- Type: `venv\Scripts\activate`
- Try again

---

### "No module named 'anthropic'"
**Cause**: Dependencies not installed

**Solution**:
1. Make sure `(venv)` is active
2. Run: `pip install -r requirements.txt`
3. Wait for completion
4. Try again

---

### "Your credit balance is too low"
**Cause**: API key issue or no credits

**Solution**:
1. Verify `.env` has correct API key
2. Check billing: https://console.anthropic.com/account/billing
3. Run: `python tests/test_api_key.py` to diagnose

---

### "File not found" or "Permission denied"
**Cause**: Wrong directory or path typo

**Solution**:
1. Check where you are: `cd` (shows current directory)
2. List files: `dir` (shows folder contents)
3. Use full paths if needed
4. Make sure virtual environment is activated

For more, see [Troubleshooting Guide](04-troubleshooting.md).

---

## 🔗 Next Steps

1. ✅ Python environment set up
2. 📖 Read: [Cursor IDE Setup](01-cursor-desktop-setup.md) (if not already done)
3. 🔧 Optional: Read [Configuration Reference](03-configuration-reference.md)
4. 🚀 Start using: `python agents/watchlist_watcher.py --watchlist vantage_portfolio`

---

## 📚 Related Documentation

- **Cursor Setup**: [Cursor IDE Setup](01-cursor-desktop-setup.md)
- **Settings Explained**: [Configuration Reference](03-configuration-reference.md)
- **More Issues**: [Troubleshooting Guide](04-troubleshooting.md)
- **Project Overview**: `CLAUDE.md` (in project root)

---

**Your desktop environment is ready!** 🎉
