---
name: MCP Registration & Configuration
description: How TradingView MCP is registered globally and technical details of the setup
type: reference
originSessionId: c5d9a43d-0457-4039-bfa5-8bd7b5c9d7df
---
## Registration Status

**Registered:** May 4, 2026 via Claude Code CLI  
**Scope:** User (global) — accessible from any project  
**Config File:** `C:\Users\marti\.claude.json` (global Claude Code config)  
**Status:** ✓ Connected

## Registration Command

```bash
claude mcp add -s user tradingview -e TV_PORT=9222 -- node C:\Users\marti\vif-trading-system\tradingview-mcp-jackson\src\server.js
```

### Command Breakdown
- `-s user` — Register globally (not project-local)
- `tradingview` — Server name (must come before flags)
- `-e TV_PORT=9222` — Environment variable (unused by server, hardcoded to 9222)
- `-- node ...` — Command to execute (Node.js runs server.js)

## How It Works (Architecture)

```
┌─────────────┐
│ Claude Code │
│  Terminal   │
└──────┬──────┘
       │ MCP (stdio)
       ▼
┌──────────────────────────────────────┐
│ MCP Server (server.js)               │
│ - 81 tools for chart control         │
│ - Routes commands via CDP            │
└──────┬───────────────────────────────┘
       │ CDP (Chrome DevTools Protocol)
       │ localhost:9222
       ▼
┌──────────────────────────────────────┐
│ TradingView Desktop (Electron app)   │
│ - Runs your live charts              │
│ - Exposes internal APIs via CDP      │
└──────────────────────────────────────┘
```

## Key Technical Details

### CDP (Chrome DevTools Protocol)
- **Port:** 9222 (hardcoded in `src/connection.js`, cannot change)
- **Launch Flag:** `--remote-debugging-port=9222`
- **Connection Type:** HTTP REST to `http://localhost:9222/json/*`
- **Why Required:** Only way to access TradingView's internal JavaScript APIs (chart state, indicators, Pine script)

### MCP Server Capabilities
**Location:** `C:\Users\marti\vif-trading-system\tradingview-mcp-jackson\src\server.js`

**Tool Groups (81 total):**
- Chart reading: `chart_get_state`, `data_get_study_values`, `quote_get`, `data_get_ohlcv`
- Chart control: `chart_set_symbol`, `chart_set_timeframe`, `chart_manage_indicator`
- Pine Script: `pine_set_source`, `pine_smart_compile`, `pine_get_errors`
- Morning brief: `morning_brief`, `session_save`, `session_get`
- Replay: `replay_start`, `replay_step`, `replay_trade`, `replay_status`
- Drawing: `draw_shape` (lines, boxes, text)
- Screenshots: `capture_screenshot`
- Alerts: `alert_create`, `alert_list`, `alert_delete`

**Config File:** `tradingview-mcp-jackson/rules.json` (defines watchlist + bias criteria)

## To Verify Registration

```bash
# Check if server is registered
claude mcp list | grep tradingview

# Expected output:
# tradingview: node C:/Users/marti/vif-trading-system/tradingview-mcp-jackson/src/server.js - ✓ Connected
```

## To Launch TradingView with CDP

```powershell
# From vif-trading-system root:
.\tradingview-mcp-jackson\scripts\launch_tv_windows_store.ps1

# Or manually:
$pkg = Get-AppxPackage -Name "*TradingView*"
$exe = Join-Path $pkg.InstallLocation "TradingView.exe"
Start-Process -FilePath $exe -ArgumentList "--remote-debugging-port=9222"
```

## To Test Connection

```bash
# From Claude Code:
Run tv_health_check

# Expected response:
{
  "success": true,
  "cdp_connected": true,
  "chart_symbol": "KLIC",
  "api_available": true
}
```

## If Connection Fails

1. **Check port 9222 is open:**
   ```powershell
   netstat -an | findstr 9222
   # Should show: TCP    127.0.0.1:9222         0.0.0.0:0              LISTENING
   ```

2. **Check TradingView is running:**
   ```powershell
   Get-Process TradingView -ErrorAction SilentlyContinue
   ```

3. **Relaunch TradingView:**
   ```powershell
   .\tradingview-mcp-jackson\scripts\launch_tv_windows_store.ps1
   ```

4. **Verify MCP server is connected:**
   ```bash
   claude mcp list | grep tradingview
   # Should show ✓ Connected
   ```

## File Structure

```
C:\Users\marti\vif-trading-system\
├── tradingview-mcp-jackson/           ← MCP server code
│   ├── src/
│   │   ├── server.js                  ← Main MCP server entry
│   │   ├── connection.js              ← CDP connection logic (port 9222 hardcoded here)
│   │   ├── tools/
│   │   │   ├── chart.js
│   │   │   ├── data.js
│   │   │   ├── pine.js
│   │   │   ├── morning.js
│   │   │   └── ... (78+ other tools)
│   │   └── core/
│   ├── scripts/
│   │   ├── launch_tv_debug.bat        ← Traditional .exe installer
│   │   ├── launch_tv_windows_store.ps1 ← Our custom Store app launcher
│   │   └── ...
│   ├── rules.json                     ← Your trading rules (watchlist, bias criteria)
│   └── package.json
└── agents/
    └── orchestrator.py                ← Calls MCP tools
```

## Environment Variables

**Registered:**
- `TV_PORT=9222` — Set but unused (server hardcodes port in code)

**Not Set (but could be useful):**
- `ANTHROPIC_API_KEY` — Used by Python agents, not by MCP server
- `CDP_TIMEOUT` — Connection timeout (not exposed)

## Limitations

1. **Port 9222 is hardcoded** — Cannot change without modifying `src/connection.js`
2. **CDP is mandatory** — Cannot use MCP without TradingView Desktop running with `--remote-debugging-port=9222`
3. **Single instance only** — Only one TradingView instance can use port 9222 at a time
4. **Local only** — MCP server only connects to `localhost:9222`, not remote machines
