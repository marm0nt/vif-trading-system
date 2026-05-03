#!/usr/bin/env python3
"""Token-level cost tracking for Claude API calls."""

import json
from datetime import datetime, timedelta
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

COST_LOG = Path("logs/cost_tracker.jsonl")
COST_LOG.parent.mkdir(exist_ok=True)

# Claude token pricing (as of May 2026)
PRICING = {
    "claude-haiku-4-5": {
        "input": 0.80 / 1_000_000,          # $0.80 per million tokens
        "output": 4.00 / 1_000_000,         # $4.00 per million tokens
        "cache_creation": 2.40 / 1_000_000, # 3x cache creation cost
        "cache_read": 0.08 / 1_000_000      # 90% discount on reads
    },
    "claude-sonnet-4-6": {
        "input": 3.00 / 1_000_000,
        "output": 15.00 / 1_000_000,
        "cache_creation": 9.00 / 1_000_000,
        "cache_read": 0.30 / 1_000_000
    },
    "claude-opus-4-7": {
        "input": 15.00 / 1_000_000,
        "output": 75.00 / 1_000_000,
        "cache_creation": 45.00 / 1_000_000,
        "cache_read": 1.50 / 1_000_000
    }
}


def get_model_cost(model):
    """Get pricing for a model."""
    return PRICING.get(model, PRICING["claude-sonnet-4-6"])


def calculate_cost(usage, model):
    """Calculate cost from usage object."""
    pricing = get_model_cost(model)

    input_tokens = getattr(usage, 'input_tokens', 0)
    output_tokens = getattr(usage, 'output_tokens', 0)
    cache_creation = getattr(usage, 'cache_creation_input_tokens', 0)
    cache_read = getattr(usage, 'cache_read_input_tokens', 0)

    cost = 0
    cost += input_tokens * pricing["input"]
    cost += output_tokens * pricing["output"]
    cost += cache_creation * pricing["cache_creation"]
    cost += cache_read * pricing["cache_read"]

    return cost


def log_api_call(usage, model, agent_name="unknown", batch_id=None):
    """Log an API call with token counts and cost."""
    try:
        cost = calculate_cost(usage, model)

        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "model": model,
            "agent": agent_name,
            "batch_id": batch_id,
            "input_tokens": getattr(usage, 'input_tokens', 0),
            "output_tokens": getattr(usage, 'output_tokens', 0),
            "cache_creation_tokens": getattr(usage, 'cache_creation_input_tokens', 0),
            "cache_read_tokens": getattr(usage, 'cache_read_input_tokens', 0),
            "cost_usd": round(cost, 6)
        }

        with open(COST_LOG, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')

        logger.debug(f"Cost logged: ${cost:.4f} ({model})")
        return cost

    except Exception as e:
        logger.warning(f"Could not log cost: {e}")
        return 0


def get_daily_cost(date_str=None):
    """Sum costs for a specific day (default today)."""
    if date_str is None:
        date_str = datetime.utcnow().strftime("%Y-%m-%d")

    total_cost = 0
    try:
        with open(COST_LOG, 'r') as f:
            for line in f:
                entry = json.loads(line)
                if entry["timestamp"].startswith(date_str):
                    total_cost += entry.get("cost_usd", 0)
    except FileNotFoundError:
        pass

    return total_cost


def get_monthly_projection(lookback_days=7):
    """Project monthly cost from last N days average."""
    try:
        daily_costs = {}
        with open(COST_LOG, 'r') as f:
            for line in f:
                entry = json.loads(line)
                date = entry["timestamp"][:10]  # YYYY-MM-DD
                daily_costs[date] = daily_costs.get(date, 0) + entry.get("cost_usd", 0)

        # Get last N days
        today = datetime.utcnow().strftime("%Y-%m-%d")
        dates = sorted(daily_costs.keys())[-lookback_days:]

        if not dates:
            return 0

        avg_daily = sum(daily_costs[d] for d in dates) / len(dates)
        return avg_daily * 30

    except Exception as e:
        logger.warning(f"Could not calculate projection: {e}")
        return 0


def get_model_breakdown(lookback_days=7):
    """Get cost breakdown by model."""
    breakdown = {}
    try:
        cutoff_date = (datetime.utcnow() - timedelta(days=lookback_days)).isoformat()
        with open(COST_LOG, 'r') as f:
            for line in f:
                entry = json.loads(line)
                if entry["timestamp"] >= cutoff_date:
                    model = entry["model"]
                    if model not in breakdown:
                        breakdown[model] = {"cost": 0, "calls": 0, "tokens": 0}
                    breakdown[model]["cost"] += entry.get("cost_usd", 0)
                    breakdown[model]["calls"] += 1
                    breakdown[model]["tokens"] += (
                        entry.get("input_tokens", 0) +
                        entry.get("output_tokens", 0)
                    )

        for model in breakdown:
            breakdown[model]["cost"] = round(breakdown[model]["cost"], 4)

    except Exception as e:
        logger.warning(f"Could not calculate breakdown: {e}")

    return breakdown


if __name__ == "__main__":
    # Demo
    print(f"Today's cost: ${get_daily_cost():.4f}")
    print(f"Monthly projection: ${get_monthly_projection():.2f}")
    print(f"Model breakdown (7 days):\n{json.dumps(get_model_breakdown(), indent=2)}")
