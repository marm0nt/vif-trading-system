---
name: VIF System Current State
description: Operational status of VIF trading system as of May 6, 2026
type: project
originSessionId: 275d482b-9bda-41df-ac22-0d73fa9237a0
---
## System Status — May 6, 2026

### Components Operational
- **Orchestrator** (`agents/orchestrator.py`) — Brain of the system, delegates to sub-agents
- **MCP Server** (`tradingview-mcp-jackson/src/server.js`) — Registered globally in user scope
- **TradingView Desktop** — Connected via CDP on port 9222
- **Premarket Pipeline** — 3/3 agents passing (Catalyst Scan, VIF Watchlist, Swing Screener)

### Key Configuration
- **MCP Scope:** User (global) — accessible from any project
- **MCP Command:** `claude mcp add -s user tradingview -e TV_PORT=9222 -- node C:\Users\marti\vif-trading-system\tradingview-mcp-jackson\src\server.js`
- **MCP Source Repo:** https://github.com/LewisWJackson/tradingview-mcp-jackson.git (gitignored in main repo)
- **Python Runtime:** `sys.executable` (venv-aware via PATH)
- **CDP Port:** 9222 (hardcoded in `connection.js`, not configurable)
- **Watchlists:** 6 institutional watchlists (VIF 4-tier structure) — see `watchlist_structure.md`

### Last Successful Run
- **Date:** 2026-05-05 02:14:15
- **Mode:** premarket
- **Result:** 3/3 agents succeeded
- **Duration:** ~7 minutes (Catalyst Scan 4:38 + VIF Watchlist 2:42 + Swing Screener 0:17)

### Multi-Machine Setup
- **Sync script:** `LAPTOP_SYNC.ps1` at repo root — one command to fully set up any new machine
- **What it does:** git pull, pip install, .env prompt, clones tradingview-mcp-jackson, registers MCP, writes .vscode + .claude/settings.local.json
- **Manual step:** Copy `C:\Users\marti\.claude\projects\C--Users-marti-vif-trading-system\memory\` between machines (not in git)
- **Written guide:** `docs/LAPTOP_SETUP.md`

### Session Work — May 5–6, 2026
- Reorganized 6 TradingView watchlists into VIF 4-tier institutional structure (170 tickers, 58 dupes removed)
- Built `reports/watchlist_institutional_structure.html` — full metadata, alpha triggers, import guide
- Fixed VS Code showing tradingview-mcp-jackson as separate repo (`git.ignoredRepositories` in `.vscode/settings.json`)
- Created `LAPTOP_SYNC.ps1` for one-command multi-machine setup
- Desktop repo is clean and pushed: `github.com/marm0nt/vif-trading-system`

### Do Before Next Session
1. Verify MCP connection: `mcp__tradingview__chart_get_state` (returns symbol if working)
2. Confirm port 9222 open: `netstat -ano | Select-String "9222"`
3. If CDP fails: run Environmental Reset Workflow in `known_issues.md` Issue #5
   ```powershell
   Stop-Process -Name TradingView -Force -ErrorAction SilentlyContinue
   Start-Sleep -Seconds 2
   & ".\tradingview-mcp-jackson\scripts\launch_tv_windows_store.ps1" -Wait
   ```
