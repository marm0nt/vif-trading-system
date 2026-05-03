# 🖥️ VIF Trading System - Desktop Setup Guide

**For Novice Users: Setting Up On Your Desktop**

**Last Updated**: 2026-04-30  
**Difficulty**: Beginner-Friendly  
**Time Required**: 30 minutes

---

## Table of Contents

1. [Quick Overview](#quick-overview)
2. [Prerequisites](#prerequisites)
3. [Method A: Simple Copy (Recommended)](#method-a-simple-copy-recommended)
4. [Method B: Git Method (More Professional)](#method-b-git-method-more-professional)
5. [Syncing Between Laptop & Desktop](#syncing-between-laptop--desktop)
6. [Troubleshooting](#troubleshooting)

---

## Quick Overview

You want to run the same VIF trading system on your desktop that you currently run on your laptop. 

**Two ways to do this:**

| Method | Difficulty | Setup Time | Best For |
|--------|-----------|-----------|----------|
| **A: Simple Copy** | ⭐ Easy | 15 min | Novices, quick setup |
| **B: Git Method** | ⭐⭐ Medium | 30 min | Professional setup, syncing |

**Recommendation**: Start with **Method A** (simple copy). It's the easiest and works great.

---

## Prerequisites

Before you start, make sure you have:

### On Your Desktop:

- [ ] **Python 3.14** installed
  - Download from: https://www.python.org/downloads/
  - ✅ Check: Open Command Prompt, type `python --version`
  - Should show: `Python 3.14.x`

- [ ] **Git** installed (only needed for Method B)
  - Download from: https://git-scm.com/download/win
  - ✅ Check: Open Command Prompt, type `git --version`

- [ ] **Your API Key** from `.env` file on laptop
  - You'll need: `ANTHROPIC_API_KEY=sk-ant-...`

---

## Method A: Simple Copy (Recommended)

**Best for**: Getting up and running quickly without git knowledge

### Step 1: Copy the Project Folder (5 minutes)

**On your laptop:**

1. Open File Explorer
2. Navigate to: `C:\Users\marti\vif-trading-system`
3. Right-click on the `vif-trading-system` folder
4. Click: **Copy**

**On your desktop:**

5. Open File Explorer
6. Navigate to your desired location (e.g., `C:\Users\YourUsername\`)
   - Or desktop itself (not recommended long-term)
7. Right-click in the empty space
8. Click: **Paste**

✅ **Result**: You now have a `vif-trading-system` folder on your desktop with all files

---

### Step 2: Open Command Prompt (1 minute)

On your desktop:

1. Press: `Windows Key + R`
2. Type: `cmd`
3. Press: `Enter`

A black Command Prompt window opens.

---

### Step 3: Navigate to Your Project (1 minute)

In Command Prompt, type:

```bash
cd C:\Users\YourUsername\vif-trading-system
```

**Replace `YourUsername`** with your actual Windows username.

**Example:**
```bash
cd C:\Users\marti\vif-trading-system
```

✅ **Success**: You should see the path in the prompt like:
```
C:\Users\marti\vif-trading-system>
```

---

### Step 4: Create a Virtual Environment (3 minutes)

In Command Prompt, type:

```bash
python -m venv venv
```

This creates a new Python environment for this project (separate from your system Python).

⏳ **Wait 1–2 minutes** while it installs.

✅ **Success**: A new folder called `venv` appears in your project folder.

---

### Step 5: Activate the Virtual Environment (1 minute)

In Command Prompt, type:

```bash
venv\Scripts\activate
```

✅ **Success**: The prompt changes to show `(venv)` at the start:
```
(venv) C:\Users\marti\vif-trading-system>
```

---

### Step 6: Install Dependencies (10 minutes)

In Command Prompt, type:

```bash
pip install -r requirements.txt
```

⏳ **Wait 5–10 minutes** while packages install. You'll see lots of text scrolling.

✅ **Success**: Message says something like:
```
Successfully installed anthropic-0.97.0 yfinance-1.0.0 ...
```

---

### Step 7: Add Your API Key (2 minutes)

**On your laptop:**

1. Open the `.env` file (in `C:\Users\marti\vif-trading-system\`)
2. Copy the line: `ANTHROPIC_API_KEY=sk-ant-...`

**On your desktop:**

3. In the `vif-trading-system` folder, find the `.env.example` file
4. Open it with Notepad
5. Replace the placeholder with your actual key:
   ```
   ANTHROPIC_API_KEY=sk-ant-YOUR_KEY_HERE
   ```
6. Save it
7. **Rename** from `.env.example` to `.env`
   - Right-click → Rename
   - Change name from ``.env.example`` to ``.env``

✅ **Success**: You now have a `.env` file with your API key

---

### Step 8: Verify Setup (3 minutes)

In Command Prompt (still with `(venv)` active), type:

```bash
python tests/test_api_key.py
```

✅ **Success**: You should see:
```
SUCCESS: key valid, billing active.
```

If you see this, you're done! Your desktop setup works.

---

## Method B: Git Method (More Professional)

**Best for**: Syncing between multiple machines, version control

### Step 1: Initialize Git on Your Laptop (2 minutes)

**On your laptop**, open Command Prompt in the project folder:

```bash
cd C:\Users\marti\vif-trading-system
git init
git add .
git commit -m "Initial commit: VIF trading system setup"
```

✅ **Result**: Your project is now a git repository locally.

---

### Step 2: Create a GitHub Repository (5 minutes)

1. Go to: https://github.com/new
2. Create a repository named: `vif-trading-system`
3. **DO NOT** initialize with README (you already have one)
4. Click: **Create repository**
5. GitHub shows you commands to run

---

### Step 3: Push to GitHub (3 minutes)

**On your laptop**, in Command Prompt in the project folder:

```bash
git remote add origin https://github.com/YOUR_USERNAME/vif-trading-system.git
git branch -M main
git push -u origin main
```

**Replace `YOUR_USERNAME`** with your GitHub username.

✅ **Result**: Your project is now on GitHub as a backup.

---

### Step 4: Clone on Your Desktop (10 minutes)

**On your desktop**, open Command Prompt:

```bash
cd C:\Users\YourUsername\
git clone https://github.com/YOUR_USERNAME/vif-trading-system.git
cd vif-trading-system
```

**Replace `YOUR_USERNAME`** with your GitHub username.

---

### Step 5: Set Up Desktop Environment (as in Method A)

Follow **Steps 4–8** from Method A:
- Create virtual environment
- Activate it
- Install dependencies
- Add `.env` file
- Verify setup

---

## Syncing Between Laptop & Desktop

### After You Make Changes on Laptop:

```bash
cd C:\Users\marti\vif-trading-system
git add .
git commit -m "Description of changes"
git push
```

### On Desktop, Update to Latest:

```bash
cd C:\Users\YourUsername\vif-trading-system
git pull
```

⚠️ **Important**: Always commit your changes before switching machines.

**DON'T commit these files** (git will ignore them automatically):
- `.env` (API key)
- `venv/` (virtual environment)
- `logs/` (log files)
- `data/` (cache files)

These are machine-specific and shouldn't be shared.

---

## Troubleshooting

### Problem: "Python is not recognized"

**Cause**: Python not installed or not added to PATH

**Solution**:
1. Download Python from: https://www.python.org/downloads/
2. During installation, **CHECK the box**: "Add Python to PATH"
3. Restart Command Prompt
4. Try again

---

### Problem: "pip: command not found"

**Cause**: Python not properly installed

**Solution**:
```bash
python -m pip install -r requirements.txt
```

Use `python -m pip` instead of just `pip`.

---

### Problem: "No module named 'anthropic'"

**Cause**: Virtual environment not activated

**Solution**:
1. Make sure you see `(venv)` at the start of the prompt
2. If not, type: `venv\Scripts\activate`
3. Then try running your script again

---

### Problem: "Your credit balance is too low"

**Cause**: API key issue or account out of credits

**Solution**:
1. Verify `.env` file has correct API key
2. Check Anthropic billing: https://console.anthropic.com/account/billing
3. Run: `python tests/test_api_key.py` to diagnose

---

### Problem: File paths not working

**Cause**: Wrong file path or wrong current directory

**Solution**:
1. Always use full paths or navigate to the correct folder first
2. Check current location with: `cd` (shows current directory)
3. List files with: `dir` (shows what's in current folder)

---

## Quick Reference: Essential Commands

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

# Update from git (Method B only)
git pull

# Commit changes (Method B only)
git add .
git commit -m "Description"
git push
```

---

## Checklist: Desktop Setup Complete

After completing either method, verify:

- [ ] Project folder copied to desktop
- [ ] Virtual environment created (`venv` folder exists)
- [ ] Virtual environment activated (you see `(venv)` in prompt)
- [ ] Dependencies installed (no errors when running `pip install`)
- [ ] `.env` file created with API key
- [ ] `python tests/test_api_key.py` succeeds
- [ ] `python scripts/check_usage.py` works

✅ **All checks pass?** You're ready to use your system on desktop!

---

## Running Your System on Desktop

Now that setup is complete, you can run:

```bash
# Make sure you're in the project folder with (venv) active

# Run watchlist analysis
python agents/watchlist_watcher.py --watchlist vantage_portfolio

# Check costs
python scripts/check_usage.py

# Run full scheduler
python schedule_daily.py
```

Everything works the same as on your laptop!

---

## Important Notes

### Virtual Environment

- **Each machine needs its own** `venv` folder
- Don't copy the `venv` folder between machines
- Always create a fresh one: `python -m venv venv`
- Takes 1–2 minutes to create, so no big deal

### API Key

- **Never commit `.env` to git** (it contains secrets)
- Create a new `.env` file on each machine
- Copy the key from your laptop's `.env`

### Data Sync

- Cache files (`data/`) and logs are machine-specific
- Reports (`reports/`) can be shared if you use git
- Don't worry about syncing temporary files

---

## Next Steps

1. **Choose your method** (A or B)
2. **Follow the steps** in order
3. **Test with**: `python tests/test_api_key.py`
4. **Start analyzing**: `python agents/watchlist_watcher.py --watchlist vantage_portfolio`

You're all set! 🚀

---

## Need Help?

| Issue | Read |
|-------|------|
| Python installation | [Python Docs](https://docs.python.org/3/using/windows.html) |
| Virtual environments | [Official Guide](https://docs.python.org/3/tutorial/venv.html) |
| Git basics | [Git Docs](https://git-scm.com/doc) |
| VIF system usage | [QUICK_START_USAGE_TRACKING.md](./QUICK_START_USAGE_TRACKING.md) |

---

**Good luck with your desktop setup!** Feel free to reach out if you hit any issues. 💪
