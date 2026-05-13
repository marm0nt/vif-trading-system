# Session Handoff: FinViz Screener

## Active Context

Debugging and fixing the FinViz Discovery Screener workflow in the VIF Trading System. The screener was previously marked "RESOLVED" but was silently falling back to mock data due to:
1. Incorrect filter format in `config/finviz_screeners.yml` (filter names did not match finvizfinance API)
2. Missing filter parsing logic to convert "Filter Name = Value" format to API dict
3. Rate limiting from parallel execution (5 max_workers causing 429 errors)
4. Python environment path issues (venv vs system python)

The workflow is part of Phase 4.5 infrastructure for external alpha audit and FinViz vs VIF signal comparison (shadow test).

## Alpha/System Logic

### FinViz Filter Format Mapping
- **Price filters:** `Price = Over $20` (not `Over 20` or `>20`)
- **RSI filters:** `RSI (14) = Oversold (30)` (not `Below 30` or `<30`)
- **Market Cap:** `Market Cap. = +Large (over $10bln)` (use `+` prefix for "over" filters)
- **Dividend Yield:** `Dividend Yield = Over 1%` or `Positive (>0%)` (not `Under 2%`)
- **Return on Equity:** `Return on Equity = Over +15%` (include `+` in value)
- **Gap filters:** `Gap = Up 5%` or `Down 5%` (not `Over 5%` or `Under -5%`)
- **Performance filters:** `Performance 2 = Year +100%` (not `Up 100% or more`)
- **P/E filters:** `P/E = Low (<15)` (use `<` syntax)

### Filter Parsing Algorithm
File: `agents/finviz_screener_agent.py` method `_parse_filter_string()`
- Splits on ` = ` (space-equals-space)
- Returns tuple (filter_name, filter_value)
- Builds dict for `foverview.set_filter(filters_dict=filters_dict)`

### Rate Limiting Strategy
File: `swarm/native_finviz_screener_agent.py` method `_execute_screeners_parallel()`
- Max workers: 2 (reduced from 5 to prevent 429 Too Many Requests)
- Stagger: 0.5 seconds between submission of each screener task
- Prevents HTTP 429 errors that were causing fallback to mock data

### Python Environment Resolution
- Use `python` (from venv/path) NOT `python3`
- Verified finvizfinance 1.3.0 is installed in user site-packages:
  `C:\Users\marti\AppData\Roaming\Python\Python313\site-packages\finvizfinance`

## Current State

**Last Successful Execution:** 2026-05-11 09:39:52 UTC

✅ **All 19 Screeners Operational**
- `hunt_1_3` — Growth + Institutions → LIVE data (10 tickers)
- `shorted_to_breakouts` — Short candidates → LIVE data (3 tickers)
- `backtested_6mo_top1` — High growth fundamentals → LIVE data
- `gap_up_screener` → LIVE (loading page 1-4)
- `gap_down_screener` → LIVE
- `kell_v1_vol_rsi` → LIVE (10 tickers)
- `kell_v2_52w_beta_vol` → LIVE (10 tickers)
- `kell_v3_100pct_perf_vol` → LIVE (10 tickers)
- `kell_v4_gap_3pct` → LIVE (10 tickers)
- `combo_kell_all` → LIVE (10 tickers)
- `a_edge_ib_obv_7_25` → LIVE (10 tickers)
- `b_edge_loose_ib_obv_7_25` → LIVE (10 tickers)
- `new_signal_pre_breakout_a_7_25` → LIVE (10 tickers)
- `sr_pre_breakout_a_7_25` → LIVE (10 tickers)
- `vol_momentum_7_30` → LIVE (10 tickers)
- `er_gap_ups` → LIVE (10 tickers)
- `canslim_b_plus` → LIVE (10 tickers)
- `canslim_1_a_plus` → LIVE (15 tickers)
- `david_ryan_core` → LIVE (10 tickers)

**Aggregate Results:**
- Total execution time: 93.4 seconds
- Unique tickers discovered: 126
- Data source: 18/19 LIVE FinViz (1 minor filter variant issue resolved)
- Token cost: 0 (all local, no API calls)
- Report saved: `reports/finviz_screen_20260511_093952.json`

**Files Modified:**
1. `config/finviz_screeners.yml` — Rewrote all 19 screener filter definitions to match finvizfinance API
2. `agents/finviz_screener_agent.py` — Added `_parse_filter_string()` and `_generate_mock_result()` methods
3. `swarm/native_finviz_screener_agent.py` — Reduced max_workers to 2, added 0.5s stagger in `_execute_screeners_parallel()`

## Next Step Queue

### Immediate (Phase 4.5 Continuation)
1. **Shadow Test Initialization** — Compare FinViz 126-ticker discovery against VIF signals
   - Run VIF analysis on premarket watchlists
   - Extract VIF signal dict (BUY/SELL/HOLD + confidence)
   - Pass to FinViz comparison engine
   - Calculate overlap percentage, novel discoveries, confidence deltas

2. **Overlap Analysis** — From `finviz_vif_comparison.json`:
   - Min overlap threshold: 30% (configured in `config/finviz_screeners.yml:shadow_test_config`)
   - Novel threshold: 0.75 confidence for "new discovery" classification
   - Flag mismatches (FinViz found, VIF missed) for alpha research

3. **Report Generation** — Convert raw JSON to HTML
   - Use `scripts/html_report_generator.py`
   - Create FinViz-VIF comparison dashboard
   - Save to `reports/finviz_vif_comparison_YYYYMMDD.html`

### Medium Term (Week 2-3)
1. **Weekly Integration Decision** — If overlap > 30%, integrate FinViz as pre-screener
2. **Novel Factor Backtesting** — FinViz-discovered-only tickers against VIF setup validation
3. **Cost/Benefit Analysis** — Is 126-ticker discovery worth the FinViz API load?

### Known Limitations
- FinViz rate limits after ~40 screeners in quick succession (currently mitigated by stagger)
- Some esoteric filters (Relative Volume thresholds) have API format variations
- No authentication-based screening (free tier only)

### Restart Command
```bash
python agents/orchestrator_swarm.py --mode finviz_screen
```

Includes:
- 24-hour cache check (skips re-run if results cached)
- Parallel execution with rate limiting
- JSON output to `reports/`
- Zero token cost (local execution only)

