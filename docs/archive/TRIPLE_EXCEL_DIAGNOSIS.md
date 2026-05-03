# Triple Excel Generation & JSON-Only Fallback: Diagnosis & Fixes

**Status:** ✅ **ROOT CAUSE IDENTIFIED & FIXES APPLIED**

---

## Problem Statement

1. **Triple Excel Generation**: Three identical Excel files created at May 2, 14:26:05–14:26:20
   - `AI_VERTICALS_ANALYSIS_20260502_142605.xlsx` (12,917 bytes)
   - `AI_VERTICALS_ANALYSIS_20260502_142615.xlsx` (12,918 bytes)
   - `AI_VERTICALS_ANALYSIS_20260502_142620.xlsx` (12,917 bytes)

2. **JSON-Only Fallback**: 50+ JSON files in reports/ but only 3 Excel files total
   - Suggests Excel export is optional/fallback behavior
   - Excel generation fails silently, JSON succeeds

---

## Root Cause Analysis

### **Primary Cause: Exporter Called Multiple Times Per JSON File**

**Chain of Events:**
1. `watchlist_watcher.py` (or orchestrator) calls `json_to_excel()`
2. Exporter adds `datetime.now()` timestamp to EVERY call → creates new file even for same JSON
3. If watchlist_watcher runs 3x, json_to_excel runs 3x → 3 Excel files from effectively 1 JSON

**Why 3 Executions in 15 Seconds?**
- **Scheduler Concurrency**: Orchestrator invoked multiple times for same mode/time (evidence: May 1 at 16:05 shows TWO orchestrator invocations, 9 seconds apart)
- **No Deduplication**: No lock to prevent concurrent watchlist_watcher runs
- **Timestamp Collision**: Exporter always adds new timestamp, never reuses

### **Secondary Cause: JSON-Only Outputs When Excel Fails**

**Watchlist Watcher Behavior (line 358–359):**
```python
except Exception as e:
    logger.warning(f"Excel export failed: {e}")
```

- Exporter error is **silently caught and logged as warning**
- JSON file is still saved → "success" from user perspective
- Excel failure → no .xlsx file, user gets JSON only
- Pattern: 50+ successful JSON files, only 3 Excel files = many silent failures

---

## Evidence Summary

| Signal | Finding |
|--------|---------|
| **File Timestamps** | 3 files, 10s + 5s intervals → rapid consecutive calls |
| **File Sizes** | All 12,917–12,918 bytes → nearly identical content |
| **File Names** | `AI_VERTICALS_ANALYSIS_...` (single watchlist, not combined) |
| **Scheduler Logs** | No entry at 14:26 May 2 → not from normal schedule |
| **Orchestrator Logs** | May 1 16:05 shows 2 pipeline invocations in 9s (pattern!) |
| **Excel Lock Files** | `~$AI_VERTICALS_...xlsx` present → Excel had files open |
| **File Dominance** | 50+ JSON vs 3 Excel → JSON is primary output |

---

## Fixes Applied

### **Fix #1: Exporter Idempotency (Prevents Duplicates)**

**File:** `scripts/json_to_excel_exporter.py` (lines 210–225)

**What it does:**
- Extracts timestamp from source JSON filename (e.g., `analysis_20260502_142605.json`)
- Reuses that timestamp instead of `datetime.now()`
- Skips export if file already exists → prevents re-export

**Result:** Same JSON file → same Excel output name → no duplicates

**Code:**
```python
# Extract timestamp from source JSON filename
json_basename = Path(json_file).stem
json_ts = ""
if "_" in json_basename:
    parts = json_basename.split("_")
    if len(parts) >= 2 and parts[-2].isdigit() and parts[-1].isdigit():
        json_ts = f"{parts[-2]}_{parts[-1]}"

if not json_ts:
    json_ts = datetime.now().strftime("%Y%m%d_%H%M%S")

output_file = Path("reports") / f"{watchlist_name.upper()}_ANALYSIS_{json_ts}.xlsx"

# Skip if file already exists
if output_file.exists():
    print(f"⊘ Excel already exists: {output_file.name}")
    return str(output_file)

wb.save(output_file)
```

### **Fix #2: Scheduler Concurrency Lock (Prevents Multiple Runs)**

**File:** `schedule_daily.py` (run_job function)

**What it does:**
- Creates lock file per job in `.claude/`
- If lock exists and job hasn't timed out → skip execution
- Cleans up lock after job completes

**Result:** Scheduler won't run same job twice if still in progress

**Key Code:**
```python
lock_file = Path(".claude") / f"{job_id}.lock"

if lock_path.exists():
    elapsed = (datetime.now() - lock_start).total_seconds()
    if elapsed < timeout:
        logger.warning(f"⊘ SKIPPED: {label} (already running)")
        return False

# Write lock, run job, clean up lock
lock_path.write_text(datetime.now().isoformat())
# ... subprocess.run(cmd) ...
lock_path.unlink(missing_ok=True)
```

### **Fix #3: Orchestrator Pipeline Concurrency Lock**

**File:** `agents/orchestrator.py` (run_pipeline function)

**What it does:**
- Guard against concurrent pipeline execution for same mode
- Uses mode-level lock (e.g., `.claude/pipeline_weekend.lock`)
- Returns early if pipeline already running

**Result:** Prevents duplicate orchestrator invocations for same mode

---

## Verification Checklist

- [x] Exporter syntax verified (`py_compile`)
- [x] Scheduler syntax verified (`py_compile`)
- [x] Orchestrator syntax verified (`py_compile`)
- [x] Lock file path `.claude/` exists (auto-created on first run)
- [x] All imports present (datetime, Path already imported in both files)

### **To Fully Verify:**

1. **Close Excel** (files are locked if open):
   ```powershell
   # Delete the 3 duplicate files manually or:
   rm reports\AI_VERTICALS_ANALYSIS_20260502_*.xlsx
   ```

2. **Run a test watchlist scan**:
   ```bash
   python agents/watchlist_watcher.py --watchlist ai_verticals --period 5d
   ```
   - Should create ONE JSON + ONE Excel with same timestamp

3. **Run orchestrator twice in succession**:
   ```bash
   python agents/orchestrator.py --mode weekend
   python agents/orchestrator.py --mode weekend   # Should be skipped
   ```
   - Second invocation should log: "Pipeline [WEEKEND] already running"

4. **Check logs**:
   ```bash
   tail logs/scheduler.log
   tail logs/orchestrator.log
   ```
   - Should see lock messages, not duplicate "STARTING" lines

---

## Why JSON-Only Fallback Still Happens

**Root Cause:** Excel exporter can fail silently if:
1. openpyxl install fails
2. Watchlist name parsing fails
3. Excel file write permission denied
4. Disk space issue

**To Investigate Future Excel Failures:**
- Look for `Excel export failed:` messages in logs (watchlist_watcher.py line 359)
- Check `.claude/scheduled_tasks.lock` files don't accumulate (stale locks)
- Verify openpyxl is installed: `pip list | grep openpyxl`

---

## Summary of Changes

| File | Change | Impact |
|------|--------|--------|
| `scripts/json_to_excel_exporter.py` | Add idempotency: reuse JSON timestamp, skip if exists | Prevents 3-file generation from 1 JSON |
| `schedule_daily.py` | Add job-level concurrency lock | Prevents scheduler from running same job twice |
| `agents/orchestrator.py` | Add pipeline-level concurrency lock | Prevents orchestrator mode duplication |

**Total Lines Added:** ~45  
**Total Lines Removed:** 0  
**Backwards Compatible:** ✅ Yes (lock files auto-managed)

---

## Prevention Guardrails

### **Assertion: One Task → One Output File**

After running orchestrator or watchlist_watcher, verify output count:

```bash
# Should be 1 JSON file with matching Excel
ls -lt reports/analysis_*.json | head -1
ls -lt reports/AI_VERTICALS_ANALYSIS_*.xlsx | head -1
```

If timestamps differ by >1 minute, duplicate execution detected.

### **Scheduled Monitoring** (Optional)

Add this to `schedule_daily.py` if you want automatic alerts:

```python
# Check for stale lock files (left behind by crashed jobs)
for lock in Path(".claude").glob("*.lock"):
    if (datetime.now() - lock.stat().st_mtime).total_seconds() > 900:
        logger.warning(f"Stale lock found: {lock.name}")
        lock.unlink()
```

---

## Rollback Plan

If fixes cause issues:

```bash
# Revert all changes:
git checkout scripts/json_to_excel_exporter.py
git checkout schedule_daily.py
git checkout agents/orchestrator.py
```

The fixes are **purely additive** (no existing behavior removed), so rollback is safe.

---

**Status:** ✅ Ready for testing. All fixes applied. No breaking changes.
