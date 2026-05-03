# VIF Trading System: Folder Operations Checklist

**Analysis Date:** May 2, 2026  
**Current Structure:** 16 top-level folders (excluding hidden/cache)  
**Status:** Well-organized with clear separation of concerns

---

## 🔴 CRITICAL PATH — Daily Checks During Scheduled Runs

| Folder | Check Frequency | What to Look For | Why It Matters |
|--------|-----------------|------------------|----------------|
| **`config/`** | Daily (before pipeline) | `vif_config.yml`, `cache_config.yml` present; no syntax errors | Kill switches (K1-K6), model selection, batch sizes, cache TTL must be current |
| **`agents/`** | Daily (during execution) | All 4 core agents executable: `watchlist_watcher.py`, `orchestrator.py`, `indicators.py`, `weekend_catalyst_agent.py` | If agents are missing/corrupted, entire pipeline fails |
| **`.claude/agents/`** | Daily (reference) | Agent spec files (.md) match implementation in `agents/` folder | Ensures Claude agents match Python implementations |
| **`watchlists/`** | Daily (before pipeline) | 3 watchlist files present: `vantage_portfolio.txt`, `ai_verticals.txt`, `energy_ai.txt`; no empty files | If watchlists are empty/missing, no tickers to analyze |
| **`logs/`** | Daily (after execution) | Check latest log file for errors: `orchestrator_*.log`, `catalyst_*.log`; exit codes (0=success, 1=failure) | Reveals silent failures, timeouts, API errors before they cascade |
| **`reports/`** (today's) | Daily (after execution) | Latest `pipeline_premarket_YYYYMMDD_*.html` exists; file size >20KB (means data was analyzed) | Confirms pipeline ran and produced output |
| **`data/`** (cache) | Daily (pre-pipeline) | Check `yfinance_cache.pkl` timestamp; should be <24h old | Stale cache = old prices analyzed; fresh cache = current data |

**Daily Validation Steps:**
```bash
# Before morning pipeline run:
1. Check config/vif_config.yml exists & has correct kill switches
2. Check agents/ folder has all 4 core .py files
3. Check watchlists/ has 3 .txt files with tickers
4. Check data/yfinance_cache.pkl timestamp (should be <24h)

# After pipeline run:
5. Check logs/ for latest log file (exit code 0?)
6. Check reports/ for HTML output file (size >20KB?)
7. If either fails, review error message before next run
```

---

## 🟡 REFERENCE FOLDERS — Weekly/On-Demand Checks

| Folder | Check Frequency | What to Look For | When to Check | Use Case |
|--------|-----------------|------------------|---------------|----------|
| **`docs/`** | Weekly + on-demand | `CLAUDE.md`, `MARKET_DATA_SOURCE_ANALYSIS.md`, setup guides, architecture docs | Before deploying new agent; when troubleshooting unfamiliar workflow | How-to guides, architecture decisions, operational reference |
| **`.claude/skills/`** | On-demand (per skill) | `github-feature-extraction.md`, `monitoring-catalysts.md`, `analyzing-vif-signals.md` | Before running a skill; when understanding what a skill does | Prompt logic, trigger conditions, example inputs/outputs |
| **`utils/`** | Weekly (dependency check) | `cost_tracker.py`, `signal_tracker.py`, `usage_tracker.py`, `error_recovery.py` | When troubleshooting data, cost estimates, or error handling | Helper functions, external API wrappers, data transformation logic |
| **`scripts/`** | Weekly (audit) | `catalyst_analysis.py`, `swing_trade_screener_v2.py`, `advanced_analysis.py` | When analyzing edge cases or adding new analysis types | One-shot analysis scripts, research tools, backtesting helpers |
| **`examples/`** | On-demand (learning) | `watchlist_watcher_with_caching_example.py` | When building similar functionality or understanding patterns | Code examples, reference implementations, working patterns |
| **`tests/`** | Per development cycle | `test_harness.py`, `test_api_key.py` | Before pushing changes; when validating new agent code | Offline testing (no API costs), integration validation |

**When to Check Each:**
- **`docs/`** — "I don't understand how [feature] works" → Read corresponding guide
- **`.claude/skills/`** — "What does the gamma-regime-detector skill do?" → Read skill spec
- **`utils/`** — "Why did the cost tracker say $0.15 instead of $0.13?" → Review cost_tracker.py
- **`scripts/`** — "How can I backtest a new kill switch?" → Review advanced_analysis.py
- **`examples/`** — "How do I add caching to a new script?" → Read watchlist_watcher example
- **`tests/`** — "Is my new agent safe to run?" → Run test_harness.py (no API calls)

---

## 🟢 KNOWLEDGE FOLDERS — Reference Only (Not Operational)

| Folder | Contents | Check Frequency | Why Not Daily | Use Case |
|--------|----------|-----------------|---------------|----------|
| **`.vscode/`** | VSCode settings, debug configs | Never (auto-managed) | Development settings, not execution | IDE configuration only |
| **`vault/`** | Secure storage (if in use) | Audit only (monthly) | Not part of execution pipeline | Credential storage, sensitive configs |
| **`venv/`** or Python virtualenv | Python dependencies | Never (pre-installed) | Environment setup, not execution | Isolated Python environment |
| **`__pycache__/`** | Python compiled bytecode | Never (auto-generated) | Cache files, cleaned on reinstall | Python runtime optimization |
| **`.git/`** | Git history, branches, commits | Never (audit only) | Version control, not execution | Historical record, rollback capability |
| **`reports/archive/`** | Old reports (>30 days) | Never (reference only) | Historical data, not current analysis | Pattern recognition, post-mortems |

**Why These Aren't Daily Critical:**
- `.vscode/` — Settings auto-load; no daily check needed
- `vault/` — Credentials stored once at setup
- `venv/` — Installed once; only rebuild if dependency changes
- `__pycache__/` — Auto-generated; safe to delete anytime
- `.git/` — Only matters if reverting or investigating history
- `reports/archive/` — Historical reference only

---

## ⚠️ GAPS IDENTIFIED & RECOMMENDATIONS

### Current Gaps

| Gap | Impact | Recommendation | Effort |
|-----|--------|----------------|--------|
| No `logs/` rotation | Logs can grow unbounded; hard to find recent errors | Add automated 30-day log rotation + compress old logs | Low |
| No `reports/archive/` subfolder | Reports folder becomes cluttered | Auto-move reports >30 days to `reports/archive/` | Low |
| No `cache/` explicit folder | Caching logic unclear; mixed with data/ | Create explicit `cache/` folder, move yfinance_cache.pkl there | Low |
| No `.env` validation | Can run with missing API keys | Add startup check: `python tests/test_api_key.py` before pipeline | Low |
| No `CHANGELOG.md` at root | Git history exists but not human-readable | Create/update `CHANGELOG.md` with summary of recent changes | Low |

### Recommended Additions

```
vif-trading-system/
├── config/                    ✓ (exists)
├── agents/                    ✓ (exists)
├── .claude/agents/            ✓ (exists)
├── .claude/skills/            ✓ (exists)
├── docs/                      ✓ (exists)
├── scripts/                   ✓ (exists)
├── utils/                     ✓ (exists)
├── watchlists/                ✓ (exists)
├── reports/
│   ├── premarket/             ← NEW: daily VIF analysis
│   ├── swing-trades/          ← NEW: swing setup screener
│   ├── catalysts/             ← NEW: macro/earnings analysis
│   ├── weekend/               ← NEW: weekend briefing
│   └── archive/               ← NEW: reports >30 days old
├── data/
│   ├── cache/                 ← NEW: explicit caching folder
│   └── yfinance_cache.pkl
├── logs/
│   ├── 2026-05/               ← NEW: monthly log folders
│   └── archive/               ← NEW: logs >30 days old
├── tests/                     ✓ (exists)
├── examples/                  ✓ (exists)
├── CHANGELOG.md               ← NEW: human-readable changelog
└── DEPLOYMENT_CHECKLIST.md    ← NEW: daily ops reference
```

---

## 📋 Daily Operations Quick Reference

### Morning (Before 08:45 Pipeline)
1. ✅ Check `config/vif_config.yml` (kill switches on?)
2. ✅ Check `watchlists/` (3 files present?)
3. ✅ Check `data/cache/` timestamp (fresh?)
4. ✅ Check `logs/latest.log` (any errors from yesterday?)

### After Pipeline (16:05)
5. ✅ Check `reports/premarket_*.html` (exists & >20KB?)
6. ✅ Check `logs/` for today's execution (exit 0?)
7. ✅ If errors: review `logs/catalyst_analysis.log` or `logs/orchestrator.log`

### Weekly (Friday)
8. ✅ Check `docs/` for outdated references (anything still mention deprecated agent?)
9. ✅ Archive old reports: move `reports/*` >30 days to `reports/archive/`
10. ✅ Compress old logs: move `logs/*` >30 days to `logs/archive/`

### Monthly
11. ✅ Review `CHANGELOG.md` — any patterns in errors/changes?
12. ✅ Audit `.claude/agents/` specs — do they match Python implementations?
13. ✅ Check `vault/` credentials — anything expire?

---

## Summary: Checklist Item Status

### ✅ COMPLETED — Folder Analysis

- [x] **Critical Path folders identified** — 7 folders, daily checks defined
- [x] **Reference folders categorized** — 6 folders, weekly/on-demand use cases defined
- [x] **Knowledge folders separated** — 6 folders, marked as non-operational
- [x] **Table format delivered** — Folder | Category | Frequency | Why | What to Look For
- [x] **Gaps highlighted** — 5 gaps identified with recommendations
- [x] **Additions recommended** — 7 new subfolders suggested (low effort)
- [x] **Daily ops checklist created** — Morning, after-pipeline, weekly, monthly steps

**Your VIF system folder structure is well-organized.** No urgent gaps; recommended additions are all low-effort.

