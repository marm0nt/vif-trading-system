# Quick Start for Gemini AI — VIF Trading System

**Purpose:** Get up to speed on VIF system in 10 minutes.

---

## What is VIF?

**VIF Trading System** analyzes 170 institutional stocks using a 4-layer framework:

1. **Gamma Regime** — Is price action bullish or bearish?
2. **Structural Levels** — Where are support/resistance?
3. **Volume Confirmation** — Is volume above 20-day average?
4. **Kill Switches** — Are there override conditions (K1-K6)?

**Output:** BUY/SELL/HOLD signals with 0-100 confidence (always deterministic).

---

## Key Concepts

### The 9-Agent Swarm

Think of the system as a council of 9 specialists:

| Agent | Job | Says |
|-------|-----|------|
| Catalyst Monitor | Earnings/policy events | "NVDA earnings 2026-05-22" |
| VIF Analyst | Technical analysis | "BUY NVDA, confidence 78" |
| FinViz Screener | Fundamental analysis | "Strong fundamentals" |
| Swing Screener | Pattern recognition | "PULLBACK_TO_MA20 setup" |
| Signal Verifier | Quality control | "All 4 gates pass → PUBLISH" |
| Critic Agent | Research validation | "Boost confidence +5 (research)" |
| Risk Agent | Position sizing | "Max position 100 shares" |
| VectorBT | Backtesting | "Win rate 62%, Sharpe 1.45" |
| Autoresearch (L8) | Macro synthesis | "Semiconductor cycle bullish" |

All 9 agents speak at once → final signal is consensus.

### The 6 Watchlists (170 Tickers)

Organized into 4 tiers each:

```
TIER 1: MACRO_VANGUARD (2-9 tickers)
  → Check first. These set regime.
  
TIER 2: PRIMARY_CONVICTION (60-70% capital)
  → Main trades. High conviction VIF signals.
  
TIER 3: SPECULATIVE_SCOUTS (20-30% capital)
  → Setup confirmation needed. Higher risk.
  
TIER 4: WAITING_LIST
  → Monitor only. Not yet tradeable.
```

Each tier serves different risk tolerance.

### Kill Switches (K1-K6)

6 veto conditions that downgrade or reject signals:

| K | Condition | Action |
|---|-----------|--------|
| K1 | Extreme volatility (RSI >80 or <20) | REJECT |
| K2 | Gap risk (5d range >10%) | DOWNGRADE |
| K3 | Low liquidity (vol <1M shares) | REJECT |
| K4 | Earnings within 5 days | DOWNGRADE |
| K5 | Correlation >0.8 with market | DOWNGRADE |
| K6 | Below 20-day MA + declining vol | REJECT |

If any K-switch triggers → signal loses confidence or dies.

---

## How It Works (Daily Flow)

### Morning (07:00-09:35 CT)

```
07:00  Catalyst Monitor scans
       → "NVDA earnings 2026-05-22 (K4 flag)"
       
08:45  VIF Analyst analyzes watchlists
       → "NVDA: BUY 78, SMCI: BUY 72, ASML: HOLD 55"
       
09:35  Swing Screener finds 2-4 week setups
       → "PULLBACK_TO_MA20: SMCI (R:R 2.4, rank #1)"
       
Reports → reports/premarket/*.html
```

### Afternoon (16:05 CT)

```
16:05  VIF Analyst (5-day lookback)
       → Daily conviction scores
       
       Signal Verifier validates
       → "All signals pass 4 gates"
       
       Risk Agent sizes positions
       → "NVDA: 100 shares, stop 140.50"
       
Reports → reports/daily/*.html
```

### Weekend (Sat 08:00, Sun 18:00)

```
       Catalyst Monitor + Autoresearch
       → Macro synthesis
       → "Monday morning briefing ready"
       
Reports → reports/weekend/*.html
```

---

## Common Workflows

### Q: "Is NVDA a buy?"

1. Check `reports/premarket/` → Latest signal
2. Read confidence score (0-100)
3. Check kill switches in `logs/orchestrator_swarm.log`
4. Review risk/reward in `reports/swing-trades/`

### Q: "Why did signal X downgrade?"

```bash
grep "DOWNGRADE" logs/orchestrator_swarm.log
# Shows K-switch trigger
# K4 = earnings risk, K5 = correlation risk, etc.
```

### Q: "What's the win rate for setup Y?"

1. `reports/setups/` → Historical backtest results
2. Check VectorBT metrics (win rate, Sharpe)
3. Confidence score reflects backtest edge

### Q: "Can I add a new stock to watchlist?"

```bash
echo "NEW_TICKER" >> watchlists/vantage_portfolio.txt
python agents/orchestrator_swarm.py --ticker NEW_TICKER
```

---

## Where to Find Things

| Question | Answer | File |
|----------|--------|------|
| What are all agents? | 9-agent overview | `docs/AGENTS_INVENTORY.md` |
| How does swarm work? | Architecture details | `docs/MULTIAGENT_SWARM_ARCHITECTURE.md` |
| What's my framework? | VIF v4.0 parameters | `config/vif_config.yml` |
| Latest system status? | Current ops overview | `docs/SYSTEM_CONTEXT.md` |
| How to run manually? | CLI commands | Below |
| What happened today? | Execution logs | `logs/orchestrator_swarm.log` |
| How much did I spend? | Cost tracking | `python scripts/active/utilities/check_usage.py` |

---

## Essential Commands

### Run Analysis
```bash
# Full automatic (all modes)
python schedule_daily.py

# Single mode
python agents/orchestrator_swarm.py --mode premarket
python agents/orchestrator_swarm.py --mode afterhours
python agents/orchestrator_swarm.py --mode full

# Single ticker
python agents/orchestrator_swarm.py --ticker NVDA

# Interactive mode (for development)
python agents/orchestrator_swarm.py --repl
```

### Check Status
```bash
# Watch live log
tail -f logs/orchestrator_swarm.log

# Check cache performance
grep "Cache hit rate:" logs/orchestrator_swarm.log

# Monitor errors
grep "\[SENTRY\]" logs/scheduler.log

# API costs
python scripts/active/utilities/check_usage.py
```

### Testing
```bash
# Offline test (no API credits)
python tests/test_harness.py

# Verify API key
python tests/test_api_key.py
```

---

## Signal Quality Checklist

Before trading on a signal, verify:

- [ ] Confidence ≥ 60 (strong signal)
- [ ] No K-switches triggered (check logs)
- [ ] Passes 4-gate verification (Volume, Fundamental, Sentiment, Macro)
- [ ] Risk/reward ≥ 2.0 (if swing setup)
- [ ] Backtest win rate ≥ 55% (if historical data available)
- [ ] Position sizing ≤ portfolio max (from Risk Agent)

---

## Performance Expectations

| Metric | Target | Reality |
|--------|--------|---------|
| Daily cost | $0.07 | Actual cost tracking in logs |
| Execution time | 12-15s | Check logs/orchestrator_swarm.log |
| Cache hit rate | 45-50% | Monitored via logs |
| Signal rejection rate | 25-30% | Via 4-gate verifier |
| Conflicts (agent disagreement) | <5% | Auto-resolved via consensus |

---

## Troubleshooting

### "No reports generated today"
```bash
# Check if scheduler is running
ps aux | grep schedule_daily.py

# Check for errors
tail -100 logs/scheduler.log | grep ERROR

# Manual run
python agents/orchestrator_swarm.py --mode premarket
```

### "Signals have low confidence"
- Check K-switch triggers: `grep K[1-6] logs/orchestrator_swarm.log`
- Verify cache warmed up: `grep "Cache hit rate:" logs/orchestrator_swarm.log`
- Check market volatility: VIX likely elevated

### "API authentication fails"
- Verify `.env` has valid `ANTHROPIC_API_KEY`
- Run: `python tests/test_api_key.py`
- Check key hasn't expired

---

## Learning Path

1. **Start here:** This file (10 min)
2. **Understand framework:** `docs/SYSTEM_CONTEXT.md` (20 min)
3. **Learn agents:** `docs/AGENTS_INVENTORY.md` (30 min)
4. **Deep dive:** `docs/MULTIAGENT_SWARM_ARCHITECTURE.md` (45 min)
5. **Configure:** `config/vif_config.yml` (15 min)
6. **Master development:** `CLAUDE.md` (full guide, 60+ min)

---

## Key Takeaways

✅ **VIF is deterministic** — Same input → same output (temperature=0)  
✅ **9-agent consensus** — Rare conflicts, high-quality signals  
✅ **50% cheaper** — KV cache optimization cuts costs in half  
✅ **Fast execution** — 12-15s per pipeline  
✅ **Continuously monitored** — Sentry catches errors automatically  
✅ **Production-ready** — Phase 1-4 complete, deployed May 15, 2026

---

**Questions?** Check `docs/SYSTEM_CONTEXT.md` or email martinadadey47@gmail.com

**Last updated:** 2026-05-15 22:45 UTC
