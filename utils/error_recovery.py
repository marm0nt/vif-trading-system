#!/usr/bin/env python3
"""
Error recovery and fallback logic for VIF Trading System.
Handles API failures, timeouts, and cache misses with intelligent retry strategies.
"""

import logging
import time
import json
from pathlib import Path
from typing import Optional, Callable, Any, TypeVar
from functools import wraps
import anthropic

logger = logging.getLogger(__name__)

T = TypeVar('T')


class APIError(Exception):
    """Custom exception for API errors."""
    pass


def retry_with_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 30.0,
    backoff_factor: float = 2.0,
    retryable_errors: tuple = (anthropic.APIError, anthropic.APIConnectionError, TimeoutError)
):
    """
    Retry decorator with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Starting delay in seconds
        max_delay: Maximum delay in seconds
        backoff_factor: Multiplier for each retry
        retryable_errors: Tuple of exception types to retry on
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            delay = initial_delay
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except retryable_errors as e:
                    last_exception = e
                    if attempt >= max_retries:
                        logger.error(f"Max retries exceeded for {func.__name__}: {e}")
                        raise

                    logger.warning(
                        f"Attempt {attempt + 1}/{max_retries + 1} failed for {func.__name__}. "
                        f"Retrying in {delay}s... Error: {e}"
                    )
                    time.sleep(delay)
                    delay = min(delay * backoff_factor, max_delay)

            raise last_exception or APIError(f"Failed after {max_retries + 1} attempts")

        return wrapper
    return decorator


def fallback_to_cache(cache_dir: Path = Path("data/fallback_cache")):
    """
    Fallback decorator that attempts to use cached response if API call fails.

    Args:
        cache_dir: Directory to store fallback cache
    """
    cache_dir.mkdir(parents=True, exist_ok=True)

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            cache_key = f"{func.__name__}_{hash(str(args) + str(kwargs))}.json"
            cache_path = cache_dir / cache_key

            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.warning(f"API call failed in {func.__name__}, attempting fallback cache...")

                if cache_path.exists():
                    try:
                        with open(cache_path, 'r') as f:
                            cached = json.load(f)
                        logger.info(f"Using cached fallback for {func.__name__}")
                        return cached
                    except Exception as cache_err:
                        logger.error(f"Failed to load cache: {cache_err}")

                logger.error(f"No fallback cache available for {func.__name__}")
                raise APIError(f"API call failed and no cache available: {e}") from e

        return wrapper
    return decorator


def cache_response(cache_dir: Path = Path("data/response_cache"), ttl_hours: int = 24):
    """
    Cache decorator that stores successful API responses.

    Args:
        cache_dir: Directory to store cache
        ttl_hours: Cache time-to-live in hours
    """
    import os
    cache_dir.mkdir(parents=True, exist_ok=True)

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            cache_key = f"{func.__name__}_{hash(str(args) + str(kwargs))}.json"
            cache_path = cache_dir / cache_key

            # Check if cache exists and is fresh
            if cache_path.exists():
                mod_time = os.path.getmtime(cache_path)
                age_hours = (time.time() - mod_time) / 3600

                if age_hours < ttl_hours:
                    try:
                        with open(cache_path, 'r') as f:
                            cached = json.load(f)
                        logger.debug(f"Cache hit for {func.__name__} (age: {age_hours:.1f}h)")
                        return cached
                    except Exception as e:
                        logger.warning(f"Failed to load cache: {e}")

            # Call function and cache result
            result = func(*args, **kwargs)
            try:
                with open(cache_path, 'w') as f:
                    json.dump(result, f)
            except Exception as e:
                logger.warning(f"Failed to cache result: {e}")

            return result

        return wrapper
    return decorator


class CircuitBreaker:
    """
    Circuit breaker pattern for API calls.
    Opens circuit after N failures to prevent cascading failures.
    """

    def __init__(self, failure_threshold: int = 5, timeout: int = 300):
        """
        Args:
            failure_threshold: Number of failures before opening circuit
            timeout: Seconds before attempting recovery (half-open state)
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    def call(self, func: Callable[..., T], *args, **kwargs) -> T:
        """Execute function through circuit breaker."""
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "HALF_OPEN"
                logger.warning("Circuit breaker entering HALF_OPEN state")
            else:
                raise APIError("Circuit breaker is OPEN - too many recent failures")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise

    def _on_success(self):
        """Reset on successful call."""
        if self.state == "HALF_OPEN":
            logger.info("Circuit breaker CLOSED - recovery successful")
            self.state = "CLOSED"
        self.failure_count = 0

    def _on_failure(self):
        """Track failure."""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            logger.error(f"Circuit breaker OPEN after {self.failure_count} failures")


class FallbackDataGenerator:
    """Generate fallback mock data when API is unavailable."""

    @staticmethod
    def generate_mock_vif_analysis(ticker: str, signal: str = "HOLD") -> dict:
        """Generate mock VIF analysis output."""
        return {
            "ticker": ticker,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "signal": signal,
            "confidence": 0.5,
            "gamma_regime": "neutral",
            "kill_switches_active": ["API_UNAVAILABLE"],
            "note": "Fallback data - API unavailable, using last cached analysis"
        }

    @staticmethod
    def generate_mock_catalyst(ticker: str) -> dict:
        """Generate mock catalyst data."""
        return {
            "ticker": ticker,
            "catalysts": [],
            "next_earnings": "Unknown",
            "macro_themes": [],
            "note": "Fallback data - API unavailable"
        }


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    # Example circuit breaker usage
    breaker = CircuitBreaker(failure_threshold=3)

    def flaky_api_call():
        import random
        if random.random() < 0.7:
            raise anthropic.APIError("Simulated error")
        return {"data": "success"}

    for i in range(5):
        try:
            result = breaker.call(flaky_api_call)
            print(f"Call {i + 1}: {result}")
        except APIError as e:
            print(f"Call {i + 1}: {e}")
        time.sleep(1)
