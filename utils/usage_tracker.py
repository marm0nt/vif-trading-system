#!/usr/bin/env python3
"""
Token usage tracking and monitoring for VIF Trading System.
Logs all Claude API calls with structured metrics for cap monitoring.
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict
import os

USAGE_DIR = Path("logs/usage")
USAGE_DIR.mkdir(parents=True, exist_ok=True)

# Token pricing (Sonnet 4.6 - Updated 2026-04-30)
# Source: https://platform.claude.com/docs/en/about-claude/pricing
SONNET_INPUT_COST = 0.003 / 1000  # $3.00 per 1M input tokens
SONNET_OUTPUT_COST = 0.015 / 1000  # $15.00 per 1M output tokens

# Cache pricing (90% cheaper reads, ~25% write cost)
CACHE_READ_COST = SONNET_INPUT_COST * 0.1  # 10% of input rate (essentially free)
CACHE_WRITE_COST = SONNET_INPUT_COST * 1.25  # 125% of input rate (5-min TTL)

# Batch API pricing (50% discount)
BATCH_DISCOUNT = 0.5  # 50% off standard rates


@dataclass
class TokenUsage:
    """Structured token usage record."""
    timestamp: str
    agent: str
    operation: str
    input_tokens: int
    output_tokens: int
    cache_creation_tokens: int = 0
    cache_read_tokens: int = 0
    batch_size: int = 1

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens + self.cache_creation_tokens + self.cache_read_tokens

    @property
    def cost_usd(self) -> float:
        """Calculate cost following Anthropic's pricing model (2026).

        Reference: https://platform.claude.com/docs/en/about-claude/pricing
        - Regular input: $3/M tokens
        - Regular output: $15/M tokens
        - Cache write: 1.25x input cost (5-min ephemeral)
        - Cache read: 0.1x input cost (~90% savings)
        """
        input_cost = self.input_tokens * SONNET_INPUT_COST
        output_cost = self.output_tokens * SONNET_OUTPUT_COST
        cache_write_cost = self.cache_creation_tokens * CACHE_WRITE_COST
        cache_read_cost = self.cache_read_tokens * CACHE_READ_COST

        total = input_cost + output_cost + cache_write_cost + cache_read_cost
        return total

    @property
    def cost_with_batch_discount(self) -> float:
        """Cost if this call was processed via Batch API (50% discount)."""
        return self.cost_usd * BATCH_DISCOUNT


class UsageTracker:
    """Track and report API token usage."""

    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.logger = logging.getLogger(f"UsageTracker[{agent_name}]")
        self.session_start = datetime.now().isoformat()

    def log_api_call(
        self,
        operation: str,
        input_tokens: int,
        output_tokens: int,
        cache_creation_tokens: int = 0,
        cache_read_tokens: int = 0,
        batch_size: int = 1
    ) -> TokenUsage:
        """Log an API call and return usage record."""
        usage = TokenUsage(
            timestamp=datetime.now().isoformat(),
            agent=self.agent_name,
            operation=operation,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cache_creation_tokens=cache_creation_tokens,
            cache_read_tokens=cache_read_tokens,
            batch_size=batch_size
        )

        # Log to structured file
        usage_file = USAGE_DIR / f"{self.agent_name}_usage.jsonl"
        with open(usage_file, 'a') as f:
            f.write(json.dumps(asdict(usage)) + '\n')

        # Log to console with metrics
        self.logger.info(
            f"TOKENS | {operation} | "
            f"Input: {usage.input_tokens:,} | "
            f"Output: {usage.output_tokens:,} | "
            f"Cache: {cache_read_tokens:,}R/{cache_creation_tokens:,}W | "
            f"Total: {usage.total_tokens:,} | "
            f"Cost: ${usage.cost_usd:.4f} | "
            f"BatchSize: {batch_size}"
        )

        return usage


def get_daily_usage(include_batch_projection: bool = True) -> Dict[str, Any]:
    """Get usage stats for the current day.

    Args:
        include_batch_projection: Calculate savings if processed via Batch API
    """
    today = datetime.now().date()

    total_input = 0
    total_output = 0
    total_cache_creation = 0
    total_cache_read = 0
    total_cost = 0.0
    total_batch_cost = 0.0  # Projected cost with Batch API
    call_count = 0
    agent_stats = {}

    for usage_file in USAGE_DIR.glob("*_usage.jsonl"):
        with open(usage_file, 'r') as f:
            for line in f:
                try:
                    record = json.loads(line)
                    record_date = datetime.fromisoformat(record['timestamp']).date()

                    if record_date != today:
                        continue

                    agent = record['agent']
                    if agent not in agent_stats:
                        agent_stats[agent] = {
                            'calls': 0, 'input': 0, 'output': 0,
                            'cache_creation': 0, 'cache_read': 0, 'cost': 0.0
                        }

                    agent_stats[agent]['calls'] += 1
                    agent_stats[agent]['input'] += record['input_tokens']
                    agent_stats[agent]['output'] += record['output_tokens']
                    agent_stats[agent]['cache_creation'] += record.get('cache_creation_tokens', 0)
                    agent_stats[agent]['cache_read'] += record.get('cache_read_tokens', 0)

                    # Calculate actual cost
                    input_cost = record['input_tokens'] * SONNET_INPUT_COST
                    output_cost = record['output_tokens'] * SONNET_OUTPUT_COST
                    cache_write = record.get('cache_creation_tokens', 0) * CACHE_WRITE_COST
                    cache_read = record.get('cache_read_tokens', 0) * CACHE_READ_COST
                    cost = input_cost + output_cost + cache_write + cache_read

                    agent_stats[agent]['calls'] += 1
                    agent_stats[agent]['input'] += record['input_tokens']
                    agent_stats[agent]['output'] += record['output_tokens']
                    agent_stats[agent]['cache_creation'] += record.get('cache_creation_tokens', 0)
                    agent_stats[agent]['cache_read'] += record.get('cache_read_tokens', 0)
                    agent_stats[agent]['cost'] += cost

                    total_input += record['input_tokens']
                    total_output += record['output_tokens']
                    total_cache_creation += record.get('cache_creation_tokens', 0)
                    total_cache_read += record.get('cache_read_tokens', 0)
                    total_cost += cost
                    call_count += 1

                except json.JSONDecodeError:
                    continue

    total_batch_cost = total_cost * BATCH_DISCOUNT if include_batch_projection else 0
    cache_savings = total_cost - (total_cost - (total_cache_read * CACHE_READ_COST))

    return {
        'date': str(today),
        'total_calls': call_count,
        'total_input_tokens': total_input,
        'total_output_tokens': total_output,
        'total_cache_creation': total_cache_creation,
        'total_cache_read': total_cache_read,
        'total_tokens': total_input + total_output + total_cache_creation + total_cache_read,
        'total_cost_usd': round(total_cost, 4),
        'cache_savings_usd': round(total_cache_read * CACHE_READ_COST, 4),
        'estimated_monthly_cost': round(total_cost * 30, 2),
        'batch_api_projection_usd': round(total_batch_cost, 4),
        'batch_api_monthly_projection': round(total_batch_cost * 30, 2),
        'agent_breakdown': agent_stats
    }


def get_monthly_usage() -> Dict[str, Any]:
    """Get usage stats for the current month."""
    today = datetime.now()
    month_start = today.replace(day=1)

    total_input = 0
    total_output = 0
    total_cache_creation = 0
    total_cache_read = 0
    total_cost = 0.0
    call_count = 0
    agent_stats = {}

    for usage_file in USAGE_DIR.glob("*_usage.jsonl"):
        with open(usage_file, 'r') as f:
            for line in f:
                try:
                    record = json.loads(line)
                    record_date = datetime.fromisoformat(record['timestamp']).date()

                    if record_date < month_start.date():
                        continue

                    agent = record['agent']
                    if agent not in agent_stats:
                        agent_stats[agent] = {
                            'calls': 0, 'input': 0, 'output': 0,
                            'cache_creation': 0, 'cache_read': 0, 'cost': 0.0
                        }

                    agent_stats[agent]['calls'] += 1
                    agent_stats[agent]['input'] += record['input_tokens']
                    agent_stats[agent]['output'] += record['output_tokens']
                    agent_stats[agent]['cache_creation'] += record.get('cache_creation_tokens', 0)
                    agent_stats[agent]['cache_read'] += record.get('cache_read_tokens', 0)

                    # Calculate actual cost
                    input_cost = record['input_tokens'] * SONNET_INPUT_COST
                    output_cost = record['output_tokens'] * SONNET_OUTPUT_COST
                    cache_write = record.get('cache_creation_tokens', 0) * CACHE_WRITE_COST
                    cache_read = record.get('cache_read_tokens', 0) * CACHE_READ_COST
                    cost = input_cost + output_cost + cache_write + cache_read

                    agent_stats[agent]['calls'] += 1
                    agent_stats[agent]['input'] += record['input_tokens']
                    agent_stats[agent]['output'] += record['output_tokens']
                    agent_stats[agent]['cache_creation'] += record.get('cache_creation_tokens', 0)
                    agent_stats[agent]['cache_read'] += record.get('cache_read_tokens', 0)
                    agent_stats[agent]['cost'] += cost

                    total_input += record['input_tokens']
                    total_output += record['output_tokens']
                    total_cache_creation += record.get('cache_creation_tokens', 0)
                    total_cache_read += record.get('cache_read_tokens', 0)
                    total_cost += cost
                    call_count += 1

                except json.JSONDecodeError:
                    continue

    total_batch_cost = total_cost * BATCH_DISCOUNT

    return {
        'month': f"{today.year}-{today.month:02d}",
        'total_calls': call_count,
        'total_input_tokens': total_input,
        'total_output_tokens': total_output,
        'total_cache_creation': total_cache_creation,
        'total_cache_read': total_cache_read,
        'total_tokens': total_input + total_output + total_cache_creation + total_cache_read,
        'total_cost_usd': round(total_cost, 4),
        'cache_savings_usd': round(total_cache_read * CACHE_READ_COST, 4),
        'batch_api_projection_usd': round(total_batch_cost, 4),
        'cost_reduction_with_batch': round((1 - BATCH_DISCOUNT) * 100, 1),
        'agent_breakdown': agent_stats
    }


if __name__ == '__main__':
    print("\n📊 DAILY USAGE REPORT")
    print("=" * 80)
    daily = get_daily_usage()
    print(f"Date: {daily['date']}")
    print(f"Total Calls: {daily['total_calls']}")
    print(f"Total Tokens: {daily['total_tokens']:,}")
    print(f"\n💰 COSTS (Realtime API)")
    print(f"  Total Cost: ${daily['total_cost_usd']:.2f}")
    if daily['cache_savings_usd'] > 0:
        print(f"  Cache Savings: ${daily['cache_savings_usd']:.2f}")
    print(f"  Est. Monthly: ${daily['estimated_monthly_cost']:.2f}")
    print(f"\n⚡ BATCH API PROJECTION (50% discount)")
    print(f"  With Batch API: ${daily['batch_api_projection_usd']:.2f}")
    print(f"  Monthly: ${daily['batch_api_monthly_projection']:.2f}")
    print(f"  Savings: ${daily['total_cost_usd'] - daily['batch_api_projection_usd']:.2f}/day")
    print("\n🤖 Breakdown by Agent:")
    for agent, stats in daily['agent_breakdown'].items():
        print(f"  {agent}: {stats['calls']} calls, {stats['input']:,}in/{stats['output']:,}out, ${stats['cost']:.4f}")

    print("\n📊 MONTHLY USAGE REPORT")
    print("=" * 80)
    monthly = get_monthly_usage()
    print(f"Month: {monthly['month']}")
    print(f"Total Calls: {monthly['total_calls']}")
    print(f"Total Tokens: {monthly['total_tokens']:,}")
    print(f"\n💰 COSTS (Realtime API)")
    print(f"  Total Cost: ${monthly['total_cost_usd']:.2f}")
    if monthly['cache_savings_usd'] > 0:
        print(f"  Cache Savings: ${monthly['cache_savings_usd']:.2f}")
    print(f"\n⚡ BATCH API PROJECTION (50% discount)")
    print(f"  With Batch API: ${monthly['batch_api_projection_usd']:.2f}")
    print(f"  Potential Monthly Savings: ${monthly['total_cost_usd'] - monthly['batch_api_projection_usd']:.2f}")
    print(f"  Cost Reduction: {monthly['cost_reduction_with_batch']}%")
    print("\n🤖 Breakdown by Agent:")
    for agent, stats in monthly['agent_breakdown'].items():
        print(f"  {agent}: {stats['calls']} calls, {stats['input']:,}in/{stats['output']:,}out, ${stats['cost']:.4f}")
