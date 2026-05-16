# AI Context Index — VIF Trading System

**Purpose:** Portable documentation package for any external AI tool (Gemini, Claude.ai, ChatGPT, etc.).

**How to use:** Start with file 1, progress through 7. Each builds on prior knowledge. Copy this entire folder to any external AI tool or document repository.

---

## Reading Order

### 📄 File 1: System Overview (15 min)
**File:** `01-SYSTEM_OVERVIEW.md`

What you'll learn:
- What is VIF Trading System (in plain language)
- 9-agent swarm architecture overview
- 6 institutional watchlists (170 tickers)
- Daily execution pipeline (07:00-16:30 CT + weekends)
- Key reports and outputs
- How to monitor system health

**Start here if:** You're new to the system.

---

### 🚀 File 2: Quick Start (10 min)
**File:** `02-QUICK_START_GEMINI.md`

What you'll learn:
- VIF framework in 60 seconds (4 layers + kill switches)
- 9-agent council metaphor (easy visualization)
- Daily workflows (morning, afternoon, weekend)
- Essential commands (run analysis, check status)
- Common troubleshooting (5 scenarios)
- Where to find things (quick lookup table)

**Start here if:** You want to run the system immediately.

---

### 🏛️ File 3: Industry Best Practices (45 min)
**File:** `03-INDUSTRY_BEST_PRACTICES.md`

What you'll learn:
- 13 architectural patterns explained
- Why each pattern matters (benefits, trade-offs)
- Industry precedents (AutoGen, vLLM, Cassandra, etc.)
- How patterns work together (integration diagram)
- Academic foundations (papers, frameworks)
- Recommended further reading

**Start here if:** You want deep architectural understanding.

---

### 📋 File 4: Complete System Architecture (20 min)
**File:** `04-SYSTEM_CONTEXT.md`

What you'll learn:
- 9-agent swarm implementation details
- System architecture overview (updated May 15)
- Core frameworks and signals
- Integration points and data flow
- Cost tracking and performance metrics
- Deployment status and operational status

**Start here if:** You need architecture reference or implementation details.

---

### 🤖 File 5: Agent Inventory & Roles (30 min)
**File:** `05-AGENTS_INVENTORY.md`

What you'll learn:
- Complete reference for all 9 agents
- Agent responsibilities and triggers
- Input/output specifications
- Dependencies and integration points
- Adding new agents (step-by-step)
- Agent communication patterns

**Start here if:** You're implementing or extending agent functionality.

---

### ⚙️ File 6: Multi-Agent Swarm Architecture (45 min)
**File:** `06-MULTIAGENT_SWARM_ARCHITECTURE.md`

What you'll learn:
- LRAgent KV cache implementation (45-50% hit rate)
- LatentMAS consensus voting mechanism
- Gossip routing protocol for agent communication
- Agent discovery and service registry
- Fault tolerance and recovery patterns
- Performance optimization strategies

**Start here if:** You're tuning agent communication, cache behavior, or scaling the system.

---

### 📚 Reference Resources
For deeper implementation details, see:

| Document | Purpose | Location |
|----------|---------|----------|
| `CLAUDE.md` | Master development guide | Parent repo |
| `.ai-context.yaml` | Portable AI context (for Cursor, Claude.ai) | Parent repo |
| `config/vif_config.yml` | All framework parameters | Parent repo |
| `requirements.txt` | Python dependencies | Parent repo |

---

## Quick Navigation

### Troubleshooting
- **No reports generated:** `02-QUICK_START_GEMINI.md` → Troubleshooting
- **Low signal confidence:** `02-QUICK_START_GEMINI.md` → Common Workflows
- **API authentication fails:** `02-QUICK_START_GEMINI.md` → Troubleshooting
- **How do kill switches work?** `02-QUICK_START_GEMINI.md` → Key Concepts
- **Why is my signal downgraded?** `logs/orchestrator_swarm.log` → Search "K[1-6]"

### Learning Paths

**Path A: Run the System (30 min)**
1. `02-QUICK_START_GEMINI.md` (10 min)
2. Essential Commands → Run Analysis section (5 min)
3. `python schedule_daily.py` (10 min execution)
4. Check `reports/premarket/` for output (5 min)

**Path B: Understand Architecture (1.5 hours)**
1. `01-SYSTEM_OVERVIEW.md` (15 min)
2. `02-QUICK_START_GEMINI.md` (10 min)
3. `04-SYSTEM_CONTEXT.md` (20 min)
4. `05-AGENTS_INVENTORY.md` → Agent Roles section (20 min)
5. `03-INDUSTRY_BEST_PRACTICES.md` (15 min)

**Path C: Deep Technical Dive (2.5+ hours)**
1. All files A-B above (1.5 hours)
2. `06-MULTIAGENT_SWARM_ARCHITECTURE.md` (45 min)
3. Parent repo `config/vif_config.yml` (review all parameters, 10 min)
4. Parent repo `CLAUDE.md` (master guide, reference as needed)

**Path D: Integrate New Feature (2-3 hours)**
1. `02-QUICK_START_GEMINI.md` (10 min context)
2. `05-AGENTS_INVENTORY.md` → "Adding New Agents" section (20 min)
3. `06-MULTIAGENT_SWARM_ARCHITECTURE.md` → Communication patterns (15 min)
4. Review similar agent source code in parent repo (30 min)
5. Implement new agent following 4-step protocol (1-2 hours)
6. Test with `python tests/test_harness.py` (10 min)

---

## Core Concepts Reference

### VIF Framework (4 Layers)
1. Gamma Regime — Price action analysis
2. Structural Levels — Support/resistance
3. Volume Confirmation — Above 20-day MA
4. Kill Switch Validation — K1-K6 override conditions

**Learn more:** `01-SYSTEM_OVERVIEW.md` → Core Frameworks

### Kill Switches (K1-K6)
| K | Condition | Action |
|---|-----------|--------|
| K1 | Extreme volatility (RSI >80/<20) | REJECT |
| K2 | Gap risk (>10% in 5d range) | DOWNGRADE |
| K3 | Low liquidity (<1M shares) | REJECT |
| K4 | Earnings within 5d | DOWNGRADE |
| K5 | Correlation >0.8 with index | DOWNGRADE |
| K6 | Below 20-day MA + declining vol | REJECT |

**Learn more:** `02-QUICK_START_GEMINI.md` → Kill Switches

### 9-Agent Swarm
| # | Agent | Role |
|---|-------|------|
| 1 | Catalyst Monitor | Earnings/policy/macro |
| 2 | VIF Analyst | Signal generation (core) |
| 3 | FinViz Screener | Fundamental analysis |
| 4 | Swing Screener | Pattern recognition (5 types) |
| 5 | Signal Verifier | 4-gate validation |
| 6 | Critic Agent | Low-conf research audit |
| 7 | Risk Agent | Position sizing |
| 8 | VectorBT | Backtesting |
| 9 | Autoresearch (L8) | Macro synthesis |

**Learn more:** `01-SYSTEM_OVERVIEW.md` → Agent Roles

### 6 Watchlists (170 Tickers)
1. AI Physical Layer & Power (47)
2. AI Verticals (31)
3. Core Growth & Macro (56)
4. Energy & AI (13)
5. Speculative & High-Beta (10)
6. Trump Admin: Onshoring (13)

Each with 4-tier hierarchy: MACRO_VANGUARD → PRIMARY_CONVICTION → SPECULATIVE_SCOUTS → WAITING_LIST

**Learn more:** `01-SYSTEM_OVERVIEW.md` → Watchlist Structure

---

## Essential Commands

### Run Analysis
```bash
python schedule_daily.py                               # Full automatic
python agents/orchestrator_swarm.py --mode premarket   # Single mode
python agents/orchestrator_swarm.py --ticker NVDA      # Single ticker
python agents/orchestrator_swarm.py --repl             # Interactive
```

### Check Status
```bash
tail -f logs/orchestrator_swarm.log                    # Watch live
grep "Cache hit rate:" logs/orchestrator_swarm.log     # Cache performance
grep "\[SENTRY\]" logs/scheduler.log                   # Error monitoring
python scripts/active/utilities/check_usage.py         # Cost tracking
```

### Testing
```bash
python tests/test_harness.py                           # Offline test (no API)
python tests/test_api_key.py                           # Verify API key
```

---

## File Structure (Abbreviated)

```
vif-trading-system/
├── docs/ai-context/              ← YOU ARE HERE (portable, copy to OneDrive)
│   ├── INDEX.md                  ← This file
│   ├── 01-SYSTEM_OVERVIEW.md     ← Start here (15 min)
│   ├── 02-QUICK_START_GEMINI.md  ← Quick start (10 min)
│   ├── 03-INDUSTRY_BEST_PRACTICES.md ← Deep dive (45 min)
│   ├── 04-SYSTEM_CONTEXT.md      ← Complete architecture (20 min)
│   ├── 05-AGENTS_INVENTORY.md    ← Agent reference (30 min)
│   └── 06-MULTIAGENT_SWARM_ARCHITECTURE.md ← KV cache, routing (45 min)
│
├── docs/                         ← Parent directory
│   ├── SYSTEM_CONTEXT.md         ← (now in ai-context as file 4)
│   ├── AGENTS_INVENTORY.md       ← (now in ai-context as file 5)
│   └── [other documentation]
│
├── agents/                        ← Agent implementations (in parent repo)
│   ├── orchestrator_swarm.py     ← Master orchestrator
│   ├── watchlist_watcher.py      ← VIF analyst (core)
│   └── [6 more agents]
│
├── config/
│   └── vif_config.yml            ← All framework parameters
│
├── schedule_daily.py             ← Entry point (cron scheduler)
├── CLAUDE.md                     ← Master dev guide
└── requirements.txt              ← Python dependencies
```

---

## Glossary

| Term | Definition | Learn More |
|------|-----------|------------|
| VIF | Volatility Imbalance Framework (core signal framework) | `01-SYSTEM_OVERVIEW.md` |
| Swarm | 9-agent council coordinating via KV cache + gossip routing | `01-SYSTEM_OVERVIEW.md` |
| KV Cache | Key-value store caching agent outputs (45-50% hit rate) | `03-INDUSTRY_BEST_PRACTICES.md` |
| Gossip Routing | Broadcast consensus-building between agents | `03-INDUSTRY_BEST_PRACTICES.md` |
| Kill Switch | K1-K6 veto conditions that downgrade/reject signals | `02-QUICK_START_GEMINI.md` |
| Confidence | 0-100 score indicating signal strength | `01-SYSTEM_OVERVIEW.md` |
| Temperature | LLM randomness setting (=0 for deterministic output) | `03-INDUSTRY_BEST_PRACTICES.md` |
| Batching | Grouping 15 tickers per API call (cost optimization) | `03-INDUSTRY_BEST_PRACTICES.md` |
| Sentry Daemon | Continuous error monitoring (every 5 min, 24/7) | `03-INDUSTRY_BEST_PRACTICES.md` |
| Brain Sync | Auto-push to GitHub after every commit | `03-INDUSTRY_BEST_PRACTICES.md` |

---

## Contact & Support

- **System Owner:** Martin Adadey
- **Email:** martinadadey47@gmail.com
- **Primary Questions?** Check `02-QUICK_START_GEMINI.md` → Troubleshooting
- **Technical Questions?** Read `CLAUDE.md` (master development guide)
- **Understand Architecture?** Read `03-INDUSTRY_BEST_PRACTICES.md`

---

## Key Metrics (As of May 15, 2026)

| Metric | Value | Status |
|--------|-------|--------|
| System Status | ✅ All operational | Phase 1-4 complete |
| Agents Active | 9 specialists | All deployed |
| Watchlists | 6 institutional (170 tickers) | Updated daily |
| Daily Cost | $0.07 | 50% reduction via cache |
| Latency | 12-15s per pipeline | 40% faster than baseline |
| Cache Hit Rate | 45-50% | LRAgent optimization |
| Signal Rejection | 25-30% | Via 4-gate verifier |
| Uptime | 24/7 continuous | Sentry monitored |
| Synced Devices | 2+ (auto-sync via git) | Zero-friction |

---

## Next Steps

**I want to:** → **Start with:**

- Run the system tomorrow → `02-QUICK_START_GEMINI.md` (Essential Commands)
- Understand how signals work → `01-SYSTEM_OVERVIEW.md` (Core Frameworks)
- Know why architecture is designed this way → `03-INDUSTRY_BEST_PRACTICES.md`
- Understand system components → `04-SYSTEM_CONTEXT.md` (Architecture reference)
- Add a new agent → `05-AGENTS_INVENTORY.md` (Adding New Agents)
- Deep technical dive on swarm → `06-MULTIAGENT_SWARM_ARCHITECTURE.md`
- Develop new features → Parent repo `CLAUDE.md` (Master guide)

---

**Welcome to VIF Trading System!**

This is a production-grade system with 9-agent swarm orchestration, 50% cost optimization, and deterministic trading signals. Start with file 1 or 2 above and progress at your pace.

**📁 Ready for OneDrive:** This entire `ai-context/` folder is self-contained and portable. Copy it directly to OneDrive, Google Drive, or any external AI chat tool for reference.

**Last updated:** 2026-05-16 00:00 UTC  
**Status:** ✅ Consolidated to 7-file portable package  
**Next update:** 2026-05-23 (weekly sync)
