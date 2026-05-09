"""
Confidence-Weighted Consensus - Resolve Agent Signal Disagreements

When agents disagree on signal (e.g., QXO should be BUY vs HOLD),
use argmax(confidence_scores) to determine consensus signal.
Log conflicts for analysis.
"""

from typing import Dict, List, Any
from datetime import datetime


class ConfidenceWeightedConsensus:
    """
    Resolves signal conflicts via confidence-weighted voting.

    Strategy: argmax(confidence_scores) wins. If multiple signals have same confidence,
    use signal priority (BUY > SELL > HOLD for long-biased portfolio).

    Log all conflicts for post-analysis.
    """

    def __init__(self, signal_priority: Dict[str, int] = None):
        """
        Initialize consensus resolver.

        Args:
            signal_priority: Ranking for tiebreaking (higher = higher priority).
                           Default: BUY=3, SELL=2, HOLD=1
        """
        self.signal_priority = signal_priority or {
            "BUY": 3,
            "SELL": 2,
            "HOLD": 1,
        }
        self.conflict_log = []

    def resolve(self, agent_signals: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """
        Resolve conflicting signals from multiple agents.

        Args:
            agent_signals: {ticker: [
                {agent_id, signal, confidence},
                {agent_id, signal, confidence},
                ...
            ]}

        Returns:
            {
                "consensus_signals": {ticker: {signal, confidence, agent_count, conflict: bool}},
                "conflicts": [
                    {ticker, agents, consensus}
                ]
            }
        """
        consensus_signals = {}
        conflicts = []

        for ticker, agent_list in agent_signals.items():
            # Filter out None/missing signals
            valid_signals = [s for s in agent_list if s.get("signal") and s.get("confidence") is not None]

            if not valid_signals:
                continue

            # Find consensus: highest confidence wins
            best = max(valid_signals, key=lambda x: (x["confidence"], self.signal_priority.get(x["signal"], 0)))

            consensus_signals[ticker] = {
                "signal": best["signal"],
                "confidence": best["confidence"],
                "agent_count": len(valid_signals),
                "consensus_agent": best["agent_id"],
                "conflict": False,
            }

            # Check if agents disagreed (different signals)
            unique_signals = set(s["signal"] for s in valid_signals)
            if len(unique_signals) > 1:
                consensus_signals[ticker]["conflict"] = True
                conflicts.append({
                    "ticker": ticker,
                    "agents": agent_list,
                    "unique_signals": list(unique_signals),
                    "consensus": best,
                    "timestamp": datetime.utcnow().isoformat(),
                })
                self.conflict_log.append({
                    "ticker": ticker,
                    "agents": agent_list,
                    "consensus": best,
                    "timestamp": datetime.utcnow().isoformat(),
                })

        return {
            "consensus_signals": consensus_signals,
            "conflicts": conflicts,
            "conflict_count": len(conflicts),
        }

    def get_conflict_log(self, ticker: str = None) -> List[Dict]:
        """
        Retrieve conflict log (optionally filtered by ticker).

        Args:
            ticker: Optional ticker to filter

        Returns:
            List of conflict records
        """
        if not ticker:
            return self.conflict_log

        return [c for c in self.conflict_log if c["ticker"] == ticker]

    def clear_conflict_log(self):
        """Clear conflict log for new session."""
        self.conflict_log.clear()

    def metrics(self) -> Dict[str, Any]:
        """Return consensus metrics."""
        return {
            "total_conflicts": len(self.conflict_log),
            "unique_tickers_conflicted": len(set(c["ticker"] for c in self.conflict_log)),
            "avg_agents_per_conflict": sum(len(c["agents"]) for c in self.conflict_log) / len(self.conflict_log) if self.conflict_log else 0,
        }
