# Signal-Validator Pipeline — Session Handoff

**Date:** 2026-05-11  
**Status:** Phase 2 Complete (Integration Validated)  
**Phase:** Multi-Agent Signal Review & Validation Framework fully wired

---

## Active Context

Implemented a **Planner-Critic-Executor signal validation pipeline** within the VIF swarm orchestrator. The system enforces multi-stage signal review before any trade signal reaches production reporting.

### Architecture

**9-Agent Sequential Execution Order:**
```
1. Catalyst Monitor (K4 earnings flags)
2. VIF Analyst (1-month data, 300 tickers, gamma regime detection)
3. Critic Agent (veto/downgrade logic, IV-aware)
4. VectorBT Backtester (6-month Sharpe validation)
5. Signal Verifier (4-gate: Vol/Fund/Sent/Macro)
6. Swing Screener ──┐
7. FinViz Screener │ → Consensus voting
8. AutoResearch ──┘
9. Report Builder (HTML + Greeks table)
```

**Signal Flow Pattern:**
- VIF Analyst generates candidates → task_context["vif_signals"]
- Critic reviews candidates → task_context["critic_signals"]
- Signal Verifier gates candidates → task_context["verified_signals"]
- Report Builder publishes vetted signals

### Code Location References

**Core Files Modified:**
- `swarm/orchestrator.py` — Sequential execution with inter-agent context injection
- `swarm/critic_agent.py` — Veto logic + IV-aware SELL signal handling
- `swarm/native_signal_verifier_agent.py` — 4-gate verdict engine (new file)
- `agents/indicators.py` — compute_options_greeks() function (Black-Scholes)
- `swarm/native_vif_analyst_agent.py` — Greeks enrichment (_enrich_with_greeks method)
- `agents/orchestrator_swarm.py` — HTML report generation + agent pool wiring
- `scripts/active/reporting/html_report_generator.py` — build_greeks_table() helper

---

## Alpha/System Logic

### 1. Critic Veto Engine

**Veto Conditions (Hard Override):**
- K4 earnings within 2 days → VETO all signals
- RSI > 85 on BUY → VETO (extreme overbought)
- Volume < 50K shares on BUY → VETO (liquidity insufficient)
- Existing kill switch (K1-K6) → VETO

**IV-Aware SELL Logic (Critical Patch):**
```python
if signal == "SELL" and rsi < 20:
    if iv_pct > 60:
        # Full VETO: downside already priced, IV crush risk on bounce
        return {"veto": True, "reason": "SELL vetoed: RSI <20 + IV >60% (downside priced, IV crush risk)"}
    else:
        # Downgrade only: potential bounce, but extreme oversold
        return {"veto": False, "downgrade": True, "reason": "RSI <20 oversold — downgrade to 60%"}
```

**Downgrade Logic (Soft Rejection):**
- RSI 75-85 on BUY → confidence × 0.75 (25% reduction)
- Volume strong on SELL (potential capitulation) → downgrade
- Munger Inversion Audit: 2+ strong invalidations → confidence × 0.75

### 2. Signal Verifier 4-Gate Logic

**Gate 1 — Volume:**
- PASS: Current vol ≥ 80% of 20-day MA
- FLAG: Vol < 80% but catalyst explains gap move (>3% change)
- FAIL: Low volume without catalyst

**Gate 2 — Fundamental:**
- BUY: Price vs MA20 alignment (pass if price > MA20 - 2%)
- SELL: Price below MA20 (pass if price < MA20 + 5%)
- HOLD: Always pass

**Gate 3 — Sentiment (RSI Proxy):**
- BUY: Pass if RSI 40-65; Flag if < 30 (bounce risk); Fail if > 75
- SELL: Pass if RSI > 55; Flag if < 20 (reversal risk)

**Gate 4 — Macro (5-day change + IV%):**
- BUY with 5-day decline > 5% → FAIL (catching falling knife)
- BUY with 8%+ gain → FLAG (chasing momentum)
- BUY with IV > 80% → FLAG (options market pricing risk)
- SELL after 5%+ rally → FLAG (late signal)
- SELL with IV < 15% → FLAG (market complacent, low conviction)

**Verdict Rules:**
- 4 PASS → PUBLISH (HIGH conviction)
- 3 PASS + 1 FLAG → PUBLISH (MEDIUM conviction)
- 3 PASS + 1 FAIL → DOWNGRADE (−30% confidence)
- ≤ 2 PASS → REJECT (removed from report)

**Auto-Reject (Skip gates):**
- Volume < 50,000 shares
- Price < $1.00 (penny stock floor)
- K3/K4 kill switch active
- No price data available

### 3. Greeks & Implied Volatility Integration

**Black-Scholes Computation (agents/indicators.py):**
```python
def compute_options_greeks(ticker, price, signal_type):
    """
    Parameters:
    - Fetches nearest 7-45 day ATM (at-the-money) options from yfinance
    - Uses scipy.stats.norm for CDF calculations
    - Risk-free rate: 4.5% (hardcoded)
    - Time to expiry: days_to_expiry / 365.0
    
    Returns:
    {
        "iv_pct": implied_volatility_percent,
        "delta": call_delta or put_delta (depending on signal),
        "gamma": gamma_value,
        "theta": theta_decay_per_day,
        "vega": vega_per_1pct_iv_change,
        "rho": rho_per_1pct_rate_change,
        "strike": ATM_strike_price,
        "expiry": days_to_expiry,
        "option_type": "call" or "put"
    }
    """
    # 24-hour cache at data/options_greeks_cache.json
    # Graceful fallback: returns {} if no liquid options chain exists
```

**IV% Color Coding in HTML Reports:**
- Green: IV < 30% (low volatility, good entry)
- Yellow: IV 30-60% (elevated, normal volatility)
- Red: IV > 60% (high volatility, elevated risk)

**Gate 4 Integration:**
- BUY signals with IV > 80% → FLAG (options market expecting move)
- SELL signals with IV < 15% → FLAG (complacency, low premium for protection)

### 4. Munger Inversion Audit

**Purpose:** Force 3 reasons the signal could be wrong before finalizing.

**Logic:**
- Only runs on signals with confidence ≥ 70%
- Calls Haiku (256 tokens max) with invalidation prompt
- Severity classification: "strong" vs "weak"
- Auto-downgrade if 2+ strong invalidations found

**Prompt Template:**
```
Analyze this [BUY|SELL] signal and identify exactly 3 specific reasons it could fail:

Ticker: {ticker}
Signal: {signal} | Confidence: {confidence}
RSI: {rsi} | Gamma: {gamma_regime}
Volume: {volume_signal} | Kill Switch: {kill_switch}
FinViz Confirmation: [YES if in screener, NO if not]

For EACH reason, classify severity as "strong" (likely invalidation) or "weak" (minor risk).

Output ONLY this JSON:
{"inversion_reasons": [
  {"reason": "reason text", "severity": "strong|weak"},
  {"reason": "reason text", "severity": "strong|weak"},
  {"reason": "reason text", "severity": "strong|weak"}
]}
```

---

## Current State

**Last Successful Completion (2026-05-11 11:47 UTC):**

1. ✅ All 9 agents wired into orchestrator_swarm.py with correct execution order
2. ✅ Critic agent fixed — now correctly reads vif_signals from task_context
3. ✅ Signal verifier fully implemented with 4-gate logic and auto-reject conditions
4. ✅ Black-Scholes Greeks computed and cached (24-hour TTL)
5. ✅ IV% integrated into all signal dictionaries (zero API token overhead)
6. ✅ HTML report generation wired into pipeline with Greeks tab
7. ✅ build_greeks_table() reusable function created and integrated
8. ✅ Critic IV-aware veto logic patched (RSI<20 + IV>60% = full veto)
9. ✅ Full pipeline connectivity audit passed — zero import errors

**Committed Changes:**
```
feat: Wire signal-verifier into swarm pipeline + fix critic signal ingestion
feat: Add Greeks + IV% to signal pipeline (4-point integration)
fix: Wire build_greeks_table into pipeline output + critic IV veto logic
```

**Files in Modified State (Staged):**
- swarm/orchestrator.py
- swarm/critic_agent.py
- swarm/native_signal_verifier_agent.py (new)
- agents/indicators.py
- agents/orchestrator_swarm.py
- scripts/active/reporting/html_report_generator.py

**System Status:**
- No errors on dry-run initialization
- All agent imports clean
- Execution order matches canonical sequence
- Inter-agent signal passing validated
- Report generation tested with sample signals

---

## Next Step Queue

### Immediate (Ready to Execute)
1. **Scheduler Integration Test**
   - Run `python schedule_daily.py` (single execution, not cron)
   - Verify all 9 agents execute in sequence without blocking
   - Check that final HTML report includes Greeks tab

2. **Signal Quality Validation**
   - Run against vantage_portfolio watchlist (full 85 tickers)
   - Verify veto/downgrade/pass rates match expected distributions
   - Sample 5 vetoed signals — confirm veto reasons are valid

3. **Performance Baseline**
   - Measure end-to-end execution time for 85 tickers
   - Token count for full pipeline (should stay under 5,000 tokens)
   - Cache hit rate on Greeks (expect 60%+ reuse within 24h)

### Phase 3 (Week 2-3)
1. **Shadow Testing vs. Historical Data**
   - Compare 5-day forward returns: verified signals vs. all signals
   - Target: validated signals outperform by 3%+ Sharpe ratio

2. **FinViz Screener Phase B Integration**
   - Currently blocked; pending 6 bug fixes (detailed in finviz_pending_fixes.md)
   - When ready: FinViz becomes 7th consensus agent (boosting α)
   - Expected novel discovery rate: 65% new tickers outside VIF watchlists

3. **AutoResearch Framework Verification**
   - Ensure research-synthesis layer feeds into swing screener ranking
   - Validate that novel factors from external audit boost conviction on low-confidence signals

### Known Blockers
1. **Docs Auto-Update** — Post-commit hook broken on Windows (python3 → python issue)
   - SYSTEM_CONTEXT.md never auto-regenerates after commits
   - Workaround: Manual update via `python scripts/update_system_context.py`

2. **FinViz Rate Limiting** — 6 integration bugs (detailed in SESSION_HANDOFF_FINVIZ.md)
   - Needs ThreadPoolExecutor tuning + filter syntax validation
   - Tabled pending system research phase

---

## Artifacts & Checkpoints

**Saved State Files:**
- `SESSION_HANDOFF_SIGNAL_VALIDATOR.md` (this file) — Complete framework documentation
- `SESSION_HANDOFF_FINVIZ.md` — FinViz screener integration status (parallel work)

**Configuration Files:**
- `config/vif_config.yml` — Framework parameters (unchanged in this session)
- `config/finviz_screeners.yml` — 19 screener definitions (Phase A complete)

**Test/Validation:**
- No breaking changes to existing tests
- Full dry-run validation passed
- Ready for live scheduler execution

**HTML Report Template:**
- `scripts/active/reporting/html_report_generator.py` — build_greeks_table() + all CSS
- Auto-generated per-run at `reports/swarm_{mode}_{timestamp}.html`

---

## Resume Instructions

When resuming after reset:

1. **Restore Environment:**
   ```bash
   python tests/test_api_key.py  # Validate API key
   python tests/test_harness.py  # Quick offline validation
   ```

2. **Run Full Pipeline:**
   ```bash
   python schedule_daily.py  # Single execution (not cron)
   # Check: logs/scheduler.log for any errors
   # Check: reports/swarm_premarket_*.html for final report
   ```

3. **Validate Signal Quality:**
   - Open latest HTML report in browser
   - Verify Greeks tab populated (all signals have IV%, delta, gamma)
   - Spot-check 3 vetoed signals — confirm reasons valid
   - Check rejection rate (<20% is normal)

4. **Next Phase Trigger:**
   - If scheduler runs clean: Proceed to Phase 3 shadow testing
   - If errors occur: Check `logs/scheduler.log` for root cause
   - If missing Greeks: Verify `data/options_greeks_cache.json` exists

---

## Session Summary

✅ Multi-agent pipeline fully integrated (9 agents, sequential execution)  
✅ Critic veto engine + IV-aware SELL logic implemented  
✅ 4-gate signal verifier deployed (Volume/Fund/Sent/Macro gates)  
✅ Black-Scholes Greeks + IV% cached and integrated (zero API tokens)  
✅ HTML reporting with reusable Greeks table template  
✅ Full connectivity audit passed — ready for operational testing

**Ready for:** Daily scheduler execution, 5-day forward validation, Phase 3 integration planning
