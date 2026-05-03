# Troubleshooting Guide

**Solutions for common setup and runtime issues**

---

## Python & Virtual Environment Issues

### Problem: "Python is not recognized"

**What it means:**
- Python not installed, or
- Python not added to PATH, or
- You're using wrong Command Prompt

**Solutions:**

**Solution 1: Verify Python is installed**
```bash
python --version
```

If this fails:
1. Download Python: https://www.python.org/downloads/
2. **IMPORTANT**: During installation, CHECK "Add Python to PATH"
3. Restart Command Prompt completely (close and reopen)
4. Try again

**Solution 2: Use Windows PowerShell instead**
- Close Command Prompt
- Right-click desktop → "Windows PowerShell"
- Try: `python --version`

**Solution 3: Use full path to Python**
```bash
C:\Users\YourUsername\AppData\Local\Programs\Python\Python314\python.exe --version
```

---

### Problem: "pip: command not found"

**What it means:**
- Virtual environment not activated, or
- Python installation issue

**Solutions:**

**Solution 1: Activate virtual environment**
```bash
venv\Scripts\activate
```

Prompt should now show: `(venv) C:\...>`

Then try:
```bash
pip install -r requirements.txt
```

**Solution 2: Use Python to run pip**
```bash
python -m pip install -r requirements.txt
```

This works even if `pip` command doesn't.

**Solution 3: Reinstall virtual environment**
```bash
deactivate
rmdir /s venv
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

---

### Problem: "No module named 'anthropic'" (or other package)

**What it means:**
- Dependencies not installed, or
- Wrong Python interpreter being used

**Solutions:**

**Solution 1: Make sure venv is activated**
```bash
# Check for (venv) in prompt
# If not there, activate:
venv\Scripts\activate

# Then try importing
python -c "import anthropic; print(anthropic.__version__)"
```

**Solution 2: Reinstall dependencies**
```bash
# Activate venv first
venv\Scripts\activate

# Then install
pip install -r requirements.txt

# Wait for completion (watch for "Successfully installed...")
```

**Solution 3: Verify correct Python version**
```bash
python --version
# Should show: Python 3.14.x
```

If wrong version, create new venv with correct Python:
```bash
C:\Users\YourUsername\AppData\Local\Programs\Python\Python314\python.exe -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

---

### Problem: Virtual environment won't activate

**What it means:**
- Command syntax wrong, or
- PowerShell vs Command Prompt issue, or
- venv folder missing/corrupted

**Solutions:**

**Solution 1: Check you're in the right folder**
```bash
cd C:\Users\YourUsername\vif-trading-system
# Verify you see "venv" folder
dir
```

**Solution 2: Use correct activation command for your shell**

**For Command Prompt (cmd.exe):**
```bash
venv\Scripts\activate
```

**For PowerShell:**
```bash
venv\Scripts\Activate.ps1
```

**For Git Bash:**
```bash
source venv/Scripts/activate
```

**Solution 3: Recreate virtual environment**
```bash
# Delete old one
rmdir /s venv

# Create new one
python -m venv venv

# Activate
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## Cursor IDE Issues

### Problem: "Python extension not found" or "No Python found"

**What it means:**
- Python extension not installed, or
- Cursor can't find Python interpreter

**Solutions:**

**Solution 1: Install Python extension**
1. Press: `Ctrl+Shift+X` (Extensions)
2. Search: "Python"
3. Click "Install" next to "Python" by Microsoft
4. Reload Cursor: `Ctrl+Shift+P` → "Reload Window"

**Solution 2: Select Python interpreter manually**
1. Press: `Ctrl+Shift+P`
2. Type: "Python: Select Interpreter"
3. Choose: `./venv/Scripts/python.exe`
4. Cursor will use that Python

**Solution 3: Check `.vscode/settings.json`**
1. Press: `Ctrl+Shift+P` → "Preferences: Open Settings (JSON)"
2. Verify this line exists:
   ```json
   "python.venvPath": "C:\\Users\\marti\\vif-trading-system\\venv"
   ```
3. If missing, add it
4. Save and reload

---

### Problem: Terminal not activating virtual environment

**What it means:**
- Terminal launching without venv auto-activation
- Or activation command not running

**Solutions:**

**Solution 1: Check settings.json**
1. Press: `Ctrl+Shift+P` → "Preferences: Open Settings (JSON)"
2. Verify this line:
   ```json
   "python.terminal.activateEnvironment": true
   ```
3. If it says `false`, change to `true`
4. Save and reload Cursor

**Solution 2: Manually activate in terminal**
1. Open terminal: `Ctrl + `` (backtick)
2. Type: `venv\Scripts\activate`
3. Press: Enter
4. Prompt should now show: `(venv) C:\...>`

**Solution 3: Reset Cursor settings**
1. Close Cursor
2. Delete: `.vscode/settings.json`
3. Reopen Cursor
4. Cursor will use defaults
5. May need to manually select interpreter: `Ctrl+Shift+P` → "Python: Select Interpreter"

---

### Problem: "Claude Code not available" or "Antigravity not working"

**What it means:**
- Extensions not installed, or
- Cursor needs reload

**Solutions:**

**Solution 1: Reload Cursor**
1. Press: `Ctrl+Shift+P`
2. Type: "Reload Window"
3. Press: Enter

**Solution 2: Verify Claude Code extension**
1. Press: `Ctrl+Shift+X` (Extensions)
2. Search: "Claude Code"
3. Should see: "Claude Code" by Anthropic (installed)
4. If not, click "Install"
5. Reload Cursor

**Solution 3: Check Cursor is up to date**
1. Close Cursor completely
2. Open Cursor again
3. It may auto-update
4. Try again

**For Antigravity (native in Cursor):**
- Highlight any code
- Right-click
- Look for "Ask Antigravity" option
- If not there, try reloading: `Ctrl+Shift+P` → "Reload Window"

---

## API & Authentication Issues

### Problem: "Your credit balance is too low" or "Invalid API key"

**What it means:**
- API key wrong or expired, or
- No credits in Anthropic account

**Solutions:**

**Solution 1: Verify `.env` file**
1. Open: `.env` (in project root)
2. Check: Line is exactly like:
   ```
   ANTHROPIC_API_KEY=sk-ant-XXXXXXXXXXXX
   ```
3. Make sure no extra spaces or quotes
4. Save and try again

**Solution 2: Check your API key in Anthropic console**
1. Go to: https://console.anthropic.com/account/billing
2. Login with your account
3. Check: Credit balance (should be >$0)
4. Check: Your API key is valid
5. Copy fresh key if needed
6. Update `.env` file

**Solution 3: Test API key directly**
```bash
python tests/test_api_key.py
```

Should show:
```
SUCCESS: key valid, billing active.
```

If it doesn't, your API key or credits are the issue.

---

### Problem: "Connection timeout" or "API unreachable"

**What it means:**
- Network issue, or
- Anthropic API temporarily down, or
- Wrong API endpoint

**Solutions:**

**Solution 1: Check internet connection**
```bash
# Try connecting to Google
ping 8.8.8.8

# Or try visiting the API
curl https://api.anthropic.com
```

**Solution 2: Wait and retry**
- Anthropic API sometimes has brief outages
- Wait 5 minutes
- Try again: `python tests/test_api_key.py`

**Solution 3: Check firewall/VPN**
- Disable VPN temporarily
- Check firewall isn't blocking Anthropic API
- Try again

---

## File & Path Issues

### Problem: "File not found" or "No such file or directory"

**What it means:**
- Wrong path typed, or
- File doesn't exist, or
- You're in wrong directory

**Solutions:**

**Solution 1: Check current directory**
```bash
cd
# Shows where you are right now
```

**Solution 2: Navigate to project**
```bash
cd C:\Users\YourUsername\vif-trading-system
```

**Solution 3: List files to see what's available**
```bash
dir
# Lists all files in current folder
```

**Solution 4: Use full paths if needed**
```bash
python C:\Users\YourUsername\vif-trading-system\tests\test_api_key.py
```

---

### Problem: ".env file not found" or "API key not loading"

**What it means:**
- `.env` file doesn't exist, or
- Wrong location, or
- Wrong filename

**Solutions:**

**Solution 1: Check if `.env` exists**
```bash
# In project folder
dir | findstr .env
```

**Solution 2: Create `.env` file**
1. In project folder, find `.env.example`
2. Copy it: Right-click → Copy
3. Paste: Right-click → Paste → Paste as `.env`
4. Open `.env` with Notepad
5. Add your API key:
   ```
   ANTHROPIC_API_KEY=sk-ant-YOUR_KEY_HERE
   ```
6. Save

**Solution 3: Verify `.env` is in project root**
- File should be at: `C:\Users\YourUsername\vif-trading-system\.env`
- Not in subdirectories

---

## Script Execution Issues

### Problem: "Permission denied" when running Python scripts

**What it means:**
- File doesn't have execute permission, or
- Antivirus is blocking, or
- User doesn't have permission

**Solutions:**

**Solution 1: Use `python` command explicitly**
```bash
# Instead of:
agents/watchlist_watcher.py

# Use:
python agents/watchlist_watcher.py
```

**Solution 2: Check file exists and is readable**
```bash
# List the file
dir agents/watchlist_watcher.py

# Or use full path
python C:\Users\YourUsername\vif-trading-system\agents\watchlist_watcher.py
```

**Solution 3: Disable antivirus temporarily**
- Windows Defender or other antivirus may block Python
- Temporarily disable to test
- If it works, add Python/Cursor to antivirus exceptions

---

### Problem: Script runs but produces wrong output

**What it means:**
- Wrong Python interpreter being used, or
- Wrong working directory, or
- Outdated code

**Solutions:**

**Solution 1: Verify which Python is running**
```bash
python -c "import sys; print(sys.executable)"
# Should show your venv path
```

**Solution 2: Verify working directory**
```bash
cd C:\Users\YourUsername\vif-trading-system
# Make sure you're in project root
python agents/watchlist_watcher.py --watchlist vantage_portfolio
```

**Solution 3: Clear cache and reinstall**
```bash
# Remove cache
rmdir /s /q data/__pycache__

# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

---

## Windows-Specific Issues

### Problem: "Command not found" in PowerShell but works in Command Prompt

**What it means:**
- PowerShell has different syntax, or
- PATH settings different in PowerShell

**Solutions:**

**Solution 1: Use Command Prompt instead**
- Press: `Windows Key + R`
- Type: `cmd`
- Press: Enter
- Use Command Prompt for all commands

**Solution 2: Use correct PowerShell syntax**
```powershell
# PowerShell version of venv activation
venv\Scripts\Activate.ps1

# PowerShell version of Python
& python --version
```

**Solution 3: Update PowerShell execution policy**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## Getting Help

### If none of these solutions work:

1. **Try again from scratch**
   ```bash
   # Delete and recreate venv
   rmdir /s venv
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   python tests/test_api_key.py
   ```

2. **Check the other guides**
   - [Cursor IDE Setup](01-cursor-desktop-setup.md)
   - [Desktop Python Setup](02-desktop-python-setup.md)
   - [Configuration Reference](03-configuration-reference.md)

3. **Check project documentation**
   - `CLAUDE.md` (project overview)
   - `QUICK_START_USAGE_TRACKING.md` (for usage issues)

4. **Verify prerequisites**
   - Python 3.14+ installed
   - Git installed (if using Method B)
   - API key valid and has credits
   - Internet connection working

---

## Common Error Messages Decoded

| Error Message | Likely Cause | Solution |
|---------------|--------------|----------|
| `python: command not found` | Python not in PATH | Install Python, add to PATH, restart terminal |
| `ModuleNotFoundError: No module named 'anthropic'` | Dependencies not installed | `pip install -r requirements.txt` |
| `permission denied` | File permissions | Use `python script.py` instead of `./script.py` |
| `ANTHROPIC_API_KEY not set` | `.env` file missing or wrong | Create `.env` with your API key |
| `Connection refused` | Network/firewall issue | Check internet, disable VPN, check firewall |
| `invalid syntax` | Python code error | Check your edits, verify indentation |
| `FileNotFoundError: [Errno 2]` | Wrong file path | Check path, use full path, verify file exists |

---

**Still stuck?** Double-check the Prerequisites section in [Desktop Python Setup](02-desktop-python-setup.md). Most issues come from missing Python, wrong PATH, or no API key.

💪 You can fix this!
