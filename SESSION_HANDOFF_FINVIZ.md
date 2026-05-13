# FinViz Screener Integration — Session Handoff

**Date:** 2026-05-11  
**Status:** Phase A Complete (Shadow Testing Ready)  
**Phase:** FinViz Discovery Screener fully integrated into VIF swarm (6th agent)

---

## 1. Filter Format Corrections

FinViz screener filters were standardized to the following format:

**Corrected Filter Syntax:**
- **Price Ranges:** `Price > 20`, `Price < 500` (numeric comparisons, no currency symbols)
- **Momentum Filters:** `RSI < 30` (oversold), `RSI > 70` (overbought)
- **Volume Filters:** `Volume > 1M` (1 million shares), `Avg Volume > 500K`
- **Technical Filters:** `EMA(20) > EMA(50)` (uptrend), `EMA(50) > EMA(200)` (major trend)
- **Market Cap Filters:** `Market Cap > 1B` (billion), `Market Cap < 500M` (million)
- **Sector/Industry:** Direct string matching, no operators needed

**Root Issue Fixed:**
- Native finviz library does not support complex boolean operators or nested grouping
- Filters are applied sequentially (AND logic by default)
- Each screener preset in finviz uses pre-configured filter logic; custom filters must adhere to library syntax

**Files Updated:**
- `swarm/native_finviz_screener_agent.py` — filter validation + escape handling
- `config/finviz_screeners.yml` — 19 screener definitions with corrected syntax

---

## 2. Rate-Limiting Configuration

**ThreadPoolExecutor Configuration:**
- **Workers:** 2 concurrent threads (prevents FinViz IP throttling)
- **Stagger Interval:** 0.5 seconds between batch submissions
- **Timeout:** 30 seconds per screener execution
- **Retry Logic:** Up to 2 retries on timeout, exponential backoff (0.5s → 1.0s)

**Implementation:**
```python
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=2)
for screener in screener_list:
    executor.submit(run_screener, screener)
    time.sleep(0.5)  # 500ms stagger between submissions
```

**Cache Strategy:**
- 24-hour TTL for screener results (keyed by screener_name + date)
- Cache stored at `data/finviz_cache.json`
- Avoids redundant API calls during day; allows shadow testing without hammering FinViz

**Files Updated:**
- `swarm/native_finviz_screener_agent.py` — ThreadPoolExecutor pool management
- `swarm/smolagents_bridge.py` — rate limit enforcement in production bridge

---

## 3. Discovery Results: 126 Unique Tickers

**19 Institutional Screeners Executed:**
1. Hunt Scanner (v1, v2, v3) — 3 screeners
2. CANSLIM Scan — 1 screener
3. Kell Channel (v1-v4) — 4 screeners  
4. David Ryan Scan — 1 screener
5. A+ / B Edge Scan — 2 screeners
6. Gap Up / Gap Down — 2 screeners
7. ER Gap Ups (Pre/Post Earnings) — 2 screeners
8. Breakout + Volume Surge — 1 screener
9. EPS Beat + Price Action — 1 screener
10. Insider Buying (Active) — 1 screener

**Aggregate Results:**
- **Total Unique Tickers:** 126
- **Overlap with VIF Watchlists:** ~35% (45 tickers also in VIF signals)
- **Novel Discoveries:** ~65% (81 tickers NOT in VIF watchlists)
- **Screener with Most Hits:** Hunt Scanner v2 (28 tickers)
- **Screener with Least Hits:** ER Gap Ups Post (3 tickers)

**Distribution by Market Cap:**
- Mega-Cap (>$300B): 12 tickers
- Large-Cap ($50B–$300B): 38 tickers
- Mid-Cap ($10B–$50B): 44 tickers
- Small-Cap ($2B–$10B): 28 tickers
- Micro-Cap (<$2B): 4 tickers

**Next Steps (Phase B — Shadow Testing):**
1. Compare 5-day forward returns: FinViz discoveries vs. VIF signals
2. Target >50% overlap rate for alignment validation
3. Integrate novel discoveries as pre-filtering layer (reduce VIF input from 300 → 50–80 tickers)
4. Estimate cost savings from selective VIF analysis

---

## Integration in VIF Swarm

**Agent Execution Order (Phase 3 Complete):**
```
Catalyst Monitor (K4 flags)
  ↓
VIF Analyst (1mo data, 300 tickers, +Greeks/IV%)
  ↓
Critic Agent (veto/downgrade logic, IV-aware)
  ↓
VectorBT Backtester (6mo Sharpe validation)
  ↓
Signal Verifier (4-gate: Vol/Fund/Sent/Macro)
  ↓
Swing Screener ──────┐
FinViz Screener (6th) │ → Consensus voting
AutoResearch ────────┘
  ↓
Risk Agent (circuit breaker)
  ↓
HTML Report (with Greeks tab)
```

**FinViz as 6th Agent:**
- Runs in-process (0 API tokens from Claude)
- 24h cached results (skip 19 screeners if today's cache exists)
- Feeds into consensus voting alongside VIF signals
- Zero latency impact on main pipeline

---

## Artifacts

- **Cache File:** `data/finviz_cache.json` (created on first run)
- **Screener Config:** `config/finviz_screeners.yml`
- **Agent Code:** `swarm/native_finviz_screener_agent.py`
- **Test Output:** `reports/finviz_screen_*.json` (one per run)
- **Integration Status:** 100% wired into orchestrator_swarm.py

---

## Known Limitations & Workarounds

1. **No Custom Boolean Operators:** FinViz library doesn't support OR/AND grouping. Workaround: Run separate screeners and merge results.
2. **Rate Limiting:** FinViz throttles at ~5 concurrent requests. Workaround: ThreadPoolExecutor(max_workers=2) + 0.5s stagger.
3. **Data Freshness:** EOD data only. Workaround: Cache with 24h TTL, refresh daily at 16:00 CT post-close.
4. **No Historical Backtest:** FinViz results are point-in-time. Workaround: VectorBT handles historical validation.

---

## Session Summary

✅ All 6 FinViz integration bugs resolved (2026-05-10)  
✅ 19 screeners operational, 126 unique ticker discovery confirmed  
✅ Rate limiting safe and cache strategy implemented  
✅ 6th agent wired into swarm orchestrator (Phase 3)  
⏳ Phase B shadow testing ready to launch

**Ready for:** 5-day forward return validation, pre-filtering layer evaluation
