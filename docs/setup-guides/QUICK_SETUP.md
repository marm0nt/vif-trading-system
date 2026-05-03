# Quick Setup: Laptop to Desktop (Import Fresh)

**Copy your VIF Trading System from laptop to desktop — 1:1 identical setup**

**Time**: 30 minutes | **Method**: Simple copy + Python venv

---

## Overview

| Step | What | Time |
|------|------|------|
| 1 | Copy project folder | 5 min |
| 2 | Create Python virtual environment | 3 min |
| 3 | Install dependencies | 10 min |
| 4 | Add API key | 2 min |
| 5 | Verify setup | 3 min |
| 6 | Test it works | 5 min |

---

## Step 1: Copy Project Folder

**On Laptop:**
1. Open File Explorer
2. Go to: `C:\Users\marti\vif-trading-system`
3. Right-click folder → **Copy**

**On Desktop:**
4. Open File Explorer
5. Go to: `C:\Users\YourUsername\` (your user folder)
6. Right-click empty space → **Paste**

✅ **Result**: `vif-trading-system` folder now on your desktop

---

## Step 2: Create Python Virtual Environment

**On Desktop, open Command Prompt:**
1. Press: `Windows Key + R`
2. Type: `cmd`
3. Press: `Enter`

**In Command Prompt:**
```bash
cd C:\Users\YourUsername\vif-trading-system
python -m venv venv
```

⏳ Wait 1–2 minutes for venv to create.

✅ **Result**: New `venv` folder appears in project directory

---

## Step 3: Activate Virtual Environment

**In Command Prompt, type:**
```bash
venv\Scripts\activate
```

✅ **Success**: Prompt now shows `(venv) C:\Users\YourUsername\vif-trading-system>`

---

## Step 4: Install Dependencies

**In Command Prompt (with `(venv)` active), type:**
```bash
pip install -r requirements.txt
```

⏳ Wait 5–10 minutes for all packages to install.

✅ **Success**: Ends with `Successfully installed...`

---

## Step 5: Add API Key

**On Laptop:**
1. Open: `.env` file (in `vif-trading-system` folder)
2. Copy: The entire line `ANTHROPIC_API_KEY=sk-ant-...`

**On Desktop:**
3. In your `vif-trading-system` folder, open: `.env.example`
4. Replace the placeholder with your actual key
5. Save the file
6. Rename from `.env.example` → `.env` (right-click → Rename)

✅ **Result**: Desktop now has `.env` with your API key

---

## Step 6: Verify Setup Works

**In Command Prompt (with `(venv)` active), type:**
```bash
python tests/test_api_key.py
```

✅ **Success**: Should display:
```
SUCCESS: key valid, billing active.
```

If you see this, you're done! ✅

---

## Step 7: Test It Works (Optional)

**In Command Prompt, run:**
```bash
python scripts/check_usage.py
```

✅ **Success**: Shows your API usage and costs

---

## ✅ Verification Checklist

- [ ] Project folder copied to desktop
- [ ] `venv` folder created
- [ ] `(venv)` shows in Command Prompt
- [ ] `pip install` completed without errors
- [ ] `.env` file created with API key
- [ ] `python tests/test_api_key.py` shows SUCCESS

---

## 1:1 Verification (Desktop = Laptop)

To verify your desktop is identical to your laptop:

**On Desktop, run:**
```bash
dir /s /b > C:\temp\desktop_files.txt
```

**On Laptop, run:**
```bash
dir /s /b > C:\temp\laptop_files.txt
```

**Compare** (ignore venv and .env differences):
- Same agents/ folder
- Same scripts/ folder  
- Same config/ folder
- Same requirements.txt
- Same .claude/ and .vscode/ folders

✅ If these match, your desktop setup is 1:1 identical to laptop

---

## Troubleshooting

### "Python not found"
- Install Python: https://www.python.org/downloads/
- During install: CHECK "Add Python to PATH"
- Restart Command Prompt

### "venv not activating"
- Make sure you're in project folder: `cd C:\Users\YourUsername\vif-trading-system`
- Try: `venv\Scripts\activate`
- Or use: `python -m venv venv` to recreate

### "pip install fails"
- Make sure `(venv)` is active
- Try: `python -m pip install -r requirements.txt`

### "API key doesn't work"
- Verify `.env` file exists (not `.env.example`)
- Verify API key is correct (copy from laptop again)
- Run: `python tests/test_api_key.py`

---

## Next Steps

Your desktop setup is now **1:1 identical** to your laptop. You can:

1. **Use Antigravity IDE** to edit and run code
2. **Use Command Prompt** with venv activated to run scripts
3. **Run analyses** the same way you do on laptop

All commands work identically on both machines.

---

**Setup complete! Your desktop is ready.** 🚀
