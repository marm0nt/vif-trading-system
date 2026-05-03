#!/usr/bin/env python3
"""
EXAMPLE: watchlist_watcher.py with prompt caching enabled

This shows how to integrate Anthropic prompt caching into your VIF analysis.
It requires ~10 lines of changes to enable 60% cost savings.

Reference: https://platform.claude.com/docs/en/build-with-claude/prompt-caching
"""

import anthropic
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# === VIF FRAMEWORK SYSTEM PROMPT (to be cached) ===
VIF_FRAMEWORK_PROMPT = """You are a professional VIF (Volatility Imbalance Framework) analyst.

FRAMEWORK RULES:
================

[GAMMA REGIME DETECTION]
- Positive gamma (volatility is bid): Price >20d MA, volume rising, consecutive higher lows
- Negative gamma (volatility is offered): Price <20d MA, volume declining, consecutive lower highs
- Transition: Initial breakout from consolidation with strong volume

[STRUCTURAL LEVELS]
- Support: 25th percentile of last 20 days
- Resistance: 75th percentile of last 20 days
- Key level strength = # of touches in lookback period

[VOLUME CONFIRMATION]
- Strong volume: Current > 1.5x 20-day MA
- Weak volume: Current < 1.0x 20-day MA
- Volume trend: Volume profile analysis vs typical distribution

[KILL SWITCHES - Override signals if ANY active]
K1: Extreme Volatility - RSI > 80 or RSI < 20
K2: Gap Risk - 5-day range > 10%
K3: Low Liquidity - Volume < 1M shares
K4: News Risk - Earnings within 5 days
K5: Correlation Risk - correlation > 0.8 with major index
K6: Technical Breakdown - close below 20-day MA AND volume declining

OUTPUT FORMAT:
==============
Provide analysis in this JSON structure:
{
  "ticker": "NVDA",
  "signal": "BUY|SELL|HOLD",
  "confidence": 0.0-1.0,
  "gamma_regime": "positive|negative|transition",
  "kill_switches_active": ["K1", "K3"],
  "reasoning": "Brief explanation",
  "price_target": "If buy/sell",
  "support_level": 100.00,
  "resistance_level": 105.00
}"""


def analyze_ticker_without_cache(client: anthropic.Anthropic, ticker: str, data_summary: str) -> dict:
    """
    BEFORE: Standard API call without caching.

    Every call includes the full VIF_FRAMEWORK_PROMPT (200+ tokens).
    Cost per call: ~$0.025 (input tokens + output tokens)
    """
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        system=VIF_FRAMEWORK_PROMPT,  # ❌ Sent with EVERY request
        messages=[{
            "role": "user",
            "content": f"Analyze {ticker}:\n{data_summary}"
        }]
    )

    usage = response.usage
    logger.info(
        f"NO CACHE | {ticker} | "
        f"Input: {usage.input_tokens:,} | Output: {usage.output_tokens:,} | "
        f"Cost: ${(usage.input_tokens * 0.003 + usage.output_tokens * 0.015) / 1000:.4f}"
    )

    return {"ticker": ticker, "signal": response.content[0].text}


def analyze_ticker_with_cache(client: anthropic.Anthropic, ticker: str, data_summary: str) -> dict:
    """
    AFTER: API call with prompt caching enabled.

    VIF_FRAMEWORK_PROMPT is cached once, reused for 5+ minutes.
    First call: ~$0.025 (cache write costs 1.25x input)
    Subsequent calls: ~$0.002 (cache read = 0.1x input)

    SAVINGS: 90% cheaper on cache hits

    Reference: https://platform.claude.com/docs/en/build-with-claude/prompt-caching
    """
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        system=[
            {
                "type": "text",
                "text": VIF_FRAMEWORK_PROMPT,
                # ✅ Add ONE line for caching
                "cache_control": {"type": "ephemeral"}  # 5-minute cache
            }
        ],
        messages=[{
            "role": "user",
            "content": f"Analyze {ticker}:\n{data_summary}"
        }]
    )

    usage = response.usage

    # Extract cache metrics
    cache_creation = getattr(usage, 'cache_creation_input_tokens', 0)  # Cost: 1.25x
    cache_read = getattr(usage, 'cache_read_input_tokens', 0)          # Cost: 0.1x
    regular_input = usage.input_tokens                                  # Cost: 1.0x
    output = usage.output_tokens                                        # Cost: 1.0x

    # Calculate actual cost with cache
    input_cost = (regular_input * 0.003) + (cache_creation * 0.003 * 1.25) + (cache_read * 0.003 * 0.1)
    output_cost = output * 0.015
    total_cost = (input_cost + output_cost) / 1000

    # Log with cache metrics
    logger.info(
        f"WITH CACHE | {ticker} | "
        f"Create: {cache_creation:,} | Read: {cache_read:,} | Regular: {regular_input:,} | Out: {output:,} | "
        f"Cost: ${total_cost:.4f}"
    )

    return {"ticker": ticker, "signal": response.content[0].text}


def analyze_watchlist_cached(client: anthropic.Anthropic, tickers: list, indicators_dict: dict) -> list:
    """
    Process multiple tickers with caching.

    Cost breakdown for 15 tickers:

    WITHOUT CACHE:
      15 × $0.025 = $0.375

    WITH CACHE:
      1st call:  $0.025 (cache write)
      2-15 calls: 14 × $0.002 (cache read) = $0.028
      Total: $0.053

    SAVINGS: 86% reduction per watchlist run
    """
    results = []

    for i, ticker in enumerate(tickers):
        data_summary = f"Close: {indicators_dict[ticker].get('close', 'N/A')}, RSI: {indicators_dict[ticker].get('rsi', 'N/A')}"

        # Use cached version
        result = analyze_ticker_with_cache(client, ticker, data_summary)
        results.append(result)

        # Log batch progress
        if (i + 1) % 5 == 0:
            logger.info(f"Processed {i + 1}/{len(tickers)} tickers | Cache should be active")

    return results


# === MONITORING CACHE EFFECTIVENESS ===

def measure_cache_savings(client: anthropic.Anthropic, ticker: str, data: str, num_calls: int = 5):
    """
    Test cache effectiveness by making repeated calls.

    Expected output:
    - Call 1: cache_creation=200 (write to cache)
    - Calls 2-5: cache_read=200, regular_input=0 (cache hits)
    - Cost: 1 write + 4 reads = (1 × $0.0025) + (4 × $0.0003) = $0.0037
    """
    total_cost_no_cache = 0
    total_cost_with_cache = 0

    for call_num in range(num_calls):
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=100,
            system=[{
                "type": "text",
                "text": VIF_FRAMEWORK_PROMPT,
                "cache_control": {"type": "ephemeral"}
            }],
            messages=[{
                "role": "user",
                "content": f"Analyze {ticker}: {data}"
            }]
        )

        usage = response.usage

        # Without cache cost (always pay full price)
        cost_no_cache = (usage.input_tokens * 0.003 + usage.output_tokens * 0.015) / 1000
        total_cost_no_cache += cost_no_cache

        # With cache cost
        cache_creation = getattr(usage, 'cache_creation_input_tokens', 0)
        cache_read = getattr(usage, 'cache_read_input_tokens', 0)
        regular_input = usage.input_tokens

        input_cost = (regular_input * 0.003) + (cache_creation * 0.003 * 1.25) + (cache_read * 0.003 * 0.1)
        output_cost = usage.output_tokens * 0.015
        cost_with_cache = (input_cost + output_cost) / 1000
        total_cost_with_cache += cost_with_cache

        print(f"Call {call_num + 1}: Cache={cache_read > 0} | No cache: ${cost_no_cache:.4f} | With cache: ${cost_with_cache:.4f}")

    savings = total_cost_no_cache - total_cost_with_cache
    savings_pct = (savings / total_cost_no_cache) * 100

    print(f"\n5 calls total:")
    print(f"  Without cache: ${total_cost_no_cache:.4f}")
    print(f"  With cache:    ${total_cost_with_cache:.4f}")
    print(f"  Savings:       ${savings:.4f} ({savings_pct:.1f}%)")


if __name__ == '__main__':
    import os
    from dotenv import load_dotenv

    load_dotenv()
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    # Test data
    ticker = "NVDA"
    data = "Close: 105.50, RSI: 65, MA20: 103.00, Volume: 50M"

    print("\n=== TESTING CACHE EFFECTIVENESS ===\n")
    measure_cache_savings(client, ticker, data, num_calls=5)
