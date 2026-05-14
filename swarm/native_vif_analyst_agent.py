#!/usr/bin/env python3
"""
Native VIF Analyst Agent - In-Process Implementation

Runs VIF framework analysis (Volatility Imbalance Framework v4.0).
Reads K4 tickers from catalyst monitor's LoRA cache, applies latent context adjustments.
Caches market data to shared KV cache (layer 1) for swing screener reuse.
Writes numpy hidden states (layers 8, 16, 24) to latent memory.

No subprocess calls. Direct import + execution within parent process.
"""

import sys
import logging
import json
from pathlib import Path
from datetime import datetime
import numpy as np

from swarm.specialist_agent import SpecialistAgent

logger = logging.getLogger(__name__)

_REPO_ROOT = Path(__file__).parent.parent

# Non-equity tickers that yfinance cannot fetch (crypto, indices, futures)
# Reuse same exclusion pattern as _PatchedSwingScreener
_NON_EQUITY_EXCLUDE = {
    'BTCUSDT', 'BTCUSDT.P', 'VIX', 'VX1!', 'VX2!',
    '3081', 'IQE', 'SIVE', 'IQEPF', 'SIVEF', 'SLOIF',
    'AYARZZX',
}


class NativeVIFAnalystAgent(SpecialistAgent):
    """
    Native VIF analyst — applies Volatility Imbalance Framework to generate signals.

    Execution order: SECOND (reads K4 from catalyst monitor).
    Latent context: Reads K4 tickers from catalyst's LoRA cache (layer 2), applies override logic.
    KV cache output: Caches market data (layer 1) for swing screener.
    Hidden state output: layer 8 (signal distribution), layer 16 (confidence stats), layer 24 (ticker intensity).
    """

    def __init__(self, agent_id: str = "vif-analyst-1"):
        super().__init__(
            agent_id=agent_id,
            agent_type="vif-analyst",
            role_description="VIF framework signal generator for institutional watchlists"
        )
        self.logger = logging.getLogger(__name__)

    def _execute_subtasks(self, subtasks: list, latent_context: dict) -> dict:
        """
        Execute VIF analysis across all watchlists.

        Steps:
        1. Parse all watchlist files
        2. Fetch market data (yfinance + indicators)
        3. Cache market data to KV layer 1 (for swing screener)
        4. Analyze via VIF framework (Claude API)
        5. Read K4 tickers from catalyst's LoRA cache
        6. Apply latent context adjustments (K4 override logic)
        7. Encode hidden states as numpy arrays
        8. Write hidden states to latent memory

        Returns:
            {
                "signals": {ticker: {signal, confidence, kill_switch, ...}},
                "metrics": {analysis_date, tickers_analyzed, ...},
                "hidden_states": {8: array, 16: array, 24: array}
            }
        """
        try:
            # Import VIF pipeline functions
            from agents.watchlist_watcher import (
                parse_watchlist,
                fetch_market_data,
                analyze_with_vif,
            )

            self.logger.info(f"{self.agent_id}: Starting VIF analysis")

            # Resolve all watchlist files
            watchlist_dir = _REPO_ROOT / "watchlists"
            watchlist_files = list(watchlist_dir.glob("*.txt"))
            self.logger.info(f"{self.agent_id}: Found {len(watchlist_files)} watchlist files")

            all_signals = {}
            all_market_data = {}

            for wl_file in watchlist_files:
                watchlist_name = wl_file.stem
                self.logger.info(f"{self.agent_id}: Parsing {watchlist_name}")

                # Parse watchlist
                tickers = parse_watchlist(str(wl_file))
                if not tickers:
                    self.logger.warning(f"{self.agent_id}: No tickers in {watchlist_name}")
                    continue

                # Filter out non-equity tickers (crypto, indices, futures)
                valid_tickers = [
                    t for t in tickers
                    if t.strip().split(":")[-1].strip() not in _NON_EQUITY_EXCLUDE
                ]
                if len(valid_tickers) < len(tickers):
                    self.logger.info(f"{self.agent_id}: Filtered {len(tickers) - len(valid_tickers)} non-equity tickers from {watchlist_name}")
                tickers = valid_tickers
                if not tickers:
                    self.logger.warning(f"{self.agent_id}: No valid equity tickers in {watchlist_name} after filter")
                    continue

                # Get market data with KV cache check
                market_data = self._get_or_fetch_market_data(tickers, period="1mo")
                self.logger.info(f"{self.agent_id}: Fetched market data for {len(market_data)} tickers from {watchlist_name}")

                # Cache to KV layer 1 (shared for swing screener)
                if self.kv_cache_binding:
                    for ticker, mkt_data in market_data.items():
                        self.kv_cache_binding.put(
                            layer=1,
                            value=mkt_data,
                            key=ticker,
                            shared=True  # Shared backbone cache
                        )
                    self.logger.info(f"{self.agent_id}: Cached {len(market_data)} tickers to KV layer 1")

                all_market_data.update(market_data)

                # Analyze with VIF framework
                self.logger.info(f"{self.agent_id}: Running VIF analysis for {watchlist_name}")
                vif_result = analyze_with_vif(market_data, watchlist_name)

                # Extract signals
                if isinstance(vif_result, dict) and "signals" in vif_result:
                    all_signals.update(vif_result["signals"])

            self.logger.info(f"{self.agent_id}: VIF analysis complete, {len(all_signals)} signals generated")

            # Enrich signals with ATM options Greeks + IV% (0 API tokens, 24h cached)
            all_signals = self._enrich_with_greeks(all_signals, all_market_data)

            # Apply latent context adjustments (K4 override from catalyst monitor)
            all_signals = self._apply_latent_context_adjustments(all_signals, latent_context)

            # Encode hidden states
            hidden_states = self._encode_hidden_states(all_signals)

            # Write hidden states to latent memory
            if self.latent_memory:
                self.latent_memory.write_hidden_states(
                    self.agent_id,
                    hidden_states
                )
                self.logger.info(f"{self.agent_id}: Wrote hidden states to latent memory")

            # Count signal types
            buy_count = sum(1 for s in all_signals.values() if s.get("signal") == "BUY")
            sell_count = sum(1 for s in all_signals.values() if s.get("signal") == "SELL")
            hold_count = sum(1 for s in all_signals.values() if s.get("signal") == "HOLD")

            metrics = {
                "analysis_date": datetime.utcnow().isoformat(),
                "tickers_analyzed": len(all_signals),
                "buy_signals": buy_count,
                "sell_signals": sell_count,
                "hold_signals": hold_count,
            }

            self.logger.info(f"{self.agent_id}: VIF complete — {buy_count} BUY, {sell_count} SELL, {hold_count} HOLD")

            return {
                "signals": all_signals,
                "metrics": metrics,
                "hidden_states": hidden_states,
            }

        except Exception as e:
            self.logger.error(f"{self.agent_id}: Execution failed: {e}", exc_info=True)
            return {
                "signals": {},
                "metrics": {"error": str(e)},
                "hidden_states": {},
            }

    def _get_or_fetch_market_data(self, tickers: list, period: str) -> dict:
        """
        Fetch market data with KV cache check per ticker.

        If cached in layer 1, reuse. Otherwise fetch from yfinance + indicators.
        Strips exchange prefix (e.g., NASDAQ:NVDA → NVDA) before yfinance call.
        """
        try:
            from agents.indicators import fetch_and_compute
        except ImportError:
            self.logger.error(f"{self.agent_id}: Failed to import indicators module")
            return {}

        market_data = {}

        for ticker in tickers:
            # Strip exchange prefix for yfinance (NASDAQ:NVDA → NVDA)
            ticker_clean = ticker.split(':')[-1] if ':' in ticker else ticker

            # Check KV cache first (use original ticker as key for cache consistency)
            cached = None
            if self.kv_cache_binding:
                cached = self.kv_cache_binding.get(layer=1, key=ticker)

            if cached is not None:
                self.logger.debug(f"{self.agent_id}: KV cache hit for {ticker}")
                market_data[ticker] = cached
            else:
                # Fetch and compute (use clean ticker for yfinance)
                self.logger.debug(f"{self.agent_id}: Fetching {ticker_clean} from yfinance")
                fetched = fetch_and_compute(ticker_clean, period)
                if fetched:
                    market_data[ticker] = fetched

        return market_data

    def _enrich_with_greeks(self, signals: dict, market_data: dict) -> dict:
        """
        Attach ATM options Greeks + IV% to each signal. Best-effort — skips on failure.
        Uses compute_options_greeks() (Black-Scholes + yfinance, 24h cached, 0 API tokens).
        """
        try:
            from agents.indicators import compute_options_greeks
        except ImportError:
            return signals

        for ticker, signal_data in signals.items():
            ticker_clean = ticker.split(":")[-1] if ":" in ticker else ticker
            price = market_data.get(ticker, {}).get("price") or signal_data.get("price", 0)
            if not price:
                continue
            greeks = compute_options_greeks(ticker_clean, price, signal_data.get("signal", "HOLD"))
            if greeks:
                signal_data.update(greeks)
        return signals

    def _apply_latent_context_adjustments(self, signals: dict, latent_context: dict) -> dict:
        """
        Apply latent context from catalyst monitor (K4 tickers, etc.).

        Pure rule-based, no extra Claude call. Reads K4 tickers from catalyst's LoRA cache (layer 2),
        enforces kill_switch field and caps confidence for earnings-risk tickers.
        """
        k4_tickers = set()

        # Read K4 tickers from catalyst monitor's LoRA cache (layer 2)
        if self.kv_cache_binding:
            cat_signals = self.kv_cache_binding.get(layer=2, key="signals_catalyst-monitor")
            if isinstance(cat_signals, dict):
                k4_tickers = {t for t, v in cat_signals.items() if v.get("kill_switch") == "K4"}

        # Apply K4 override
        for ticker in k4_tickers:
            if ticker in signals:
                signals[ticker]["kill_switch"] = "K4"
                signals[ticker]["confidence"] = min(signals[ticker].get("confidence", 50), 40)
                note = signals[ticker].get("note", "")
                if "[K4 earnings risk]" not in note:
                    signals[ticker]["note"] = (note + " [K4 earnings risk]").strip()

        return signals

    def _encode_hidden_states(self, signals: dict) -> dict:
        """
        Encode VIF analysis results as numpy hidden states.

        Layer 8: Signal distribution [buy_frac, sell_frac, hold_frac, kill_frac] shape (4,)
        Layer 16: Confidence stats [mean_conf, std_conf, max_conf] shape (3,)
        Layer 24: Ticker intensity vector (32-element, zero-padded) shape (32,)
        """
        # Layer 8: signal distribution
        n = max(len(signals), 1)
        buy_frac = sum(1 for s in signals.values() if s.get("signal") == "BUY") / n
        sell_frac = sum(1 for s in signals.values() if s.get("signal") == "SELL") / n
        hold_frac = sum(1 for s in signals.values() if s.get("signal") == "HOLD") / n
        kill_frac = sum(1 for s in signals.values() if s.get("kill_switch") not in (None, False, "")) / n

        h8 = np.array([buy_frac, sell_frac, hold_frac, kill_frac], dtype=np.float32)

        # Layer 16: confidence centroid
        confs = np.array([s.get("confidence", 50) for s in signals.values()], dtype=np.float32) / 100.0
        if len(confs) == 0:
            h16 = np.array([0.5, 0.0, 0.5], dtype=np.float32)
        else:
            h16 = np.array([confs.mean(), confs.std(), confs.max()], dtype=np.float32)

        # Layer 24: ticker intensity
        confs_sorted = sorted([s.get("confidence", 0) / 100.0 for s in signals.values()], reverse=True)
        h24 = np.zeros(32, dtype=np.float32)
        for i, c in enumerate(confs_sorted[:32]):
            h24[i] = c

        return {
            8: h8,
            16: h16,
            24: h24,
        }
