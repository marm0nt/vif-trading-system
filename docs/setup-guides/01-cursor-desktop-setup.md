# Cursor IDE Desktop Setup

**Getting Cursor configured and ready to work on your project**

**Updated**: 2026-04-30  
**Difficulty**: Beginner-Friendly  
**Time Required**: 5 minutes

---

## 🎯 Quick Answer: Setup Flow Question

When Cursor asks: "Choose a setup flow", select:

### **✅ "Import Fresh"** (RECOMMENDED)

**Why?**
- You're starting this project fresh on desktop
- No existing Cursor configuration to import
- Clean slate is simpler to set up
- Takes ~2 minutes to configure

---

## Step-by-Step Cursor Setup

### Step 1: Choose "Import Fresh" (1 minute)

**When Cursor first launches**, you see:

```
Please select how you want to set up Cursor:

○ Import from Cursor
○ Import from VS Code
○ Import Fresh (SELECT THIS)
```

**Your choice:**
- Click: **"Import Fresh"**
- Click: **Next**

Cursor will load with a clean workspace.

✅ **Success**: Cursor opens with empty workspace.

---

### Step 2: Open Your Project Folder (1 minute)

1. Press: `Ctrl+K, Ctrl+O` (or File → Open Folder)
2. Navigate to: `C:\Users\YourUsername\vif-trading-system`
3. Click: **Select Folder**

✅ **Success**: Project folder opens in Cursor. You see all files in left panel.

---

### Step 3: Open Terminal and Activate Virtual Environment (2 minutes)

1. Press: `Ctrl + `` (backtick) to open terminal at bottom
2. Type: 
   ```bash
   venv\Scripts\activate
   ```
3. Press: Enter

✅ **Success**: Prompt now shows `(venv)` at the start

---

### Step 4: Install Python Extension (1 minute)

1. Press: `Ctrl+Shift+X` (Extensions panel)
2. Search: `Python`
3. Install: **Python** by Microsoft
4. Reload Cursor

**Why?** For syntax highlighting, auto-completion, and debugging in Python files.

---

### Step 5: Verify Everything Works (1 minute)

In the terminal (with `(venv)` active), run:

```bash
python tests/test_api_key.py
```

✅ **Success**: Should show:
```
SUCCESS: key valid, billing active.
```

You're done! ✅

---

## 🎮 Essential Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Command Palette | `Ctrl+Shift+P` |
| File Search | `Ctrl+P` |
| Symbol Search | `Ctrl+Shift+O` |
| Terminal | `Ctrl+`` (backtick) |
| **Antigravity AI Chat** | Highlight code + right-click → "Ask Antigravity" |
| Find in File | `Ctrl+F` |
| Find & Replace | `Ctrl+H` |
| Format Document | `Shift+Alt+F` |
| Go to Definition | `F12` |
| Rename Symbol | `F2` |

---

## 🚀 Using Antigravity in Cursor

**To ask questions about your code:**

1. Highlight any code in the editor
2. Right-click on the highlighted code
3. Select: **"Ask Antigravity"**
4. Type your question
5. Antigravity generates answers

**You can ask things like:**
- "Explain this function"
- "How do I fix this error?"
- "Refactor this code"
- "What does this do?"

---

## ✅ Verification Checklist

After setup:

- [ ] Cursor opened with your project folder
- [ ] Terminal shows `(venv)` in prompt
- [ ] `python tests/test_api_key.py` shows SUCCESS
- [ ] Python extension installed
- [ ] Can see project files in left panel

---

## 📞 Troubleshooting

### Terminal Not Showing Virtual Environment

**Solution:**
1. Make sure you're in the project folder
2. Type: `venv\Scripts\activate`
3. Should now see: `(venv)` in prompt

---

### Python Extension Missing

**Solution:**
1. Press: `Ctrl+Shift+X` (Extensions)
2. Search: `Python`
3. Install by Microsoft
4. Reload Cursor

---

### "Python not found" When Running Scripts

**Solution:**
1. Make sure `(venv)` appears in terminal prompt
2. Activate: `venv\Scripts\activate`
3. Try again

---

### Antigravity Not Available

**Antigravity is built into Cursor**, so it should work immediately.

- Highlight code
- Right-click
- Select "Ask Antigravity"

If it's not there, reload Cursor: `Ctrl+Shift+P` → "Reload Window"

---

## 🔗 Next Steps

1. ✅ Cursor is set up
2. 🚀 Try running: `python agents/watchlist_watcher.py --watchlist vantage_portfolio`
3. 📖 Optional: Read [Desktop Python Setup](02-desktop-python-setup.md) if you hit issues
4. 💬 Use Antigravity: Highlight code and right-click → "Ask Antigravity"

---

## 📚 Related Documentation

- **Desktop Python Setup**: [Desktop Python Setup](02-desktop-python-setup.md)
- **Settings Explained**: [Configuration Reference](03-configuration-reference.md)
- **More Issues**: [Troubleshooting Guide](04-troubleshooting.md)
- **Project Overview**: `CLAUDE.md` (in project root)

---

**Cursor is ready! You're all set to work on your project.** 🚀
