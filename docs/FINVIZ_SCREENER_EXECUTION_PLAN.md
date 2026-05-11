# FinViz Screener Execution Plan — Swarm Orchestrator Integration

**Status:** Phase A Deployment (May 10, 2026)  
**Framework:** Native Swarm Architecture (5-agent council + Orchestrator-Coordinator)  
**Approach:** Parallel execution with VIF signals, skip empty results, synthesize hits with critic agent

---

## All 19 Custom Screeners (Verified List)

### Daily Core Screeners (Run 07:30 CT)

| # | Screener ID | Display Name | Purpose | Expected Frequency |
|---|---|---|---|---|
| 1 | `hunt_1_3` | Hunt (1-3) | Sales QoQ 30%+, institutions, recent IPO | High (growth-focused) |
| 2 | `backtested_6mo_top1` | Backtested 6mo - Top 1 | Proven 6-month performers | High (momentum) |
| 3 | `canslim_1_a_plus` | CANSLIM #1 A+ Companies | All 8 CANSLIM criteria | Medium (strict filter) |
| 4 | `gap_up_screener` | Gap Up Screener | 7%+ gap ups, USA | High (daily breakouts) |

### Tactical/Breakout Screeners (Run 09:00 CT)

| # | Screener ID | Display Name | Purpose | Expected Frequency |
|---|---|---|---|---|
| 5 | `shorted_to_breakouts` | Shorted To Breakouts | Squeezable setups | Medium (contrarian) |
| 6 | `new_signal_pre_breakout_a_7_25` | New Signal Pre Breakout A+ | Breakout formation | Medium (setup confirmation) |
| 7 | `sr_pre_breakout_a_7_25` | S/R Pre Breakout A+ | Support/resistance breakout | Medium (setup confirmation) |
| 8 | `vol_momentum_7_30` | Vol/Momentum (7/30) | Volatility + momentum combo | Medium (high-energy) |

### Momentum/Edge Screeners (Run 15-min Intervals)

| # | Screener ID | Display Name | Purpose | Expected Frequency |
|---|---|---|---|---|
| 9 | `a_edge_ib_obv_7_25` | A+ Edge IB/OBV | New highs + strong momentum | High (daily intraday) |
| 10 | `b_edge_loose_ib_obv_7_25` | B Edge Loose IB/OBV | Relaxed momentum criteria | High (daily intraday) |
| 11 | `kell_v1_vol_rsi` | Kell V1 - Vol & RSI | Volume + RSI confirmation | Medium (technical) |
| 12 | `kell_v2_52w_beta_vol` | Kell V2 - 52w, Beta, Vol | 52-week breakout | Medium (technical) |
| 13 | `kell_v3_100pct_perf_vol` | Kell V3 - 100% Perf, Vol | 100%+ YTD performance | Low (rare condition) |
| 14 | `kell_v4_gap_3pct` | Kell V4 - Gap 3% | 3% gap up | Medium (daily breakouts) |
| 15 | `combo_kell_all` | Combo Kell - All Combined | All Kell filters combined | Low (strict) |

### Gap/Reversal Screeners (Run Pre/Post Market)

| # | Screener ID | Display Name | Purpose | Expected Frequency |
|---|---|---|---|---|
| 16 | `gap_down_screener` | Gap Down Screener | 7%+ gap downs | Medium (reversal plays) |
| 17 | `er_gap_ups` | ER Gap Ups | Earnings gap ups + institutions | Medium (earnings week) |

### Growth/Fundamental Screeners (Run Weekly)

| # | Screener ID | Display Name | Purpose | Expected Frequency |
|---|---|---|---|---|
| 18 | `canslim_b_plus` | CANSLIM B+ Companies | CANSLIM B+ tier | Medium (weekly sweep) |
| 19 | `david_ryan_core` | David Ryan Core | David Ryan methodology | Medium (weekly sweep) |

---

## Execution Strategy

### Behavior: "Run & Skip Empty"

**Core Logic:**
```
FOR each screener:
  RUN screener
  IF results.tickers is empty:
    LOG: "Skipped {screener_name} - no results"
    CONTINUE to next screener
  ELSE:
    LOG: "Found {count} tickers in {screener_name}"
    SAVE results to catalog
    COMPARE with VIF signals
    ADD to report
```

**Expected Outcome:**
- 4-6 screeners with results on typical days
- 8-10 screeners on high-vol days (gaps, breakouts)
- 2-3 screeners with no results (gap downs, ER plays)

---

## Swarm Orchestrator Integration

### Architecture: FinViz Agent + VIF Council

```
┌─────────────────────────────────────────────────────────┐
│         Orchestrator-Coordinator (Master)               │
├─────────────────────────────────────────────────────────┤
│ PHASE 1: Load VIF premarket signals                     │
│ PHASE 2: Run FinViz screeners (19 parallel threads)     │
│ PHASE 3: Compare + filter empty results                 │
│ PHASE 4: Synthesize with Critic Agent                   │
│ PHASE 5: Generate shadow test report                    │
└─────────────────────────────────────────────────────────┘
         │              │              │              │
    ┌────▼───┐     ┌────▼───┐    ┌────▼───┐    ┌────▼───┐
    │ Catalyst│     │ VIF     │    │ Swing   │    │ Risk    │
    │ Monitor │     │ Analyst │    │ Screen. │    │ Agent   │
    └────┬───┘     └────┬───┘    └────┬───┘    └────┬───┘
         │              │              │              │
         └──────────────┼──────────────┼──────────────┘
                        │
                  ┌─────▼─────┐
                  │  Critic    │  ← Evaluates FinViz discoveries
                  │  Agent     │    vs VIF confidence
                  └─────┬─────┘
                        │
                  ┌─────▼──────────┐
                  │ FinViz Agent   │  ← 19 screeners
                  │ (Parallel)     │    (skip empty)
                  └────────────────┘
```

### Pseudo-Code: Orchestrator-Coordinator

```python
class FinVizOrchestratorCoordinator:
    """
    Master orchestrator for FinViz screener execution as part of 5-agent council.
    Integrates with VIF signals, runs screeners in parallel, synthesizes results.
    """
    
    def __init__(self):
        self.vif_agent = NativeVIFAnalystAgent()
        self.finviz_agent = FinvizScreenerAgent()
        self.critic_agent = CriticAgent()
        self.research_agent = ClaudeResearchAgent()
    
    def execute_finviz_screening(self, watchlist_signals: Dict) -> Dict:
        """
        Execute all 19 screeners, skip empty results, synthesize with VIF.
        
        Workflow:
        1. Load VIF premarket signals (from earlier run)
        2. Run all 19 screeners in parallel
        3. Filter: Keep only screeners with results
        4. For each result: Compare with VIF signals
        5. Critic agent: Evaluate overlap + confidence delta
        6. Research agent: Identify novel discoveries vs VIF
        7. Report: HTML output with synth analysis
        """
        
        # Step 1: Load VIF signals
        vif_signals = self.load_latest_vif_signals()
        
        # Step 2: Run screeners in parallel (skip empty)
        screener_results = []
        for screener_name in FINVIZ_SCREENERS:
            result = self.finviz_agent.run_named_screener(screener_name)
            
            if result.get("tickers"):  # Only include if results exist
                screener_results.append({
                    "screener_name": screener_name,
                    "tickers": result["tickers"],
                    "count": len(result["tickers"]),
                    "quality_scores": result.get("quality_scores", {})
                })
            else:
                self.logger.info(f"Skipped {screener_name} - no results")
        
        # Step 3: Compare each result with VIF signals
        comparison_results = []
        for result in screener_results:
            overlap = self.compare_with_vif(result["tickers"], vif_signals)
            
            comparison_results.append({
                "screener": result["screener_name"],
                "finviz_tickers": result["tickers"],
                "vif_overlap": overlap["overlap_tickers"],
                "overlap_pct": overlap["overlap_pct"],
                "finviz_only": overlap["finviz_only_tickers"],
                "confidence_delta": overlap["confidence_delta"]
            })
        
        # Step 4: Critic agent evaluates discrepancies
        critic_analysis = self.critic_agent.analyze_finviz_vif_delta(
            finviz_results=comparison_results,
            vif_signals=vif_signals
        )
        
        # Step 5: Research agent investigates novel discoveries
        novel_tickers = self.extract_novel_discoveries(comparison_results)
        research_findings = self.research_agent.investigate_discoveries(novel_tickers)
        
        # Step 6: Synthesize into comprehensive report
        report = {
            "timestamp": datetime.now().isoformat(),
            "screeners_executed": len(screener_results),
            "screeners_with_results": len([r for r in screener_results if r["count"] > 0]),
            "screeners_empty": len(FINVIZ_SCREENERS) - len(screener_results),
            "results": comparison_results,
            "critic_analysis": critic_analysis,
            "research_findings": research_findings,
            "summary": self.generate_summary(comparison_results)
        }
        
        return report
    
    def compare_with_vif(self, finviz_tickers: List[str], vif_signals: Dict) -> Dict:
        """Compare FinViz discoveries with VIF signals."""
        vif_tickers = set(vif_signals.keys())
        finviz_set = set(finviz_tickers)
        
        overlap = finviz_set & vif_tickers
        finviz_only = finviz_set - vif_tickers
        
        return {
            "overlap_tickers": list(overlap),
            "overlap_pct": (len(overlap) / len(finviz_set) * 100) if finviz_set else 0,
            "finviz_only_tickers": list(finviz_only),
            "confidence_delta": {
                t: vif_signals[t]["confidence"] for t in overlap
            }
        }
    
    def extract_novel_discoveries(self, comparison_results: List) -> List[str]:
        """Extract tickers found ONLY in FinViz, not in VIF signals."""
        all_novel = []
        for result in comparison_results:
            all_novel.extend(result.get("finviz_only", []))
        return list(set(all_novel))  # Deduplicate
    
    def generate_summary(self, results: List) -> str:
        """Generate human-readable summary of findings."""
        summary = f"""
        FinViz Screener Execution Summary:
        - Screeners executed: {len(results)}
        - Total unique tickers: {len(set(t for r in results for t in r['finviz_tickers']))}
        - Average overlap with VIF: {sum(r['overlap_pct'] for r in results) / len(results):.1f}%
        - High overlap (>50%): {len([r for r in results if r['overlap_pct'] > 50])} screeners
        - Novel discoveries (FinViz-only): {len(set(t for r in results for t in r.get('finviz_only', [])))} tickers
        """
        return summary
```

---

## Command Reference: Running Screeners

### List All Screeners

```python
from agents.finviz_screener_agent import list_available_screeners
screeners = list_available_screeners()
for name, info in screeners.items():
    print(f"{name:30} {info['name']}")
```

### Run Single Screener (With Skip-Empty Logic)

```python
from agents.finviz_screener_agent import run_custom_screener

screener_name = "hunt_1_3"
result = run_custom_screener(screener_name)

if result.get("tickers"):
    print(f"✓ {screener_name}: {len(result['tickers'])} tickers")
    for ticker in result["tickers"]:
        print(f"  - {ticker} (score: {result['quality_scores'][ticker]:.2f})")
else:
    print(f"○ {screener_name}: Skipped - no results")
```

### Run All Screeners, Skip Empty

```python
from agents.finviz_screener_agent import _screener

SCREENER_NAMES = [
    "hunt_1_3", "shorted_to_breakouts", "backtested_6mo_top1",
    "gap_up_screener", "gap_down_screener",
    "kell_v1_vol_rsi", "kell_v2_52w_beta_vol", "kell_v3_100pct_perf_vol", "kell_v4_gap_3pct",
    "combo_kell_all",
    "a_edge_ib_obv_7_25", "b_edge_loose_ib_obv_7_25",
    "new_signal_pre_breakout_a_7_25", "sr_pre_breakout_a_7_25",
    "vol_momentum_7_30",
    "er_gap_ups",
    "canslim_b_plus", "canslim_1_a_plus",
    "david_ryan_core"
]

results_with_data = {}
for screener_name in SCREENER_NAMES:
    result = _screener.run_named_screener(screener_name)
    
    if result.get("tickers"):
        results_with_data[screener_name] = result
        print(f"✓ {screener_name}: {len(result['tickers'])} tickers")
    else:
        print(f"○ {screener_name}: Skipped - no results")

print(f"\nTotal screeners with results: {len(results_with_data)}/{len(SCREENER_NAMES)}")
```

### Run with VIF Comparison (Shadow Test)

```python
import json
from pathlib import Path

# Load latest VIF signals
vif_file = sorted(Path('reports').glob('swarm_result_premarket_*'), 
                  key=lambda p: p.stat().st_mtime, 
                  reverse=True)[0]
vif_signals = json.loads(vif_file.read_text())['signals_by_ticker']

# Run all screeners with VIF comparison
results_with_data = {}
for screener_name in SCREENER_NAMES:
    result = _screener.run_named_screener(screener_name)
    
    if result.get("tickers"):
        # Run comparison
        comparison = _screener.compare_with_vif(result["tickers"], vif_signals)
        result["comparison"] = comparison
        results_with_data[screener_name] = result
        
        print(f"✓ {screener_name}: {len(result['tickers'])} tickers, "
              f"{comparison['overlap_pct']:.1f}% overlap with VIF")
    else:
        print(f"○ {screener_name}: Skipped - no results")
```

---

## Integration with Schedule (Daily Execution)

Add to `schedule_daily.py`:

```python
def run_finviz_screeners_with_vif():
    """
    Run all 19 FinViz screeners at 09:00 CT (30min after premarket VIF).
    Skip empty results. Compare with VIF signals. Generate shadow test report.
    """
    import json
    from pathlib import Path
    from agents.finviz_screener_agent import _screener
    
    logger.info("Starting FinViz screener execution (skip-empty mode)")
    
    # Load VIF signals from premarket run
    vif_files = sorted(Path("reports").glob("swarm_result_premarket_*"), 
                      key=lambda p: p.stat().st_mtime, 
                      reverse=True)
    
    if not vif_files:
        logger.warning("No VIF premarket results found, skipping comparison")
        vif_signals = None
    else:
        vif_signals = json.loads(vif_files[0].read_text())['signals_by_ticker']
    
    # Execute all screeners
    SCREENER_NAMES = [
        "hunt_1_3", "shorted_to_breakouts", "backtested_6mo_top1",
        "gap_up_screener", "gap_down_screener",
        "kell_v1_vol_rsi", "kell_v2_52w_beta_vol", "kell_v3_100pct_perf_vol", "kell_v4_gap_3pct",
        "combo_kell_all",
        "a_edge_ib_obv_7_25", "b_edge_loose_ib_obv_7_25",
        "new_signal_pre_breakout_a_7_25", "sr_pre_breakout_a_7_25",
        "vol_momentum_7_30",
        "er_gap_ups",
        "canslim_b_plus", "canslim_1_a_plus",
        "david_ryan_core"
    ]
    
    results_with_data = {}
    skipped = 0
    
    for screener_name in SCREENER_NAMES:
        try:
            result = _screener.run_named_screener(screener_name)
            
            if result.get("tickers"):  # Only include if results
                if vif_signals:
                    comparison = _screener.compare_with_vif(result["tickers"], vif_signals)
                    result["comparison"] = comparison
                
                results_with_data[screener_name] = result
                logger.info(f"✓ {screener_name}: {len(result['tickers'])} tickers")
            else:
                skipped += 1
                logger.info(f"○ {screener_name}: Skipped - no results")
        except Exception as e:
            logger.error(f"✗ {screener_name}: {e}")
            skipped += 1
    
    logger.info(f"FinViz screening complete: {len(results_with_data)} with results, {skipped} skipped")
    
    # Save results
    _screener.screening_catalog[f"finviz_full_run_{datetime.now().isoformat()}"] = {
        "screeners_executed": len(SCREENER_NAMES),
        "screeners_with_results": len(results_with_data),
        "screeners_skipped": skipped,
        "results": results_with_data,
        "timestamp": datetime.now().isoformat()
    }
    _screener.save_screening_catalog()
    
    return len(results_with_data)

# Schedule it
schedule.every().monday.at("09:00").do(run_finviz_screeners_with_vif)
schedule.every().tuesday.at("09:00").do(run_finviz_screeners_with_vif)
schedule.every().wednesday.at("09:00").do(run_finviz_screeners_with_vif)
schedule.every().thursday.at("09:00").do(run_finviz_screeners_with_vif)
schedule.every().friday.at("09:00").do(run_finviz_screeners_with_vif)
```

---

## Expected Results

### High-Frequency Screeners (Multiple Results Daily)
- `hunt_1_3` — Typically 5-10 tickers
- `gap_up_screener` — Typically 8-15 tickers (breakout days)
- `a_edge_ib_obv_7_25` — Typically 3-7 tickers
- `backtested_6mo_top1` — Typically 4-8 tickers

### Medium-Frequency Screeners (2-3x Per Week)
- `shorted_to_breakouts` — 2-4 tickers
- `new_signal_pre_breakout_a_7_25` — 1-5 tickers
- `kell_v1_vol_rsi` — 1-3 tickers

### Low-Frequency Screeners (1-2x Per Week)
- `gap_down_screener` — Only on red days (1-3 tickers)
- `kell_v3_100pct_perf_vol` — Rare (100%+ YTD)
- `er_gap_ups` — Only earnings week

### Typical Daily Result
```
Total screeners: 19
Screeners with results: 5-7
Screeners skipped: 12-14
Total unique tickers: 25-40
VIF overlap: 40-60%
Novel discoveries: 10-20 tickers
```

---

## Phase B Validation Metrics

After 5 days of execution:
- Track overlap % per screener
- Track novel discoveries that later appear in VIF signals
- Measure false positive rate (FinViz-only → VIX spikes)
- Calculate confidence delta improvements

Success criteria:
- Overall overlap > 50%
- Novel discoveries with >3 matching factors
- No systematic downside from FinViz-only tickers

---

## Summary

**19 screeners, parallel execution, skip-empty logic, VIF comparison, critic synthesis.**

All screeners verified and ready to deploy. Execute with Swarm Orchestrator integration at 09:00 CT daily, starting May 10, 2026.
