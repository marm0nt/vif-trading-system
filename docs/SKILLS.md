---
name: vif-trading-system
description: >
  Analyzes stock watchlists using the VIF (Volatility Imbalance Framework) v4.0.
  Use when the user asks about stock signals, gamma regime, swing trade setups,
  kill switches, catalyst analysis, or market analysis for tickers in the
  vantage_portfolio, ai_verticals, or energy_ai watchlists.
---

# VIF Trading System Skills

> Anthropic SKILL.md standard applied. Each skill is concise, action-oriented,
> and links to specialized sub-files only when needed (progressive disclosure).

## Contents
- [Skill 1: Parsing Watchlists](#skill-1-parsing-watchlists) → `skills/parsing-watchlists.md`
- [Skill 2: Fetching Market Data](#skill-2-fetching-market-data) → `skills/fetching-market-data.md`
- [Skill 3: Computing Indicators](#skill-3-computing-indicators) → `skills/computing-indicators.md`
- [Skill 4: Analyzing VIF Signals](#skill-4-analyzing-vif-signals) → `skills/analyzing-vif-signals.md`
- [Skill 5: Screening Swing Setups](#skill-5-screening-swing-setups) → `skills/screening-swing-setups.md`
- [Skill 6: Monitoring Catalysts](#skill-6-monitoring-catalysts) → `skills/monitoring-catalysts.md`
- [Skill 7: Briefing Weekend Macro](#skill-7-briefing-weekend-macro) → `skills/briefing-weekend-macro.md`
- [Skill 8: Orchestrating Pipelines](#skill-8-orchestrating-pipelines) → `skills/orchestrating-pipelines.md`

---

## Skill 1: Parsing Watchlists
**Agent:** `agents/watchlist_watcher.py` (parser stage)
**Trigger:** User mentions a watchlist name, asks to load tickers, or starts any analysis run.
**Quick start:**
```bash
python agents/watchlist_watcher.py --watchlist energy_ai
python agents/watchlist_watcher.py --all
```
**Details:** See [skills/parsing-watchlists.md](skills/parsing-watchlists.md)

---

## Skill 2: Fetching Market Data
**Agent:** `agents/watchlist_watcher.py` (fetcher stage) + `agents/indicators.py`
**Trigger:** After watchlist is loaded, or user asks for price/volume data on any ticker.
**Quick start:**
```python
from agents.indicators import fetch_and_compute
data = fetch_and_compute("NVDA", period="6mo")
```
**Details:** See [skills/fetching-market-data.md](skills/fetching-market-data.md)

---

## Skill 3: Computing Indicators
**Agent:** `agents/indicators.py` (shared engine — used by ALL agents)
**Trigger:** Any time technical indicators (RSI, MACD, Bollinger Bands, ATR, EMA, volume) are needed.
**Quick start:**
```bash
python agents/indicators.py   # smoke test on NVDA
```
**Details:** See [skills/computing-indicators.md](skills/computing-indicators.md)

---

## Skill 4: Analyzing VIF Signals
**Agent:** `agents/watchlist_watcher.py` (Claude VIF analyst stage)
**Trigger:** User asks for gamma regime, kill switch status, BUY/SELL/HOLD signal, or confidence score on any ticker.
**Quick start:**
```bash
python agents/watchlist_watcher.py --watchlist vantage_portfolio --period 1mo
```
**Details:** See [skills/analyzing-vif-signals.md](skills/analyzing-vif-signals.md)

---

## Skill 5: Screening Swing Setups
**Agent:** `swing_trade_screener_v2.py`
**Trigger:** User asks for swing trade setups, 2-4 week opportunities, top setups ranked by R:R, or best entry points.
**Quick start:**
```bash
python swing_trade_screener_v2.py
```
**Details:** See [skills/screening-swing-setups.md](skills/screening-swing-setups.md)

---

## Skill 6: Monitoring Catalysts
**Agent:** `catalyst_analysis.py`
**Trigger:** User asks about policy catalysts, government contracts, earnings dates, sector themes, or macro events.
**Quick start:**
```bash
python catalyst_analysis.py
```
**Details:** See [skills/monitoring-catalysts.md](skills/monitoring-catalysts.md)

---

## Skill 7: Briefing Weekend Macro
**Agent:** `agents/weekend_catalyst_agent.py`
**Trigger:** User asks for Monday briefing, weekend catalyst scan, earnings calendar, sector rotation, or macro themes.
**Quick start:**
```bash
python agents/weekend_catalyst_agent.py
```
**Details:** See [skills/briefing-weekend-macro.md](skills/briefing-weekend-macro.md)

---

## Skill 8: Orchestrating Pipelines
**Agent:** `agents/orchestrator.py`
**Trigger:** User asks to run a full analysis session, all watchlists, a premarket/afterhours scan, or a single-ticker deep dive.
**Quick start:**
```bash
python agents/orchestrator.py --mode premarket
python agents/orchestrator.py --ticker NVDA
python agents/orchestrator.py --mode full
```
**Details:** See [skills/orchestrating-pipelines.md](skills/orchestrating-pipelines.md)
