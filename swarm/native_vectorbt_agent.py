#!/usr/bin/env python3
"""
VectorBT Backtester Agent — 7th Member of VIF Council

Signal validation via historical portfolio simulation:
- Runs 6-month momentum backtest per ticker (RSI + SMA proxy for VIF rules)
- Computes Sharpe ratio, max drawdown, win rate, CAGR
- Flags signals with poor historical performance (Sharpe < 0.5 OR drawdown > 20%)
- 24-hour result cache (avoids redundant computation)
- Writes metrics to latent memory layer 32 for Critic + Risk agents
- 0 API tokens (fully local Numba-accelerated computation)

Execution order: AFTER Critic → BEFORE Swing Screener
"""

import logging
import json
import numpy as np
from pathlib import Path
from datetime import datetime, date
from typing import Dict, List, Optional, Any

from swarm.specialist_agent import SpecialistAgent

logger = logging.getLogger(__name__)

_REPO_ROOT = Path(__file__).parent.parent

# Backtest configuration
BACKTEST_CONFIG = {
    "period": "6mo",          # 6 months of history for meaningful signal validation
    "interval": "1d",
    "init_cash": 10_000,
    "fees": 0.001,            # 0.1% commission per trade
    "rsi_entry": 50,          # RSI < 50 = entry (oversold-ish, momentum building)
    "rsi_exit": 70,           # RSI > 70 = exit (overbought)
    "sma_fast": 20,
    "sma_slow": 50,
    "sharpe_threshold": 0.5,  # Below this = flag signal
    "drawdown_threshold": 0.20,  # Max drawdown > 20% = flag signal
    "min_trades": 2,           # Minimum trades for valid backtest
}

LATENT_MEMORY_LAYER = 32  # New layer, does not conflict with critic (8, 16, 24) or risk (8)


class NativeVectorBTAgent(SpecialistAgent):
    """
    7th Agent in VIF Council — Backtests VIF signals using vectorbt.

    Integration:
    - Runs after Critic, before Swing Screener
    - Reads post-critic signals from task_context
    - Writes Sharpe/drawdown/win_rate per ticker to latent memory layer 32
    - Flags underperforming signals for Risk Agent awareness
    - Cache: 24-hour TTL per ticker (date-keyed JSON)

    Token cost: 0 (all local Numba computation via vectorbt)
    """

    def __init__(self, agent_id: str = "vectorbt-backtester", kv_cache_binding=None):
        super().__init__(
            agent_id=agent_id,
            agent_type="vectorbt-backtester",
            role_description="Signal validation via 6-month historical backtest (Sharpe, drawdown, win rate)"
        )
        self.kv_cache_binding = kv_cache_binding
        self.latent_memory = None
        self.cache_path = _REPO_ROOT / "data" / "vectorbt_cache"
        self.cache_path.mkdir(parents=True, exist_ok=True)
        self.cache_today_path = self.cache_path / f"backtest_{date.today().isoformat()}.json"
        self._daily_cache: Dict = {}
        self._load_daily_cache()

    # ── Cache ─────────────────────────────────────────────────────────────────

    def _load_daily_cache(self):
        if self.cache_today_path.exists():
            try:
                self._daily_cache = json.loads(self.cache_today_path.read_text())
            except Exception:
                self._daily_cache = {}

    def _save_daily_cache(self):
        try:
            self.cache_today_path.write_text(json.dumps(self._daily_cache, indent=2))
        except Exception as e:
            self.logger.warning(f"Cache save failed: {e}")

    # ── Swarm Protocol ─────────────────────────────────────────────────────────

    def execute(self, subtasks=None, kv_cache_binding=None, latent_memory=None, task_context=None) -> Dict:
        """
        Swarm calling convention: execute(subtasks, kv_cache_binding, latent_memory, task_context).

        Extracts from task_context:
          - critic_signals: post-critic VIF signals dict {ticker: {signal, confidence, ...}}
          - vif_signals: fallback if critic_signals absent
        """
        task_context = task_context or {}
        if kv_cache_binding is not None:
            self.kv_cache_binding = kv_cache_binding
        if latent_memory is not None:
            self.latent_memory = latent_memory

        # Pull signals — prefer post-critic, fall back to raw VIF
        signals = (
            task_context.get("critic_signals")
            or task_context.get("vif_signals")
            or {}
        )

        start_time = datetime.now()
        self.logger.info(f"[{self.agent_id}] Starting backtest validation for {len(signals)} signals")

        if not signals:
            self.logger.warning(f"[{self.agent_id}] No signals to backtest — returning empty result")
            return self._empty_result(start_time)

        # Run backtests
        backtest_results = {}
        flagged_tickers = []
        cache_hits = 0

        for ticker, signal_data in signals.items():
            if ticker in self._daily_cache:
                backtest_results[ticker] = self._daily_cache[ticker]
                cache_hits += 1
                continue

            result = self._backtest_ticker(ticker, signal_data)
            backtest_results[ticker] = result
            self._daily_cache[ticker] = result

            if result.get("flagged"):
                flagged_tickers.append(ticker)

        self._save_daily_cache()

        # Write to latent memory layer 32
        hidden_states = self._encode_hidden_states(backtest_results, signals)
        if self.latent_memory:
            self.latent_memory.write_hidden_states(self.agent_id, hidden_states)

        # Write to KV cache for Risk Agent
        if self.kv_cache_binding:
            self.kv_cache_binding.put(
                layer=LATENT_MEMORY_LAYER,
                value={"backtest_results": backtest_results, "flagged": flagged_tickers},
                key=f"signals_{self.agent_id}",
                shared=True,
            )

        execution_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        passed = len(signals) - len(flagged_tickers)

        self.logger.info(
            f"[{self.agent_id}] Complete: {passed}/{len(signals)} passed, "
            f"{len(flagged_tickers)} flagged, {cache_hits} cache hits, "
            f"{execution_time_ms}ms, 0 tokens"
        )

        return {
            "agent_id": self.agent_id,
            "timestamp": datetime.now().isoformat(),
            "signals_validated": len(signals),
            "signals_passed": passed,
            "signals_flagged": len(flagged_tickers),
            "flagged_tickers": flagged_tickers,
            "backtest_results": backtest_results,
            "hidden_states": hidden_states,
            "execution_time_ms": execution_time_ms,
            "cache_hits": cache_hits,
            "token_cost": 0,
        }

    # ── Core Backtest ──────────────────────────────────────────────────────────

    def _backtest_ticker(self, ticker: str, signal_data: Dict) -> Dict:
        """
        Run 6-month momentum backtest for a single ticker.
        Uses RSI + SMA crossover as VIF signal proxy.
        """
        try:
            return self._run_vectorbt(ticker, signal_data)
        except ImportError:
            self.logger.debug(f"vectorbt not installed — using pandas fallback for {ticker}")
            return self._run_pandas_fallback(ticker, signal_data)
        except Exception as e:
            self.logger.warning(f"Backtest failed for {ticker}: {e}")
            return self._error_result(ticker, str(e))

    def _run_vectorbt(self, ticker: str, signal_data: Dict) -> Dict:
        """
        Full vectorbt backtest — Numba-accelerated.
        Uses pandas for indicator computation (avoids vbt indicator API version drift),
        passes boolean signals + stop-loss/take-profit into Portfolio.from_signals().
        """
        import vectorbt as vbt
        import yfinance as yf
        import pandas as pd

        data = yf.download(
            ticker,
            period=BACKTEST_CONFIG["period"],
            interval=BACKTEST_CONFIG["interval"],
            progress=False,
            auto_adjust=True,
        )

        if data.empty or len(data) < 30:
            return self._insufficient_data_result(ticker)

        close = data["Close"].squeeze()

        # Compute indicators via pandas (avoids vbt indicator API version drift between v0.2x and v1.0)
        delta = close.diff()
        gain = delta.clip(lower=0).rolling(14).mean()
        loss = (-delta.clip(upper=0)).rolling(14).mean()
        rsi = 100 - (100 / (1 + gain / loss.replace(0, np.nan)))
        sma_fast = close.rolling(BACKTEST_CONFIG["sma_fast"]).mean()
        sma_slow = close.rolling(BACKTEST_CONFIG["sma_slow"]).mean()

        # Entry: RSI below threshold AND fast SMA above slow SMA
        entries = (rsi < BACKTEST_CONFIG["rsi_entry"]) & (sma_fast > sma_slow)
        # Exit: RSI overbought OR momentum cross-under
        exits = (rsi > BACKTEST_CONFIG["rsi_exit"]) | (sma_fast < sma_slow)

        # Drop NaN rows (indicator warmup period)
        valid_idx = entries.dropna().index
        close_v = close.loc[valid_idx]
        entries_v = entries.loc[valid_idx].fillna(False)
        exits_v = exits.loc[valid_idx].fillna(False)

        portfolio = vbt.Portfolio.from_signals(
            close=close_v,
            entries=entries_v,
            exits=exits_v,
            init_cash=BACKTEST_CONFIG["init_cash"],
            fees=BACKTEST_CONFIG["fees"],
            sl_stop=0.07,    # 7% trailing stop-loss (aligned with Risk Agent circuit breaker)
            freq="1D",
        )

        # Use pf.stats() for full metrics suite (v1.0 recommended approach)
        try:
            stats = portfolio.stats()
            total_return = float(stats.get("Total Return [%]", 0)) / 100
            sharpe = float(stats.get("Sharpe Ratio", 0))
            max_dd = float(stats.get("Max Drawdown [%]", 0)) / -100
            win_rate = float(stats.get("Win Rate [%]", 50)) / 100
            n_trades = int(stats.get("Total Trades", 0))
        except Exception:
            # Fallback to individual method calls
            total_return = float(portfolio.total_return())
            sharpe = float(portfolio.sharpe_ratio())
            max_dd = float(portfolio.max_drawdown())
            trades = portfolio.trades
            n_trades = len(trades.records) if hasattr(trades, "records") else 0
            win_rate = float(trades.win_rate()) if n_trades > 0 else 0.5

        if n_trades < BACKTEST_CONFIG["min_trades"]:
            return self._insufficient_trades_result(ticker, n_trades)

        flagged = (
            sharpe < BACKTEST_CONFIG["sharpe_threshold"]
            or abs(max_dd) > BACKTEST_CONFIG["drawdown_threshold"]
        )

        return {
            "ticker": ticker,
            "status": "completed",
            "engine": "vectorbt_v1",
            "period": BACKTEST_CONFIG["period"],
            "n_trades": n_trades,
            "total_return": round(total_return, 4),
            "sharpe_ratio": round(sharpe, 3),
            "max_drawdown": round(max_dd, 4),
            "win_rate": round(win_rate, 3),
            "flagged": flagged,
            "flag_reason": self._flag_reason(sharpe, max_dd) if flagged else None,
            "vif_signal": signal_data.get("signal"),
            "vif_confidence": signal_data.get("confidence"),
            "timestamp": datetime.now().isoformat(),
        }

    def _run_pandas_fallback(self, ticker: str, signal_data: Dict) -> Dict:
        """
        Pandas-only fallback when vectorbt not installed.
        Computes simplified momentum metrics (buy-and-hold + RSI cross).
        """
        import yfinance as yf
        import pandas as pd

        data = yf.download(
            ticker,
            period=BACKTEST_CONFIG["period"],
            interval=BACKTEST_CONFIG["interval"],
            progress=False,
            auto_adjust=True,
        )

        if data.empty or len(data) < 20:
            return self._insufficient_data_result(ticker)

        close = data["Close"].squeeze()

        # Simple buy-and-hold return for the period
        total_return = float((close.iloc[-1] - close.iloc[0]) / close.iloc[0])

        # Rolling RSI (pandas)
        delta = close.diff()
        gain = delta.clip(lower=0).rolling(14).mean()
        loss = (-delta.clip(upper=0)).rolling(14).mean()
        rs = gain / loss.replace(0, np.nan)
        rsi = 100 - (100 / (1 + rs))

        # SMA crossover
        sma_fast = close.rolling(BACKTEST_CONFIG["sma_fast"]).mean()
        sma_slow = close.rolling(BACKTEST_CONFIG["sma_slow"]).mean()
        entries = (rsi < BACKTEST_CONFIG["rsi_entry"]) & (sma_fast > sma_slow)

        # Count signal occurrences as proxy for n_trades
        n_trades = int(entries.sum())

        # Rolling max drawdown
        roll_max = close.cummax()
        drawdown = (close - roll_max) / roll_max
        max_dd = float(drawdown.min())

        # Approximate Sharpe (annualized daily returns)
        daily_returns = close.pct_change().dropna()
        sharpe = float((daily_returns.mean() / daily_returns.std()) * np.sqrt(252)) if daily_returns.std() > 0 else 0.0

        win_rate = 0.5  # Cannot compute accurately without full trade sim

        flagged = (
            sharpe < BACKTEST_CONFIG["sharpe_threshold"]
            or abs(max_dd) > BACKTEST_CONFIG["drawdown_threshold"]
        )

        return {
            "ticker": ticker,
            "status": "completed",
            "engine": "pandas_fallback",
            "period": BACKTEST_CONFIG["period"],
            "n_trades": n_trades,
            "total_return": round(total_return, 4),
            "sharpe_ratio": round(sharpe, 3),
            "max_drawdown": round(max_dd, 4),
            "win_rate": round(win_rate, 3),
            "flagged": flagged,
            "flag_reason": self._flag_reason(sharpe, max_dd) if flagged else None,
            "vif_signal": signal_data.get("signal"),
            "vif_confidence": signal_data.get("confidence"),
            "timestamp": datetime.now().isoformat(),
        }

    # ── Hidden State Encoding ──────────────────────────────────────────────────

    def _encode_hidden_states(self, backtest_results: Dict, signals: Dict) -> Dict:
        """
        Layer 32: Backtest quality signal for downstream agents.

        h32[0]: avg_sharpe (normalized 0-1, clipped at 2.0)
        h32[1]: avg_max_drawdown (absolute)
        h32[2]: flagged_fraction
        h32[3]: avg_win_rate
        """
        completed = [r for r in backtest_results.values() if r.get("status") == "completed"]
        if not completed:
            return {LATENT_MEMORY_LAYER: np.zeros(4, dtype=np.float32)}

        avg_sharpe = np.mean([r.get("sharpe_ratio", 0) for r in completed])
        avg_drawdown = np.mean([abs(r.get("max_drawdown", 0)) for r in completed])
        flagged_frac = sum(1 for r in completed if r.get("flagged")) / len(completed)
        avg_win_rate = np.mean([r.get("win_rate", 0.5) for r in completed])

        h32 = np.array([
            min(avg_sharpe / 2.0, 1.0),   # normalize Sharpe to 0-1 (cap at 2.0)
            avg_drawdown,
            flagged_frac,
            avg_win_rate,
        ], dtype=np.float32)

        return {LATENT_MEMORY_LAYER: h32}

    # ── Helpers ────────────────────────────────────────────────────────────────

    def _flag_reason(self, sharpe: float, max_dd: float) -> str:
        reasons = []
        if sharpe < BACKTEST_CONFIG["sharpe_threshold"]:
            reasons.append(f"Sharpe {sharpe:.2f} < {BACKTEST_CONFIG['sharpe_threshold']}")
        if abs(max_dd) > BACKTEST_CONFIG["drawdown_threshold"]:
            reasons.append(f"MaxDD {abs(max_dd):.1%} > {BACKTEST_CONFIG['drawdown_threshold']:.0%}")
        return " | ".join(reasons)

    def _insufficient_data_result(self, ticker: str) -> Dict:
        return {
            "ticker": ticker, "status": "insufficient_data",
            "engine": "skipped", "flagged": False,
            "flag_reason": "Not enough price history",
            "timestamp": datetime.now().isoformat(),
        }

    def _insufficient_trades_result(self, ticker: str, n_trades: int) -> Dict:
        return {
            "ticker": ticker, "status": "insufficient_trades",
            "engine": "skipped", "n_trades": n_trades, "flagged": False,
            "flag_reason": f"Only {n_trades} trades in 6mo (min {BACKTEST_CONFIG['min_trades']})",
            "timestamp": datetime.now().isoformat(),
        }

    def _error_result(self, ticker: str, error: str) -> Dict:
        return {
            "ticker": ticker, "status": "error",
            "engine": "failed", "flagged": False,
            "flag_reason": error[:120],
            "timestamp": datetime.now().isoformat(),
        }

    def _empty_result(self, start_time: datetime) -> Dict:
        ms = int((datetime.now() - start_time).total_seconds() * 1000)
        return {
            "agent_id": self.agent_id,
            "timestamp": datetime.now().isoformat(),
            "signals_validated": 0,
            "signals_passed": 0,
            "signals_flagged": 0,
            "flagged_tickers": [],
            "backtest_results": {},
            "hidden_states": {LATENT_MEMORY_LAYER: np.zeros(4, dtype=np.float32)},
            "execution_time_ms": ms,
            "cache_hits": 0,
            "token_cost": 0,
        }


# ── Singleton + convenience ────────────────────────────────────────────────────

_vectorbt_agent = NativeVectorBTAgent()


def run_signal_backtest(signals: Optional[Dict] = None) -> Dict:
    """
    Convenience function for direct calls outside the swarm.

    Usage:
        from swarm.native_vectorbt_agent import run_signal_backtest
        result = run_signal_backtest(signals={"NVDA": {"signal": "BUY", "confidence": 78}})
    """
    return _vectorbt_agent.execute(
        subtasks=[],
        kv_cache_binding=None,
        latent_memory=None,
        task_context={"vif_signals": signals or {}},
    )
