# Quick Start: Usage Tracking & Monitoring

Get started monitoring your API costs in **5 minutes**.

---

## TL;DR

1. **Add credits now**: https://console.anthropic.com/account/billing/overview
2. **Verify setup**: `python tests/test_api_key.py`
3. **Check usage daily**: `python scripts/check_usage.py`

---

## Step 1: Add Credits (Required First)

Your API balance is zero. You must add credits before any agents can run.

**Go to**: https://console.anthropic.com/account/billing/overview

**Choose one**:
- Pay-as-you-go: Add $25 in prepaid credits (lasts ~6 months)
- Monthly plan: $5–$100/month subscription

**For your usage** (~$0.13/day), $25 prepaid credits will last 6+ months.

---

## Step 2: Verify Connection

After adding credits, test:

```bash
python tests/test_api_key.py
```

Should output:
```
✓ API key valid
✓ Anthropic API accessible
✓ Ready for analysis
```

---

## Step 3: Check Usage Daily

Run this after your agents finish:

```bash
python scripts/check_usage.py
```

Output will show:
- Total API calls and tokens used
- Cost breakdown by agent
- Daily costs and monthly projection
- Status (green if <$0.20/day)

---

## Step 4: Integrate Into Agents (Optional but Recommended)

To enable token-per-call tracking, add this to your agents:

**In `agents/watchlist_watcher.py`** (or any agent):

```python
from utils.structured_logging import setup_logger, MetricsLogger
from utils.usage_tracker import UsageTracker

# Add at module level
logger = setup_logger("watchlist_watcher")
metrics = MetricsLogger(logger)
usage_tracker = UsageTracker("watchlist_watcher")

# In your Claude API call:
response = client.messages.create(...)

# Log the tokens used
usage_tracker.log_api_call(
    operation="vif_analysis",
    input_tokens=response.usage.input_tokens,
    output_tokens=response.usage.output_tokens,
    batch_size=15  # Number of tickers analyzed
)
```

After integration, `python scripts/check_usage.py` will show per-agent breakdowns.

---

## Cost Targets

| Metric | Target | Current |
|--------|--------|---------|
| Daily Cost | <$0.15 | ? |
| Monthly Cost | <$5.00 | ? |
| Cache Hit Rate | >50% | ? (after integration) |

---

## Usage Patterns to Watch For

🟢 **Good** (~$0.10/day):
- Batching 15+ tickers per call
- Cache hits on 50%+ of data fetches
- Daily schedules (6–8 API calls)

🟡 **Caution** (~$0.20–$0.30/day):
- More frequent analysis runs (multiple per hour)
- Smaller batches (5–10 tickers per call)
- No caching enabled

🔴 **Concerning** (>$0.50/day):
- Individual ticker analysis (1 ticker per call)
- High-frequency monitoring
- Broken retry loops (repeated failed calls)

---

## Monitor Logs

Real-time logs are written to:

```bash
# Watch agent logs as they run
tail -f logs/watchlist_watcher.log

# View structured token data
tail -f logs/usage/watchlist_watcher_usage.jsonl
```

---

## Files You Should Know About

| File | Purpose |
|------|---------|
| `API_STATUS_REPORT.md` | Full status & recommendations |
| `utils/INTEGRATION_GUIDE.md` | How to integrate tracking into agents |
| `scripts/check_usage.py` | Daily cost report |
| `utils/usage_tracker.py` | Token counting backend |
| `utils/error_recovery.py` | Retry & fallback logic (optional) |
| `utils/structured_logging.py` | Metrics logging (optional) |

---

## Common Issues

### "Your credit balance is too low"
→ Go to step 1, add credits

### "No usage data found when I run check_usage.py"
→ Normal if you just integrated. Usage logs appear after agents run.

### "Usage report shows very high numbers"
→ Check if retry loop is stuck. See `logs/watchlist_watcher.log`

---

## Next: Run Your First Analysis

Once credits are added and verified:

```bash
python agents/watchlist_watcher.py --watchlist vantage_portfolio
```

Then:

```bash
python scripts/check_usage.py
```

This will show the cost of analyzing one watchlist.

---

## Full Documentation

- Architecture: `CLAUDE.md`
- Integration: `utils/INTEGRATION_GUIDE.md`
- Error recovery: `utils/error_recovery.py` (docstrings)
- Logging: `utils/structured_logging.py` (docstrings)

---

**Questions?** Check `API_STATUS_REPORT.md` for troubleshooting.
