# VIF Trading System — New LLM Onboarding Guide

**Read this first.** Then read `CLAUDE.md` for deep dives.

---

## What This System Does (60 seconds)

**VIF Trading System** = AI-powered signal generation for swing trades.

- **Input:** 170 institutional tickers across 6 watchlists (AI, Energy, Macro, Trump Admin themes)
- **Framework:** Volatility Imbalance Framework v4.0 (gamma regime + structural levels + volume + kill switches)
- **Output:** BUY/SELL/HOLD signals with confidence scores (0-100) for 2-4 week holding periods
- **Cost:** ~$0.13/day (13,000 tokens/day via Claude API)
- **Models Used:** Sonnet 4.6 (main analyst), Haiku 4.5 (router), Opus 4.7 (synthesis)

---

## Why This Exists

Swing traders need signals based on technical + macro context, not sentiment or algos. VIF filters for **regime confirmation + structural confirmation + volume confirmation**, then applies 6 kill switches to reject false signals before publishing.

Result: **3 high-conviction signals > 30 low-confidence noise.**

---

## System Architecture (5 minutes)

### The Pipeline

```
Watchlist Files (6 institutional lists, 170 tickers)
        ↓
[Watchlist Parser] → Clean ticker list
        ↓
[Data Fetcher] → yfinance + cache → OHLCV + RSI/MACD/BB/EMA/ATR
        ↓
[VIF Analyst] → Claude API (deterministic, temp=0) → BUY/SELL/HOLD
        ↓
[Kill Switch Validator] → K1–K6 override checks
        ↓
[Signal Verifier] → 4-gate validation (Volume, Fundamental, Sentiment, Macro)
        ↓
[Report Builder] → JSON + HTML output
```

### The 6 Watchlists (4-tier each)

Each watchlist has 4 organizational tiers:

| Tier | Purpose | Usage |
|------|---------|-------|
| **VANGUARD** | Regime instruments only | Check first before any entry |
| **PRIMARY_CONVICTION** | High-conviction entries | Default scan tier (60–70% capital) |
| **SCOUTS** | Setup confirmation needed | Speculative, requires confirmation (20–30% capital) |
| **WAITING_LIST** | Monitor only | Pre-screened for future entry |

**Watchlist names & IDs:**
- **WL1:** AI Physical Layer & Power Infrastructure (47 tickers, Risk-On)
- **WL2:** AI Verticals Supply Chain (31 tickers, Risk-On)
- **WL3:** Core Growth & Macro Indices (56 tickers, Both regimes)
- **WL4:** Energy & AI Power Convergence (13 tickers, Risk-On)
- **WL5:** Speculative & High-Beta (10 tickers, Risk-On ONLY)
- **WL6:** Trump Admin Onshoring (13 tickers, Risk-On)

---

## Critical Files to Know

### If You Want To...

**Understand the whole system:**
- Read: `CLAUDE.md` (master guide, all architecture + examples)
- Read: `.ai-context.yaml` (this portable context card)

**Understand VIF signal logic:**
- Read: `agents/watchlist_watcher.py` (core analyzer)
- Reference: `config/vif_config.yml` (all framework parameters)
- Check: `docs/SWARM_ORCHESTRATOR_GUIDE.md` (pipeline flow)

**Understand the 6 watchlists:**
- Read: `.claude/memory/watchlist_structure.md` (tier breakdown)
- View: `reports/watchlist_institutional_structure.html` (full inventory with tickers)

**Run analysis yourself:**
```bash
# Single watchlist
python agents/watchlist_watcher.py --watchlist vantage_portfolio

# Full pipeline (all watchlists, all modes)
python schedule_daily.py

# Test offline (no API credits spent)
python tests/test_harness.py
```

**Check API costs:**
```bash
python scripts/active/utilities/check_usage.py
# Output: daily spend, monthly projection, cache hit rate
```

---

## VIF Framework (The Secret Sauce)

### 4-Layer Signal Logic

| Layer | What It Does | Example |
|-------|-------------|---------|
| **Gamma Regime** | Is price action showing positive (bullish) or negative (bearish) momentum? | Last 3 bars: Higher Highs + Higher Lows = Positive regime |
| **Structural Levels** | Where are key support/resistance zones? | 20-day lookback: 25th percentile = support, 75th = resistance |
| **Volume Confirmation** | Is volume backing this move? | Current vol > 1.5x 20-day MA = confirmation |
| **Kill Switch Validation** | Does any override condition trigger? | K1 (extreme RSI) OR K2 (gap risk) → REJECT |

### 6 Kill Switches (Override Conditions)

**K1 — Extreme Volatility:** RSI > 80 or < 20 → REJECT
**K2 — Gap Risk:** 5-day range > 10% → DOWNGRADE
**K3 — Low Liquidity:** Volume < 1M shares → REJECT
**K4 — News Risk:** Earnings within 5 days → DOWNGRADE
**K5 — Correlation Risk:** > 0.8 correlation with major index → DOWNGRADE
**K6 — Technical Breakdown:** Below 20-day MA + declining volume → REJECT

**How they work:** If ANY kill switch triggers, signal confidence is reduced or rejected outright.

---

## Key Concepts

### Signal Confidence (0–100)

- **80+:** High conviction (publish immediately)
- **55–79:** Moderate conviction (pass through signal_verifier 4 gates)
- **<55:** Low conviction (trigger external_alpha_auditor for GitHub/HF research validation)

### Temperature = 0 (Deterministic)

All Claude API calls use `temperature=0`, meaning the same ticker analyzed twice will produce identical signals. This ensures reproducibility and prevents variance in trading decisions.

### Batching (Cost Optimization)

Tickers are analyzed in batches of 15 per Claude call (not individual calls). This reduces token spend from $1+/day to $0.13/day.

### Cache Layer (Speed Optimization)

yfinance data is cached locally for 24 hours. Indicators (RSI, MACD, etc.) are computed once and reused across multiple analyses.

---

## Common Questions

**Q: How do I add a new watchlist?**
A: Create a new `.txt` file in `watchlists/` with comma- or newline-separated tickers. Then run `python agents/watchlist_watcher.py --watchlist <name_without_txt>`.

**Q: What if a signal fires but I don't trust it?**
A: Check the confidence score. If < 55%, the external_alpha_auditor will have searched GitHub/Hugging Face for supporting research. Read the audit notes in `reports/raw/`.

**Q: How do I modify kill switches?**
A: Edit `config/vif_config.yml` under the `kill_switches` section. Reload the script and rerun analysis.

**Q: Can I use Haiku instead of Sonnet to save costs?**
A: Not recommended. Sonnet 4.6 is the analyst model for a reason — it has the reasoning depth needed for VIF framework. Haiku is used for cheap routing only. Switching analysts will degrade signal quality.

**Q: Where do reports go?**
A: `reports/` folder, organized by pipeline mode:
- `reports/premarket/` — Morning signals
- `reports/catalysts/` — Market-open catalyst scans
- `reports/swing-trades/` — Setup rankings
- `reports/weekend/` — Monday briefing
- `reports/raw/` — JSON data (intermediate format)

---

## Your First Task (5 minutes)

1. **Verify setup:**
   ```bash
   python tests/test_api_key.py
   ```
   ✓ You should see: "API key valid. Ready for analysis."

2. **Run offline test (no credits):**
   ```bash
   python tests/test_harness.py
   ```
   ✓ You should see mock signal output in terminal.

3. **Run real analysis (uses credits):**
   ```bash
   python agents/watchlist_watcher.py --watchlist vantage_portfolio
   ```
   ✓ You should see JSON output in `reports/raw/`.

4. **Check the report:**
   Open: `reports/watch list_institutional_structure.html` (browser-friendly overview)

---

## Quick Reference: Terminology for Prompts

Use this shorthand when talking to me about your project:

| Term | Means |
|------|-------|
| **Full institutional sweep** | Run all 6 watchlists, all 4 tiers |
| **Scan PRIMARY** | Analyze PRIMARY_CONVICTION tier only (default) |
| **Check VANGUARD** | Analyze regime instruments only |
| **WL1:SCOUTS** | Analyze WL1's speculative scouts |
| **Run the portfolio** | Run full pipeline via `schedule_daily.py` |
| **Tier scan** | Check VANGUARD first, then PRIMARY (typical workflow) |

---

## External Integrations (Advanced)

### GitHub & Hugging Face MCP
- **Purpose:** Validate low-confidence signals against academic research + open-source implementations
- **When it triggers:** Automatically when signal confidence < 55%
- **Cost:** ~$0.019/month (negligible, cached 30 days)
- **Setup:** Requires GitHub personal access token + Hugging Face token in `.env`

### TradingView MCP
- **Purpose:** Live chart control (screenshot, Pine Script, alerts, replay)
- **Status:** Separate from Python pipeline (node.js-based)
- **Setup:** See `docs/TradingView-MCP-Setup.md`

---

## Support & Documentation

| Resource | When to Use |
|----------|------------|
| `CLAUDE.md` | Deep dive into architecture + all examples |
| `.ai-context.yaml` | Portable summary for other AI platforms |
| `docs/AGENTS.md` | Agent inventory + detailed roles |
| `docs/SWARM_ORCHESTRATOR_GUIDE.md` | Pipeline orchestration patterns |
| `docs/QUICKSTART.md` | Installation + first run |
| `.claude/memory/` | User preferences + architecture decisions |

---

## Next Steps

1. ✅ **Read this file** (you're here)
2. → **Read `CLAUDE.md`** (architecture + all details)
3. → **Run your first analysis** (see "Your First Task" above)
4. → **Customize `config/vif_config.yml`** (tune framework for your risk tolerance)
5. → **Schedule daily runs** (set up cron via `schedule_daily.py`)

---

## Glossary

- **VIF:** Volatility Imbalance Framework (proprietary signal logic)
- **Gamma Regime:** Price action momentum (positive/negative/transition)
- **Structural Levels:** Support/resistance zones from historical lookback
- **Kill Switch:** Override condition that downgrades or rejects a signal
- **Signal Confidence:** 0–100 score indicating how confident we are in a signal
- **Temperature:** Randomness parameter (0 = deterministic, 1.0 = random). We use 0.
- **Batching:** Processing multiple tickers per API call (cost optimization)
- **Cache TTL:** Time-to-live for cached data (24 hours for yfinance data)

---

**You're ready. Start with the "Your First Task" section, then dive into `CLAUDE.md` for the full picture.**
