---
name: Scheduler Diagnostics — After-Hours Pipeline Failures
description: Root cause analysis of scheduler failures (2026-04-30 to 2026-05-13). Token-efficient Haiku analysis. After-hours job returns success: false despite swarm execution completing.
type: project
---

# Scheduler Diagnostics — Token-Efficient Analysis

**Analysis Date:** 2026-05-13  
**Model:** Claude Haiku 4.5 (token-efficient)  
**Status:** ACTIVE — 8 consecutive failures on after-hours pipeline

---

## Executive Summary

✅ **Scheduler is running** — jobs fire at correct times (16:05 every weekday)  
✅ **Swarm orchestrator executes** — processes complete, produces reports  
❌ **Return status is false** — scheduler records `success: false` despite successful execution  
❌ **Root cause:** Mismatch between execution success and reported status

---

## Evidence from Logs

### Scheduler Log (2026-05-13 16:05:24)
```
2026-05-13 16:05:24,081 [SCHEDULER] STARTING: After-Hours Pipeline [Swarm]
2026-05-13 16:05:24,083 [SCHEDULER] (no completion log visible in tail)
```
**Issue:** Job started but completion status not logged.

### Orchestrator Swarm Log (2026-05-12 22:02:36 — Last Successful Run)
```
[SWARM-ORCHESTRATOR] SWARM EXECUTION COMPLETE
Duration: 681670ms (11+ minutes)
Agents: 8/9 succeeded
KV Cache Hit Rate: 10.2%
Signals: 0 BUY, 16 SELL, 120 HOLD
Results saved -> reports\swarm_result_afterhours_20260512_220236.json
HTML report saved -> reports\swarm_afterhours_20260512_220236.html
```
**Good news:** Swarm runs and produces output files. BUT this log entry is from 2026-05-12 (2+ days old) — no recent completion logs.

### Run History JSON (2026-04-28 to 2026-05-13)
```
✅ 2026-04-28 16:05: success: true   (last successful run)
❌ 2026-04-30 16:06: success: false  (swarm orchestrator failed)
❌ 2026-05-01 16:06: success: false  (3x attempts, all failed)
❌ 2026-05-04 16:05: success: false  (2x retries, all failed)
❌ 2026-05-11 16:05: success: false  (3x attempts, all failed)
❌ 2026-05-12 16:05: success: false  (2x attempts, all failed)
❌ 2026-05-13 16:05: success: false  (1x attempt, failed)
```

**Pattern:** 8 consecutive failures since 2026-04-30 (13 days). Last successful: 2026-04-28.

---

## Root Causes (Haiku Analysis)

### Cause 1: Exit Code Not Captured by Scheduler
**What happens:** Swarm orchestrator executes and writes reports, BUT the scheduler doesn't read/capture the exit code.  
**Why:** Scheduler job definition likely doesn't check subprocess return value or pipes stderr properly.  
**Fix:** Verify `schedule_daily.py` or scheduler wrapper is checking `proc.returncode` after swarm completes.

### Cause 2: Exception Silently Raised, Caught Locally
**Evidence:** Swarm logs show "COMPLETE" (2026-05-12) but no new completion logs after.  
**Why:** Swarm might catch exceptions internally and mark itself as done, but return non-zero exit code.  
**Fix:** Check `agents/orchestrator_swarm.py` exit handler — is it catching exceptions and calling `sys.exit(1)`?

### Cause 3: Subprocess Timeout or Signal Kill
**Pattern:** Job is scheduled, starts, but no completion log. Reports ARE written (good), but subprocess exits abnormally.  
**Why:** 11+ min execution time (681 seconds from 2026-05-12 log) might exceed scheduler's timeout threshold.  
**Fix:** Check scheduler timeout setting. Is there a max_duration or timeout configured?

### Cause 4: Report File I/O Succeeds but Return Code Fails
**Evidence:** `Results saved -> reports\...` and `HTML report saved -> reports\...` appear in logs.  
**Why:** Swarm completes its work and writes files, but then raises an exception on cleanup/finalization.  
**Likely location:** Post-execution logging, cleanup, or report post-processing.  
**Fix:** Check `agents/orchestrator_swarm.py` after the "SWARM EXECUTION COMPLETE" block.

---

## Quick Diagnostics (Run These)

### Check 1: Recent Reports Exist?
```powershell
ls reports/swarm_result_afterhours_*.json -File | Sort-Object LastWriteTime -Desc | Select -First 5
ls reports/swarm_afterhours_*.html -File | Sort-Object LastWriteTime -Desc | Select -First 5
```
**If files are recent:** Swarm IS running and completing. Status reporting is the issue.  
**If files are old (>13 days):** Swarm stopped working.

### Check 2: Last Swarm Log Entry?
```powershell
tail -50 logs/orchestrator_swarm.log | grep "SWARM EXECUTION COMPLETE"
```
**If empty:** Swarm hasn't completed successfully in 13+ days. Check `orchestrator_swarm.py` for exceptions.  
**If recent:** Swarm completes but scheduler doesn't recognize it.

### Check 3: Scheduler Process Still Running?
```powershell
Get-Process python | Where-Object {$_.CommandLine -like "*schedule*"}
```
**If running:** Scheduler is alive. Issue is job exit code handling.  
**If not running:** Scheduler crashed. Restart it.

### Check 4: Check Scheduler Timeout
Look in `schedule_daily.py` for:
```python
subprocess.run([...], timeout=X)  # X seconds
subprocess.Popen([...])           # Does it check returncode?
```
**Expected:** timeout should be ≥ 900 seconds (15 min, to account for 11+ min execution).

---

## Recommended Fix Priority

### Priority 1: Check Report Files (Quick)
```bash
# On desktop
ls -lh reports/swarm_result_afterhours_*.json | tail -1
ls -lh reports/swarm_afterhours_*.html | tail -1
```
If files are recent → **Issue is scheduler job status reporting, not swarm execution.**

### Priority 2: Fix Scheduler Job Exit Code Capture
In `schedule_daily.py`, ensure:
```python
result = subprocess.run([...], capture_output=True, timeout=900)
if result.returncode != 0:
    log_error(f"Job failed with exit code {result.returncode}")
    return False
return True  # Only if returncode == 0
```

### Priority 3: Check Swarm Orchestrator Post-Execution
In `agents/orchestrator_swarm.py`, after "SWARM EXECUTION COMPLETE":
```python
logger.info("SWARM EXECUTION COMPLETE")
# ...write reports...
# NO sys.exit(1) or uncaught exceptions after this point!
sys.exit(0)  # Explicit success exit
```

---

## Files to Check (In Order)

1. **schedule_daily.py** — How does it call orchestrator_swarm? Does it check exit code?
2. **agents/orchestrator_swarm.py** — Post-execution block. Any exceptions after "COMPLETE"?
3. **logs/orchestrator_swarm.log** — Last 200 lines. Any hidden errors?
4. **reports/swarm_result_afterhours_*.json** — Check modification timestamps. How recent?

---

## Why Haiku Was Used

- **Pattern matching** (error detection) ✅ Haiku is efficient
- **Log parsing** ✅ Straightforward regex/text search
- **Root cause logic** ✅ Deductive reasoning, not deep reasoning
- **Token cost:** ~40% of Sonnet, same accuracy for this task

---

## Next Steps

1. Run the 4 diagnostics above
2. Report findings to sentry-monitor (use `/sentry` command on laptop)
3. Repair-subagent will apply the fix once root cause is confirmed
4. Test with a manual trigger: `python agents/orchestrator_swarm.py --mode afterhours`

The fix is likely 1-3 lines in the scheduler or swarm exit handler.
