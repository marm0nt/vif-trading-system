# VIF Trading System - Agent Architecture

## Overview
Three-agent system for TradingView watchlist monitoring with VIF framework analysis.

### Agent 1: **Watchlist Parser**
**Role:** Ingest and validate watchlist files
- Parses CSV/TXT watchlist exports from TradingView
- Deduplicates tickers across watchlists
- Normalizes ticker symbols (handles NASDAQ:, NYSE:, etc.)
- Outputs clean ticker list for analysis
- **Cost:** Minimal (local file processing)

### Agent 2: **Data Fetcher** 
**Role:** Fetch market data efficiently
- Pulls OHLCV data from free APIs (Yahoo Finance via yfinance)
- Caches data to minimize API calls
- Computes technical indicators (MA, RSI, Volume)
- Returns structured data for VIF analysis
- **Cost:** Token-light (API data → structured summary)

### Agent 3: **VIF Analyst**
**Role:** Apply VIF framework and generate signals
- Analyzes gamma regime (positive/negative/transition) from price action
- Identifies structural levels (support/resistance from recent price history)
- Confirms volume signals from ATAS-like volume profile
- Flags K1-K6 kill switches (override conditions)
- Generates buy/sell/hold signals with confidence scores
- **Cost:** Higher (complex analysis, but batched)

---

## Workflow
1. **User:** Runs `python agents/watchlist_watcher.py --watchlist vantage_portfolio`
2. **Parser Agent:** Loads and validates watchlist file
3. **Data Fetcher:** Grabs latest OHLCV + volume for all tickers (cached)
4. **VIF Analyst:** Runs VIF framework, returns signals
5. **Output:** Daily report with top opportunities + kill switch alerts

## Token Budget Strategy
- **Batching:** Process 10-15 tickers per Claude call (not individually)
- **Caching:** Store fetched data locally, only update on demand
- **Focus:** Only analyze tickers meeting volatility threshold
- **Efficiency:** Use summaries, not raw data dumps

---

## Files
- `agents/watchlist_parser.py` - Parse & validate
- `agents/data_fetcher.py` - Fetch & cache
- `agents/vif_analyst.py` - VIF signals
- `agents/watchlist_watcher.py` - Main orchestrator
- `config/vif_config.yml` - VIF parameters
