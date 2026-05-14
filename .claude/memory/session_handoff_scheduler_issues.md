---
name: Session Handoff - Scheduler Issues + Cross-Device Setup
description: Context for laptop session continuation. Scheduler running on desktop but jobs failing silently. Workflows not consistently posting. Sentry agents available for diagnosis.
type: project
---

# Session Handoff (2026-05-13 → Laptop)

## What Was Just Built (Desktop, This Session)

1. **Brain-sync framework** — `brain-sync.bat`, `sync.bat`, `SYNC.md` for cross-device git sync
2. **Auto-push post-commit hook** — `.git/hooks/post-commit` now auto-pushes every commit to GitHub in background
3. **Self-healing swarm agents** (new in `.claude/agents/`):
   - `sentry-monitor` (Haiku) — scans `logs/` for errors, triages by severity
   - `repair-subagent` (Sonnet) — receives A2A JSON handoff, applies surgical fixes
4. **All synced to GitHub via origin/main** — laptop just needs `git pull origin main`

## Active Problem: Scheduler Failures

**Issue:** Workflows are not consistently running when scheduled. After-hours pipeline has failed 3 days in a row.

### Evidence (from `logs/run_history.json`)
```json
{
  "date": "2026-05-11T16:05:xx", "label": "after_hours_swarm_orchestrator", "success": false
},
{
  "date": "2026-05-12T16:05:04", "label": "after_hours_swarm_orchestrator", "success": false
},
{
  "date": "2026-05-12T16:05:27", "label": "after_hours_swarm_orchestrator", "success": false
},
{
  "date": "2026-05-13T16:05:24", "label": "after_hours_swarm_orchestrator", "success": false
}
```

### Scheduler State (from `logs/scheduler.log`)
- Scheduler **IS running** (last started 2026-05-13 12:11:23)
- All 8 job slots registered correctly:
  - Weekdays 07:00 — Premarket Pipeline (Swarm)
  - Weekdays 07:30 — FinViz Discovery (Independent, 19 screeners)
  - Weekdays 08:45 — Premarket Full 1mo VIF
  - Weekdays 09:35 — Market-Open Swing
  - Weekdays 16:05 — After-Hours 5d VIF + conviction ⚠️ **FAILING**
  - Fridays 16:30 — Friday close
  - Saturday 08:00 / Sunday 18:00 — Weekend macro briefing
- Architecture: Multi-agent swarm with KV cache sharing (Phase 1-3 deployed)
- Scheduler started job at 16:05:24 today but didn't log success/failure visible in tail

### What This Means
- The cron-style scheduling itself works (jobs fire at the right time)
- The **job EXECUTION** is failing silently (returns `success: false`)
- Other jobs may have similar issues — run_history only showed afterhours tail

## Cross-Device Setup Status

### Desktop (this machine)
- `schedule_daily.py` (or similar) running as background Python process
- Scheduler log: `logs/scheduler.log`
- Run history: `logs/run_history.json`
- Auto-push hook: ✅ installed
- Branch: main, clean working tree

### Laptop (target)
- ❌ Does NOT have the scheduler running
- ❌ Needs `git pull origin main` to get latest agents + brain-sync framework
- ❌ Needs auto-push hook installed: `powershell scripts\install-brain-sync-hook.ps1`
- ❌ Needs `.env` copied manually (API key)
- ✅ Already has the project folder, just needs sync

## Recommended Next Steps (on Laptop)

### Step 1: Sync the brain
```powershell
cd C:\Users\marti\vif-trading-system  # or wherever it lives on laptop
git pull origin main
powershell scripts\install-brain-sync-hook.ps1  # install auto-push hook
```

### Step 2: Diagnose scheduler with sentry-monitor
Start a new Claude Code session and invoke:
```
@sentry-monitor scan logs/ for after-hours pipeline failures
```

The agent will:
1. Parse `logs/scheduler.log`, `logs/orchestrator_swarm.log`, `logs/run_history.json`
2. Identify the actual error (likely import error, API timeout, or swarm consensus failure)
3. Build A2A JSON handoff for repair-subagent
4. Repair-subagent applies surgical fix and commits

### Step 3: Investigate why jobs return success: false
Likely culprits to check:
- `logs/orchestrator_swarm.log` for stack traces around 16:05 timestamps
- `agents/orchestrator_swarm.py` after-hours mode execution path
- Swarm consensus failures (LRAgent KV cache, gossip routing)
- API timeouts during VIF analysis
- yfinance data fetch failures after market close

### Step 4: Cross-check what's actually running
On laptop, check if you want the scheduler running there too (or keep it desktop-only):
```powershell
# To check what's running on desktop (you can do this remotely via git)
# Otherwise, check Task Scheduler / Task Manager on desktop
```

**Decision needed:** Do you want the scheduler running on BOTH devices (redundant) or just one (single source of truth)? If both, you'll get duplicate API calls. Recommend: **keep scheduler on desktop only**, use laptop for development + investigation.

## Known Architecture Context

- **VIF v4.0** Volatility Imbalance Framework
- **Cost:** $0.07/day (after swarm KV cache 50% reduction)
- **Models:** Sonnet 4.6 (analysis) + Haiku 4.5 (parsing) + Opus 4.7 (synthesis)
- **Watchlists:** vantage_portfolio (85 tickers), ai_verticals, energy_ai, etc.
- **Pipeline modes:** premarket / market_open / afterhours / weekend
- **Swarm Phase 1-3:** COMPLETE & PRODUCTION-READY (LRAgent KV + LatentMAS + gossip + consensus)

## Files to Read on Laptop (priority order)

1. `logs/run_history.json` — see which jobs are failing
2. `logs/scheduler.log` (last 100 lines) — confirm scheduler is running
3. `logs/orchestrator_swarm.log` (last 200 lines) — find actual error
4. `agents/orchestrator_swarm.py` — afterhours mode implementation
5. `.claude/memory/MEMORY.md` — full project memory index
6. `.claude/memory/vif_system_state.md` — current system state
7. `.claude/memory/known_issues.md` — 5 documented issues + workarounds

## How to Apply

When starting fresh on laptop:
1. Read this file first (`.claude/memory/session_handoff_scheduler_issues.md`)
2. Read `MEMORY.md` for full project index
3. Run `git pull origin main` to ensure laptop is up to date
4. Invoke `@sentry-monitor` to start automated triage
5. Let `@repair-subagent` apply fixes (it auto-commits + auto-pushes)

The sentry → repair flow handles failed jobs automatically once you trigger it.

## Why This Memory Exists

This file is the "session bridge" — it's the **first thing** the laptop's Claude Code session should load to understand:
- What was just built (sync framework, sentry agents)
- What's broken (after-hours pipeline)
- What to do next (run sentry-monitor, let repair-subagent fix it)
- What NOT to touch (scheduler is desktop-only, don't double-run)

Memory files auto-load via `.claude/memory/` on every Claude Code session, so this context carries forward without manual copy-paste.
