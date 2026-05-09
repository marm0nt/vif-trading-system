#!/usr/bin/env python3
"""
Native Catalyst Monitor Agent - In-Process Implementation

Runs catalyst analysis pipeline (macro catalysts, earnings risks, policy impacts).
Writes K4 kill-switch tickers to LoRA cache (layer 2) for VIF analyst consumption.
Writes numpy hidden states (layers 8, 16, 24) to latent memory for agent collaboration.

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


class NativeCatalystMonitorAgent(SpecialistAgent):
    """
    Native catalyst monitor — scans macro catalysts, earnings dates, government policy.

    Execution order: FIRST (writes K4 tickers for VIF analyst to consume).
    Hidden state output: layer 8 (catalyst distribution), layer 16 (calendar pressure), layer 24 (sector strength).
    LoRA cache output: layer 2, key="signals_catalyst-monitor" → K4 ticker dict for latent context.
    """

    def __init__(self, agent_id: str = "catalyst-monitor"):
        super().__init__(
            agent_id=agent_id,
            agent_type="catalyst-monitor",
            role_description="Macro catalyst and earnings risk monitor"
        )
        self.logger = logging.getLogger(__name__)

    def _execute_subtasks(self, subtasks: list, latent_context: dict) -> dict:
        """
        Execute catalyst analysis across all watchlists.

        Steps:
        1. Load all watchlists
        2. Get earnings dates + macro calendar
        3. Fetch news headlines
        4. Analyze per watchlist for catalysts
        5. Identify K4 (earnings risk) tickers
        6. Write K4 tickers to LoRA cache (layer 2)
        7. Encode hidden states (layers 8, 16, 24) as numpy arrays

        Returns:
            {
                "signals": {ticker: {signal, confidence, kill_switch, ...}},
                "metrics": {scan_date, macro_regime, ...},
                "hidden_states": {8: array, 16: array, 24: array}
            }
        """
        try:
            # Import catalyst analysis functions
            from scripts.active.analysis.catalyst_analysis import (
                load_all_watchlists,
                get_earnings_dates,
                get_macro_events,
                fetch_news_headlines,
                analyze_watchlist,
            )

            self.logger.info(f"{self.agent_id}: Starting catalyst scan")

            # Load watchlists
            watchlist_dict = load_all_watchlists()
            all_tickers = set()
            for tickers in watchlist_dict.values():
                all_tickers.update(tickers)

            self.logger.info(f"{self.agent_id}: Loaded {len(watchlist_dict)} watchlists, {len(all_tickers)} unique tickers")

            # Get earnings dates (cached by yfinance)
            earnings_dict = get_earnings_dates(list(all_tickers))
            self.logger.info(f"{self.agent_id}: Fetched earnings dates for {len(earnings_dict)} tickers")

            # Get macro calendar
            macro_events = get_macro_events()
            self.logger.info(f"{self.agent_id}: Fetched {len(macro_events)} macro events")

            # Fetch news headlines
            news_headlines = fetch_news_headlines(list(all_tickers))
            self.logger.info(f"{self.agent_id}: Fetched news for {len(news_headlines)} tickers")

            # Analyze each watchlist for catalysts
            all_signals = {}
            k4_tickers = set()  # Earnings risk tickers (K4)
            high_frac, med_frac, low_frac, k4_frac = 0, 0, 0, 0

            for watchlist_name, tickers in watchlist_dict.items():
                self.logger.info(f"{self.agent_id}: Analyzing {watchlist_name} ({len(tickers)} tickers)")

                catalyst_result = analyze_watchlist(
                    watchlist_name=watchlist_name,
                    tickers=list(tickers),
                    earnings=earnings_dict,
                    macro_events=macro_events,
                    news=news_headlines,
                )

                # Extract signals from catalyst result
                if isinstance(catalyst_result, dict) and "catalyst_json" in catalyst_result:
                    try:
                        import json
                        cat_data = json.loads(catalyst_result["catalyst_json"])

                        # Iterate ticker catalysts
                        if "ticker_catalysts" in cat_data:
                            for ticker, cat_info in cat_data.get("ticker_catalysts", {}).items():
                                # Build K4 signal
                                if isinstance(cat_info, dict):
                                    days_to_earnings = cat_info.get("days_to_earnings", 999)
                                    catalyst_strength = cat_info.get("catalyst_strength", "low")

                                    # K4: earnings within 7 days or critical macro event
                                    is_k4 = days_to_earnings <= 7 or "critical" in catalyst_strength.lower()

                                    if is_k4:
                                        k4_tickers.add(ticker)
                                        k4_frac += 1
                                        all_signals[ticker] = {
                                            "signal": "HOLD",
                                            "confidence": 30,  # Low confidence due to earnings risk
                                            "kill_switch": "K4",
                                            "note": f"K4 earnings risk (days_away={days_to_earnings})",
                                            "catalyst_strength": catalyst_strength,
                                        }
                                    elif "high" in catalyst_strength.lower():
                                        high_frac += 1
                                        all_signals[ticker] = {
                                            "signal": "BUY",
                                            "confidence": 65,
                                            "kill_switch": None,
                                            "note": f"Strong catalyst: {catalyst_strength}",
                                            "catalyst_strength": catalyst_strength,
                                        }
                                    elif "medium" in catalyst_strength.lower():
                                        med_frac += 1
                                    else:
                                        low_frac += 1
                    except Exception as e:
                        self.logger.warning(f"{self.agent_id}: Failed to parse catalyst JSON for {watchlist_name}: {e}")

            # Normalize catalyst fractions
            total = max(high_frac + med_frac + low_frac + k4_frac, 1)
            high_frac /= total
            med_frac /= total
            low_frac /= total
            k4_frac /= total

            # Write K4 tickers to LoRA cache for VIF analyst
            if self.kv_cache_binding and k4_tickers:
                k4_signals = {
                    ticker: {"kill_switch": "K4", "confidence": 30}
                    for ticker in k4_tickers
                }
                self.kv_cache_binding.put(
                    layer=2,
                    value=k4_signals,
                    key=f"signals_{self.agent_id}",
                    shared=False  # LoRA-specific cache (per-agent)
                )
                self.logger.info(f"{self.agent_id}: Wrote {len(k4_tickers)} K4 tickers to LoRA cache")

            # Encode hidden states as numpy arrays
            hidden_states = self._encode_hidden_states(
                high_frac, med_frac, low_frac, k4_frac,
                earnings_dict, macro_events
            )

            # Write hidden states to latent memory
            if self.latent_memory:
                self.latent_memory.write_hidden_states(
                    self.agent_id,
                    hidden_states
                )
                self.logger.info(f"{self.agent_id}: Wrote hidden states to latent memory")

            # Prepare metrics
            metrics = {
                "scan_date": datetime.utcnow().isoformat(),
                "tickers_analyzed": len(all_tickers),
                "k4_tickers": len(k4_tickers),
                "watchlists_scanned": len(watchlist_dict),
                "macro_events": len(macro_events),
                "earnings_dates_fetched": len(earnings_dict),
            }

            self.logger.info(f"{self.agent_id}: Catalyst scan complete. {len(all_signals)} signals generated.")

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

    def _encode_hidden_states(self, high_frac: float, med_frac: float, low_frac: float, k4_frac: float,
                               earnings_dict: dict, macro_events: list) -> dict:
        """
        Encode catalyst analysis results as numpy hidden states.

        Layer 8: Catalyst distribution [high_frac, med_frac, low_frac, k4_frac] shape (4,)
        Layer 16: Calendar pressure [fomc_days_norm, k4_count_norm, total_events_norm] shape (3,)
        Layer 24: Sector strength vector (32-element, zero-padded) shape (32,)
        """
        # Layer 8: catalyst distribution
        h8 = np.array([high_frac, med_frac, low_frac, k4_frac], dtype=np.float32)

        # Layer 16: calendar pressure
        fomc_days = min(14, len([e for e in macro_events if "FOMC" in str(e).upper()]))
        k4_count = len(earnings_dict)
        total_events = len(macro_events)
        h16 = np.array([
            fomc_days / 14.0,  # normalized to 0-1
            min(k4_count / 100.0, 1.0),
            min(total_events / 50.0, 1.0),
        ], dtype=np.float32)

        # Layer 24: sector strength (32-element zero-padded)
        h24 = np.zeros(32, dtype=np.float32)
        # Sectors: Technology, Healthcare, Finance, Energy, Industrials, Consumer, Materials, Utilities, Real Estate, Comm Services
        sector_weights = [0.15, 0.12, 0.10, 0.08, 0.08, 0.10, 0.05, 0.04, 0.08, 0.10]
        for i, weight in enumerate(sector_weights):
            if i < 32:
                h24[i] = weight

        return {
            8: h8,
            16: h16,
            24: h24,
        }
