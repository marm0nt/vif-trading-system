# VIF Trading System Documentation Index

**Navigate the complete documentation here. Updated automatically on each commit.**

---

## 🎯 Start Here

**New to VIF?** Start with these in order:
1. [QUICK_START_SETUP.md](#setup) — Installation (15 min)
2. [QUICK_RECIPES.md](#quick-recipes) — Copy-paste workflows
3. [LEVERAGE_GUIDE.md](#understanding-the-system) — How to trade with these tools

**Returning user?** Jump to:
- [System Status](#current-status) — Is everything working?
- [Today's Briefing](#todays-briefing) — What changed?
- [Quick Recipes](#quick-recipes) — Run a command

---

## 📚 Documentation by Category

### Setup & Configuration
- **[setup/QUICK_SETUP.md](setup/QUICK_SETUP.md)** — 5-minute Python + API key setup
- **[setup/01-cursor-desktop-setup.md](setup/01-cursor-desktop-setup.md)** — Cursor IDE configuration
- **[setup/02-desktop-python-setup.md](setup/02-desktop-python-setup.md)** — Python environment setup
- **[setup/03-configuration-reference.md](setup/03-configuration-reference.md)** — All config options
- **[setup/04-troubleshooting.md](setup/04-troubleshooting.md)** — Common issues + fixes

### System Architecture
- **[system/system_context.md](system/system_context.md)** — Complete agent + framework inventory (auto-updated)
- **[system/LEVERAGE_GUIDE.md](system/LEVERAGE_GUIDE.md)** — Backtested patterns + consensus best practices
- **[system/AGENT_COMBINATIONS.md](system/AGENT_COMBINATIONS.md)** — How agents work together
- **[system/CHANGELOG.md](system/CHANGELOG.md)** — Auto-generated change history (updated on each commit)

### Quick Reference
- **[guides/QUICK_RECIPES.md](guides/QUICK_RECIPES.md)** — Copy-paste commands for 10 common tasks
- **[guides/report-format.md](guides/report-format.md)** — Understanding HTML reports
- **[AGENTS.md](AGENTS.md)** — Agent reference (legacy, see system/system_context.md)
- **[SKILLS.md](SKILLS.md)** — Skill reference (legacy, see system/system_context.md)

### Workflows & Operations
- **[workflows/OPTIMIZED_DAILY_TRADING_WORKFLOW.md](workflows/OPTIMIZED_DAILY_TRADING_WORKFLOW.md)** — Daily routine
- **[agent-documentation/DAILY_TASK_SCHEDULE_AND_AGENT_WORKFLOW.md](agent-documentation/DAILY_TASK_SCHEDULE_AND_AGENT_WORKFLOW.md)** — What runs when
- **[guides/usage-tracking.md](guides/usage-tracking.md)** — Monitor API costs
- **[DEPLOYMENT_STATUS.md](DEPLOYMENT_STATUS.md)** — System health check

### Advanced Topics
- **[MASTER_DOCUMENTATION_INDEX.md](MASTER_DOCUMENTATION_INDEX.md)** — Comprehensive reference
- **[META_TOOLS_GUIDE.md](META_TOOLS_GUIDE.md)** — Using GitHub analysis tools
- **[orchestrator_framework.md](orchestrator_framework.md)** — Orchestrator internals
- **[SWARM_ORCHESTRATOR_GUIDE.md](SWARM_ORCHESTRATOR_GUIDE.md)** — Swarm intelligence details

### Data & Market Analysis
- **[MARKET_DATA_SOURCE_ANALYSIS.md](MARKET_DATA_SOURCE_ANALYSIS.md)** — Data sources (yfinance, etc.)
- **[TA_LIBRARY_INTEGRATION_COMPLETE.md](TA_LIBRARY_INTEGRATION_COMPLETE.md)** — Technical analysis library
- **[TradingView-MCP-Setup.md](TradingView-MCP-Setup.md)** — TradingView integration

---

## Current Status

### System Health
- **Last Update:** Auto-generated on commit
- **Agents Active:** 7 core agents (orchestrator, vif-analyst, catalyst-monitor, swing-screener, weekend-analyst, report-builder, cost-analyzer)
- **Frameworks:** Multi-agent orchestrator + Swarm intelligence (consensus routing)
- **Daily Cost:** ~$0.13 (~13,000 tokens/day)
- **Watchlists:** 3 (vantage_portfolio, ai_verticals, energy_ai)

### Recent Changes
Check **[system/CHANGELOG.md](system/CHANGELOG.md)** for automated updates from the last 10 commits.

---

## Today's Briefing

### What to Run Today

**Morning (08:30 CT):**
```bash
python agents/orchestrator.py --mode premarket
```
Output: [reports/premarket_YYYY-MM-DD.html](../reports/)

**After Market Open (09:35 CT):**
```bash
python agents/orchestrator.py --mode market_open
```
Output: [reports/market_open_YYYY-MM-DD.html](../reports/)

**End of Day (16:05 CT):**
```bash
python agents/orchestrator.py --mode afterhours
```
Output: [reports/afterhours_YYYY-MM-DD.html](../reports/)

**All Commands**
See **[guides/QUICK_RECIPES.md](guides/QUICK_RECIPES.md)** for 10 ready-to-copy workflows.

---

## Quick Recipes

Copy and paste these into your terminal:

### 1. Daily Premarket
```bash
cd C:\Users\marti\vif-trading-system && python agents/orchestrator.py --mode premarket
```

### 2. Monday Morning Macro
```bash
cd C:\Users\marti\vif-trading-system && python agents/orchestrator.py --mode weekend
```

### 3. Find Best Setups
```bash
cd C:\Users\marti\vif-trading-system && python scripts/swing_trade_screener_v2.py --watchlist ai_verticals
```

### 4. Deep Dive (1 Ticker)
```bash
cd C:\Users\marti\vif-trading-system && python agents/orchestrator.py --ticker NVDA --period 1mo
```

### 5. Check Earnings Risk
```bash
cd C:\Users\marti\vif-trading-system && python scripts/catalyst_analysis.py --watchlist vantage_portfolio
```

See **[guides/QUICK_RECIPES.md](guides/QUICK_RECIPES.md)** for 5 more + troubleshooting.

---

## Understanding the System

### Level 1: Beginner (Want to run daily analysis)
1. **[setup/QUICK_SETUP.md](setup/QUICK_SETUP.md)** — Get it running
2. **[guides/QUICK_RECIPES.md](guides/QUICK_RECIPES.md)** — Run commands
3. **[guides/report-format.md](guides/report-format.md)** — Read reports

### Level 2: Intermediate (Want to understand how signals work)
1. **[system/LEVERAGE_GUIDE.md](system/LEVERAGE_GUIDE.md)** — Backtested patterns (START HERE)
2. **[system/system_context.md](system/system_context.md)** — What agents do
3. **[system/AGENT_COMBINATIONS.md](system/AGENT_COMBINATIONS.md)** — How they work together
4. **[DEPLOYMENT_STATUS.md](DEPLOYMENT_STATUS.md)** — System architecture

### Level 3: Advanced (Want to modify / extend)
1. **[system/orchestrator_framework.md](orchestrator_framework.md)** — Master pipeline
2. **[system/SWARM_ORCHESTRATOR_GUIDE.md](SWARM_ORCHESTRATOR_GUIDE.md)** — Consensus logic
3. **[META_TOOLS_GUIDE.md](META_TOOLS_GUIDE.md)** — Building new agents
4. **[setup/03-configuration-reference.md](setup/03-configuration-reference.md)** — Fine-tune parameters

---

## File Organization

```
docs/
├── INDEX.md                          ← YOU ARE HERE
├── system/
│   ├── system_context.md             (auto-updated on commits)
│   ├── CHANGELOG.md                  (auto-updated on commits)
│   ├── LEVERAGE_GUIDE.md             (backtested patterns)
│   ├── AGENT_COMBINATIONS.md         (multi-agent workflows)
│   ├── orchestrator_framework.md
│   └── SWARM_ORCHESTRATOR_GUIDE.md
├── guides/
│   ├── QUICK_RECIPES.md              (10 copy-paste commands)
│   ├── report-format.md
│   ├── usage-tracking.md
│   └── (other guides)
├── setup/
│   ├── QUICK_SETUP.md
│   ├── 01-cursor-desktop-setup.md
│   ├── 02-desktop-python-setup.md
│   ├── 03-configuration-reference.md
│   ├── 04-troubleshooting.md
│   └── README.md
├── workflows/
│   └── OPTIMIZED_DAILY_TRADING_WORKFLOW.md
├── agent-documentation/
│   └── DAILY_TASK_SCHEDULE_AND_AGENT_WORKFLOW.md
├── archive/                          (deprecated docs)
│   ├── (old analysis files)
│   └── (legacy guides)
├── AGENTS.md                         (legacy, see system/system_context.md)
├── SKILLS.md                         (legacy, see system/system_context.md)
├── DEPLOYMENT_STATUS.md              (system health)
├── MASTER_DOCUMENTATION_INDEX.md     (comprehensive reference)
└── (other root-level docs)
```

---

## Auto-Update System

This documentation is kept fresh via a **git post-commit hook**:

1. **On each commit**, the script `scripts/update_system_context.py` runs automatically
2. **Scans** agents/, scripts/, skills/ for changes
3. **Updates** `system/system_context.md` with current inventory
4. **Generates** `system/CHANGELOG.md` with what changed
5. **Commits** changes automatically (non-blocking)

**Result:** System documentation is always in sync with code. No manual updates needed.

---

## Need Help?

### Quick Questions
- **"How do I...?"** → [guides/QUICK_RECIPES.md](guides/QUICK_RECIPES.md)
- **"What does X agent do?"** → [system/system_context.md](system/system_context.md)
- **"When should I use agent Y?"** → [system/LEVERAGE_GUIDE.md](system/LEVERAGE_GUIDE.md)
- **"How do X and Y work together?"** → [system/AGENT_COMBINATIONS.md](system/AGENT_COMBINATIONS.md)

### Setup Issues
- **Installation problems?** → [setup/04-troubleshooting.md](setup/04-troubleshooting.md)
- **API key not working?** → [setup/03-configuration-reference.md](setup/03-configuration-reference.md)
- **System not running?** → [DEPLOYMENT_STATUS.md](DEPLOYMENT_STATUS.md)

### Deep Dives
- **How does the system work?** → Read Levels 1–3 above in order
- **How to optimize?** → [system/LEVERAGE_GUIDE.md](system/LEVERAGE_GUIDE.md) + [guides/usage-tracking.md](guides/usage-tracking.md)
- **Want to extend?** → [META_TOOLS_GUIDE.md](META_TOOLS_GUIDE.md) + [system/orchestrator_framework.md](orchestrator_framework.md)

---

## Last Updated

**Date:** Auto-generated on every commit  
**Docs Version:** 2026-05-09  
**System Status:** ✅ All agents operational

See [system/CHANGELOG.md](system/CHANGELOG.md) for the latest changes.
