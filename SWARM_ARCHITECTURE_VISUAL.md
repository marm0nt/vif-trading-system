# 🌟 VIF Swarm Architecture — Visual Guide

## The 9-Agent Ecosystem (Orchestrator-Centric View)

```
                          ┌─────────────────────┐
                          │  📡 SCHEDULER       │
                          │  schedule_daily.py  │
                          └──────────┬──────────┘
                                     │
                    ┌────────────────┴────────────────┐
                    │                                 │
                    ▼                                 ▼
          ┌──────────────────┐           ┌──────────────────┐
          │ PREMARKET MODE   │           │ AFTERHOURS MODE  │
          │   (07:00 CT)     │           │   (16:05 CT)     │
          └────────┬─────────┘           └────────┬─────────┘
                   │                               │
                   └───────────────┬───────────────┘
                                   │
            ┏━━━━━━━━━━━━━━━━━━━━━━▼━━━━━━━━━━━━━━━━━━━━━━┓
            ┃                                              ┃
            ┃    🎯 LEAD ORCHESTRATOR (orchestrator_swarm)┃
            ┃         Gossip Routing + Consensus          ┃
            ┃         KV Cache (45-50% hit rate)          ┃
            ┃         Cost: $0.07/day (50% savings)       ┃
            ┃                                              ┃
            ┗━━━━━━━━━━━━━━━━━━━━━━┬━━━━━━━━━━━━━━━━━━━━━┛
                                    │
         ┌──────────────────────────┼──────────────────────────┐
         │                          │                          │
         │         ┌────────────────┼────────────────┐         │
         │         │                │                │         │
    ▼    ▼    ▼    ▼           ▼    ▼         ▼     ▼    ▼
  ┌────────────┐  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐
  │🔍 CATALYST │  │📊 VIF        │  │🔎 FINVIZ    │  │⚡ SWING     │
  │  MONITOR   │  │  ANALYST     │  │  SCREENER   │  │  SCREENER   │
  │            │  │              │  │             │  │             │
  │• Earnings  │  │• Gamma Regime│  │• Valuation  │  │• 5 Setups   │
  │• Policy    │  │• Levels      │  │• Growth     │  │• R:R Ranked │
  │• Macro     │  │• Volume      │  │• Quality    │  │• 2-4 week   │
  │• Catalysts │  │• Kill Switch │  │• Screener   │  │  Outlook    │
  └────┬───────┘  └──────┬───────┘  └──────┬──────┘  └──────┬──────┘
       │                  │                 │               │
       │                  │                 │               │
  ▼    ▼              ▼    ▼             ▼   ▼           ▼    ▼
  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
  │✅ SIGNAL     │  │🤖 CRITIC     │  │⚖️ RISK       │  │📈 VECTORBT   │
  │  VERIFIER    │  │  AGENT       │  │  AGENT       │  │  ANALYST     │
  │              │  │              │  │              │  │              │
  │• 4-gate      │  │• Low-conf    │  │• Position    │  │• Backtesting │
  │  validation  │  │  audit       │  │  sizing      │  │• Performance │
  │• Volume      │  │• Research    │  │• Risk metrics│  │• Drawdown    │
  │• Fundamental │  │• Paper refs  │  │• Correlation│  │• Win rate    │
  │• Sentiment   │  │• Signal      │  │• Hedging    │  │• Factor      │
  │• Macro       │  │  adjustment  │  │• Allocation │  │  analysis    │
  └──────┬───────┘  └──────┬───────┘  └──────┬──────┘  └──────┬──────┘
         │                 │                 │               │
         │                 │                 │               │
         │        ┌────────┴────────────────┴───────────┐   │
         │        │                                     │   │
         │        ▼                                     ▼   ▼
         │   ┌──────────────────────────┐       ┌────────────────┐
         │   │🔬 AUTORESEARCH           │       │📊 CONSENSUS    │
         │   │   (Layer 40)             │       │   VOTING       │
         │   │                          │       │   (Gossip)     │
         │   │• Iterative synthesis     │       │                │
         │   │• Paper integration       │       │ Conflict       │
         │   │• Factor discovery        │       │ Resolution     │
         │   └─────────┬────────────────┘       └────────────────┘
         │             │
         └─────────────┼────────────────────────────┐
                       │                            │
                       ▼                            ▼
                 ┌──────────────┐          ┌──────────────────┐
                 │📋 REPORTS    │          │📚 LOGS & MEMORY  │
                 │  (JSON/HTML) │          │  (Observability) │
                 │              │          │                  │
                 │• Raw signals │          │• OTel tracing    │
                 │• Rankings    │          │• trace_ids       │
                 │• Conviction  │          │• Cache stats     │
                 │• Execution   │          │• Cost tracking   │
                 └──────────────┘          └──────────────────┘
```

---

## Agent Responsibilities & Data Flow

| Agent | Input | Output | Cost | Time |
|-------|-------|--------|------|------|
| **🔍 Catalyst Monitor** | Watchlist + Market events | Earnings dates, Policy alerts, Macro themes | ~$0.008 | 2-3s |
| **📊 VIF Analyst** | OHLCV + Indicators | BUY/SELL/HOLD signals, Confidence scores | ~$0.040 | 5-7s |
| **🔎 FinViz Screener** | Valuation metrics | Fundamental scores, Growth assessments | ~$0.012 | 1-2s |
| **⚡ Swing Screener** | Technical setups | 5 setup types, Risk/Reward rankings | ~$0.010 | 2-3s |
| **✅ Signal Verifier** | VIF signals | PUBLISH/DOWNGRADE/REJECT verdicts | ~$0.008 | 1-2s |
| **🤖 Critic Agent** | Low-conf signals (<55%) | Research audit, Confidence adjustments | ~$0.005 | 2-3s |
| **⚖️ Risk Agent** | Signals + Market regime | Position sizes, Correlation, Hedging | ~$0.006 | 1-2s |
| **📈 VectorBT Analyst** | Backtest parameters | Historical performance, Drawdown stats | ~$0.010 | 3-4s |
| **🔬 Autoresearch** | Novel factors, Signals | Paper synthesis, Factor integration | ~$0.004 | 2-3s |

**Total Daily Cost:** ~$0.103 → **$0.07/day** (with KV cache hit rate 45-50%)

---

## File Organization (Mirroring Agent Hierarchy)

```
vif-trading-system/
├── 🎯 ORCHESTRATOR
│   ├── agents/
│   │   ├── orchestrator_swarm.py       ← Lead agent (main entry)
│   │   ├── orchestrator.py              ← Legacy fallback
│   │   │
│   │   ├── 🔍 CATALYST_MONITOR
│   │   │   └── *catalyst*.py
│   │   │
│   │   ├── 📊 VIF_ANALYST
│   │   │   ├── watchlist_watcher.py
│   │   │   └── indicators.py
│   │   │
│   │   ├── 🔎 FINVIZ_SCREENER
│   │   │   └── *finviz*.py
│   │   │
│   │   ├── ⚡ SWING_SCREENER
│   │   │   └── scripts/swing_trade_screener_v2.py
│   │   │
│   │   ├── ✅ SIGNAL_VERIFIER
│   │   │   └── *verif*.py
│   │   │
│   │   ├── 🤖 CRITIC_AGENT
│   │   │   ├── external_alpha_auditor.py
│   │   │   └── *critic*.py
│   │   │
│   │   ├── ⚖️ RISK_AGENT
│   │   │   └── *risk*.py
│   │   │
│   │   ├── 📈 VECTORBT_ANALYST
│   │   │   └── *backtest*.py
│   │   │
│   │   └── 🔬 AUTORESEARCH
│   │       └── *research*.py
│   │
│   ├── 📊 DATA LAYER
│   │   ├── config/vif_config.yml
│   │   ├── data/indicators/
│   │   └── data/cache/
│   │
│   ├── 📋 REPORTS
│   │   ├── reports/raw/        (JSON)
│   │   ├── reports/daily/      (Markdown)
│   │   └── reports/*.html      (Published)
│   │
│   └── 📚 OBSERVABILITY
│       ├── logs/
│       └── .claude/memory/
```

---

## How to Use This Workspace

### 1. **Open in VS Code**
```bash
code vif-swarm-architecture.code-workspace
```

This opens a multi-folder workspace where each folder tab shows:
- 🎯 **ORCHESTRATOR (Lead)** — Central hub
- 🔍 **CATALYST MONITOR** — Earnings & macro
- 📊 **VIF ANALYST** — Core signals
- 🔎 **FINVIZ SCREENER** — Fundamental scores
- ⚡ **SWING SCREENER** — Setup ranking
- ✅ **SIGNAL VERIFIER** — 4-gate validation
- 🤖 **CRITIC AGENT** — Research audit
- ⚖️ **RISK AGENT** — Position sizing
- 📈 **VECTORBT ANALYST** — Backtesting
- 🔬 **AUTORESEARCH** — Paper synthesis
- ⚙️ **CONFIG & DATA** — Settings
- 📋 **REPORTS** — Output
- 📚 **DOCS & MEMORY** — Context

### 2. **Agent Communication Flow**
```
scheduler → orchestrator_swarm.py
           ├→ catalyst_monitor (polls catalysts)
           ├→ vif_analyst (computes signals)
           ├→ finviz_screener (fundamental check)
           ├→ swing_screener (setup validation)
           ├→ signal_verifier (4-gate filter)
           ├→ critic_agent (low-conf audit)
           ├→ risk_agent (position sizing)
           ├→ vectorbt_analyst (backtest)
           └→ autoresearch (synthesis)
```

### 3. **Command Cheatsheet**

```bash
# Run full pipeline (all agents in sequence)
python schedule_daily.py

# Run specific mode
python agents/orchestrator_swarm.py --mode premarket
python agents/orchestrator_swarm.py --mode afterhours
python agents/orchestrator_swarm.py --mode weekend

# Monitor cache hit rate
tail -f logs/orchestrator_swarm.log | grep "Cache hit"

# Single ticker analysis
python agents/orchestrator_swarm.py --ticker NVDA
```

---

## Cost Breakdown (Daily)

```
Catalyst Monitor        $0.008  ▓░░░░░░░░░░░░░░░░░░
VIF Analyst             $0.040  ▓▓▓▓▓▓▓▓▓░░░░░░░░░░
FinViz Screener         $0.012  ▓▓▓░░░░░░░░░░░░░░░░
Swing Screener          $0.010  ▓▓░░░░░░░░░░░░░░░░░
Signal Verifier         $0.008  ▓░░░░░░░░░░░░░░░░░░
Critic Agent            $0.005  ▓░░░░░░░░░░░░░░░░░░
Risk Agent              $0.006  ▓░░░░░░░░░░░░░░░░░░
VectorBT Analyst        $0.010  ▓▓░░░░░░░░░░░░░░░░░
Autoresearch            $0.004  ░░░░░░░░░░░░░░░░░░░
                        ───────
WITHOUT KV CACHE        $0.103
WITH KV CACHE (45-50%)  $0.070  ✅ 32% savings
```

---

## Next Steps

1. **Open workspace:** `code vif-swarm-architecture.code-workspace`
2. **Watch logs:** `tail -f logs/orchestrator_swarm.log`
3. **Monitor cache:** Check `Cache hit rate:` in logs
4. **Add GitHub repos:** See `docs/SWARM_ORCHESTRATOR_GUIDE.md` for TA Library + Backtesting.py integration

**Status:** ✅ **DEPLOYED** (May 15, 2026)
