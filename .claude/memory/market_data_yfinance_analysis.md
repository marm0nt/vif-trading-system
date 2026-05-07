---
name: Market Data Source: yfinance Analysis
description: Verified yfinance as production-grade choice; Ran Aroussi authentic with 30+ years experience, 23.3k stars
type: project
originSessionId: bac8b4cd-87f1-42f0-897f-c9b6288f7171
---
**Analysis Complete (May 2, 2026):** Evaluated yfinance vs. all major alternatives (Alpha Vantage, Finnhub, AKShare, pandas-datareader, Polygon.io) for live market data in VIF Trading System.

**Consensus Result: yfinance is the best free choice for your swing trading system.** ✓

## Why yfinance is Optimal

1. **No authentication required** — Zero setup, zero API key friction
2. **Cost: $0/month** — Completely free vs. $5-50/month for alternatives
3. **Adequate for swing trading** — 15-20min lag is acceptable (not day trading)
4. **Author authentic**: Ran Aroussi (ranaroussi on GitHub)
   - 30+ years building production systems
   - 91 repositories maintained
   - 3.7k GitHub followers
   - Portfolio includes: quantstats (7.1k★), ccpm (8.1k★), production AI handbook
5. **Community consensus**: 23.3k GitHub stars, 10M+ monthly users, 20M+ monthly installs
6. **Integration**: Seamless with pandas/numpy (existing stack)

## Current Implementation

Your system fetches from yfinance at three points:
- **OHLCV data** via `yfinance.Ticker.history()` (cached 24h)
- **Earnings dates** via `yfinance.Ticker.calendar` (K4 kill switch)
- **News headlines** via `yfinance.Ticker.get_news()` (catalyst analysis)

## Optional Future Enhancement

Could dual-source earnings dates (yfinance primary + Finnhub supplement) if completeness becomes issue, but not urgent.

## Decision

**Status: Keep yfinance, no changes needed.** Production-grade and cost-optimal.
