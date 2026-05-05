# TradingView MCP Setup Guide

**Last Updated:** May 5, 2026  
**Status:** ✓ Operational (3/3 agents passing premarket pipeline)

---

## What Was Built

Integration of Jackson's TradingView MCP server into the VIF trading system, enabling Claude Code to read live charts and control TradingView Desktop via the Volatility Imbalance Framework (VIF v4.0).

### Final Architecture
```
Claude Code (MCP tools) 
  ↕ stdio
MCP Server (tradingview-mcp-jackson/src/server.js)
  ↕ CDP port 9222
TradingView Desktop (Electron app)
```

---

## Quick Start (For Future Sessions)

### 1. Launch TradingView with CDP
```powershell
# From vif-trading-system root:
.\tradingview-mcp-jackson\scripts\launch_tv_windows_store.ps1

# This auto-detects the Store-installed TradingView and launches with --remote-debugging-port=9222
```

### 2. Verify Connection
```bash
# In Claude Code:
Run tv_health_check

# Expected: { "cdp_connected": true, "chart_symbol": "...", "api_available": true }
```

### 3. Run Analysis
```bash
python agents/orchestrator.py --mode premarket
# OR
python agents/orchestrator.py --mode afterhours
python agents/orchestrator.py --mode full
```

---

## Installation (Reference)

If you need to reinstall, follow these steps:

### Step 1: Repository Structure
```
/vif-trading-system
├── /agents          (Python analysis agents)
├── /tradingview-mcp-jackson  (MCP server — contains Node.js code)
├── /docs            (This file)
└── /watchlists      (CSV exports from TradingView)
```

### Step 2: Move MCP Inside Project
The `tradingview-mcp-jackson` folder should live inside `vif-trading-system`, not at the root user level.

### Step 3: Register MCP Globally
```bash
claude mcp add -s user tradingview -e TV_PORT=9222 -- node C:\Users\marti\vif-trading-system\tradingview-mcp-jackson\src\server.js
```

**Note:** This registers the MCP in your global Claude Code config (`~/.claude.json`), making it available from any project.

### Step 4: Update .gitignore
Add to `vif-trading-system/.gitignore`:
```
tradingview-mcp-jackson/
claude-trading-skills/
```

These are external repos that shouldn't be committed.

---

## Known Issues & Solutions

### Issue 1: Python Exit Code 103

**Problem:** Claude Code blocks Python calls on Windows with `No Python at '"/usr/bin\python.exe'`

**Root Cause:** Claude Code intercepts Python process calls and tries to resolve to Unix path (doesn't exist).

**Solution:**
1. Copy `C:\Python313\python.exe` to `C:\Users\marti\bin\python.exe`
2. In `agents/orchestrator.py`, use `sys.executable` instead of hardcoded venv path

**Status:** ✓ Resolved

---

### Issue 2: TradingView Not Found by Batch Script

**Problem:** `launch_tv_debug.bat` fails because TradingView is a Microsoft Store app

**Root Cause:** Traditional batch scripts only check standard install paths (`%PROGRAMFILES%`, `%LOCALAPPDATA%`). Store apps live in `WindowsApps` and require `Get-AppxPackage` to locate.

**Solution:** Use `scripts/launch_tv_windows_store.ps1` (custom PowerShell script that detects Store app)

**Status:** ✓ Resolved — this script is unique to this project

---

### Issue 3: MCP Registration Syntax

**Problem:** `claude mcp add` command syntax is non-obvious

**Correct Order:**
```bash
claude mcp add -s user tradingview -e TV_PORT=9222 -- node "path/to/server.js"
#             ↑              ↑                 ↑            ↑
#        name must come  before -e flag    separator    command
```

---

## Architecture Details

### MCP Server (Node.js)
- **Path:** `tradingview-mcp-jackson/src/server.js`
- **Tools:** 81 MCP tools for chart control, Pine Script editing, replay, alerts, etc.
- **Connection:** Communicates with TradingView via Chrome DevTools Protocol (CDP)

### CDP (Chrome DevTools Protocol)
- **Port:** 9222 (hardcoded, cannot change)
- **Launch Flag:** `--remote-debugging-port=9222`
- **Why:** Only way to access TradingView's internal JavaScript APIs

### Python Agents
- **Orchestrator:** `agents/orchestrator.py` — Master controller for pipelines
- **Watchlist Watcher:** `agents/watchlist_watcher.py` — VIF v4.0 analysis
- **Swing Screener:** `scripts/swing_trade_screener_v2.py` — 2-4 week setups
- **Catalyst Scanner:** `scripts/catalyst_analysis.py` — Macro + earnings alerts

---

## Testing & Verification

### Before Each Session
```bash
# 1. Port 9222 open?
netstat -an | findstr 9222
# Expected: TCP    127.0.0.1:9222         0.0.0.0:0              LISTENING

# 2. MCP registered?
claude mcp list | grep tradingview
# Expected: tradingview: node ... - ✓ Connected

# 3. TradingView running?
Get-Process TradingView -ErrorAction SilentlyContinue
# Expected: TradingView process listed

# 4. Orchestrator works?
python agents/orchestrator.py --mode premarket
# Expected: 3/3 agents succeeded (Catalyst Scan, VIF Watchlist, Swing Screener)
```

### If Something Breaks
1. Relaunch TradingView: `.\tradingview-mcp-jackson\scripts\launch_tv_windows_store.ps1`
2. Wait 5 seconds for CDP to stabilize
3. Verify port 9222 is open: `netstat -an | findstr 9222`
4. Test connection: `Run tv_health_check` (in Claude Code)

---

## Limitations

| Limitation | Impact | Workaround |
|-----------|--------|-----------|
| Port 9222 hardcoded | Cannot change without editing `src/connection.js` | Not needed — use as-is |
| CDP mandatory | Cannot use MCP without TradingView running | Always launch TradingView first |
| Single instance | Only one TradingView instance per port 9222 | Works fine for single user |
| Local only | Cannot connect to remote TradingView instances | Use locally on your machine |
| Store app requirement | Windows desktop version only | Download at tradingview.com/desktop |

---

## Reports & Outputs

### Premarket Pipeline Output
- **HTML Dashboard:** `reports/pipeline_premarket_YYYYMMDD_HHMMSS.html`
- **Catalyst JSON:** `reports/catalyst_analysis_YYYYMMDD_HHMMSS.json`
- **Swing Setups:** `reports/swing_setups_YYYYMMDD_HHMMSS.json`
- **Orchestrator Log:** `reports/orchestrator_premarket_YYYYMMDD_HHMMSS.json`

All reports are timestamped and archived for historical comparison.

---

## References

- **Original MCP:** [tradesdontlie/tradingview-mcp](https://github.com/tradesdontlie/tradingview-mcp)
- **Fork (Jackson):** [LewisWJackson/tradingview-mcp-jackson](https://github.com/LewisWJackson/tradingview-mcp-jackson)
- **VIF Framework:** See `config/vif_config.yml`
- **System Memory:** See `.claude/projects/c--Users-marti-vif-trading-system/memory/`

---

## Next Steps

1. ✅ System is operational
2. Run daily via `schedule_daily.py` or manually via orchestrator
3. Monitor `reports/` folder for analysis output
4. Integrate with your trading workflow
5. Expand watchlists as needed in `watchlists/` folder
