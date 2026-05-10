# FinViz Custom Screeners — Command Reference

**Status:** Phase A Complete (May 10, 2026)  
**Screeners Loaded:** 20 custom screeners from `config/finviz_screeners.yml`  
**Integration:** Independent agent (not pipeline), shadow test comparison enabled

---

## Quick Start

### List All Available Screeners

```python
from agents.finviz_screener_agent import list_available_screeners

screeners = list_available_screeners()
for name, info in screeners.items():
    print(f"{name}: {info['name']} ({info['filter_count']} filters)")
```

### Run a Single Custom Screener

```python
from agents.finviz_screener_agent import run_custom_screener

# Run Hunt (1-3) screener
result = run_custom_screener("hunt_1_3")
print(f"Tickers: {result['tickers']}")
print(f"Quality Scores: {result['quality_scores']}")
```

### Run All Daily Screeners

```python
from agents.finviz_screener_agent import run_screener_group

daily_results = run_screener_group("daily_screeners")
for screener_name, screener_result in daily_results['screeners'].items():
    print(f"{screener_name}: {len(screener_result.get('tickers', []))} tickers")
```

### Compare with VIF Signals (Shadow Test)

```python
import json
from pathlib import Path
from agents.finviz_screener_agent import run_custom_screener

# Load last VIF premarket result
vif_file = sorted(Path('reports').glob('swarm_result_premarket_*'), 
                  key=lambda p: p.stat().st_mtime, 
                  reverse=True)[0]
vif_data = json.loads(vif_file.read_text())
vif_signals = {t: v.get('signal', 'HOLD') for t, v in vif_data['signals_by_ticker'].items()}

# Run screener with comparison
result = run_custom_screener("hunt_1_3", compare_with_vif=vif_signals)

# View comparison
if 'comparison' in result:
    comp = result['comparison']
    print(f"Overlap: {comp['overlap_pct']:.1f}%")
    print(f"Overlap Tickers: {comp['overlap_tickers']}")
    print(f"Avg Confidence Delta: {comp['validation_metrics']['overlap_avg_delta']:.1f}")
```

---

## Screener Groups

### Daily Screeners (Run Premarket)

Run every morning before market open:

```python
from agents.finviz_screener_agent import run_screener_group
result = run_screener_group("daily_screeners")
```

**Included:**
- `hunt_1_3` — Sales QoQ growth + institutions
- `backtested_6mo_top1` — Top 6-month performers
- `canslim_1_a_plus` — CANSLIM A+ methodology
- `gap_up_screener` — Gap up opportunities

### Tactical Screeners (Run on Breakout Days)

```python
result = run_screener_group("tactical_screeners")
```

**Included:**
- `shorted_to_breakouts` — Heavily shorted, high volatility
- `new_signal_pre_breakout_a_7_25` — Pre-breakout formation
- `sr_pre_breakout_a_7_25` — Support/resistance breakout
- `vol_momentum_7_30` — High volatility + momentum

### Momentum Screeners (Run 15-min Intervals)

```python
result = run_screener_group("momentum_screeners")
```

**Included:**
- `a_edge_ib_obv_7_25` — A+ edge (new highs + momentum)
- `b_edge_loose_ib_obv_7_25` — Loose version
- `kell_v1_vol_rsi` — Volume + RSI
- `kell_v2_52w_beta_vol` — 52-week momentum

### Earnings Screeners (Run Earnings Week)

```python
result = run_screener_group("earnings_screeners")
```

**Included:**
- `er_gap_ups` — Earnings gap ups with institutional support

---

## All Available Screeners

| Screener | Type | Description | Filters |
|----------|------|-------------|---------|
| **hunt_1_3** | Growth | Sales QoQ 30%+, USA, 3yr IPO, short interest | 10 |
| **shorted_to_breakouts** | Reversal | Small float, oversold, high vol | 8 |
| **backtested_6mo_top1** | Momentum | EPS/Sales growth, SMA alignment | 10 |
| **gap_up_screener** | Breakout | 7%+ gap up, high volume | 5 |
| **gap_down_screener** | Reversal | 7%+ gap down, high volume | 5 |
| **kell_v1_vol_rsi** | Momentum | Volume momentum + RSI | 4 |
| **kell_v2_52w_beta_vol** | Breakout | 52-week high, beta > 1 | 4 |
| **kell_v3_100pct_perf_vol** | Momentum | 100%+ YTD performance | 3 |
| **kell_v4_gap_3pct** | Breakout | 3% gap up | 3 |
| **combo_kell_all** | Combined | All Kell filters combined | 5 |
| **a_edge_ib_obv_7_25** | Momentum | New highs, 1w +10%, RSI OB | 6 |
| **b_edge_loose_ib_obv_7_25** | Momentum | Loose version of A+ | 4 |
| **new_signal_pre_breakout_a_7_25** | Breakout | Small caps, breakout formation | 7 |
| **sr_pre_breakout_a_7_25** | Breakout | S/R breakout confirmation | 8 |
| **vol_momentum_7_30** | Momentum | Volatility + momentum combo | 7 |
| **er_gap_ups** | Earnings | Earnings gap ups + institutions | 10 |
| **canslim_b_plus** | Growth | CANSLIM B+ methodology | 8 |
| **canslim_1_a_plus** | Growth | CANSLIM A+ methodology (all 8 C) | 14 |
| **david_ryan_core** | Growth | David Ryan methodology | 6 |

---

## Command-Line Usage

### Run Screener from CLI

```bash
cd ~/vif-trading-system

# List all screeners
python -c "from agents.finviz_screener_agent import list_available_screeners; import json; print(json.dumps(list_available_screeners(), indent=2))"

# Run single screener
python -c "
from agents.finviz_screener_agent import run_custom_screener
result = run_custom_screener('hunt_1_3')
print(f'Tickers: {result[\"tickers\"]}')
"

# Run screener group
python -c "
from agents.finviz_screener_agent import run_screener_group
results = run_screener_group('daily_screeners')
print(f'Screeners executed: {results[\"screeners_executed\"]}')
"
```

### Run with VIF Comparison

```bash
python -c "
import json
from pathlib import Path
from agents.finviz_screener_agent import run_screener_group

# Load latest VIF signals
vif_file = sorted(Path('reports').glob('swarm_result_premarket_*'), 
                  key=lambda p: p.stat().st_mtime, 
                  reverse=True)[0]
vif_signals = json.loads(vif_file.read_text())['signals_by_ticker']

# Run daily screeners with comparison
results = run_screener_group('daily_screeners', compare_with_vif=vif_signals)

# View aggregate comparison
if 'group_comparison' in results:
    comp = results['group_comparison']
    print(f'Total overlap: {comp[\"overlap_pct\"]:.1f}%')
    print(f'Tickers in overlap: {comp[\"overlap_tickers\"]}')
"
```

---

## Integration with Orchestrator

Add to `schedule_daily.py` for automated execution:

```python
# In schedule_daily.py

def run_finviz_daily_screeners():
    """Run daily FinViz screeners at 07:30 CT (after catalyst scan)"""
    from agents.finviz_screener_agent import run_screener_group
    import json
    from pathlib import Path
    
    try:
        # Run daily screeners
        results = run_screener_group("daily_screeners")
        
        # Load VIF signals from previous premarket run (if available)
        vif_files = sorted(Path("reports").glob("swarm_result_premarket_*"), 
                          key=lambda p: p.stat().st_mtime, 
                          reverse=True)
        
        if vif_files:
            vif_signals = json.loads(vif_files[0].read_text())['signals_by_ticker']
            
            # Run comparison for each screener
            for screener_name, screener_result in results['screeners'].items():
                tickers = screener_result.get('tickers', [])
                # Comparison happens automatically in run_custom_screener
        
        logging.info(f"FinViz daily screeners: {len(results['screeners'])} executed")
        return results
    except Exception as e:
        logging.error(f"FinViz screeners error: {e}")
        return None

# Schedule it
schedule.every().monday.at("07:30").do(run_finviz_daily_screeners)
schedule.every().tuesday.at("07:30").do(run_finviz_daily_screeners)
schedule.every().wednesday.at("07:30").do(run_finviz_daily_screeners)
schedule.every().thursday.at("07:30").do(run_finviz_daily_screeners)
schedule.every().friday.at("07:30").do(run_finviz_daily_screeners)
```

---

## Shadow Test Workflow (Phase B)

### Daily Comparison (Automated)

Results are saved to: `reports/finviz_vif_comparison.json`

```python
from agents.finviz_screener_agent import _screener
import json

# View latest comparison
with open("reports/finviz_vif_comparison.json") as f:
    comparisons = json.load(f)
    
latest = comparisons[-1]
print(f"Overlap: {latest['overlap_pct']:.1f}%")
print(f"Overlap tickers: {latest['overlap_tickers']}")
```

### Success Metrics (Phase B Validation)

Target thresholds (from config):

```yaml
overlap_warning: 0.20      # Alert if < 20% overlap
overlap_success: 0.50      # Good if > 50% overlap
confidence_delta_max: 25   # Max acceptable deviation
```

---

## Output Format

### Screener Result

```json
{
  "screener_name": "hunt_1_3",
  "filters_applied": ["fa_salesqoq_u30", "geo_usa", "..."],
  "tickers": ["NVDA", "MSFT", "TSLA", "AAPL"],
  "metadata": {
    "total_results": 47,
    "top_k": 10,
    "execution_time_ms": 2150,
    "quality_gate_applied": true,
    "data_source": "finviz_live"
  },
  "quality_scores": {
    "NVDA": 0.92,
    "MSFT": 0.89,
    "TSLA": 0.85
  },
  "timestamp": "2026-05-10T08:30:00Z",
  "comparison": {
    "overlap_count": 3,
    "overlap_pct": 75.0,
    "overlap_tickers": ["NVDA", "MSFT", "TSLA"],
    "finviz_only_count": 1,
    "vif_only_count": 0,
    "confidence_delta": {
      "NVDA": -5,
      "MSFT": -2,
      "TSLA": 3
    }
  }
}
```

---

## Installation & Dependencies

### Install FinViz Library (Optional)

For live data instead of mock results:

```bash
pip install finviz
```

If `finviz` is not installed, the agent automatically falls back to mock data (same tickers, testing only).

### Verify Configuration

```python
from agents.finviz_screener_agent import SCREENER_CONFIG

print(f"Screeners loaded: {len(SCREENER_CONFIG['screeners'])}")
print(f"Groups configured: {list(SCREENER_CONFIG['shadow_test_config'].keys())}")
```

---

## Troubleshooting

### No tickers returned from FinViz

**Cause:** FinViz library not installed or filter combination returns 0 results  
**Solution:** Install `pip install finviz` or adjust filter criteria

### Connection timeout to FinViz

**Cause:** Rate limiting or network issue  
**Solution:** System implements 0.5 req/sec with exponential backoff (max 3 retries)

### Configuration not loading

**Cause:** YAML syntax error or missing file  
**Solution:** Verify `config/finviz_screeners.yml` exists and YAML is valid

---

## Phase C Integration (Planned)

When validation metrics are met (overlap > 50%, confidence delta < 25):

1. Add FinViz pre-screening layer to VIF pipeline
2. Filter watchlist tickers through Hunt + CANSLIM before VIF analysis
3. Reduce computation by 30-40% (only analyze A-list tickers)
4. Benchmark cost reduction before Costa Rica deployment

---

## Next Steps

1. **Today (May 10):** Run daily screeners at 07:30 CT (30 min after VIF premarket)
2. **Week 1:** Accumulate 5 days of comparison data
3. **Week 2:** Evaluate metrics and decide on Phase C integration
4. **Week 3:** If validated, integrate as pre-screening filter

Status: **Phase A ✓ Complete → Phase B Running → Phase C Pending Validation**
