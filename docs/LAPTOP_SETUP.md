# Laptop Setup — VIF Trading System

Run these in order in a PowerShell terminal. ~5 minutes total.

---

## 1. Clone & Enter Repo

```powershell
git clone https://github.com/marm0nt/vif-trading-system.git
cd vif-trading-system
```

---

## 2. Python Environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

## 3. API Key

```powershell
copy .env.example .env
notepad .env
```

Set `ANTHROPIC_API_KEY=sk-ant-...` (copy from desktop or 1Password).

---

## 4. VS Code Settings (not in git — recreate manually)

Create `.vscode/settings.json` with:

```json
{
  "python.terminal.useEnvFile": true,
  "python.locator": "js",
  "python.venvPath": "C:\\Users\\<YOUR_USERNAME>\\vif-trading-system",
  "python.venvFolders": ["venv"],
  "python.interpreter.infoVisibility": "always",
  "python.terminal.activateEnvironment": true,
  "python.analysis.extraPaths": [
    "C:\\Users\\<YOUR_USERNAME>\\vif-trading-system\\venv\\Lib\\site-packages"
  ],
  "terminal.integrated.defaultProfile.windows": "PowerShell",
  "terminal.integrated.env.windows": {
    "PYTHONUTF8": "1",
    "PYTHONDONTWRITEBYTECODE": "1",
    "VIRTUAL_ENV": "C:\\Users\\<YOUR_USERNAME>\\vif-trading-system\\venv"
  },
  "git.ignoredRepositories": [
    "C:\\Users\\<YOUR_USERNAME>\\vif-trading-system\\tradingview-mcp-jackson"
  ],
  "[python]": {
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "ms-python.python"
  }
}
```

Replace `<YOUR_USERNAME>` with your laptop Windows username.

---

## 5. TradingView MCP Server

```powershell
# Clone the MCP server (gitignored in the main repo)
git clone https://github.com/marm0nt/tradingview-mcp-jackson.git
# OR copy the folder from desktop via USB/network

cd tradingview-mcp-jackson
npm install
cd ..
```

---

## 6. Register TradingView MCP in Claude Code

```powershell
claude mcp add -s user tradingview -e TV_PORT=9222 -- node "$PWD\tradingview-mcp-jackson\src\server.js"
```

Verify:
```powershell
claude mcp list
```

---

## 7. Claude Code Local Permissions (not in git — paste into Claude Code)

Run `claude` in the project directory, then paste this into a session to restore permissions:

> "Please update my local Claude Code settings to allow these tools without prompting: Bash, PowerShell, Read, Write, Edit, WebFetch, WebSearch, Agent, Glob, Grep, and the tradingview MCP tools: tv_health_check, tv_launch, chart_get_state, watchlist_get, ui_evaluate"

---

## 8. Memory Files (optional but recommended)

The memory files live outside the repo at `C:\Users\marti\.claude\projects\`.
Copy them from the desktop via USB/network to the same path on your laptop:

```
C:\Users\marti\.claude\projects\C--Users-marti-vif-trading-system\memory\
```

Files to copy:
- `MEMORY.md`
- `feedback_autonomy.md`
- `feedback_public_submissions.md`
- `vif_system_state.md`
- `known_issues.md`
- `watchlist_structure.md`
- `github_repos_improvement_roadmap.md`
- `anthropic_api_improvements_may2026.md`

---

## 9. Verify

```powershell
python tests/test_api_key.py
python tests/test_harness.py
```

Both should pass. System is ready.

---

## What's Already in GitHub (no action needed)

- All 6 reorganized watchlists (`watchlists/*.txt`) with VIF 4-tier structure
- All agents, scripts, config (`config/vif_config.yml`)
- CLAUDE.md, requirements.txt, schedule_daily.py
- `.claude/` directory (settings.json, hooks — but NOT settings.local.json)
