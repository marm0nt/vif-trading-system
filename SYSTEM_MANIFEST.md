# System Manifest

**Auto-generated:** 2026-05-10T20:05:51.731180

This document is the complete registry of all files, agents, skills, scripts, and configurations in the VIF Trading System. It serves as a single source of truth for what exists, where it is, and what it does.

**How to use this manifest:**
- Find a component by name or type
- See when it was last modified (git commit)
- Understand dependencies between components
- Track what's active vs archived

---

## Quick Stats

- **Total Agents:** 9
- **Total Skills:** 12
- **Total Scripts:** 14
- **Total Configs:** 4
- **Total Watchlists:** 9
- **Total Docs:** 65
- **Total Utilities:** 6

---

## Agents

Core analysis agents that drive the VIF trading system.

### `claude_research_agent`
**File:** `agents/claude_research_agent.py`
**Last Modified:** 2026-05-02 21:22:20 -0500 (a8018d0)
**Description:** Knowledge: - Layer 1: Gamma regime (positive/negative/transition) - Layer 2: Structural levels (supp

### `external_alpha_auditor`
**File:** `agents/external_alpha_auditor.py`
**Last Modified:** 2026-05-09 23:01:27 -0500 (cc22b2f)
**Description:** External Alpha Auditor — GitHub & Hugging Face MCP Integration  Critic agent uses this module to: 1.

### `finviz_orchestrator_coordinator`
**File:** `agents/finviz_orchestrator_coordinator.py`
**Description:** FinViz Orchestrator-Coordinator — Swarm Integration Layer  Manages FinViz screener execution as part

### `finviz_screener_agent`
**File:** `agents/finviz_screener_agent.py`
**Last Modified:** 2026-05-10 12:43:18 -0500 (b189e8f)
**Description:** FinViz Screener Agent — Custom Screener Framework  Runs independently from VIF pipeline. Provides "S

### `indicators`
**File:** `agents/indicators.py`
**Last Modified:** 2026-05-09 20:34:30 -0500 (e543075)
**Description:** Shared Technical Indicator Engine – VIF Trading System =============================================

### `orchestrator`
**File:** `agents/orchestrator.py`
**Last Modified:** 2026-05-07 19:41:54 -0500 (523c027)
**Description:** VIF Orchestrator - Master Delegation Agent ========================================== Master pipelin

### `orchestrator_swarm`
**File:** `agents/orchestrator_swarm.py`
**Last Modified:** 2026-05-10 12:43:18 -0500 (b189e8f)
**Description:** Swarm Intelligence Orchestrator - Phase 3 Integration  Replaces sequential subprocess orchestration 

### `watchlist_watcher`
**File:** `agents/watchlist_watcher.py`
**Last Modified:** 2026-05-02 21:22:20 -0500 (a8018d0)
**Description:** try: with open(watchlist_file, 'r') as f: 

### `weekend_catalyst_agent`
**File:** `agents/weekend_catalyst_agent.py`
**Last Modified:** 2026-05-02 21:22:20 -0500 (a8018d0)
**Description:** Weekend Catalyst Agent – VIF Trading System Scans for macro news, earnings catalysts, and sector eve

## Skills

Trading analysis and utility skills used by agents.

### `agent-design-principles`
**File:** `.claude/skills/agent-design-principles.md`
**Description:** >

### `analyzing-vif-signals`
**File:** `.claude/skills/analyzing-vif-signals.md`
**Description:** Skill: Analyzing VIF Signals

### `briefing-weekend-macro`
**File:** `.claude/skills/briefing-weekend-macro.md`
**Description:** Skill: Briefing Weekend Macro

### `computing-indicators`
**File:** `.claude/skills/computing-indicators.md`
**Description:** Skill: Computing Indicators

### `fetching-market-data`
**File:** `.claude/skills/fetching-market-data.md`
**Description:** Skill: Fetching Market Data

### `file-organizer`
**File:** `.claude/skills/file-organizer.md`
**Description:** Organizes files and folders locally using bash analysis and categorization. Use 

### `github-feature-extraction`
**File:** `.claude/skills/github-feature-extraction.md`
**Description:** End-to-end workflow for discovering, evaluating, extracting, and integrating fea

### `monitoring-catalysts`
**File:** `.claude/skills/monitoring-catalysts.md`
**Description:** Run or interpret catalyst scan results from scripts/catalyst_analysis.py. Use wh

### `orchestrating-pipelines`
**File:** `.claude/skills/orchestrating-pipelines.md`
**Description:** Skill: Orchestrating Pipelines

### `parsing-watchlists`
**File:** `.claude/skills/parsing-watchlists.md`
**Description:** Skill: Parsing Watchlists

### `screening-swing-setups`
**File:** `.claude/skills/screening-swing-setups.md`
**Description:** Skill: Screening Swing Setups

### `skill-creator`
**File:** `.claude/skills/skill-creator.md`
**Description:** Guides the creation and packaging of Claude skills. Use when creating new skills

## Scripts

Standalone analysis and utility scripts.

### Active Scripts

- **catalyst_analysis** (`scripts/active/analysis/catalyst_analysis.py`)
  - Catalyst Analysis Agent — VIF Trading System ============================================= Live Clau
- **daily_watchlist_analysis** (`scripts/active/analysis/daily_watchlist_analysis.py`)
  - import json import pandas as pd import yfinance as yf from datetime import datetime from pathlib imp
- **swing_trade_screener_v2** (`scripts/active/analysis/swing_trade_screener_v2.py`)
  - Swing Trade Screener V2 - Confirmed Buy Setups (2-4 Week Horizon) Backtested investment firm models:
- **build_may8_report** (`scripts/active/reporting/build_may8_report.py`)
  - Full Pipeline Report Builder — May 8, 2026 Applies VIF v4.0 framework to live market data already fe
- **generate_vif_master_report** (`scripts/active/reporting/generate_vif_master_report.py`)
  - VIF Master Interactive Report Generator ======================================== Reads the latest an
- **html_report_generator** (`scripts/active/reporting/html_report_generator.py`)
  - HTML Report Generator - Creates professional, readable reports Converts analysis data into formatted
- **check_usage** (`scripts/active/utilities/check_usage.py`)
  - Quick usage check and cost projection. Run this daily to monitor API spending. if not USAGE_DIR.exis

### Archived Scripts

- **advanced_analysis** (`scripts/archive/advanced_analysis.py`)
- **autonomous_improvements** (`scripts/archive/autonomous_improvements.py`)
- **daily_changelog_generator** (`scripts/archive/daily_changelog_generator.py`)
- **daily_news_monitor** (`scripts/archive/daily_news_monitor.py`)
- **generate_daily_html_report** (`scripts/archive/generate_daily_html_report.py`)
- **options_execution_plan** (`scripts/archive/options_execution_plan.py`)
- **tqqq_options_analysis** (`scripts/archive/tqqq_options_analysis.py`)

## Configuration Files

- **cache_config** (`config/cache_config.yml`)
  - Configuration file (.yml)
- **finviz_screeners** (`config/finviz_screeners.yml`)
  - Configuration file (.yml)
- **prompts_compiled** (`config/prompts_compiled.json`)
  - Configuration file (.json)
- **vif_config** (`config/vif_config.yml`)
  - Configuration file (.yml)

## Watchlists

- **AI Physical Layer & Power Infrastructure** (1 tickers) - `watchlists/AI Physical Layer & Power Infrastructure.txt`
- **AI Verticals (Supply Chain)** (1 tickers) - `watchlists/AI Verticals (Supply Chain).txt`
- **Core Growth & Macro Indices (Large-Cap Anchors)** (1 tickers) - `watchlists/Core Growth & Macro Indices (Large-Cap Anchors).txt`
- **Energy & AI (Power Convergence)** (1 tickers) - `watchlists/Energy & AI (Power Convergence).txt`
- **Speculative _ High-Beta** (1 tickers) - `watchlists/Speculative _ High-Beta.txt`
- **Trump Admin_ Onshoring** (1 tickers) - `watchlists/Trump Admin_ Onshoring.txt`
- **ai_verticals** (1 tickers) - `watchlists/legacy/ai_verticals.txt`
- **energy_ai** (1 tickers) - `watchlists/legacy/energy_ai.txt`
- **vantage_portfolio** (1 tickers) - `watchlists/legacy/vantage_portfolio.txt`

## Utilities

Shared utilities and helpers.

### `cost_tracker`
**File:** `utils/cost_tracker.py`
**Description:**  import json from datetime import datetime, timedelta from pathlib import Path i

### `error_recovery`
**File:** `utils/error_recovery.py`
**Description:** Error recovery and fallback logic for VIF Trading System. Handles API failures, 

### `signal_tracker`
**File:** `utils/signal_tracker.py`
**Description:**  import sqlite3 import json from datetime import datetime, timedelta from pathli

### `structured_logging`
**File:** `utils/structured_logging.py`
**Description:** Structured logging setup for VIF Trading System. Provides consistent logging wit

### `telemetry`
**File:** `utils/telemetry.py`
**Description:** Unified telemetry system for VIF Trading System. Logs ALL system events (agents,

### `usage_tracker`
**File:** `utils/usage_tracker.py`
**Description:** Token usage tracking and monitoring for VIF Trading System. Logs all Claude API 

## Documentation

- [AGENTS](docs/AGENTS.md)
- [DEPLOYMENT_STATUS](docs/DEPLOYMENT_STATUS.md)
- [FINVIZ_COMMAND_REFERENCE](docs/FINVIZ_COMMAND_REFERENCE.md)
- [FINVIZ_SCREENER_EXECUTION_PLAN](docs/FINVIZ_SCREENER_EXECUTION_PLAN.md)
- [FINVIZ_SWARM_INTEGRATION_GUIDE](docs/FINVIZ_SWARM_INTEGRATION_GUIDE.md)
- [FOLDER_OPERATIONS_CHECKLIST](docs/FOLDER_OPERATIONS_CHECKLIST.md)
- [GITHUB_AGENT_WORKFLOW_STATUS](docs/GITHUB_AGENT_WORKFLOW_STATUS.md)
- [GITHUB_MCP_SETUP](docs/GITHUB_MCP_SETUP.md)
- [IMPROVEMENT_RECOMMENDATIONS](docs/IMPROVEMENT_RECOMMENDATIONS.md)
- [INDEX](docs/INDEX.md)
- [LAPTOP_SETUP](docs/LAPTOP_SETUP.md)
- [MARKET_DATA_SOURCE_ANALYSIS](docs/MARKET_DATA_SOURCE_ANALYSIS.md)
- [MASTER_DOCUMENTATION_INDEX](docs/MASTER_DOCUMENTATION_INDEX.md)
- [META_TOOLS_GUIDE](docs/META_TOOLS_GUIDE.md)
- [OBSERVABILITY_GUIDE](docs/OBSERVABILITY_GUIDE.md)
- [PHASE_1_3_IMPLEMENTATION](docs/PHASE_1_3_IMPLEMENTATION.md)
- [PHASE_4_DEPLOYMENT_SUMMARY](docs/PHASE_4_DEPLOYMENT_SUMMARY.md)
- [QUICKSTART](docs/QUICKSTART.md)
- [QUICK_START_FRIDAY_PREP](docs/QUICK_START_FRIDAY_PREP.md)
- [SETUP](docs/SETUP.md)
- [SKILLS](docs/SKILLS.md)
- [SWARM_ORCHESTRATOR_GUIDE](docs/SWARM_ORCHESTRATOR_GUIDE.md)
- [SYSTEM_CONTEXT](docs/SYSTEM_CONTEXT.md)
- [SYSTEM_HEALTH](docs/SYSTEM_HEALTH.md)
- [Session-Log-2026-05-04-to-05](docs/Session-Log-2026-05-04-to-05.md)
- [TA_LIBRARY_INTEGRATION_COMPLETE](docs/TA_LIBRARY_INTEGRATION_COMPLETE.md)
- [TODAYS_REPORTS_SUMMARY](docs/TODAYS_REPORTS_SUMMARY.md)
- [TOP_10_SWARM_PROMPT_TRIGGERS](docs/TOP_10_SWARM_PROMPT_TRIGGERS.md)
- [TradingView-MCP-Setup](docs/TradingView-MCP-Setup.md)
- [DAILY_TASK_SCHEDULE_AND_AGENT_WORKFLOW](docs/agent-documentation/DAILY_TASK_SCHEDULE_AND_AGENT_WORKFLOW.md)
- [API_STATUS_REPORT](docs/archive/API_STATUS_REPORT.md)
- [AUTONOMOUS_SYSTEM_SETUP](docs/archive/AUTONOMOUS_SYSTEM_SETUP.md)
- [DOCUMENTATION_CREATED_20260502](docs/archive/DOCUMENTATION_CREATED_20260502.md)
- [IMPLEMENTATION_COMPLETE](docs/archive/IMPLEMENTATION_COMPLETE.md)
- [TRIPLE_EXCEL_DIAGNOSIS](docs/archive/TRIPLE_EXCEL_DIAGNOSIS.md)
- [analysis_20260428_051025](docs/archive/analysis_20260428_051025.md)
- [EXCEL_COLUMN_GUIDE_AND_ALPHA_EXTRACTION](docs/guides/EXCEL_COLUMN_GUIDE_AND_ALPHA_EXTRACTION.md)
- [QUICK_RECIPES](docs/guides/QUICK_RECIPES.md)
- [optimization-checklist](docs/guides/optimization-checklist.md)
- [report-format](docs/guides/report-format.md)
- [usage-tracking](docs/guides/usage-tracking.md)
- [orchestrator_framework](docs/orchestrator_framework.md)
- [01-cursor-desktop-setup](docs/setup-guides/01-cursor-desktop-setup.md)
- [02-desktop-python-setup](docs/setup-guides/02-desktop-python-setup.md)
- [03-configuration-reference](docs/setup-guides/03-configuration-reference.md)
- [04-troubleshooting](docs/setup-guides/04-troubleshooting.md)
- [QUICK_SETUP](docs/setup-guides/QUICK_SETUP.md)
- [README](docs/setup-guides/README.md)
- [desktop-setup](docs/setup-guides/desktop-setup.md)
- [ide-setup](docs/setup-guides/ide-setup.md)
- [external-alpha-audit](docs/skills/external-alpha-audit.md)
- [finviz-custom-screeners](docs/skills/finviz-custom-screeners.md)
- [repo-navigation](docs/skills/repo-navigation.md)
- [AGENT_COMBINATIONS](docs/system/AGENT_COMBINATIONS.md)
- [CHANGELOG](docs/system/CHANGELOG.md)
- [LEVERAGE_GUIDE](docs/system/LEVERAGE_GUIDE.md)
- [system_context](docs/system/system_context.md)
- [~$ENT_COMBINATIONS](docs/system/~$ENT_COMBINATIONS.md)
- [~$stem_context](docs/system/~$stem_context.md)
- [OPTIMIZED_DAILY_TRADING_WORKFLOW](docs/workflows/OPTIMIZED_DAILY_TRADING_WORKFLOW.md)
- [~$ASE_4_DEPLOYMENT_SUMMARY](docs/~$ASE_4_DEPLOYMENT_SUMMARY.md)
- [~$INDEX](docs/~$INDEX.md)
- [~$STEM_CONTEXT](docs/~$STEM_CONTEXT.md)
- [~$THUB_MCP_SETUP](docs/~$THUB_MCP_SETUP.md)
- [~$adingView-MCP-Setup](docs/~$adingView-MCP-Setup.md)

---

## Telemetry & Observability

This manifest is **static** (updated by running `generate_manifest.py`). For **dynamic** system observability, see:

- `logs/telemetry.jsonl` — Runtime event log (agents starting/ending, APIs called, errors, etc.)
- `docs/SYSTEM_HEALTH.md` — System health dashboard (updated periodically)
- `logs/*.log` — Agent-specific logs (structured)

## Integration with CI/CD

To keep this manifest up-to-date:

```bash
# Add to pre-commit hook or CI pipeline
python scripts/generate_manifest.py
git add SYSTEM_MANIFEST.md
git commit -m "Update system manifest"
```

