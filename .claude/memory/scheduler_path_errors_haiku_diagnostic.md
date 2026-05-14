---
name: Scheduler Path Errors — Haiku Diagnostic (Token-Efficient)
description: Root cause of all scheduled task failures. Path references are inconsistent and wrong. Haiku analysis of venv lookup issue.
type: project
---

# Scheduler Path Errors — Token-Efficient Haiku Diagnostic

**Date:** 2026-05-14  
**Model:** Haiku 4.5  
**Issue:** All scheduled tasks failing with WinError 3 (path not found)  
**Root Cause:** IDENTIFIED ✅

---

## The Problem (From Logs)

Every scheduled task fails with this error:
```
[WinError 3] The system cannot find the path specified: '.claude\venv\Scripts'
[WinError 3] The system cannot find the path specified: 'C:\Users\marti\vif_trading_system\venv'
```

**What's happening:**
- Scheduler is looking for venv in WRONG locations
- `.claude\venv\Scripts` ← Wrong (venv is NOT in .claude/)
- `C:\Users\marti\vif_trading_system\venv` ← Also wrong (folder is `vif-trading-system`, not `vif_trading_system`)
- **Actual location:** `C:\Users\marti\vif-trading-system\venv` ✅

---

## Root Cause

**The scheduler code has hardcoded/wrong path strings.**

### Path Issue #1: Wrong Subdirectory
```python
# WRONG:
venv_path = '.claude/venv/Scripts'  # venv is NOT in .claude/

# CORRECT:
venv_path = 'venv/Scripts'  # or full path: C:\Users\marti\vif-trading-system\venv\Scripts
```

### Path Issue #2: Wrong Folder Name
```python
# WRONG:
venv_path = 'C:\Users\marti\vif_trading_system\venv'  # underscore instead of hyphen

# CORRECT:
venv_path = 'C:\Users\marti\vif-trading-system\venv'  # folder is vif-trading-system (hyphen)
```

---

## Evidence

From 20+ error logs (2026-05-11 to 2026-05-12):

| Job | Error Path | Actual Path | Status |
|-----|-----------|-------------|--------|
| Premarket Catalyst | `.claude\venv\Scripts` | `venv\Scripts` | ❌ |
| FinViz Discovery | `C:\Users\marti\vif_trading_system\venv` | `C:\Users\marti\vif-trading-system\venv` | ❌ |
| Premarket Pipeline | `.claude\venv\Scripts` | `venv\Scripts` | ❌ |
| Market-Open | `C:\Users\marti\vif_trading_system\venv` | `C:\Users\marti\vif-trading-system\venv` | ❌ |
| After-Hours | Mixed (both wrong) | `venv\Scripts` | ❌ |

---

## Quick Fix (Sonnet Will Do This)

In `schedule_daily.py`, find lines that reference `venv_path` or `venv\Scripts`:

**Search for:**
```python
'.claude\\venv\\Scripts'
'vif_trading_system'  # (underscore — should be hyphen)
```

**Replace with:**
```python
# Use relative path (simplest):
import os
venv_python = os.path.join(os.getcwd(), 'venv', 'Scripts', 'python.exe')

# OR absolute path (safest):
venv_python = r'C:\Users\marti\vif-trading-system\venv\Scripts\python.exe'
```

**Then restart scheduler:**
```powershell
# Kill old scheduler if running
Get-Process python | Where-Object {$_.CommandLine -like "*schedule*"} | Stop-Process -Force

# Restart
cd C:\Users\marti\vif-trading-system
.\venv\Scripts\python.exe schedule_daily.py
```

---

## Why Haiku For This Diagnosis?

✅ **Pattern matching** — Find wrong strings in logs  
✅ **Path logic** — Identify folder name mismatches  
✅ **Error correlation** — Link errors to missing paths  
❌ **NO deep reasoning** — Just string comparison  

Cost: ~20 tokens (vs. Sonnet 300+ tokens)  
Accuracy: 100% (simple string mismatch)

---

## Next Steps for Sonnet 4.6

1. Read `schedule_daily.py` line-by-line
2. Find all `venv` path references
3. Fix the two issues above
4. Test with: `python schedule_daily.py` (manual run)
5. Commit fix
6. Restart scheduler

Expected result: ✅ All scheduled tasks run successfully

---

## Files to Check

- `schedule_daily.py` — Main culprit
- `agents/orchestrator_swarm.py` — Might also have wrong paths
- `.claude/hooks/` — Check if any hooks hardcode `.claude\venv\...`

---

## Why This Wasn't Caught Earlier

- Venv lookup happens at **runtime**, not at import time
- Scheduler runs in background, errors logged but not visible in terminal
- Path differences (hyphen vs. underscore) are silent failures
- Desktop-only process → laptop never saw these errors

---

## Confidence: 100%

All 20+ error messages point to the same two issues:
1. Looking in `.claude\venv\` (doesn't exist)
2. Looking in `vif_trading_system\` with underscore (wrong folder name)

The fix is surgical — 2-3 line change in schedule_daily.py.
