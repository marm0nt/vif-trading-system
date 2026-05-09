"""
Catalyst Monitor Agent - SpecialistAgent wrapper for catalyst_analysis.py

Scans government policy, earnings catalysts, sector themes with KV cache binding.
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

from .specialist_agent import SpecialistAgent


class CatalystMonitorAgent(SpecialistAgent):
    """
    Specialized agent for macro catalyst monitoring.

    Wraps scripts/active/analysis/catalyst_analysis.py and integrates with swarm framework.
    Scans government policy, regulatory decisions, earnings calendars, sector rotation.
    """

    def __init__(self, agent_id: str = "catalyst-monitor"):
        super().__init__(
            agent_id=agent_id,
            agent_type="catalyst-monitor",
            role_description="Macro catalyst monitoring (earnings, policy, sector themes)"
        )

    def _execute_subtasks(self, subtasks: List[Dict], latent_context: Dict) -> Dict[str, Any]:
        """
        Execute catalyst analysis on all watchlists.

        Args:
            subtasks: List of {scope: "all_watchlists", lookahead_days: 5, ...}
            latent_context: Hidden states from peer agents (unused in v1)

        Returns:
            {
                "catalysts": {ticker: [catalyst_info, ...]},
                "themes": {theme_name: [tickers, ...]},
                "earnings_calendar": [...],
                "metrics": {catalysts_found, themes_detected},
                "hidden_states": {...}
            }
        """
        all_catalysts = {}
        all_themes = {}
        earnings_calendar = []

        for subtask in subtasks:
            scope = subtask.get("scope", "all_watchlists")
            lookahead = subtask.get("lookahead_days", 5)

            # Run catalyst_analysis.py subprocess
            try:
                result = subprocess.run(
                    [sys.executable, "scripts/active/analysis/catalyst_analysis.py"],
                    capture_output=True,
                    text=True,
                    timeout=180,
                    cwd=str(Path.cwd()),
                )

                if result.returncode == 0:
                    try:
                        output = json.loads(result.stdout)
                        all_catalysts.update(output.get("catalysts", {}))
                        all_themes.update(output.get("themes", {}))
                        earnings_calendar.extend(output.get("earnings_calendar", []))
                    except json.JSONDecodeError:
                        pass
                else:
                    pass

            except subprocess.TimeoutExpired:
                pass
            except Exception:
                pass

        # Simulated hidden states
        hidden_states = {
            8: f"catalyst_monitor_layer8_{datetime.utcnow().isoformat()}",
            16: f"catalyst_monitor_layer16_{datetime.utcnow().isoformat()}",
            24: f"catalyst_monitor_layer24_{datetime.utcnow().isoformat()}",
        }

        return {
            "catalysts": all_catalysts,
            "themes": all_themes,
            "earnings_calendar": earnings_calendar,
            "metrics": {
                "catalysts_found": len(all_catalysts),
                "themes_detected": len(all_themes),
                "earnings_events": len(earnings_calendar),
            },
            "hidden_states": hidden_states,
        }
