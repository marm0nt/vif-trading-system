"""
Swing Screener Agent - SpecialistAgent wrapper for swing_trade_screener_v2.py

Identifies 2-4 week swing trade setups with KV cache binding.
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

from .specialist_agent import SpecialistAgent


class SwingScreenerAgent(SpecialistAgent):
    """
    Specialized agent for swing trade screening.

    Wraps scripts/active/analysis/swing_trade_screener_v2.py and integrates with swarm framework.
    Screens for 5 setup types: PULLBACK_TO_MA20, BULLISH_MA_MOMENTUM, SUPPORT_BOUNCE, CONSOLIDATION_BREAKOUT, OVERSOLD_BOUNCE.
    Ranks by risk/reward ratio.
    """

    def __init__(self, agent_id: str = "swing-screener"):
        super().__init__(
            agent_id=agent_id,
            agent_type="swing-screener",
            role_description="Swing trade setup screening (2-4 week timeframe, 5 setup types)"
        )

    def _execute_subtasks(self, subtasks: List[Dict], latent_context: Dict) -> Dict[str, Any]:
        """
        Execute swing screener on all watchlists.

        Args:
            subtasks: List of {scope: "all_watchlists", rank_by: "risk_reward_ratio", ...}
            latent_context: Hidden states from peer agents (unused in v1)

        Returns:
            {
                "setups": [{ticker, setup_type, price, entry, stop_loss, target_1, target_2, risk_reward, confidence, ...}, ...],
                "metrics": {total_setups, setup_type_breakdown},
                "hidden_states": {...}
            }
        """
        all_setups = []
        setup_type_count = {}

        for subtask in subtasks:
            scope = subtask.get("scope", "all_watchlists")
            rank_by = subtask.get("rank_by", "risk_reward_ratio")

            # Run swing_trade_screener_v2.py subprocess
            try:
                result = subprocess.run(
                    [sys.executable, "scripts/active/analysis/swing_trade_screener_v2.py"],
                    capture_output=True,
                    text=True,
                    timeout=240,
                    cwd=str(Path.cwd()),
                )

                if result.returncode == 0:
                    try:
                        output = json.loads(result.stdout)
                        setups = output.get("setups", output.get("top_setups", []))
                        all_setups.extend(setups)

                        # Count setup types
                        for setup in setups:
                            setup_type = setup.get("setup_type", "unknown")
                            setup_type_count[setup_type] = setup_type_count.get(setup_type, 0) + 1

                    except json.JSONDecodeError:
                        pass
                else:
                    pass

            except subprocess.TimeoutExpired:
                pass
            except Exception:
                pass

        # Sort by risk/reward ratio (descending)
        try:
            all_setups.sort(key=lambda s: float(s.get("risk_reward", 0)), reverse=True)
        except (ValueError, KeyError, TypeError):
            pass

        # Simulated hidden states
        hidden_states = {
            8: f"swing_screener_layer8_{datetime.utcnow().isoformat()}",
            16: f"swing_screener_layer16_{datetime.utcnow().isoformat()}",
            24: f"swing_screener_layer24_{datetime.utcnow().isoformat()}",
        }

        return {
            "setups": all_setups,
            "metrics": {
                "total_setups": len(all_setups),
                "setup_types": setup_type_count,
            },
            "hidden_states": hidden_states,
        }
