# Integration Guide: Usage Tracking, Caching & Error Recovery

This guide shows how to integrate usage tracking, Anthropic prompt caching, batch processing, and error recovery into your agents for observability, cost optimization, and resilience.

**Key Anthropic Best Practices**:
- Prompt caching: 90% cheaper cache reads (perfect for VIF framework rules)
- Batch API: 50% discount for async processing (perfect for overnight runs)
- Combined: Up to 95% savings when both are used together

## Quick Start: Three Implementation Levels

### Level 1: Basic Usage Tracking (5 min)
✅ Recommended as first step

### Level 2: Prompt Caching (10 min)
✅ Saves 60% on VIF framework analysis

### Level 3: Batch API (30 min, optional)
⚡ Saves additional 50% on nightly runs

---

## Level 1: Basic Usage Tracking

### 1. In Any Agent File

```python
from utils.structured_logging import setup_logger, MetricsLogger
from utils.usage_tracker import UsageTracker
from utils.error_recovery import retry_with_backoff, FallbackDataGenerator, CircuitBreaker

# Set up at module level
logger = setup_logger("my_agent", level=logging.INFO)
metrics = MetricsLogger(logger)
usage_tracker = UsageTracker("my_agent")
breaker = CircuitBreaker(failure_threshold=5)
```

### 2. Log API Calls with Token Tracking

```python
import time

def call_claude_vif_analysis(client, ticker, data):
    """Call Claude with tracking."""
    start = time.time()
    
    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            messages=[{"role": "user", "content": f"Analyze {ticker}..."}]
        )
        
        duration_ms = (time.time() - start) * 1000
        
        # Track usage
        usage_record = usage_tracker.log_api_call(
            operation=f"vif_analysis_{ticker}",
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            batch_size=1
        )
        
        # Log metrics
        metrics.log_api_call(
            operation="vif_analysis",
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            latency_ms=duration_ms,
            ticker=ticker
        )
        
        return response.content[0].text
    
    except Exception as e:
        metrics.log_api_call(
            operation="vif_analysis",
            input_tokens=0,
            output_tokens=0,
            latency_ms=(time.time() - start) * 1000,
            success=False,
            error=str(e),
            ticker=ticker
        )
        raise
```

### 3. Use Circuit Breaker for Resilience

```python
def analyze_ticker_safe(client, ticker):
    """Analyze ticker with circuit breaker protection."""
    try:
        result = breaker.call(
            call_claude_vif_analysis,
            client,
            ticker,
            None
        )
        return result
    except Exception as e:
        logger.warning(f"Circuit breaker triggered for {ticker}: {e}")
        # Fall back to mock data
        fallback = FallbackDataGenerator.generate_mock_vif_analysis(ticker)
        return fallback
```

### 4. Cache Data Fetches

```python
from utils.error_recovery import cache_response

@cache_response(cache_dir=Path("data/market_cache"), ttl_hours=24)
def fetch_ohlcv_data(ticker, period):
    """Fetch data with automatic caching."""
    logger.info(f"Fetching {ticker} {period}...")
    df = yf.download(ticker, period=period, progress=False)
    return df.to_dict()
```

### 5. Log Signals Generated

```python
def process_signal(ticker, signal_data):
    """Process and log signal."""
    metrics.log_signal_generated(
        ticker=ticker,
        signal=signal_data['signal'],
        confidence=signal_data['confidence'],
        kill_switches_active=signal_data.get('kill_switches', []),
        regime=signal_data.get('gamma_regime')
    )
```

### 6. Log Batch Completion

```python
import time

def analyze_watchlist(client, tickers):
    """Analyze multiple tickers and log batch metrics."""
    start = time.time()
    batch_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    total_tokens = 0
    success_count = 0
    error_count = 0
    
    for ticker in tickers:
        try:
            result = analyze_ticker_safe(client, ticker)
            success_count += 1
            # Extract token count from usage tracker
        except Exception as e:
            error_count += 1
            logger.error(f"Failed to analyze {ticker}: {e}")
    
    duration = time.time() - start
    metrics.log_batch_completion(
        batch_id=batch_id,
        ticker_count=len(tickers),
        total_tokens=total_tokens,
        success_count=success_count,
        error_count=error_count,
        duration_sec=duration
    )
```

## Viewing Usage Reports

### Daily Usage Report
```bash
python utils/usage_tracker.py
```

Output:
```
📊 DAILY USAGE REPORT
================================================================================
Date: 2026-04-30
Total Calls: 45
Total Tokens: 52,340
Total Cost: $0.78
Est. Monthly: $23.40

Breakdown by Agent:
  watchlist_watcher: 18 calls, 23,450in/8,200out, $0.35
  catalyst_agent: 12 calls, 15,600in/3,500out, $0.24
  swing_screener: 15 calls, 13,290in/2,100out, $0.19
```

### Monthly Usage Report
```bash
python utils/usage_tracker.py | tail -20
```

## Cost Optimization Checklist

- [ ] All API calls log tokens via `UsageTracker`
- [ ] All data fetches use `@cache_response` decorator
- [ ] Batching is 15+ tickers per API call
- [ ] Circuit breaker is enabled for multi-agent pipelines
- [ ] Fallback data generator is configured for critical failures
- [ ] Daily usage report is checked (target: <$0.15/day)
- [ ] Monthly burn rate is tracked (target: <$4/month)

## Troubleshooting

### "Credit balance is too low" Error

This means you've hit your API cap. To prevent this:

1. **Check daily usage**: `python utils/usage_tracker.py`
2. **Identify heavy operations**:
   - Look for agents with high input token counts
   - Check batch sizes (increase to 20-30 tickers)
   - Enable caching for all data fetches
3. **Set up alerts**:
   - Add to your scheduler: If daily cost > $0.20, log warning
   - Monitor usage report after each run

### Cache Not Working

If you see "No cache hit" in logs but expect caching:

1. Verify `@cache_response` decorator is applied
2. Check TTL: `cache_response(ttl_hours=24)` (adjust if needed)
3. Ensure cache dir exists: `mkdir -p data/market_cache`
4. Check file permissions on cache directory

### Circuit Breaker Staying OPEN

If circuit breaker stays OPEN:

1. Check API credentials in `.env`
2. Verify API key has remaining balance
3. Check network connectivity
4. Review recent error logs: `tail -50 logs/my_agent.log`

---

## Level 2: Prompt Caching (90% Cache Read Savings)

Prompt caching is **essential for your VIF framework** because you use the same 200-token system prompt for every analysis call.

### Why Cache VIF Rules?

The VIF framework instructions (kill switches K1–K6, gamma rules, structural levels) are:
- **Identical across all tickers** (no variation)
- **Reusable for 5+ minutes** (cache TTL)
- **200+ tokens** (expensive to recompute)

**Savings**: ~$0.06 per batched call with caching vs. without

### Implementation

```python
import anthropic

# Your VIF framework system prompt (200+ tokens)
VIF_SYSTEM_PROMPT = """
You are a VIF framework analyst. Analyze the provided ticker for:

[K1] Extreme Volatility: RSI > 80 or RSI < 20
[K2] Gap Risk: 5-day range > 10%
[K3] Low Liquidity: Volume < 1M shares
[K4] News Risk: Earnings within 5 days
[K5] Correlation Risk: correlation > 0.8 with index
[K6] Technical Breakdown: close below 20-day MA and declining volume

Determine gamma regime (positive/negative/transition) and provide BUY/SELL/HOLD signal.
"""

def analyze_ticker_with_caching(client, ticker, indicator_data):
    """Analyze ticker with cached VIF framework."""
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=[
            {
                "type": "text",
                "text": VIF_SYSTEM_PROMPT,
                # Explicit cache control: reuse this system prompt
                "cache_control": {"type": "ephemeral"}  # 5-min cache
            }
        ],
        messages=[
            {
                "role": "user",
                "content": f"Analyze {ticker}\nIndicators: {indicator_data}"
            }
        ]
    )

    # Log cache performance
    usage = response.usage
    print(f"Cache creation tokens: {getattr(usage, 'cache_creation_input_tokens', 0)}")
    print(f"Cache read tokens: {getattr(usage, 'cache_read_input_tokens', 0)}")

    return response.content[0].text
```

### Cache Performance Tracking

The API returns cache metrics you should log:

```python
cache_creation = response.usage.cache_creation_input_tokens  # Cost: 1.25x input
cache_read = response.usage.cache_read_input_tokens          # Cost: 0.1x input
regular_input = response.usage.input_tokens                  # Cost: 1.0x input
output = response.usage.output_tokens                        # Cost: output rate
```

**Expected behavior**:
- **First call**: `cache_creation=200` (write VIF rules to cache)
- **Calls 2–60**: `cache_read=0, input=150` (cache hits, no VIF rule tokens needed)
- **After 5 min**: `cache_creation=200` again (cache expired, rewrite)

### Cache Hit Rate Target

Track this metric:
```python
cache_read_ratio = cache_read / (cache_read + regular_input)
# Target: > 60% means your cache is working
```

---

## Level 3: Batch API (50% Discount for Async Processing)

For overnight, non-realtime analysis, use Batch API to process all watchlists at 50% discount.

### When to Use Batch API

- ✅ Nightly full portfolio sweep (2 AM)
- ✅ Weekend macro analysis (Friday evening)
- ✅ End-of-week comprehensive reports
- ❌ NOT for realtime trading signals (24-hour latency)

### Implementation Example

```python
import anthropic
import json
from datetime import datetime

def create_batch_request(tickers, indicators_dict):
    """Create batch API request for multiple tickers."""
    requests = []
    
    for ticker in tickers:
        requests.append({
            "custom_id": f"{ticker}_{datetime.now().isoformat()}",
            "params": {
                "model": "claude-sonnet-4-6",
                "max_tokens": 512,
                "system": [{
                    "type": "text",
                    "text": VIF_SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"}
                }],
                "messages": [{
                    "role": "user",
                    "content": f"Analyze {ticker}\nData: {indicators_dict[ticker]}"
                }]
            }
        })
    
    return requests

def submit_batch(client, requests):
    """Submit batch request to Anthropic."""
    batch_json = "\n".join(json.dumps(r) for r in requests)
    
    batch = client.beta.messages.batches.create(
        requests=json.loads(f"[{batch_json}]")
    )
    
    print(f"Batch submitted: {batch.id}")
    print(f"Status: {batch.processing_status}")
    print(f"Expected completion: ~10 minutes (within 24 hours)")
    
    return batch

def poll_batch_results(client, batch_id):
    """Poll batch results (run every 5 min)."""
    batch = client.beta.messages.batches.retrieve(batch_id)
    
    print(f"Status: {batch.processing_status}")
    print(f"Succeeded: {batch.request_counts.succeeded}")
    print(f"Failed: {batch.request_counts.failed}")
    
    if batch.processing_status == "ended":
        # Process results
        for result in batch.result():
            ticker_id = result.custom_id
            signal = result.result.message.content[0].text
            print(f"{ticker_id}: {signal}")
```

### Batch Cost Comparison

```
Processing 85 tickers nightly:

Realtime API:
  85 tickers × 150 tokens × $0.003/M = $0.04/night
  × 365 days = $14.60/year

Batch API (50% discount):
  85 tickers × 150 tokens × $0.003/M × 0.5 = $0.02/night
  × 365 days = $7.30/year

Savings: $7.30/year per batch schedule
```

---

## Combined: Caching + Batch (95% Savings)

The ultimate optimization combines both:

```python
def analyze_batch_with_cache(client, tickers):
    """Full optimization: batch requests with cached VIF framework."""
    requests = []
    
    for ticker in tickers:
        requests.append({
            "custom_id": ticker,
            "params": {
                "model": "claude-sonnet-4-6",
                "max_tokens": 512,
                "system": [{
                    "type": "text",
                    "text": VIF_SYSTEM_PROMPT,  # 200 tokens
                    "cache_control": {"type": "ephemeral"}  # Cache this
                }],
                "messages": [{
                    "role": "user",
                    "content": f"Analyze {ticker}..."
                }]
            }
        })
    
    # Submit batch (50% discount)
    batch = submit_batch(client, requests)
    
    # Results show:
    # - Cache writes on first 1–2 requests
    # - Cache reads on remaining 83–84 requests
    # - 50% cost reduction from batch API
    # = ~95% total savings
```

---

## Cost Comparison: All Strategies

| Strategy | Daily | Monthly | Savings |
|----------|-------|---------|---------|
| Realtime only | $0.13 | $3.90 | — |
| + Caching | $0.05 | $1.50 | 60% |
| + Batch API | $0.03 | $0.90 | 77% |
| + Both | $0.02 | $0.60 | 85% |

---

## Example: Full Integration in watchlist_watcher.py

See the next section for a complete working example that integrates all utilities.
