# VIF Trading System Memory Index

## 🚨 ACTIVE SESSION HANDOFF (READ FIRST)
- [Scheduler Path Errors — HAIKU DIAGNOSTIC (2026-05-14)](scheduler_path_errors_haiku_diagnostic.md) — **ROOT CAUSE FOUND:** venv path lookup is wrong. `.claude\venv\` doesn't exist. Folder name is `vif-trading-system` not `vif_trading_system`. Fix: 2-3 lines in schedule_daily.py
- [Session Handoff: Scheduler Issues + Sync Setup (2026-05-13)](session_handoff_scheduler_issues.md) — After-hours pipeline failing 3 days in a row; sentry-monitor + repair-subagent now available
- [Scheduler Diagnostics — Haiku Analysis (2026-05-13)](scheduler_diagnostics_haiku.md) — Exit code capture investigation

## User Preferences & Policies
- [Operational Autonomy & Lead Orchestrator (2026-05-13)](feedback_operational_autonomy.md) — **ACTIVE:** Agents execute without approval, orchestrator leads all workflows, bypass permissions globally, don't break anything
- [Public Submission Protocol](feedback_public_submissions.md) — All public repos/skills require Martin's permission; Martin is sole author, never "Agent"
- [Autonomy & Decision-Making](feedback_autonomy.md) — Execute autonomously; only escalate irreversible/genuinely ambiguous decisions

## Watchlists
- [Institutional Watchlist Structure (2026-05-05)](watchlist_structure.md) — 6 watchlists, 4-tier VIF hierarchy, 170 tickers, report at reports/watchlist_institutional_structure.html

## Architecture & Configuration
- [VIF System Current State](vif_system_state.md) — Operational status, last run (2026-05-05 02:14), recovery procedures
- [Known Issues & Workarounds](known_issues.md) — 5 documented issues + Environmental Reset workflow for CDP reconnection
- [GitHub Repos for VIF System Improvement](github_repos_improvement_roadmap.md) — Top 5 open-source repos with 30-day implementation roadmap
- [Anthropic API Improvements (May 2026)](anthropic_api_improvements_may2026.md) — Cost optimization opportunities and recommended changes

## Quick Reference

### Recommended Quick Wins (May 2026)
1. **Prompt Caching** (5 min effort, save $0.012/day)
2. **Hybrid Model Routing** (moderate effort, save $0.05/day)
3. **Structured Outputs** (easy, eliminate JSON errors)

### 30-Day Optimization Roadmap
- **Week 1:** TA Library + Backtesting.py
- **Week 2-3:** TradingAgents debate + PyBroker acceleration
- **Week 4+:** AgenticTrading (Phase 2, defer)

### Current System Status
- **Cost:** $0.13/day (potential to reduce to $0.068/day)
- **Models:** Sonnet 4.6 + Haiku 4.5 + Opus 4.7 (all current)
- **Cache:** 24-hour local disk (insulated from API changes)
- **Scheduler:** Running continuously (next jobs May 2 at 07:00/08:45/09:35)
