---
name: vif-agent-reference
description: Centralized CLI reference for all VIF Trading System subagents
---

# Agent CLI Reference

All subagents delegate to corresponding Python implementations. Use these commands to run analysis directly via CLI, or invoke subagents through `/agents` panel for Claude-managed execution.

---

## VIF Analyst → `agents/watchlist_watcher.py`

Analyze tickers using the VIF v4.0 framework. Generates BUY/SELL/HOLD signals with kill switch evaluation.

```bash
# Single watchlist
python agents/watchlist_watcher.py --watchlist vantage_portfolio

# All watchlists
python agents/watchlist_watcher.py --all

# Specific watchlist with custom period
python agents/watchlist_watcher.py --watchlist ai_verticals --period 1mo
```

---

## Market Researcher → `agents/claude_research_agent.py`

Ad-hoc VIF framework Q&A. Explain signals, gamma regimes, technical patterns.

```bash
# Single query
python agents/claude_research_agent.py --query "Why is NVDA showing a BUY signal?"

# With model role (router/analyst/synthesizer)
python agents/claude_research_agent.py --query "Explain gamma regime for QQQ" --model analyst
```

---

## Weekend Catalyst Analyst → `agents/weekend_catalyst_agent.py`

Scan all watchlists for catalysts, earnings, macro themes. Generates Monday morning briefing.

```bash
# Generate weekend briefing
python agents/weekend_catalyst_agent.py

# Output: reports/weekend_briefing_{timestamp}.json
```

---

## Swing Trade Screener → `scripts/swing_trade_screener_v2.py`

Identify 2–4 week swing setups across all watchlists. Ranks by risk/reward.

```bash
# Run full screening
python scripts/swing_trade_screener_v2.py

# Output: reports/swing_trades_{timestamp}.json
```

---

## Catalyst Monitor → `scripts/catalyst_analysis.py`

Static catalyst database (government contracts, earnings, regulatory). Generates catalyst report.

```bash
python scripts/catalyst_analysis.py

# Output: reports/catalysts_{timestamp}.json
```

---

## Report Builder → `agents/report_ui_agent.py`

Convert JSON analysis → Markdown reports. Also uses `scripts/html_report_generator.py` for HTML.

```bash
# Process all raw JSON → Markdown
python agents/report_ui_agent.py

# Convert single report
python agents/report_ui_agent.py reports/raw/analysis_20260502.json

# Output: reports/daily/{timestamp}.md
```

---

## Orchestrator Coordinator → `agents/orchestrator.py`

Master pipeline controller. Coordinates all agents for multi-mode analysis (premarket, full, afterhours, weekend, single-ticker).

```bash
# Premarket scan (1-month data, Haiku + Sonnet routing)
python agents/orchestrator.py --mode premarket

# Full end-of-week (all watchlists, deep analysis)
python agents/orchestrator.py --mode full

# Single ticker deep dive (all frameworks)
python agents/orchestrator.py --ticker NVDA

# Weekend macro briefing
python agents/orchestrator.py --mode weekend

# All watchlists
python agents/orchestrator.py --all

# Output: reports/orchestrator_{mode}_{timestamp}.json
```

---

## Indicator Engine → `agents/indicators.py`

Shared technical indicator library (RSI, MACD, Bollinger Bands, EMA, ATR, Volume Profile, Kill Switches, Gamma Regime).

```bash
# Direct import usage (in Python):
from agents.indicators import IndicatorEngine

engine = IndicatorEngine(df)
indicators = engine.compute()
```

---

## Cost Analyzer → `utils/cost_tracker.py` + `scripts/check_usage.py`

Track token usage and API costs. Check budget status.

```bash
# View usage costs
python scripts/check_usage.py

# Log API call cost (automatic, called after each run)
python -c "from utils.cost_tracker import log_api_call; ..."

# Output: logs/cost_tracker.jsonl (appended daily)
```

---

## Quick Reference: Model Assignment

| Agent | Model | Cost Tier | Use For |
|-------|-------|-----------|---------|
| **vif-analyst** | Sonnet | Mid | Core signal analysis |
| **market-researcher** | Haiku | Low | Read-only exploration |
| **weekend-catalyst-analyst** | Opus | High | Weekly macro synthesis |
| **swing-trade-screener** | Sonnet | Mid | Setup ranking |
| **catalyst-monitor** | Sonnet | Mid | Live catalyst assessment |
| **report-builder** | Haiku | Low | Formatting only |
| **orchestrator-coordinator** | Sonnet | Mid | Pipeline coordination |
| **indicator-engine** | Haiku | Low | Indicator computation |
| **cost-analyzer** | Haiku | Low | Cost tracking |

---

## Scheduled Execution

Master scheduler: `schedule_daily.py`

```
Weekdays 07:00   → catalyst_analysis.py (macro catalysts)
Weekdays 08:45   → orchestrator.py --mode premarket
Weekdays 09:35   → orchestrator.py --mode market_open
Weekdays 16:05   → orchestrator.py --mode afterhours
Fridays  16:30   → orchestrator.py --mode full
Saturdays 08:00  → orchestrator.py --mode weekend
Sundays  18:00   → orchestrator.py --mode weekend
```

Start scheduler:
```bash
python schedule_daily.py
```

---

## Configuration

All framework parameters in `config/vif_config.yml`:
- Gamma regime thresholds (default: ±0.5)
- Kill switch conditions (K1–K6)
- Data batch size (default: 15 tickers)
- Cache TTL (default: 24 hours)
- Model assignments

All pricing and cache config in `config/cache_config.yml`.

---

## Monitoring & Logs

- **Scheduler log:** `logs/scheduler.log`
- **Run history:** `logs/run_history.json`
- **Cost tracking:** `logs/cost_tracker.jsonl` (new)
- **Signal tracking:** `data/signals.db` (new, SQLite)
- **Audit trail:** `logs/claude-audit.jsonl` (via hooks)

---

## Common Workflows

**Daily premarket prep:**
```bash
python agents/orchestrator.py --mode premarket
```

**Weekend briefing (Friday EOD):**
```bash
python agents/orchestrator.py --mode full
```

**Single ticker analysis:**
```bash
python agents/orchestrator.py --ticker TSLA
```

**Check API costs:**
```bash
python scripts/check_usage.py
```

**Research a signal:**
```bash
python agents/claude_research_agent.py --query "Why did NVDA get a BUY?"
```

---

## Troubleshooting

**Agent not found:** Confirm `agents/` and `scripts/` directories exist and are in PYTHONPATH.

**yfinance failures:** Check internet connection. System falls back to mock data with warning (disabled in production).

**Memory errors:** Batch size may be too large. Reduce `data_fetching.batch_size` in `vif_config.yml`.

**Rate limit (429):** API call throttling. Retry with exponential backoff (handled by `utils/api_retry.py`).
