# VIF Trading System — Complete System Map

**Generated:** 2026-05-11 | **Status:** Zero-Friction Context Layer Complete (Phase 1-4)

---

## How to Use This System

### For **First-Time LLM Instance** (Claude.ai, Cursor, Gemini):

```
1. Read ONBOARDING.md (5 min)      ← START HERE
2. Read .ai-context.yaml (10 min)  ← Portable context card
3. Read CLAUDE.md (deep dive)      ← Full architecture
4. Run: python tests/test_api_key.py ← Verify setup
```

### For **Claude Code Users** (You):

```
1. Reference .claude/memory/ for context continuity
2. Use CLAUDE.md for technical deep dives
3. Run agents/orchestrator_swarm.py for full pipeline
```

---

## Core Concepts (60 seconds)

| Concept | Definition |
|---------|-----------|
| **VIF** | Volatility Imbalance Framework v4.0 — proprietary signal logic (4 layers: gamma regime + structural levels + volume + kill switches) |
| **Signal** | BUY/SELL/HOLD recommendation with confidence score (0–100) for 2–4 week holding periods |
| **Watchlist** | Curated set of tickers organized into 4 tiers (VANGUARD / PRIMARY / SCOUTS / WAITING) |
| **Kill Switch** | Override condition (K1–K6) that downgrades or rejects a signal (extreme volatility, gap risk, low liquidity, news risk, correlation risk, technical breakdown) |
| **Pipeline** | Orchestrated sequence: parse → fetch → analyze → verify → report |
| **Confidence** | 0–100 score. <55% triggers GitHub/HF research audit automatically. >80% publishes immediately. |

---

## 6 Watchlists (170 tickers, 4-tier each)

| ID | Name | Tickers | Regime | Driver | File |
|----|------|---------|--------|--------|------|
| **WL1** | AI Physical Layer & Power Infrastructure | 47 | Risk-On | Tape + CapEx | watchlists/AI Physical Layer & Power Infrastructure.txt |
| **WL2** | AI Verticals (Supply Chain) | 31 | Risk-On | CapEx + Tape | watchlists/AI Verticals (Supply Chain).txt |
| **WL3** | Core Growth & Macro Indices | 56 | Both | Earnings + Macro | watchlists/Core Growth & Macro Indices (Large-Cap Anchors).txt |
| **WL4** | Energy & AI (Power Convergence) | 13 | Risk-On | Contract + CapEx | watchlists/Energy & AI (Power Convergence).txt |
| **WL5** | Speculative & High-Beta | 10 | Risk-On ONLY | Momentum | watchlists/Speculative _ High-Beta.txt |
| **WL6** | Trump Admin: Onshoring | 13 | Risk-On | Contract + Macro | watchlists/Trump Admin_ Onshoring.txt |

**Every watchlist contains 4 tiers:**
- `###01_MACRO_VANGUARD` — Regime instruments (check first)
- `###02_PRIMARY_CONVICTION` — High-conviction entries (default scan)
- `###03_SPECULATIVE_SCOUTS` — Setup confirmation needed
- `###04_WAITING_LIST` — Monitor only

---

## Architecture Overview

### 9 Core Agents

| Agent | File | Role | Triggers |
|-------|------|------|----------|
| **watchlist_watcher** | `agents/watchlist_watcher.py` | VIF Analyst (parse + fetch + analyze) | Manual or scheduled |
| **orchestrator_swarm** | `agents/orchestrator_swarm.py` | Master Pipeline Controller (Phase 3) | `schedule_daily.py` or `--mode premarket` |
| **indicators** | `agents/indicators.py` | Shared Technical Engine (RSI/MACD/BB/EMA/ATR) | Called by watchlist_watcher |
| **weekend_catalyst_agent** | `agents/weekend_catalyst_agent.py` | Macro & Earnings Briefing | Sat 08:00, Sun 18:00 CT |
| **external_alpha_auditor** | `agents/external_alpha_auditor.py` | GitHub/HF Research (low-confidence signals) | Confidence < 55% |
| **finviz_screener_agent** | `agents/finviz_screener_agent.py` | Custom Screener (independent mode) | Manual or scheduled |
| **finviz_orchestrator_coordinator** | `agents/finviz_orchestrator_coordinator.py` | FinViz Swarm Integration | Swarm pipeline |
| **claude_research_agent** | `agents/claude_research_agent.py` | Ad-hoc Research Q&A | Manual prompt |
| **(archived)** report_ui_agent | `agents/archive/report_ui_agent.py` | JSON→Markdown converter | Legacy (use HTML instead) |

### Swarm Layer (Phase 3 Ready)

9 specialist agents + KV cache manager + gossip router + consensus engine.
Status: Infrastructure deployed, integration pending.

---

## Pipeline Modes & Schedules

| Mode | When | Sequence | Output |
|------|------|----------|--------|
| **premarket** | 08:45 ET (weekdays) | catalyst_monitor → vif_analyst (1mo) → signal_verifier → report_builder | `reports/premarket/*.json` + `.html` |
| **market_open** | 09:35 ET (weekdays) | swing_trade_screener (2–4 week setups) | Ranked by risk/reward |
| **afterhours** | 16:05 ET (weekdays) | vif_analyst (5d) → postmarket_debrief → alpha_extractor | Daily conviction + 5%+ mover analysis |
| **weekend** | Sat 08:00, Sun 18:00 CT | weekend_catalyst_analyst (macro + earnings + rotation) | Monday morning briefing |
| **full** | On-demand | All modes sequentially | Complete analysis |

**Entry point:** `python schedule_daily.py`

---

## Configuration & Tuning

All framework parameters in **`config/vif_config.yml`:**

```yaml
vif_framework:
  gamma_regime.positive_threshold: 0.5
  structural_levels.lookback_days: 20
  volume.ma_period: 20
  volume.strong_threshold: 1.5x

kill_switches:
  K1: RSI >80 or <20 → REJECT
  K2: 5-day range >10% → DOWNGRADE
  K3: Volume <1M → REJECT
  K4: Earnings <5 days → DOWNGRADE
  K5: Correlation >0.8 → DOWNGRADE
  K6: Below MA + declining volume → REJECT

api:
  models: {router: haiku-4-5, analyst: sonnet-4-6, synthesizer: opus-4-7}
  temperature: 0 (deterministic)
  max_tokens: 1024
  batch_size: 15 tickers per call

data_fetching:
  cache_ttl_hours: 24
  period_default: "5d"
```

---

## File Structure (AI Navigation Guide)

### 🔴 **READ FIRST** (Core Understanding)

```
ONBOARDING.md                          ← 5-min new contributor guide
.ai-context.yaml                       ← Portable project metadata
CLAUDE.md                              ← Full technical reference
config/vif_config.yml                  ← All framework parameters
agents/watchlist_watcher.py            ← Core VIF signal logic
agents/orchestrator_swarm.py           ← Pipeline orchestration
```

### 🟡 **READ SECOND** (Reference & Deep Dives)

```
docs/SWARM_ORCHESTRATOR_GUIDE.md       ← Multi-agent patterns
docs/AGENTS.md                         ← Agent inventory + workflows
docs/QUICKSTART.md                     ← Installation + first run
.claude/memory/watchlist_structure.md  ← Tier breakdown + tickers
```

### 🟢 **REFERENCE ONLY** (Supporting Materials)

```
docs/                                  ← 50+ docs (setup, guides, system context)
.claude/skills/                        ← 12 skills (catalyst, screening, parsing)
.claude/memory/                        ← User preferences + arch decisions
scripts/active/                        ← Analysis scripts (catalyst, swing, reporting)
reports/                               ← Output (JSON + HTML)
```

### ⚫ **IGNORE** (Dependencies, Cache, Version Control)

```
venv/                                  ← Python virtual environment
.git/                                  ← Version control
data/cache/                            ← Temporary files
logs/                                  ← Execution traces (only if debugging)
scripts/archive/                       ← Deprecated implementations
```

---

## Common Commands

### Quick Verification (No API Credits)

```bash
python tests/test_api_key.py           # Validate API key
python tests/test_harness.py           # Offline mock analysis
```

### Single Watchlist Analysis

```bash
python agents/watchlist_watcher.py --watchlist vantage_portfolio
python agents/watchlist_watcher.py --watchlist ai_verticals
python agents/watchlist_watcher.py --watchlist energy_ai
```

### Full Pipeline (All Watchlists)

```bash
python schedule_daily.py               # Run all modes once
```

### Cost Monitoring

```bash
python scripts/active/utilities/check_usage.py
```

---

## Cost Structure

| Metric | Value |
|--------|-------|
| **Daily** | $0.13 USD (~13,000 tokens) |
| **Monthly** | $3.90 USD (~390,000 tokens) |
| **Model Routing** | Haiku (dispatch, cheap) → Sonnet (analyst) → Opus (synthesis) |
| **Cache Efficiency** | 24-hr yfinance cache + indicator reuse |
| **Batching** | 15 tickers per API call (not individual calls) |

---

## MCP Integrations (External Knowledge)

| Service | Purpose | Status | Config |
|---------|---------|--------|--------|
| **GitHub** | External alpha audit (repo scanning) | Phase 1 complete | `agents/external_alpha_auditor.py` |
| **Hugging Face** | Academic paper research (30-day cache) | Phase 1 complete | `agents/external_alpha_auditor.py` |
| **TradingView** | Live chart control (78 tools) | Standalone node module | `tradingview-mcp-jackson/` |

---

## Key Concepts

### Signal Confidence Scoring

- **80–100:** High conviction → PUBLISH immediately
- **55–79:** Moderate conviction → Pass 4-gate verification (volume, fundamental, sentiment, macro)
- **<55:** Low confidence → Trigger GitHub/HF research audit automatically
- **0:** No signal generated

### Temperature = 0 (Deterministic)

Same ticker analyzed twice = identical output. Ensures reproducibility in signal generation.

### Batching Strategy (Cost Optimization)

- 15 tickers per Claude call (not 1 ticker per call)
- Reduces token spend from $1+ to $0.13/day
- Enabled via `data_fetching.batch_size` in `config/vif_config.yml`

### Kill Switch Logic

If **ANY** kill switch triggers → signal is downgraded or rejected outright:
- K1, K3, K6 → REJECT (confidence = 0)
- K2, K4, K5 → DOWNGRADE (confidence -= penalty)

---

## Quick Glossary

| Term | Meaning |
|------|---------|
| **VIF** | Volatility Imbalance Framework (proprietary signal logic) |
| **Gamma Regime** | Price action momentum (positive/negative/transition from higher highs/lows) |
| **Structural Levels** | Support/resistance from 20-day historical lookback (25th/75th percentiles) |
| **Kill Switch** | Override condition (K1–K6) that downgrades/rejects signals |
| **Confidence** | 0–100 score indicating signal conviction (>80 = publish, <55 = audit) |
| **Temperature** | Randomness parameter (0 = deterministic, 1.0 = random). We use 0. |
| **Batching** | Processing 15 tickers per API call (cost optimization) |
| **TTL** | Time-to-live (24 hours for cached yfinance data) |
| **VANGUARD** | Regime instruments tier (regime read, check first) |
| **PRIMARY** | High-conviction entries tier (default scan) |
| **SCOUTS** | Speculative, setup confirmation needed tier |
| **WAITING** | Monitor-only tier (pre-screened for future entry) |

---

## For Other AI Platforms (Copy-Paste Prompt)

When sharing this project with ChatGPT, Gemini, or other LLMs, use this boilerplate:

```
I'm using the VIF Trading System (AI signal generation for swing trades).

WHAT IT DOES:
- Analyzes 170 institutional tickers across 6 watchlists (4-tier structure)
- Applies VIF v4.0 framework (gamma regime + structural levels + volume + kill switches)
- Generates BUY/SELL/HOLD signals with confidence scores (0-100)
- Validates via 4 gates (Volume, Fundamental, Sentiment, Macro)
- Costs ~$0.13/day via Claude API (Sonnet 4.6 analyst, Haiku 4.5 router)

KEY FILES:
- ONBOARDING.md → 5-min intro
- .ai-context.yaml → Portable context
- CLAUDE.md → Full architecture
- config/vif_config.yml → Framework tuning
- agents/orchestrator_swarm.py → Pipeline orchestration

AGENTS:
- watchlist_watcher: Core VIF logic
- orchestrator_swarm: Master controller
- indicators: Shared technical engine
- weekend_catalyst_agent: Macro briefing
- external_alpha_auditor: GitHub/HF research

WATCHLISTS (6 institutional, 170 tickers):
1. AI Physical Layer & Power Infrastructure (47)
2. AI Verticals Supply Chain (31)
3. Core Growth & Macro Indices (56)
4. Energy & AI Power Convergence (13)
5. Speculative & High-Beta (10)
6. Trump Admin Onshoring (13)

QUESTION: [Your question here]
```

---

## Next Steps

1. ✅ **Phase 1 Complete:** System scan & inventory
2. ✅ **Phase 2 Complete:** `.ai-context.yaml` + `ONBOARDING.md` created
3. ✅ **Phase 3 Complete:** Architectural documentation (this file)
4. ✅ **Phase 4 Complete:** Cross-reference validation

**You're now ready to:**
- Share this project with Cursor, Gemini, or Claude.ai
- Onboard new team members (send them `ONBOARDING.md`)
- Run analysis immediately (`python schedule_daily.py`)
- Integrate with external platforms via MCP

---

**Status:** Zero-Friction Context Layer **OPERATIONAL** (May 11, 2026)
