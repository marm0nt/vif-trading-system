# VIF Trading System — Complete Agent Inventory

**Last updated:** 2026-05-15 22:35 UTC  
**Status:** 9 specialist agents + 3 support systems operational  
**Framework:** Multi-agent swarm orchestration (KV cache + gossip routing + consensus)

---

## Quick Reference: Agent Roles & Responsibilities

| # | Agent | File | Role | Input | Output | Dependencies | Cache Layer |
|---|-------|------|------|-------|--------|--------------|-------------|
| 1 | **Catalyst Monitor** | `agents/weekend_catalyst_agent.py` | Earnings, policy, macro events | Watchlist tickers, date range | JSON: catalyst alerts, K4 flags | yfinance, beautifulsoup4 | L1 (KV) |
| 2 | **VIF Analyst** | `agents/watchlist_watcher.py` | Core signal logic (Volatility Imbalance Framework) | OHLCV + indicators, VIF config | BUY/SELL/HOLD signals, confidence (0-100) | yfinance, ta, anthropic | L2 (KV) |
| 3 | **FinViz Screener** | `agents/finviz_screener_agent.py` | 19 institutional screeners (Hunt, CANSLIM, etc.) | Finviz API, screener config | Fundamental + technical rankings | finvizfinance, requests | L2 (KV) |
| 4 | **Swing Trade Screener** | `scripts/active/analysis/swing_trade_screener_v2.py` | 5 setup types: PULLBACK_TO_MA20, BULLISH_MA_MOMENTUM, SUPPORT_BOUNCE, CONSOLIDATION_BREAKOUT, OVERSOLD_BOUNCE | Price action, volume, MA | Risk/reward ranked setups | yfinance, ta, numpy | Disk (24h) |
| 5 | **Signal Verifier** | Native in `swarm/__init__.py` | 4-gate validation: Volume, Fundamental, Sentiment, Macro | Raw signals, market context | PUBLISH / DOWNGRADE / REJECT | anthropic, ta | L2 (KV) |
| 6 | **Critic Agent** | `agents/external_alpha_auditor.py` | Low-confidence audit (<55%) via GitHub/HF MCP | VIF signals, research queries | Confidence boost/downgrade (+5 max, -10 floor) | anthropic, GitHub MCP, HF MCP | L3 (KV) |
| 7 | **Risk Agent** | `swarm/risk_agent.py` | Position sizing, drawdown analysis, circuit breaker | Portfolio state, risk config | Position size, stop-loss level, K1-K6 checks | yfinance, numpy, pandas | Real prices (cached) |
| 8 | **VectorBT Analyst** | `agents/indicators.py` (backtest integration) | Historical validation, Monte Carlo simulation | Historical OHLCV, strategy params | Backtest metrics, win rate, Sharpe | yfinance, vectorbt, numpy | Disk (vectorbt_cache/) |
| 9 | **Autoresearch Agent** | `swarm/autoresearch_agent.py` (Layer 8) | Iterative research synthesis, literature review | Trade setups, research prompts | Summary insights, factor validation | anthropic, requests | L4 (KV) |

---

## Detailed Agent Documentation

### 1. Catalyst Monitor Agent
**File:** `agents/weekend_catalyst_agent.py`

**Purpose:**  
Scans for earnings dates, government policy announcements, regulatory decisions, sector themes, and macro catalysts across all watchlists.

**When it runs:**
- Weekdays 07:00 CT (premarket catalyst scan)
- Saturday 08:00 CT (weekend macro briefing)
- Sunday 18:00 CT (Monday morning prep)

**Inputs:**
- Watchlist tickers (6 watchlists, 170 tickers)
- Historical earnings dates (24+ months)
- Policy/regulatory calendar

**Outputs:**
```json
{
  "catalyst_id": "catalyst-20260515-001",
  "ticker": "NVDA",
  "catalyst_type": "earnings",
  "date": "2026-05-22T04:00:00Z",
  "confidence": 95,
  "k4_flag": true,
  "impact": "DOWNGRADE",
  "context": "Quarterly earnings (Q1 FY27), high volatility expected"
}
```

**Kill Switches:**
- K4 (News Risk): Earnings within 5 days → DOWNGRADE signal confidence by 20-30 points

**Integration:**
- Called first by orchestrator (input to VIF analyst)
- Outputs to `reports/catalysts/`

---

### 2. VIF Analyst Agent (Core)
**File:** `agents/watchlist_watcher.py`

**Purpose:**  
Implements the Volatility Imbalance Framework v4.0. Analyzes price action, technical indicators, volume, and structural levels to generate BUY/SELL/HOLD signals.

**When it runs:**
- Premarket: 08:45 CT (1-month data lookback)
- After-hours: 16:05 CT (5-day data lookback)

**Inputs:**
- Ticker symbol
- OHLCV data (yfinance)
- Computed indicators: RSI, MACD, Bollinger Bands, EMA, ATR
- VIF framework config (`config/vif_config.yml`)
- Catalyst alerts (from Catalyst Monitor)

**Framework Layers:**
1. **Gamma Regime Detection** — Positive/negative/transition from price action
2. **Structural Levels** — Support/resistance from 20-day lookback
3. **Volume Confirmation** — Current vol vs. 20-day MA (threshold 1.5x)
4. **Kill Switch Validation** — K1-K6 override conditions

**Outputs:**
```json
{
  "ticker": "NVDA",
  "signal": "BUY",
  "confidence": 78,
  "reasoning": "Positive gamma regime, volume confirmation, structural support at $120.50",
  "gamma_regime": "positive",
  "volume_strength": 2.1,
  "structural_level": 120.50,
  "rsi": 62,
  "macd": "bullish_crossover",
  "kill_switches_triggered": []
}
```

**Kill Switches Applied:**
- K1: Extreme volatility → REJECT
- K2: Gap risk → DOWNGRADE
- K3: Low liquidity → REJECT
- K4: News risk (earnings) → DOWNGRADE
- K5: Correlation risk → DOWNGRADE
- K6: Technical breakdown → REJECT

**Model Configuration:**
- Model: claude-sonnet-4-6
- Temperature: 0 (deterministic)
- Max tokens: 1024
- Batching: 15 tickers per Claude call

**Integration:**
- Input from Catalyst Monitor
- Batched across 15 tickers
- Output to Signal Verifier + Report Builder
- Cache hit: 45-50% (KV cache L2)

---

### 3. FinViz Screener Agent
**File:** `agents/finviz_screener_agent.py`

**Purpose:**  
Runs 19 institutional screeners independently (Hunt, CANSLIM, Kell variants, earnings-driven) to discover stocks matching expert criteria. Compares results with VIF signals for overlap analysis.

**When it runs:**
- Weekdays 07:30 CT (independent discovery scan)
- Separate from main VIF watchlist analysis

**Screeners implemented:**
1. Hunt Screener (5 setups)
2. CANSLIM Screener (2 variants)
3. Kell Screener (1 base + variants)
4. Earnings-Driven (quarterly)
5. Value + Growth hybrid (2)
6. Momentum + Tape (2)
7. Sector rotation (2)

**Inputs:**
- FinViz API context (cached, updated 07:30 daily)
- Market data (sector, industry, volatility)
- Fundamental data (earnings, revenue, margin)

**Outputs:**
```json
{
  "screener": "hunt_growth",
  "matches": [
    {
      "ticker": "VSCO",
      "rank": 1,
      "score": 94,
      "factors": ["revenue_growth", "margin_expansion", "relative_strength"],
      "vif_overlap": true,
      "vif_signal": "BUY"
    }
  ],
  "overlap_rate": 0.68,
  "novel_discoveries": 5
}
```

**Integration:**
- Runs independently before VIF watchlist analysis
- Discovers tickers outside watchlist scope
- Novel discoveries flagged for research (Autoresearch Agent)
- Can feed back into watchlist expansion

---

### 4. Swing Trade Screener Agent
**File:** `scripts/active/analysis/swing_trade_screener_v2.py`

**Purpose:**  
Screens all watchlists for 2-4 week swing trade setups. Identifies 5 archetypal patterns and ranks by risk/reward ratio.

**When it runs:**
- Weekdays 09:35 CT (market-open swing screener)
- On-demand via `python swing_trade_screener_v2.py`

**5 Setup Types:**
1. **PULLBACK_TO_MA20** — Pullback to 20-day MA, bullish MA stack
2. **BULLISH_MA_MOMENTUM** — Bullish EMA crossover, increasing volume
3. **SUPPORT_BOUNCE** — Price bounces from key support level
4. **CONSOLIDATION_BREAKOUT** — Consolidation rectangle, volume breakout
5. **OVERSOLD_BOUNCE** — RSI <30, reversing higher on volume

**Inputs:**
- Watchlist tickers (170 total)
- Price action (daily/4h charts)
- Volume analysis
- EMA/SMA configuration

**Outputs:**
```json
{
  "setup_type": "PULLBACK_TO_MA20",
  "ticker": "SMCI",
  "entry": 37.50,
  "stop_loss": 35.20,
  "target": 42.80,
  "risk_reward": 2.4,
  "confidence": 72,
  "rank": 1
}
```

**Ranking Criteria:**
- Risk/reward ratio (2.5+ preferred)
- Confidence score (volume + RSI + MA alignment)
- Position in market structure

**Integration:**
- Runs after market open (09:35 CT)
- Output to reports/swing-trades/
- Feeds into Risk Agent for position sizing

---

### 5. Signal Verifier Agent
**File:** Native in `swarm/__init__.py`

**Purpose:**  
Independent 4-gate validation of all generated signals before publication. Prevents low-quality signals from reaching traders.

**4 Validation Gates:**
1. **Volume Gate** — Sufficient liquidity and volume confirmation
2. **Fundamental Gate** — Company fundamentals aligned with signal
3. **Sentiment Gate** — Market sentiment supports direction (news, social)
4. **Macro Gate** — Broader market conditions support signal (sector, indices)

**Inputs:**
- Raw signals from VIF Analyst
- Market context (volume, sentiment, macro conditions)
- Kill switch status

**Outputs:**
```json
{
  "signal_id": "vif-20260515-nvda-buy",
  "ticker": "NVDA",
  "original_signal": "BUY",
  "original_confidence": 78,
  "action": "PUBLISH",
  "gates": {
    "volume": "PASS",
    "fundamental": "PASS",
    "sentiment": "PASS",
    "macro": "PASS"
  },
  "final_confidence": 78
}
```

**Possible Actions:**
- **PUBLISH** — Signal passes all gates
- **DOWNGRADE** — 1-2 gates fail; reduce confidence
- **REJECT** — 3+ gates fail; do not publish

**Integration:**
- Runs after VIF Analyst (before Report Builder)
- Can reduce confidence or reject signals
- Prevents bad signals from reaching traders

---

### 6. Critic Agent
**File:** `agents/external_alpha_auditor.py`

**Purpose:**  
For low-confidence signals (<55%), queries GitHub and Hugging Face for external validation. Searches academic papers, GitHub repos for similar setups, factor validation.

**When it runs:**
- Triggered by Signal Verifier on signals <55% confidence
- Or on-demand for specific ticker deep dives

**Inputs:**
- VIF signal + reasoning
- Ticker fundamentals
- Recent price action

**Research process:**
1. Search GitHub for reference implementations (factor matching)
2. Search Hugging Face for academic papers
3. Compare factors to VIF baseline
4. Extract novel factors for future integration

**Outputs:**
```json
{
  "signal_id": "vif-20260515-tsm-buy",
  "original_confidence": 48,
  "research_result": "BOOST",
  "boost_amount": 8,
  "final_confidence": 56,
  "reasoning": "2 GitHub repos confirm semiconductor uptrend; paper validates volume/momentum factors",
  "novel_factors": ["foundry_utilization", "customer_mix_improvement"],
  "references": [
    "github.com/repo1/semiconductor-screener",
    "huggingface.co/paper/semiconductor-momentum"
  ]
}
```

**Confidence adjustments:**
- Boost: +5 max (if research confirms signal)
- Downgrade: -10 floor (if research contradicts signal)

**Integration:**
- Optional layer (cost-optimized: only runs on <55% confidence)
- Feeds back into knowledge base (`data/external_repos_catalog.json`)
- Week 2-3 roadmap: Novel factor backtesting

---

### 7. Risk Agent
**File:** `swarm/risk_agent.py`

**Purpose:**  
Computes position sizing, drawdown analysis, and enforces circuit breaker conditions. Ensures portfolio stays within risk bounds.

**When it runs:**
- After Signal Verifier (before Report Builder)
- Continuous monitoring (circuit breaker checks every 5 min)

**Inputs:**
- Verified signals (from Signal Verifier)
- Current portfolio state
- Risk configuration (`config/vif_config.yml`)
- Live market prices (cached, real, not random)

**Risk Calculations:**
1. **Position Sizing** — Kelly criterion or fixed fractional (configurable)
2. **Stop-Loss Placement** — Based on ATR, structural levels
3. **Drawdown Analysis** — Rolling 20-day max drawdown
4. **Circuit Breaker** — Emergency stop if drawdown >15% or volatility extreme

**Outputs:**
```json
{
  "signal_id": "vif-20260515-nvda-buy",
  "position_size": 100,
  "entry": 145.20,
  "stop_loss": 140.50,
  "target": 155.80,
  "risk_amount": 470,
  "reward_amount": 1060,
  "kelly_fraction": 0.08,
  "circuit_breaker": "PASS",
  "portfolio_drawdown": "8.2%"
}
```

**Circuit Breaker Conditions:**
- K1: RSI >80 or <20 (extreme volatility)
- Portfolio drawdown >15%
- VIX >40 (market stress)
- Correlation breakdown (>0.8 with index)

**May 15 Fix:**
- Replaced `np.random.uniform()` random prices with real cached prices from yfinance
- Circuit breaker now uses actual market data, not simulation

**Integration:**
- Final validation before position execution
- Can reject signals based on portfolio risk
- Feeds position sizing to Report Builder

---

### 8. VectorBT Analyst Agent
**File:** `agents/indicators.py` (backtesting integration)

**Purpose:**  
Historical validation and Monte Carlo simulation. Tests signals on past data to estimate win rate, Sharpe ratio, and edge confidence.

**When it runs:**
- Weekly validation runs (Friday 16:30 CT)
- On-demand for signal analysis
- Overnight backtests (non-blocking)

**Inputs:**
- Historical OHLCV (1-5 years)
- Signal strategy parameters
- Risk/reward assumptions

**Backtesting metrics:**
```json
{
  "signal_type": "VIF_BUY",
  "lookback_period": "252 days",
  "win_rate": 0.62,
  "avg_win": 0.034,
  "avg_loss": -0.018,
  "profit_factor": 2.1,
  "sharpe_ratio": 1.45,
  "max_drawdown": -0.12,
  "monte_carlo_confidence": 0.78
}
```

**Integration:**
- Validates signal edge (ensures 55%+ win rate minimum)
- Feeds confidence adjustment to Signal Verifier
- Reports to `reports/setups/` for trader review
- Long-term: Backtesting.py integration (1-2 day task)

---

### 9. Autoresearch Agent
**File:** `swarm/autoresearch_agent.py` (Layer 8 in swarm)

**Purpose:**  
Iterative research synthesis. Takes trade setups, novel factors, and research queries from other agents. Synthesizes findings into actionable insights.

**When it runs:**
- Triggered by Critic Agent on novel factors
- Weekly macro synthesis (Sunday evening)
- On-demand research prompts

**Research workflow:**
1. Receive research query from another agent
2. Query anthropic.Anthropic() for synthesis
3. Integrate with cached research database
4. Output actionable insights + confidence adjustments

**Inputs:**
- Novel factors from Critic Agent
- Macro context from Catalyst Monitor
- Trade setups from any specialist

**Outputs:**
```json
{
  "research_id": "autoresearch-20260515-001",
  "query": "semiconductor equipment cyclicality",
  "synthesis": "ASML → ASML tools → foundry demand → AI CapEx",
  "confidence_boost": 5,
  "factors_validated": ["foundry_utilization", "tool_ship_rate"],
  "integration_status": "ready_for_backtest",
  "weekly_report": "reports/research/synthesis-20260515.md"
}
```

**Layer 8 Position:**
- Part of Swarm KV cache architecture (L4)
- Benefits from latent collaboration with other agents
- Feeds insights back into Critic Agent + VIF Analyst

**Integration:**
- Triggered by novel factors from Critic Agent
- Outputs to research database + weekly synthesis report
- Feeds back into signal confidence adjustments

---

## Support Systems

### Agent Manager Fix (`agents/agent_manager_fix.py`)
**Purpose:** Prevents "ModuleNotFoundError in managed agents" by aligning Python environment before orchestrator initialization.

**Functions:**
- `initialize_agent_manager()` — Drop-in replacement for agent initialization
- `diagnose_agent_environment()` — Check environment status
- `_align_agent_environment()` — Internal alignment function

**Usage:**
```python
from agents.agent_manager_fix import initialize_agent_manager

manager = initialize_agent_manager(
    model=client,
    tools=[search_tool],
    managed_agents=[researcher, coder],
    max_steps=10
)
```

### Environment Bootstrap (`bootstrap.py`, `scripts/activate_agent_env.py`)
**Purpose:** Venv-free architecture validation. Ensures system Python is used, not broken venv paths.

**Key checks:**
- Python executable path
- PYTHONPATH environment variable
- Critical imports: anthropic, smolagents, pandas, numpy

---

## Swarm Orchestration Architecture

### KV Cache Layer (3-layer recomputation)
- **L1:** Catalyst Monitor outputs (earnings dates, policy)
- **L2:** VIF Analyst + FinViz Screener outputs (signals, fundamentals)
- **L3:** Critic Agent (research validation results)
- **L4:** Autoresearch synthesis (novel factors, macro insights)

**Hit rate:** 45-50% (LRAgent, updated daily)

### Gossip Router (500ms timeout)
- Broadcast-based agent communication
- Consensus-building via message passing
- Conflict resolution via Confidence-Weighted Consensus

### Consensus Resolver
- Weighted by agent confidence scores
- Handles conflicting outputs (rare, <5% incidence)
- Final signal reflects collective agent reasoning

---

## Agent Execution Order (All Modes)

```
PREMARKET (08:45 CT):
  1. Catalyst Monitor    → Earnings/policy alerts
  2. VIF Analyst         → BUY/SELL/HOLD signals (batched)
  3. Swing Screener      → 5 setup types
  4. Signal Verifier     → 4-gate validation
  5. [Critic Agent]      → If <55% confidence
  6. Risk Agent          → Position sizing
  7. Report Builder      → HTML output

MARKET_OPEN (09:35 CT):
  1. Swing Screener      → Updated market-open analysis
  2. Risk Agent          → Position adjustment
  3. Report Builder      → Updated report

AFTERHOURS (16:05 CT):
  1. VIF Analyst (5d)    → Daily conviction
  2. Signal Verifier     → Validation
  3. Risk Agent          → EOD adjustments
  4. Report Builder      → Daily summary
  5. Postmarket Debrief  → Hit rate analysis + alpha extraction

WEEKEND (Sat/Sun):
  1. Catalyst Monitor    → Earnings + macro catalysts
  2. Autoresearch        → Macro synthesis
  3. Report Builder      → Monday briefing

FULL (On-demand):
  → All above modes sequentially
```

---

## Adding New Agents (4-Step Protocol)

1. **Create agent file** in `agents/` or `swarm/`
2. **Implement standard interface:**
   - `execute(context: dict) → dict` method
   - Return JSON with signal/analysis + confidence
3. **Register in orchestrator:**
   - Import in `agents/orchestrator_swarm.py`
   - Add to `PIPELINES[mode]` task_prompt
4. **Test offline first:**
   - Use `test_harness.py` (no API credits)
   - Verify output schema matches expectations

---

## Dependencies & Integration Points

### Core Libraries
- **anthropic** ≥0.97.0 — Claude API
- **yfinance** ≥1.0.0 — Market data
- **finvizfinance** ≥1.3.0 — Institutional screeners
- **ta** ≥0.11.0 — Technical indicators
- **pandas**, **numpy** — Data processing
- **PyYAML** — Config loading

### MCP Integrations
- **GitHub MCP** — External repo research (Critic Agent)
- **HuggingFace MCP** — Academic paper search (Critic Agent)

### External Services
- **Claude API** (Sonnet 4.6, Haiku 4.5, Opus 4.7)
- **Yahoo Finance** (free OHLCV)
- **Finviz API** (fundamental + technical screeners)

---

## Performance Benchmarks (May 15, 2026)

| Metric | Value | Notes |
|--------|-------|-------|
| Premarket execution | 12-15s | All 170 tickers, batched |
| Cache hit rate | 45-50% | KV cache L1-L4 |
| Cost per pipeline | ~$0.015 | Batching + cache optimization |
| Daily budget | $0.07 | All 8 pipeline types |
| Signal rejection rate | 25-30% | Via 4-gate verifier |
| Risk agent circuit breaker fires | <5 per month | Normal operation |

---

## Troubleshooting & Monitoring

### Agent Failures
- Check `logs/orchestrator_swarm.log` for error messages
- Sentry daemon scans logs every 5 min
- Failed signals → repair-subagent handoff (A2A JSON)

### Low Signal Volume
- Verify catalog reloads: `grep "Loading watchlist" logs/orchestrator_swarm.log`
- Check kill switch triggers: `grep "K[1-6]" logs/orchestrator_swarm.log`
- Run offline test: `python tests/test_harness.py`

### Cache Misses
- Monitor: `grep "Cache hit rate:" logs/orchestrator_swarm.log`
- Expected: 45-50% (improvements via backtesting.py integration)
- Reset: Delete `data/` cache directories (regenerates on next run)

---

## References

- **CLAUDE.md** — Master development guide
- **docs/SWARM_ORCHESTRATOR_GUIDE.md** — Best practices + GitHub repos
- **config/vif_config.yml** — All framework parameters
- **docs/system/CHANGELOG.md** — Detailed version history

---

**Last updated:** 2026-05-15 22:35 UTC  
**Maintained by:** Claude Code + auto-update post-commit hook  
**Next review:** 2026-05-22 (weekly sync)
