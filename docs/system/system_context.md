# VIF Trading System — Complete Architecture Map

**Last updated:** 2026-05-13 01:25:55
**Status:** All systems operational

---

## 1. Active Agents

| Agent | File | Status |
|-------|------|--------|
| claude_research_agent | agents\claude_research_agent.py | ✅ Active |
| external_alpha_auditor | agents\external_alpha_auditor.py | ✅ Active |
| finviz_orchestrator_coordinator | agents\finviz_orchestrator_coordinator.py | ✅ Active |
| finviz_screener_agent | agents\finviz_screener_agent.py | ✅ Active |
| indicators | agents\indicators.py | ✅ Active |
| orchestrator | agents\orchestrator.py | ✅ Active |
| orchestrator_swarm | agents\orchestrator_swarm.py | ✅ Active |
| watchlist_watcher | agents\watchlist_watcher.py | ✅ Active |
| weekend_catalyst_agent | agents\weekend_catalyst_agent.py | ✅ Active |

---

## 2. Skills & Knowledge Modules

| Skill | Purpose | Last Updated |
|-------|---------|--------------|
| TEMPLATE_SKILL | Core framework reference | 2026-04-29 14:44 |
| agent-design-principles | Core framework reference | 2026-05-02 16:49 |
| analyzing-vif-signals | Core framework reference | 2026-05-09 17:58 |
| briefing-weekend-macro | Core framework reference | 2026-04-29 01:22 |
| computing-indicators | Core framework reference | 2026-04-29 01:21 |
| fetching-market-data | Core framework reference | 2026-04-29 01:23 |
| file-organizer | Core framework reference | 2026-05-07 19:31 |
| github-feature-extraction | Core framework reference | 2026-05-02 18:30 |
| monitoring-catalysts | Core framework reference | 2026-05-02 18:36 |
| orchestrating-pipelines | Core framework reference | 2026-05-02 16:49 |
| parsing-watchlists | Core framework reference | 2026-04-29 01:23 |
| screening-swing-setups | Core framework reference | 2026-04-29 01:22 |
| skill-creator | Core framework reference | 2026-05-07 19:31 |

---

## 3. Active Frameworks

### multi-agent-orchestrator
- Status: active
- Agents: catalyst-monitor, vif-analyst, swing-trade-screener

---

## 4. Recent Changes

**Added:**
- (none)

**Modified:**
- (none)

---

## 5. How to Use This Documentation

1. **For system overview:** Read Section 3 (Active Frameworks)
2. **To understand agents:** Check Section 1 (Active Agents)
3. **For skill reference:** See Section 2 (Skills & Knowledge Modules)
4. **To track changes:** Review Section 4 (Recent Changes) and CHANGELOG.md

---

See **LEVERAGE_GUIDE.md** for backtested patterns and consensus best practices.
See **CHANGELOG.md** for detailed change history.
