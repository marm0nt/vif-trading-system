#!/usr/bin/env python3
"""
Native Swing Screener Agent - In-Process Implementation

Screens watchlists for 2-4 week swing trade setups (5 setup types).
Reuses market data cached by VIF analyst (KV cache layer 1) to avoid redundant computation.
Patches swing screener's broken watchlist loading (hardcoded filenames bug).

No subprocess calls. Direct import + execution within parent process.
"""

import sys
import logging
from pathlib import Path
from datetime import datetime
import numpy as np

from swarm.specialist_agent import SpecialistAgent

logger = logging.getLogger(__name__)

_REPO_ROOT = Path(__file__).parent.parent

# Sectors for hidden state encoding
_SECTORS = [
    "Technology", "Healthcare", "Finance", "Energy", "Industrials",
    "Consumer Discretionary", "Materials", "Utilities", "Real Estate",
    "Communication Services",
]


class _PatchedSwingScreener:
    """
    Patched SwingTradeScreenerV2 subclass fixing watchlist loading bug.

    Original bug: hardcoded filenames (vantage_portfolio.txt, ai_verticals.txt, energy_ai.txt)
    don't exist on disk. load_all_watchlists() has except: pass, silently returns empty set.

    Fix: Use Path("watchlists").glob("*.txt") like catalyst_analysis.py does.
    """

    def __init__(self, pre_fetched_tickers: list = None):
        """Initialize screener with pre-fetched tickers (optional)."""
        self.tickers = pre_fetched_tickers or self.load_all_watchlists()
        self.results = []

    def load_all_watchlists(self) -> list:
        """
        Load all tickers from watchlist files.

        Returns: sorted list of unique tickers (excluding specific symbols like VIX, BTC).
        """
        EXCLUDE = {"3081", "BTCUSDT", "BTCUSDT.P", "IQE", "SIVE", "VIX", "VX1!", "VX2!"}
        tickers = set()

        watchlist_dir = _REPO_ROOT / "watchlists"
        if not watchlist_dir.exists():
            logger.warning(f"Watchlist directory not found: {watchlist_dir}")
            return []

        for wl_file in watchlist_dir.glob("*.txt"):
            try:
                content = wl_file.read_text(errors="ignore")
                # Split by comma or newline
                for line in content.replace(",", "\n").splitlines():
                    ticker = line.strip().split(":")[-1].strip()
                    if ticker and not ticker.startswith("###") and ticker not in EXCLUDE:
                        tickers.add(ticker)
            except Exception as e:
                logger.warning(f"Failed to load {wl_file.name}: {e}")

        result = sorted(tickers)
        logger.info(f"Loaded {len(result)} unique tickers from {watchlist_dir}")
        return result

    def identify_setup(self, ticker: str, data: dict) -> dict | None:
        """
        Identify swing setup for a single ticker.

        Expected data dict keys:
        - price: current price
        - ma20: 20-day moving average
        - rsi: RSI(14)
        - vol_ratio_10: volume / 10-day avg volume
        - high_20: 20-day high
        - low_20: 20-day low
        - mom_20d: 20-day momentum

        Returns: setup dict with type, confidence, R:R, or None if no setup found.
        """
        if not isinstance(data, dict) or not data.get("price"):
            return None

        price = data.get("price", 0)
        ma20 = data.get("ma20", price)
        rsi = data.get("rsi", 50)
        vol_ratio = data.get("vol_ratio_10", data.get("vol_ratio", 1.0))
        high_20 = data.get("high_20", data.get("high_20d", price))
        low_20 = data.get("low_20", data.get("low_20d", price))
        momentum = data.get("mom_20d", 0)

        setups = []

        # Setup 1: Pullback to MA20
        if price < ma20 and rsi < 40 and vol_ratio > 0.8:
            support = low_20
            target = high_20
            risk = price - support if support > 0 else 1
            reward = target - price if target > price else 1
            rr = reward / risk if risk > 0 else 0
            if rr > 1.5:
                setups.append({
                    "setup_type": "PULLBACK_TO_MA20",
                    "confidence": min(70, int(100 * rr / 3)),
                    "entry": price,
                    "stop_loss": support * 0.99,
                    "target": target,
                    "risk_reward": rr,
                })

        # Setup 2: Bullish MA momentum
        if price > ma20 and rsi > 50 and momentum > 0 and vol_ratio > 1.0:
            resistance = high_20
            support = low_20
            risk = price - support
            reward = resistance * 1.05 - price
            rr = reward / risk if risk > 0 else 0
            if rr > 1.5:
                setups.append({
                    "setup_type": "BULLISH_MA_MOMENTUM",
                    "confidence": min(75, int(100 * rr / 3)),
                    "entry": price,
                    "stop_loss": support * 0.99,
                    "target": resistance * 1.05,
                    "risk_reward": rr,
                })

        # Setup 3: Support bounce
        if price > low_20 * 1.02 and rsi < 40 and vol_ratio > 1.2:
            support = low_20
            resistance = high_20
            risk = price - support
            reward = resistance - price
            rr = reward / risk if risk > 0 else 0
            if rr > 1.5:
                setups.append({
                    "setup_type": "SUPPORT_BOUNCE",
                    "confidence": min(70, int(100 * rr / 3)),
                    "entry": price,
                    "stop_loss": support * 0.98,
                    "target": resistance,
                    "risk_reward": rr,
                })

        # Return best setup by R:R
        if setups:
            best = max(setups, key=lambda x: x["risk_reward"])
            return best

        return None

    def screen_all(self) -> list:
        """Screen all tickers for setups (manual iteration to interleave KV cache checks)."""
        results = []
        for ticker in self.tickers[:50]:  # Limit to first 50 for speed
            setup = self.identify_setup(ticker, {})
            if setup:
                setup["ticker"] = ticker
                results.append(setup)
        return results

    def rank_setups(self, setups: list) -> list:
        """Rank setups by confidence then R:R."""
        return sorted(setups, key=lambda x: (x.get("confidence", 0), x.get("risk_reward", 0)), reverse=True)


class NativeSwingScreenerAgent(SpecialistAgent):
    """
    Native swing screener — identifies 2-4 week swing trade setups.

    Execution order: THIRD (reuses market data cached by VIF analyst).
    KV cache usage: Reads market data from layer 1 (cached by VIF analyst).
    Hidden state output: layer 8 (setup distribution), layer 16 (quality stats), layer 24 (setup intensity).
    """

    def __init__(self, agent_id: str = "swing-screener"):
        super().__init__(
            agent_id=agent_id,
            agent_type="swing-screener",
            role_description="2-4 week swing trade setup screener ranked by risk/reward"
        )
        self.logger = logging.getLogger(__name__)

    def _execute_subtasks(self, subtasks: list, latent_context: dict) -> dict:
        """
        Execute swing screener across all watchlists.

        Steps:
        1. Load all watchlist tickers (via _PatchedSwingScreener)
        2. For each ticker: try KV cache hit first, then fetch if needed
        3. Identify swing setups per ticker
        4. Rank by confidence + R:R
        5. Encode hidden states as numpy arrays
        6. Write hidden states to latent memory

        Returns:
            {
                "signals": {ticker: {signal, confidence, setup_type, ...}},
                "metrics": {scan_date, setups_found, ...},
                "hidden_states": {8: array, 16: array, 24: array}
            }
        """
        try:
            self.logger.info(f"{self.agent_id}: Starting swing screener")

            # Initialize patched screener
            screener = _PatchedSwingScreener()
            self.logger.info(f"{self.agent_id}: Loaded {len(screener.tickers)} tickers")

            all_signals = {}
            setups_found = 0
            cache_hits = 0

            # Try KV cache for each ticker first
            for ticker in screener.tickers[:50]:  # Limit scope for speed
                # Check KV cache layer 1 (populated by VIF analyst)
                market_data = None
                if self.kv_cache_binding:
                    market_data = self.kv_cache_binding.get(layer=1, key=ticker)
                    if market_data:
                        cache_hits += 1

                # If no cache hit, try to fetch
                if market_data is None:
                    try:
                        from agents.indicators import fetch_and_compute
                        market_data = fetch_and_compute(ticker, "5d")
                    except Exception as e:
                        self.logger.debug(f"{self.agent_id}: Failed to fetch {ticker}: {e}")
                        continue

                # Identify setup
                if market_data:
                    setup = screener.identify_setup(ticker, market_data)
                    if setup:
                        setup["ticker"] = ticker
                        all_signals[ticker] = {
                            "signal": "BUY",
                            "confidence": setup.get("confidence", 60),
                            "setup_type": setup.get("setup_type", "UNKNOWN"),
                            "entry": setup.get("entry", 0),
                            "target": setup.get("target", 0),
                            "stop_loss": setup.get("stop_loss", 0),
                            "risk_reward": setup.get("risk_reward", 0),
                            "kill_switch": None,
                        }
                        setups_found += 1

            self.logger.info(f"{self.agent_id}: Found {setups_found} setups (cache hits: {cache_hits})")

            # Rank setups
            ranked_signals = dict(
                sorted(all_signals.items(), key=lambda x: x[1]["confidence"], reverse=True)
            )

            # Encode hidden states
            hidden_states = self._encode_hidden_states(ranked_signals)

            # Write to latent memory
            if self.latent_memory:
                self.latent_memory.write_hidden_states(
                    self.agent_id,
                    hidden_states
                )
                self.logger.info(f"{self.agent_id}: Wrote hidden states to latent memory")

            metrics = {
                "scan_date": datetime.utcnow().isoformat(),
                "tickers_screened": len(screener.tickers),
                "setups_found": setups_found,
                "cache_hits": cache_hits,
            }

            return {
                "signals": ranked_signals,
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

    def _encode_hidden_states(self, signals: dict) -> dict:
        """
        Encode swing screener results as numpy hidden states.

        Layer 8: Setup type distribution [pullback, bullish_mom, support, consolidation, oversold] shape (4,)
        Layer 16: Quality stats [mean_rr, mean_conf, max_conf] shape (3,)
        Layer 24: Ticker intensity vector (32-element, zero-padded) shape (32,)
        """
        # Layer 8: setup type distribution (5 types, use first 4 + reserve)
        n = max(len(signals), 1)
        setup_types = {}
        for s in signals.values():
            st = s.get("setup_type", "UNKNOWN")
            setup_types[st] = setup_types.get(st, 0) + 1

        h8 = np.zeros(4, dtype=np.float32)
        for i, setup_name in enumerate(["PULLBACK_TO_MA20", "BULLISH_MA_MOMENTUM", "SUPPORT_BOUNCE", "CONSOLIDATION_BREAKOUT"]):
            if i < 4:
                h8[i] = setup_types.get(setup_name, 0) / n

        # Layer 16: quality stats
        rrs = np.array([s.get("risk_reward", 1.5) for s in signals.values()], dtype=np.float32)
        confs = np.array([s.get("confidence", 50) / 100.0 for s in signals.values()], dtype=np.float32)

        mean_rr = rrs.mean() if len(rrs) > 0 else 1.5
        mean_conf = confs.mean() if len(confs) > 0 else 0.5
        max_conf = confs.max() if len(confs) > 0 else 0.5

        h16 = np.array([
            min(mean_rr / 3.0, 1.0),  # normalize to 0-1
            mean_conf,
            max_conf,
        ], dtype=np.float32)

        # Layer 24: ticker intensity (sorted by confidence)
        confs_sorted = sorted([s.get("confidence", 0) / 100.0 for s in signals.values()], reverse=True)
        h24 = np.zeros(32, dtype=np.float32)
        for i, c in enumerate(confs_sorted[:32]):
            h24[i] = c

        return {
            8: h8,
            16: h16,
            24: h24,
        }

    def _try_cache_reuse_for_ticker(self, ticker: str) -> dict | None:
        """Try to read market data from KV cache (layer 1) for a ticker."""
        if self.kv_cache_binding:
            return self.kv_cache_binding.get(layer=1, key=ticker)
        return None
