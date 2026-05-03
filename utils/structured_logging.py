#!/usr/bin/env python3
"""
Structured logging setup for VIF Trading System.
Provides consistent logging with metrics tracking across all agents.
"""

import logging
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, Optional

# Create logs directory if it doesn't exist
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)


class StructuredFormatter(logging.Formatter):
    """Structured logging formatter that outputs JSON for critical events."""

    def __init__(self, agent_name: str, include_json: bool = False):
        super().__init__()
        self.agent_name = agent_name
        self.include_json = include_json

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with structured data."""
        timestamp = datetime.fromtimestamp(record.created).isoformat()

        # Extract custom fields from record
        custom_fields = {
            k: v for k, v in record.__dict__.items()
            if k.startswith('metric_') or k.startswith('event_')
        }

        # Build base log message
        base_msg = f"[{timestamp}] [{self.agent_name}] [{record.levelname}] {record.getMessage()}"

        if custom_fields and self.include_json:
            custom_fields['timestamp'] = timestamp
            custom_fields['agent'] = self.agent_name
            custom_fields['level'] = record.levelname
            custom_fields['message'] = record.getMessage()
            return json.dumps(custom_fields)

        if custom_fields:
            custom_str = " | ".join([f"{k}={v}" for k, v in custom_fields.items()])
            return f"{base_msg} | {custom_str}"

        return base_msg


def setup_logger(agent_name: str, level: int = logging.INFO, include_json: bool = False) -> logging.Logger:
    """
    Set up a structured logger for an agent.

    Args:
        agent_name: Name of the agent (used for file naming and tagging)
        level: Logging level
        include_json: Output JSON format for critical events

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(agent_name)
    logger.setLevel(level)
    logger.handlers.clear()  # Remove existing handlers

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_formatter = StructuredFormatter(agent_name, include_json=False)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler (one per agent)
    log_file = LOGS_DIR / f"{agent_name}.log"
    file_handler = logging.FileHandler(log_file, mode='a')
    file_handler.setLevel(level)
    file_formatter = StructuredFormatter(agent_name, include_json=include_json)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    return logger


class MetricsLogger:
    """Helper class for logging metrics as structured data."""

    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def log_api_call(
        self,
        operation: str,
        input_tokens: int,
        output_tokens: int,
        latency_ms: float,
        success: bool = True,
        error: Optional[str] = None,
        **kwargs
    ):
        """Log API call metrics."""
        total_tokens = input_tokens + output_tokens
        level = logging.INFO if success else logging.ERROR

        extra = {
            'metric_operation': operation,
            'metric_input_tokens': input_tokens,
            'metric_output_tokens': output_tokens,
            'metric_total_tokens': total_tokens,
            'metric_latency_ms': latency_ms,
            'metric_success': success,
            **{f'metric_{k}': v for k, v in kwargs.items()}
        }

        msg = f"API_CALL | {operation} | {total_tokens:,} tokens | {latency_ms:.0f}ms"
        if error:
            extra['metric_error'] = error
            msg += f" | ERROR: {error}"

        self.logger.log(level, msg, extra=extra)

    def log_cache_hit(self, ticker: str, cache_age_hours: float, key: str = ""):
        """Log cache hit."""
        extra = {
            'event_type': 'cache_hit',
            'event_ticker': ticker,
            'metric_cache_age_hours': cache_age_hours,
            'event_cache_key': key
        }
        self.logger.info(f"CACHE_HIT | {ticker} | age={cache_age_hours:.1f}h", extra=extra)

    def log_data_fetch(self, ticker: str, period: str, source: str, success: bool, **kwargs):
        """Log data fetch operation."""
        level = logging.INFO if success else logging.WARNING
        extra = {
            'event_type': 'data_fetch',
            'metric_ticker': ticker,
            'metric_period': period,
            'metric_source': source,
            'metric_success': success,
            **{f'metric_{k}': v for k, v in kwargs.items()}
        }
        self.logger.log(level, f"DATA_FETCH | {ticker} | {period} | {source}", extra=extra)

    def log_signal_generated(
        self,
        ticker: str,
        signal: str,
        confidence: float,
        kill_switches_active: list,
        **kwargs
    ):
        """Log generated trading signal."""
        extra = {
            'event_type': 'signal_generated',
            'metric_ticker': ticker,
            'metric_signal': signal,
            'metric_confidence': confidence,
            'metric_kill_switches': len(kill_switches_active),
            **{f'metric_{k}': v for k, v in kwargs.items()}
        }
        msg = f"SIGNAL | {ticker} | {signal} | confidence={confidence:.2f} | KillSwitches={len(kill_switches_active)}"
        self.logger.info(msg, extra=extra)

    def log_batch_completion(
        self,
        batch_id: str,
        ticker_count: int,
        total_tokens: int,
        success_count: int,
        error_count: int,
        duration_sec: float
    ):
        """Log batch processing completion."""
        extra = {
            'event_type': 'batch_complete',
            'metric_batch_id': batch_id,
            'metric_tickers': ticker_count,
            'metric_total_tokens': total_tokens,
            'metric_success': success_count,
            'metric_errors': error_count,
            'metric_duration_sec': duration_sec,
            'metric_tokens_per_ticker': total_tokens // max(ticker_count, 1)
        }
        msg = (
            f"BATCH_COMPLETE | {batch_id} | {ticker_count} tickers | "
            f"{total_tokens:,} tokens | {success_count}✓ {error_count}✗ | {duration_sec:.1f}s"
        )
        self.logger.info(msg, extra=extra)


# Example usage
if __name__ == '__main__':
    # Set up logger for an agent
    logger = setup_logger("test_agent", level=logging.INFO)
    metrics = MetricsLogger(logger)

    # Log some sample events
    metrics.log_api_call("vif_analysis", 1200, 450, 2300, batch_size=15)
    metrics.log_cache_hit("NVDA", 2.3, key="NVDA_5d")
    metrics.log_data_fetch("AAPL", "1mo", "yfinance", True, rows=252)
    metrics.log_signal_generated("MSFT", "BUY", 0.85, ["K2_FLAGGED"], reason="bullish_breakout")
    metrics.log_batch_completion("batch_001", 15, 18000, 14, 1, 45.2)

    print(f"\nLogs written to: {LOGS_DIR / 'test_agent.log'}")
