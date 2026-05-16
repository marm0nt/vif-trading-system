# VIF Trading System — Gemini AI Context Layer

**Purpose:** Complete system context for Google Gemini or any external AI tool.  
**Last updated:** 2026-05-15 22:45 UTC  
**Status:** ✅ Production operational (9-agent swarm)

---

## System at a Glance

**VIF Trading System v4.0** is a production-grade multi-agent trading analysis platform:

- **Agents:** 9 specialist agents (catalyst, VIF, FinViz, swing, signal verifier, critic, risk, vectorbt, autoresearch)
- **Watchlists:** 6 institutional (170 tickers) across 4-tier hierarchy
- **Framework:** Volatility Imbalance Framework (VIF) + Kill Switches (K1-K6)
- **Architecture:** Swarm orchestration with KV cache, gossip routing, consensus voting
- **Cost:** $0.07/day (50% reduction from baseline)
- **Latency:** 12-15s per pipeline (40% faster than sequential)
- **Cache hit rate:** 45-50% (LRAgent + 24-hour disk TTL)

---

## Core Frameworks

### 1. Volatility Imbalance Framework (VIF) v4.0
**Location:** `agents/watchlist_watcher.py`, `config/vif_config.yml`

Four-layer analysis:
1. **Gamma Regime Detection** — Price action (positive/negative/transition)
2. **Structural Levels** — Support/resistance from 20-day lookback
3. **Volume Confirmation** — Current vol vs. 20-day MA (threshold 1.5x)
4. **Kill Switch Validation** — K1-K6 override conditions

**Output:** BUY/SELL/HOLD signals with 0-100 confidence, deterministic (temperature=0).

**Kill Switches (Rejection Criteria):**
- K1: Extreme volatility (RSI >80 or <20) → REJECT
- K2: Gap risk (5-day range >10%) → DOWNGRADE
- K3: Low liquidity (volume <1M shares) → REJECT
- K4: News risk (earnings within 5 days) → DOWNGRADE
- K5: Correlation risk (>0.8 with major index) → DOWNGRADE
- K6: Technical breakdown (below 20-day MA + declining vol) → REJECT

### 2. Multi-Agent Swarm Orchestration
**Location:** `agents/orchestrator_swarm.py`, `swarm/` module

Three core components:
1. **KV Cache Manager (500MB, 45-50% hit rate)** — 4-layer recomputation
2. **Latent Working Memory (8 layers)** — Distributed reasoning feedback loops
3. **Gossip Router (500ms timeout)** — Broadcast consensus-building

**Result:** 50% cost reduction, 40% latency improvement, rare conflicts (<5%).

### 3. Institutional Screener Integration
**Location:** `agents/finviz_screener_agent.py`

19 institutional screeners:
- Hunt Screener (5 setups)
- CANSLIM (2 variants)
- Kell (1 base + variants)
- Earnings-Driven (quarterly)
- Value + Growth (2)
- Momentum + Tape (2)
- Sector Rotation (2)

Runs independently at 07:30 CT. Compared with VIF watchlists for overlap analysis.

### 4. Swing Trade Pattern Recognition
**Location:** `scripts/active/analysis/swing_trade_screener_v2.py`

5 archetypal setups:
1. PULLBACK_TO_MA20 — Pullback to 20-day MA, bullish MA stack
2. BULLISH_MA_MOMENTUM — EMA crossover, increasing volume
3. SUPPORT_BOUNCE — Price bounce from key support
4. CONSOLIDATION_BREAKOUT — Rectangle breakout on volume
5. OVERSOLD_BOUNCE — RSI <30, reversing higher

**Output:** Risk/reward ranked (2.5+ preferred), confidence scored.

---

## Daily Execution Pipeline

### Scheduled Jobs (via `schedule_daily.py`)

| Time (CT) | Job | Mode | Agents | Output |
|-----------|-----|------|--------|--------|
| 07:00 | Premarket Catalyst | premarket | Catalyst → VIF | Catalyst alerts |
| 07:30 | FinViz Discovery | finviz_screen | FinViz (19) | Screener results |
| 08:45 | Premarket VIF (1mo) | premarket | VIF (batched) | BUY/SELL/HOLD signals |
| 09:35 | Market-Open Swing | market_open | Swing | Setup rankings |
| 16:05 | After-Hours Analysis | afterhours | VIF (5d) + Verifier | Daily conviction |
| 16:30 (Fri) | Friday Full Pipeline | full | All agents | End-of-week |
| 08:00 (Sat) | Weekend Catalyst | weekend | Catalyst + macro | Monday prep |
| 18:00 (Sun) | Sunday Evening Prep | weekend | Catalyst + macro | Monday briefing |
| Every 5min | Sentry Daemon | N/A | Error scanner | Repair dispatch |

### On-Demand Modes
```bash
python agents/orchestrator_swarm.py --mode premarket    # Single run
python agents/orchestrator_swarm.py --ticker NVDA       # Single ticker
python agents/orchestrator_swarm.py --mode full         # All modes
python agents/orchestrator_swarm.py --repl              # Interactive
```

---

## Watchlist Structure (6 Institutional, 170 Tickers)

Each watchlist follows identical 4-tier hierarchy:

```
###01_MACRO_VANGUARD (2-9 tickers)
  → Check first before any entry
  → Regime-read instruments

###02_PRIMARY_CONVICTION (60-70% capital)
  → High-conviction entries
  → Pass all VIF framework checks
  → Default scanning tier

###03_SPECULATIVE_SCOUTS (20-30% capital)
  → Setup confirmation needed
  → Lower conviction, higher risk/reward

###04_WAITING_LIST
  → Monitor only, no active positions
  → Pre-screened for future entry
```

**Watchlists:**
1. AI Physical Layer & Power Infrastructure (47 tickers)
2. AI Verticals (Supply Chain) (31 tickers)
3. Core Growth & Macro Indices (56 tickers)
4. Energy & AI (Power Convergence) (13 tickers)
5. Speculative & High-Beta (10 tickers)
6. Trump Admin: Onshoring (13 tickers)

---

## Agent Roles (9-Agent Pool)

| # | Agent | Role | Input | Output |
|---|-------|------|-------|--------|
| 1 | Catalyst Monitor | Earnings/policy/macro | Tickers + calendar | K4 alerts |
| 2 | VIF Analyst (core) | Signal generation | OHLCV + config | BUY/SELL/HOLD (0-100) |
| 3 | FinViz Screener | Fundamental discovery | Screener API | Rankings |
| 4 | Swing Screener | Setup detection | Price action | 5 types ranked |
| 5 | Signal Verifier | 4-gate validation | Raw signals | PUBLISH/DOWNGRADE/REJECT |
| 6 | Critic Agent | Low-conf audit (<55%) | VIF + research | Confidence ±5/-10 |
| 7 | Risk Agent | Position sizing | Portfolio state | Position size, stop-loss |
| 8 | VectorBT | Historical validation | OHLCV + params | Backtest metrics |
| 9 | Autoresearch (L8) | Research synthesis | Setups + queries | Insights |

---

## Data & Configuration

### Primary Configuration
- **File:** `config/vif_config.yml`
- **Controls:** VIF thresholds, kill switches, API settings, batch sizes, cache TTL
- **Model:** claude-sonnet-4-6 (temperature=0, deterministic)
- **Max tokens:** 1024 per call
- **Batch size:** 15 tickers per Claude call

### Data Storage
- **Market data cache:** `data/` (24-hour TTL, yfinance)
- **FinViz context:** `data/finviz_cache/` (updated 07:30 daily)
- **Research outputs:** `data/autoresearch_cache/` (7-day TTL)
- **Backtest results:** `data/vectorbt_cache/` (persistent)

### Watchlist Format
- CSV/TXT exports from TradingView
- Normalized tickers (NASDAQ:NVDA → NVDA)
- Located in `watchlists/`

---

## Reports & Outputs

### Report Types
- **`reports/premarket/*.html`** — Morning analysis (BUY/SELL/HOLD)
- **`reports/swing-trades/*.html`** — Swing setups with R:R
- **`reports/daily/*.html`** — EOD conviction scores
- **`reports/weekend/*.html`** — Monday morning briefing
- **`reports/catalysts/*.html`** — Earnings + macro alerts
- **`reports/raw/`** — JSON exports (structured data)

### Report Format (HTML)
Professional templates with:
- Gradient headers
- Tabbed navigation
- Color-coded alerts (success, warning, danger, info)
- Badges and metrics cards
- Responsive, print-friendly CSS

---

## Logging & Monitoring

### Primary Logs
- **`logs/scheduler.log`** — Daily job execution
- **`logs/orchestrator_swarm.log`** — Swarm agent routing, consensus
- **`logs/orchestrator.log`** — Legacy fallback
- **`logs/catalyst_analysis.log`** — Catalyst scan output
- **`logs/system_context_update.log`** — Auto-update post-commit
- **`logs/brain_sync.log`** — Git push activity

### Sentry Daemon (Every 5 minutes)
- Scans logs for ERROR/CRITICAL lines
- Creates A2A JSON handoffs in `logs/sentry_handoffs/`
- Dispatches to repair-subagent for auto-fix
- Format: `{error_id, severity, error_type, error_message, source_log, context}`

### Monitoring Commands
```bash
# Watch orchestrator
tail -f logs/orchestrator_swarm.log

# Check cache hit rate
grep "Cache hit rate:" logs/orchestrator_swarm.log

# Monitor sentry
grep "\[SENTRY\]" logs/scheduler.log

# API cost tracking
python scripts/active/utilities/check_usage.py
```

---

## Cost & Performance

### Daily Budget
- **Cost:** $0.07/day (~7,000 tokens)
- **Monthly:** ~$2.10 (~210,000 tokens)
- **Model routing:** Haiku (dispatch) → Sonnet (analyst) → Opus (synthesis)

### Latency
- **Premarket:** 12-15s (all 170 tickers)
- **Market open:** 10-12s
- **After-hours:** 15-18s
- **Cache overhead:** Negligible (<1s)

### Cost Optimization
1. **Batching:** 15 tickers per Claude call (not individual)
2. **KV Cache:** 45-50% hit rate (reuse outputs)
3. **Local disk cache:** 24-hour TTL (yfinance data)
4. **Selective analysis:** Only tickers meeting volatility thresholds
5. **Model routing:** Cheap models for dispatch, expensive for synthesis

---

## Integration Points

### External Services
- **Claude API** — Sonnet 4.6, Haiku 4.5, Opus 4.7
- **Yahoo Finance** — Free OHLCV data (yfinance)
- **Finviz API** — Fundamental + technical screeners
- **GitHub MCP** — External repo research (Critic Agent)
- **HuggingFace MCP** — Academic paper search (Critic Agent)

### Key Dependencies
```
anthropic>=0.97.0           # Claude API
yfinance>=1.0.0             # Market data
finvizfinance>=1.3.0        # Screeners
ta>=0.11.0                  # Indicators (RSI, MACD, BB, EMA, ATR)
pandas>=2.0.0, numpy>=1.24.0 # Data processing
PyYAML>=6.0                 # Config
schedule>=1.2.0             # Cron-style jobs
smolagents>=1.10.0          # Multi-agent framework
requests, beautifulsoup4    # HTTP + HTML parsing
```

---

## Deployment & Reliability

### Venv-Free Architecture
- Dependencies installed **globally** via `pip install -r requirements.txt`
- No venv path lookups (portable across devices)
- Bootstrap guard checks environment on startup
- System Python directly: `python schedule_daily.py`

### Auto-Sync (Brain Sync)
- **Post-commit hook:** `.githooks/post-commit` (Windows-safe)
- **Runs after every commit:** `git push origin main` (background)
- **Enables:** Cross-device sync (desktop ↔ laptop)
- **Pull to sync:** `git pull origin main` (full context transferred)

### Sentry Monitoring
- Continuous 5-minute error scanning
- Auto-dispatch repair-subagent on ERROR/CRITICAL
- JSON handoffs for audit trail
- Non-blocking (doesn't interrupt scheduler)

---

## Next Steps & Roadmap

### Quick Wins (Week 1, 1-2 days)
1. **TA Library integration** (5k★) — Better indicators
2. **Backtesting.py** (8.3k★) — Signal validation

### Medium-term (Week 2-3, 3-5 days)
3. **TradingAgents framework** (59.4k★) — Multi-agent debate (10-15% signal lift)
4. **PyBroker** (3.3k★) — 8x faster computation

### Long-term (Month 2-3, defer)
5. **Live TradingView integration** (via MCP)
6. **Persistent memory** (AgenticTrading)
7. **Custom screener expansion** (beyond FinViz)

---

## File Structure Reference

```
vif-trading-system/
├── agents/                    # Agent implementations
│   ├── orchestrator_swarm.py # Master orchestrator
│   ├── watchlist_watcher.py  # VIF analyst (core)
│   ├── weekend_catalyst_agent.py # Catalyst monitor
│   ├── external_alpha_auditor.py # Critic agent
│   └── [6 more agents]
├── scripts/active/
│   ├── analysis/             # Analysis scripts
│   └── reporting/            # Report generators
├── config/
│   └── vif_config.yml        # Framework parameters
├── watchlists/               # 6 institutional watchlists
├── data/                     # Caches (yfinance, FinViz, etc.)
├── reports/                  # Output (HTML, JSON)
├── logs/                     # Execution traces
├── docs/                     # Comprehensive documentation
│   ├── SYSTEM_CONTEXT.md    # Architecture overview
│   ├── AGENTS_INVENTORY.md  # Agent detailed inventory
│   ├── MULTIAGENT_SWARM_ARCHITECTURE.md
│   └── gemini-context/       # This folder (Gemini AI context)
├── .claude/                  # Claude Code configuration
│   ├── memory/               # Auto-persisted context
│   ├── agents/               # Agent definitions
│   └── skills/               # Skill definitions
├── schedule_daily.py         # Master scheduler entry point
├── CLAUDE.md                 # Master development guide
└── requirements.txt          # Python dependencies
```

---

## Key Differentiators

**Why VIF Trading System works:**

1. **Signal determinism** (temperature=0) — Reproducible outputs
2. **Kill switches** — Prevents bad signals at source
3. **Multi-agent consensus** — Rare conflicts (<5%), high agreement
4. **KV cache optimization** — 50% cost reduction via smart caching
5. **Institutional tiers** — 4-tier hierarchy matches trader workflows
6. **Continuous monitoring** — Sentry catches errors in real-time
7. **Cross-device sync** — Full context transfers via GitHub

---

## Contact & Resources

- **Owner:** Martin Adadey
- **Email:** martinadadey47@gmail.com
- **Primary doc:** `CLAUDE.md` (master development guide)
- **Context file:** `.ai-context.yaml` (portable AI context)
- **Latest status:** `docs/SYSTEM_CONTEXT.md` (updated weekly)

---

**Last updated:** 2026-05-15 22:45 UTC  
**Status:** ✅ Production operational  
**Maintained by:** Claude Code + auto-update post-commit hook  
**Next review:** 2026-05-22 (weekly sync)
