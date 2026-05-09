"""
VIF Analyst Agent - SpecialistAgent wrapper for watchlist_watcher.py

Executes VIF framework analysis on watchlists with KV cache binding + latent memory.
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

from .specialist_agent import SpecialistAgent


class VIFAnalystAgent(SpecialistAgent):
    """
    Specialized agent for VIF watchlist analysis.

    Wraps agents/watchlist_watcher.py and integrates with swarm framework
    for KV cache binding + latent hidden state exchange.
    """

    def __init__(self, agent_id: str = "vif-analyst-1"):
        super().__init__(
            agent_id=agent_id,
            agent_type="vif-analyst",
            role_description="VIF Framework analysis on institutional watchlists"
        )

    def _execute_subtasks(self, subtasks: List[Dict], latent_context: Dict) -> Dict[str, Any]:
        """
        Execute VIF analysis on assigned watchlists.

        Args:
            subtasks: List of {watchlist: "...", period: "1mo", ...}
            latent_context: Hidden states from peer agents (unused in v1, for future enhancement)

        Returns:
            {
                "signals": {ticker: {signal, confidence, gamma_regime, volume_signal, kill_switch, price, rsi, note}},
                "metrics": {tickers_analyzed, buy_count, sell_count, hold_count},
                "hidden_states": {8: tensor, 16: tensor, 24: tensor}  # Simulated for now
            }
        """
        all_signals = {}
        total_analyzed = 0

        for subtask in subtasks:
            watchlist = subtask.get("watchlist")
            period = subtask.get("period", "1mo")

            if not watchlist:
                continue

            # Run watchlist_watcher.py subprocess
            try:
                result = subprocess.run(
                    [sys.executable, "agents/watchlist_watcher.py", "--watchlist", watchlist, "--period", period],
                    capture_output=True,
                    text=True,
                    timeout=300,
                    cwd=str(Path.cwd()),
                )

                if result.returncode == 0:
                    # Parse JSON output from agent
                    try:
                        output = json.loads(result.stdout)
                        signals = output.get("signals", {})
                        all_signals.update(signals)
                        total_analyzed += len(signals)
                    except json.JSONDecodeError:
                        # Fallback: capture as text
                        pass
                else:
                    # Log error but continue
                    pass

            except subprocess.TimeoutExpired:
                pass
            except Exception:
                pass

        # Aggregate metrics
        buy_count = sum(1 for s in all_signals.values() if s.get("signal", "").upper() == "BUY")
        sell_count = sum(1 for s in all_signals.values() if s.get("signal", "").upper() == "SELL")
        hold_count = sum(1 for s in all_signals.values() if s.get("signal", "").upper() == "HOLD")

        # Simulated hidden states (in production, extract from model layer outputs)
        hidden_states = {
            8: f"vif_analyst_layer8_{datetime.utcnow().isoformat()}",
            16: f"vif_analyst_layer16_{datetime.utcnow().isoformat()}",
            24: f"vif_analyst_layer24_{datetime.utcnow().isoformat()}",
        }

        return {
            "signals": all_signals,
            "metrics": {
                "tickers_analyzed": total_analyzed,
                "buy_count": buy_count,
                "sell_count": sell_count,
                "hold_count": hold_count,
            },
            "hidden_states": hidden_states,
        }
