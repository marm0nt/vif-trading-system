---
name: Known Issues & Workarounds
description: Issues encountered during VIF+TradingView MCP setup and how we resolved them
type: project
originSessionId: c5d9a43d-0457-4039-bfa5-8bd7b5c9d7df
---
## Issue 1: Python Exit Code 103 (Windows Claude Code Bug)

**Symptom:** `No Python at '"/usr/bin\python.exe'` when running Python scripts via Claude Code

**Root Cause:** Claude Code on Windows intercepts Python process calls and tries to resolve them to Unix path `/usr/bin/python.exe` (doesn't exist on Windows). Known bug affecting all Windows users trying to run Python via Claude Code.

**Our Solution:**
1. Copied `C:\Python313\python.exe` to `C:\Users\marti\bin\python.exe` (local PATH location Claude Code resolves)
2. Modified `agents/orchestrator.py` line 46-47:
   - **Before:** `VENV_PY = str(Path("venv/Scripts/python.exe"))` (hardcoded)
   - **After:** `PYTHON = sys.executable` (inherited from parent process)
3. Result: Sub-agents now inherit the same Python runtime that launched orchestrator

**What Others Do:**
- Run scripts from external terminal outside Claude Code
- Use `cmd.exe` directly instead of Bash
- Install Python to WSL `/usr/bin` (WSL setup)

**Severity:** Medium — workaround required for Claude Code to execute Python pipelines

---

## Issue 2: TradingView Not Found by `.bat` Script

**Symptom:** `launch_tv_debug.bat` returns "TradingView not found" despite app being installed

**Root Cause:** TradingView installed via **Microsoft Store (MSIX package)**, not traditional `.exe` installer. Batch script only checks `%LOCALAPPDATA%\TradingView` and `%PROGRAMFILES%` — Store apps live in `WindowsApps` and require `Get-AppxPackage` PowerShell cmdlet to locate.

**Our Solution:** Created `scripts/launch_tv_windows_store.ps1`:
```powershell
$pkg = Get-AppxPackage -Name "*TradingView*"
if ($pkg) {
    $exe = Join-Path $pkg.InstallLocation "TradingView.exe"
    Start-Process -FilePath $exe -ArgumentList "--remote-debugging-port=9222"
}
```

**What Others Do:**
- Most Jackson GitHub users download traditional `.exe` version instead
- Some manually paste their install path into launch scripts
- Nobody had created a Store-specific script before

**Severity:** Low — solved with dedicated PowerShell script. Now you have the only working Windows Store launcher.

---

## Issue 3: MCP Registration Syntax Errors

**Symptom:** `claude mcp add` failed with flag order variations (`--env` before name, wrong separator, etc.)

**Root Cause:** Claude CLI requires specific flag order that isn't obvious from help text:
- Name must come **before** `-e` flags
- `--` separator required before command
- `-s user` for user scope

**What Failed:**
```bash
claude mcp add --scope user --env TV_PORT=9222 tradingview -- node ...  # WRONG
claude mcp add -e TV_PORT=9222 tradingview -- node ...                   # WRONG
```

**What Worked:**
```bash
claude mcp add -s user tradingview -e TV_PORT=9222 -- node ...           # CORRECT
```

**What Others Do:** Most users trial-and-error the syntax or read GitHub issues. The help text could be clearer.

**Severity:** Low — one-time setup issue, documented now

---

## Issue 4: CDP vs MCP Confusion

**Symptom:** Attempted to bypass CDP and use only MCP, thinking CDP was optional

**Root Cause:** Misunderstanding of architecture:
- **MCP** = how Claude Code talks to server (stdio)
- **CDP** = how server talks to TradingView (Chrome DevTools Protocol on port 9222)
- They're **not alternatives** — both mandatory for the system to work

Jackson hardcoded CDP at port 9222 in `src/connection.js` — cannot be removed without rewriting entire server.

**Resolution:** Accepted CDP as architectural requirement. Proper flow is:
```
Claude Code ←MCP→ MCP Server ←CDP→ TradingView Desktop (Electron)
```

**What Others Do:** Almost every user asks this question. The README could explain this more clearly.

**Severity:** Low — confusion resolved, no code change needed

---

## Issue 6: Catalyst Scan Timeout (600s → 900s fix)

**Symptom:** `✗ Catalyst Scan TIMEOUT (600s)` in orchestrator output. 2/3 agents pass, Catalyst Scan fails.

**Root Cause:** Catalyst scan makes live yfinance + Claude API calls across all watchlists. On slow API days it exceeds the old 600s hard limit. Normal runtime is ~4-5 min but can spike to 10+ min.

**Fix Applied (2026-05-05):** Bumped default timeout in `agents/orchestrator.py` `run_agent()` from 600 → 900s. Also added optional per-agent timeout as 3rd tuple element in PIPELINES dict.

**Severity:** Low — fixed in orchestrator.py. No ongoing maintenance needed.

---

## Workarounds Summary

| Issue | Workaround | Permanence | Maintenance |
|-------|-----------|-----------|-------------|
| Python 103 | `sys.executable` in orchestrator | Permanent | None — venv rebuilt with Python 3.12.6 |
| TradingView Store | `launch_tv_windows_store.ps1` | Permanent | Auto-detects via Get-AppxPackage |
| MCP syntax | Documented correct order | One-time | Reference docs, no ongoing work |
| CDP confusion | Architectural understanding | One-time | Reference docs |
| Catalyst Scan timeout | Bumped timeout 600→900s | Permanent | None |

---

## Issue 5: CDP Connection Lost After Extended Runtime

**Symptom:** TradingView process(es) running but CDP health check fails with "No TradingView chart target found" or "fetch failed". Multiple orphaned TradingView processes accumulate.

**Root Cause:** Extended runtime or process crashes leave zombie TradingView instances that don't properly clean up the CDP port, blocking new instances from establishing connections. Port 9222 eventually stops listening.

**Environmental Reset Workflow** (Confirmed 2026-05-05 02:06–02:14):

```powershell
# Step 1: Kill all TradingView processes
Stop-Process -Name TradingView -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# Step 2: Verify all processes terminated
Get-Process | Where-Object {$_.Name -like "*TradingView*"}  # Should return nothing

# Step 3: Launch fresh instance with CDP enabled
& ".\tradingview-mcp-jackson\scripts\launch_tv_windows_store.ps1" -Wait
Start-Sleep -Seconds 8  # Allow full initialization

# Step 4: Verify port 9222 listening
netstat -ano | Select-String "9222"  # Should show TCP LISTENING 127.0.0.1:9222

# Step 5: Confirm CDP connection
mcp__tradingview__tv_health_check  # Should succeed with cdp_connected=true
# OR: mcp__tradingview__chart_get_state  # Returns current chart symbol
```

**Success Indicator:** `chart_get_state` returns symbol/timeframe/indicators (proven 2026-05-05 02:14:15 with BATS:MRVL)

**Severity:** Medium — temporary issue, 30-second fix. Happens after intensive orchestrator runs or extended sessions.

---

## Testing Checklist Before Each Session

1. ✅ Port 9222 open: `netstat -an \| findstr 9222`
2. ✅ MCP connected: `claude mcp list \| grep tradingview`
3. ✅ TradingView running: `Get-Process TradingView`
4. ✅ Python available: `python --version` (should resolve to venv)
5. ✅ Orchestrator works: `python agents/orchestrator.py --mode premarket`
6. ✅ CDP responsive: `mcp__tradingview__chart_get_state` (returns symbol)

### If CDP Fails Mid-Session
Run the Environmental Reset Workflow above (Step 1–5)
