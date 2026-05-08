#!/usr/bin/env python3
"""
Quick usage check and cost projection.
Run this daily to monitor API spending.
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

USAGE_DIR = Path("logs/usage")


def analyze_usage():
    """Analyze current usage and project costs."""
    if not USAGE_DIR.exists():
        print("❌ No usage data found. Run agents to generate logs.")
        return

    # Token pricing (Sonnet 4.6 - Jan 2026 pricing)
    SONNET_INPUT_COST = 0.003 / 1000
    SONNET_OUTPUT_COST = 0.015 / 1000

    # Aggregate data
    daily_data = defaultdict(lambda: {
        'calls': 0,
        'input': 0,
        'output': 0,
        'cache_creation': 0,
        'cache_read': 0,
        'cost': 0.0,
        'agents': defaultdict(int)
    })

    # Parse all usage files
    for usage_file in USAGE_DIR.glob("*_usage.jsonl"):
        with open(usage_file, 'r') as f:
            for line in f:
                try:
                    record = json.loads(line)
                    date = record['timestamp'][:10]

                    input_tokens = record['input_tokens']
                    output_tokens = record['output_tokens']
                    cache_creation = record.get('cache_creation_tokens', 0)
                    cache_read = record.get('cache_read_tokens', 0)

                    # Calculate cost
                    cost = (
                        input_tokens * SONNET_INPUT_COST +
                        output_tokens * SONNET_OUTPUT_COST +
                        cache_creation * SONNET_INPUT_COST * 0.25 +
                        cache_read * SONNET_INPUT_COST * 0.1
                    )

                    daily_data[date]['calls'] += 1
                    daily_data[date]['input'] += input_tokens
                    daily_data[date]['output'] += output_tokens
                    daily_data[date]['cache_creation'] += cache_creation
                    daily_data[date]['cache_read'] += cache_read
                    daily_data[date]['cost'] += cost
                    daily_data[date]['agents'][record['agent']] += 1

                except (json.JSONDecodeError, KeyError):
                    continue

    if not daily_data:
        print("❌ No valid usage records found.")
        return

    # Print report
    print("\n" + "=" * 90)
    print("📊 VIF TRADING SYSTEM - API USAGE REPORT")
    print("=" * 90)

    # Summary stats
    total_cost = sum(d['cost'] for d in daily_data.values())
    total_calls = sum(d['calls'] for d in daily_data.values())
    total_input = sum(d['input'] for d in daily_data.values())
    total_output = sum(d['output'] for d in daily_data.values())
    total_cache_read = sum(d['cache_read'] for d in daily_data.values())

    print(f"\n📈 OVERALL STATS")
    print(f"  Total API Calls: {total_calls:,}")
    print(f"  Total Tokens: {total_input + total_output:,}")
    print(f"    - Input: {total_input:,}")
    print(f"    - Output: {total_output:,}")
    print(f"  Cache Reads: {total_cache_read:,} (saved ~${total_cache_read * 0.00000003:.2f})")
    print(f"  Total Cost: ${total_cost:.2f}")

    # Daily breakdown
    print(f"\n📅 DAILY BREAKDOWN")
    print(f"{'Date':<12} {'Calls':<8} {'Input':<10} {'Output':<10} {'Cost':<10} {'Status':<20}")
    print("-" * 80)

    for date in sorted(daily_data.keys()):
        data = daily_data[date]
        status = "✓ Normal" if data['cost'] < 0.20 else "⚠️  High" if data['cost'] < 0.50 else "🔴 CRITICAL"
        print(
            f"{date:<12} {data['calls']:<8} {data['input']:<10,} "
            f"{data['output']:<10,} ${data['cost']:<9.2f} {status:<20}"
        )

    # Agent breakdown
    print(f"\n🤖 AGENTS BREAKDOWN")
    agent_stats = defaultdict(lambda: {'calls': 0, 'cost': 0.0, 'days': set()})

    for date, data in daily_data.items():
        for agent, calls in data['agents'].items():
            agent_stats[agent]['calls'] += calls
            agent_stats[agent]['days'].add(date)

    for agent in sorted(agent_stats.keys()):
        stats = agent_stats[agent]
        days_active = len(stats['days'])
        print(f"  {agent:<25} {stats['calls']:<6} calls | {days_active} days active")

    # Projections
    print(f"\n🔮 PROJECTIONS")
    if len(daily_data) > 0:
        avg_daily_cost = total_cost / len(daily_data)
        projected_monthly = avg_daily_cost * 30
        days_elapsed = len(daily_data)

        print(f"  Average Daily Cost: ${avg_daily_cost:.2f}")
        print(f"  Projected Monthly: ${projected_monthly:.2f}")
        print(f"  Days with Usage: {days_elapsed}")

        if projected_monthly < 5:
            print(f"  Status: ✅ HEALTHY (well under $20/month budget)")
        elif projected_monthly < 15:
            print(f"  Status: ⚠️  CAUTION (approaching budget)")
        else:
            print(f"  Status: 🔴 CRITICAL (over budget)")

    # Recommendations
    print(f"\n💡 RECOMMENDATIONS")

    # Check if caching is being used
    if total_cache_read == 0:
        print("  • ⚠️  No cache reads detected. Ensure @cache_response decorator is used.")
    else:
        cache_savings = (total_cache_read / (total_input + total_cache_read)) * 100
        print(f"  • ✓ Cache hit rate: {cache_savings:.1f}% (good)")

    # Check average batch size
    avg_batch = total_calls / len(daily_data) if daily_data else 0
    if avg_batch < 5:
        print(f"  • 📦 Consider increasing batch size. Currently {avg_batch:.0f} calls/day.")
    elif avg_batch > 15:
        print(f"  • ✓ Batch size is good ({avg_batch:.0f} calls/day)")

    # Cost warnings
    if total_cost > 5:
        print(f"  • 🔴 CRITICAL: You've already spent ${total_cost:.2f}. Check for excessive API calls.")
    elif total_cost > 1:
        print(f"  • ⚠️  Already at ${total_cost:.2f} spent. Monitor closely.")
    else:
        print(f"  • ✓ Still well under budget at ${total_cost:.2f}")

    print("\n" + "=" * 90 + "\n")


if __name__ == '__main__':
    analyze_usage()
