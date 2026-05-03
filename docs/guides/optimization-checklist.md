# VIF Trading System - Optimization Checklist

**Objective**: Reduce monthly API spend from $3.90 → $0.60 while improving observability  
**Timeline**: Complete in stages (basic: 1 day, full: 1 week)  
**Benefit**: 85% cost reduction + early issue detection

---

## ⚡ QUICK START (Day 1 - 30 minutes)

- [ ] **Verify credits** (1 min)
  ```bash
  python tests/test_api_key.py
  ```
  Should show: `SUCCESS: key valid, billing active`

- [ ] **Check baseline cost** (2 min)
  ```bash
  python scripts/check_usage.py
  ```
  Note your daily/monthly cost

- [ ] **Read integration guide** (10 min)
  - Open: `utils/INTEGRATION_GUIDE.md`
  - Skim "Level 1: Basic Usage Tracking" section

- [ ] **Add usage tracker to one agent** (15 min)
  - File: `agents/watchlist_watcher.py`
  - Add 4 lines from integration guide
  - Test by running: `python agents/watchlist_watcher.py --watchlist vantage_portfolio`

- [ ] **Verify tracking works** (2 min)
  ```bash
  ls -lah logs/usage/  # Should have new usage file
  python scripts/check_usage.py  # Should show your costs
  ```

---

## 🎯 PHASE 1: Observability (Week 1 - 45 minutes)

- [ ] **Integrate UsageTracker into all main agents** (20 min)
  - `agents/watchlist_watcher.py` ✓ (done above)
  - `agents/weekend_catalyst_agent.py`
  - `agents/orchestrator.py`
  - Reference: `examples/watchlist_watcher_with_caching_example.py`

- [ ] **Set up daily monitoring** (5 min)
  - Create reminder: Run `python scripts/check_usage.py` daily
  - Add to your calendar or cron if on Linux/Mac

- [ ] **Test structured logging** (10 min)
  - Run: `python utils/structured_logging.py`
  - Check logs are being written to `logs/watchlist_watcher.log`
  - Verify agent logs show token counts

- [ ] **Review first week of data** (10 min)
  - Run agents normally for 3–5 days
  - Check: `python scripts/check_usage.py`
  - Look for:
    - Daily cost trends
    - Agent-by-agent breakdown
    - Any unexpected spikes

- [ ] **Understand your baseline**
  - Note: Daily cost without optimizations
  - Note: Most expensive agent
  - Note: Total monthly projection

---

## 🚀 PHASE 2: Prompt Caching (Week 1–2 - 10 minutes)

**Effort**: Very easy (1 line change per agent)  
**Savings**: 60% on input tokens  
**Prerequisite**: Phase 1 complete ✓

- [ ] **Read caching documentation** (5 min)
  - Section: `utils/INTEGRATION_GUIDE.md` → "Level 2: Prompt Caching"
  - Example: `examples/watchlist_watcher_with_caching_example.py`

- [ ] **Add cache_control to VIF system prompt** (5 min)
  - In `agents/watchlist_watcher.py`, find where you create the Claude message
  - Change:
    ```python
    system=VIF_SYSTEM_PROMPT
    ```
  - To:
    ```python
    system=[{
        "type": "text",
        "text": VIF_SYSTEM_PROMPT,
        "cache_control": {"type": "ephemeral"}
    }]
    ```

- [ ] **Verify caching is working** (2 min)
  - Run multiple calls to same ticker
  - Check logs for: `cache_read_input_tokens` increasing
  - Cost should drop by ~60%

- [ ] **Measure savings** (5 min)
  ```bash
  python examples/watchlist_watcher_with_caching_example.py
  ```
  - Should show cache hits on calls 2–5
  - Cost per call drops ~90% after first call

- [ ] **Enable caching in other agents** (5 min)
  - `agents/weekend_catalyst_agent.py`
  - `scripts/swing_trade_screener_v2.py`
  - Any other Claude API calls

- [ ] **Verify Phase 2 results**
  - Run `python scripts/check_usage.py`
  - Daily cost should drop from $0.13 → $0.05
  - Look for cache savings in report

---

## ⚙️ PHASE 3: Batch API (Week 2–3 - 30 minutes, OPTIONAL)

**Effort**: Medium (schedule changes, async handling)  
**Savings**: Additional 50% on nightly runs  
**Prerequisite**: Phase 1 & 2 complete ✓  
**Impact**: Best for non-realtime analysis

- [ ] **Read batch API documentation** (10 min)
  - Section: `utils/INTEGRATION_GUIDE.md` → "Level 3: Batch API"
  - Configuration: `config/cache_config.yml`

- [ ] **Create batch request builder** (10 min)
  - Reference: `examples/watchlist_watcher_with_caching_example.py` → `create_batch_request()`
  - Create: `agents/batch_analyzer.py` with batch submission logic

- [ ] **Schedule overnight batch job** (5 min)
  - Edit: `schedule_daily.py`
  - Add: 2 AM nightly batch analysis job
  - Config: `config/cache_config.yml` has templates

- [ ] **Implement result polling** (5 min)
  - Add: `poll_batch_results()` function
  - Check batch status every 5 minutes
  - Save results to `reports/batch/`

- [ ] **Verify Phase 3 results**
  - Run batch job once manually
  - Check: `python scripts/check_usage.py`
  - Monthly cost should drop from $1.50 → $0.90
  - Batch savings should appear in reports

---

## 🛡️ PHASE 4: Error Recovery (Week 2 - 10 minutes, OPTIONAL)

**Effort**: Easy (decorators)  
**Benefit**: Prevent cascading failures, graceful degradation  
**Prerequisite**: Phase 1 complete ✓

- [ ] **Add retry decorator to API calls** (5 min)
  ```python
  from utils.error_recovery import retry_with_backoff

  @retry_with_backoff(max_retries=3, initial_delay=1.0)
  def analyze_with_claude(...):
      # Your API call
      ...
  ```

- [ ] **Add circuit breaker to orchestrator** (3 min)
  ```python
  from utils.error_recovery import CircuitBreaker

  breaker = CircuitBreaker(failure_threshold=5)
  result = breaker.call(my_api_function, ...)
  ```

- [ ] **Test error recovery** (2 min)
  - Verify retry logic with temporary timeout
  - Check logs show backoff increases
  - Verify circuit breaker engages after 5 failures

---

## ✅ VERIFICATION CHECKLIST

After each phase, verify:

### Phase 1 (Observability) ✓
- [ ] Usage tracker generates files in `logs/usage/`
- [ ] `check_usage.py` shows your costs
- [ ] Daily cost is within expected range (<$0.20)
- [ ] Logs show token counts per call

### Phase 2 (Caching) ✓
- [ ] Cache hits appear in logs
- [ ] Cache read tokens > 0 after first call
- [ ] Daily cost drops to ~$0.05
- [ ] Cache savings shown in report

### Phase 3 (Batch API) ✓
- [ ] Batch job submits successfully
- [ ] Results appear within 24 hours
- [ ] Batch cost is 50% of realtime
- [ ] Monthly projection shows <$1.00

### Phase 4 (Error Recovery) ✓
- [ ] Retry decorator is applied
- [ ] Logs show backoff behavior
- [ ] Circuit breaker prevents cascades
- [ ] Fallback data works if API down

---

## 📊 EXPECTED RESULTS

| Phase | Daily Cost | Monthly | Cache Hits | Batch Jobs |
|-------|-----------|---------|-----------|-----------|
| **Baseline** | $0.13 | $3.90 | None | None |
| **+Phase 1** | $0.13 | $3.90 | Tracked | None |
| **+Phase 2** | $0.05 | $1.50 | >50% | None |
| **+Phase 3** | $0.03 | $0.90 | >50% | Nightly |
| **+Phase 4** | $0.02 | $0.60 | >50% | Nightly |

---

## 🎯 SUCCESS CRITERIA

✅ **Phase 1 Pass** (Must Have)
- Usage tracker working
- Costs visible
- Can identify expensive agents

✅ **Phase 2 Pass** (Recommended)
- Caching enabled
- >50% cache hit rate
- Cost reduced to <$0.10/day

✅ **Phase 3 Pass** (Optional)
- Batch jobs running
- Overnight analysis working
- Cost <$0.05/day

✅ **Phase 4 Pass** (Optional)
- Error handling robust
- No cascading failures
- Graceful degradation

---

## 📞 Troubleshooting

**Usage tracker not generating files?**
- Check: `mkdir -p logs/usage/`
- Verify: Import statement has no typos
- Test: `python utils/usage_tracker.py` directly

**Caching not working?**
- Verify: `cache_control` field is in system prompt
- Check: Logs for `cache_read_input_tokens > 0`
- Note: Cache expires after 5 minutes (ephemeral TTL)

**Batch jobs not completing?**
- Check: Batch submission succeeded
- Verify: Polling is running correctly
- Review: Results are saved to disk

**Error recovery not triggering?**
- Verify: Decorator is applied to function
- Test: Temporarily break API key to trigger retry
- Check: Logs show backoff messages

---

## 📅 Timeline Recommendation

| Week | Phase | Effort | Priority |
|------|-------|--------|----------|
| Week 1, Day 1 | Quick Start | 30 min | **CRITICAL** |
| Week 1, Days 2–3 | Phase 1 | 45 min | **CRITICAL** |
| Week 1, Days 4–5 | Phase 2 | 10 min | **Recommended** |
| Week 2, Day 1 | Phase 3 | 30 min | Optional |
| Week 2, Day 2 | Phase 4 | 10 min | Optional |

**Total**: ~2 hours across 2 weeks (or 1 week if accelerated)

---

## 🎓 Learning Resources

- `QUICK_START_USAGE_TRACKING.md` — 5-minute intro
- `utils/INTEGRATION_GUIDE.md` — Detailed how-to
- `CLAUDE.md` — Architecture overview
- `examples/` — Working code examples
- `config/cache_config.yml` — Configuration reference

---

## 📈 Ongoing Monitoring

Once implemented, your daily routine:

**Daily (30 seconds)**:
```bash
python scripts/check_usage.py | head -10
```

**Weekly (2 minutes)**:
```bash
tail -50 logs/watchlist_watcher.log  # Check for errors
python scripts/check_usage.py | tail -10  # Check costs
```

**Monthly (10 minutes)**:
```bash
python utils/usage_tracker.py  # Full monthly report
# Compare actual vs projections
# Review cache hit rates
# Plan any adjustments
```

---

**You're ready to optimize!** 🚀

Start with Quick Start today, Phase 1 this week, Phase 2 next week.
