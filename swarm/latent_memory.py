"""
Latent Working Memory - LatentMAS Pattern Implementation

Layer-wise hidden state sharing between agents.
Reference: arXiv 2511.20639 (LatentMAS)

Agents exchange last-layer hidden states for collaborative reasoning.
Enables consensus without message-passing overhead.
"""

from typing import Dict, Optional, List, Any, Tuple
from datetime import datetime
import json


class LatentWorkingMemory:
    """
    Shared latent working memory for multi-agent collaboration.

    Agents write their hidden states (after reasoning), other agents read them
    to incorporate peer perspective into their reasoning.

    Based on LatentMAS: latent thoughts exchanged via layer-wise hidden states.
    """

    def __init__(self, layers_to_share: Optional[List[int]] = None):
        """
        Initialize latent memory.

        Args:
            layers_to_share: Which transformer layers to share.
                            Default: [8, 16, 24] (every 8 layers, cover range)
        """
        self.layers_to_share = layers_to_share or [8, 16, 24]
        # Structure: {(layer, agent_id): hidden_state_tensor}
        self.shared_states: Dict[Tuple[int, str], Any] = {}
        self.write_history: Dict[str, List[Dict]] = {}
        self.read_history: Dict[str, List[Dict]] = {}

    def read_hidden_states(self, agent_id: str, source_agents: Optional[List[str]] = None, layers: Optional[List[int]] = None) -> Dict[int, Any]:
        """
        Read hidden states from peer agents.

        Args:
            agent_id: Requesting agent's ID
            source_agents: Which agents' states to read. None = all agents except self
            layers: Which layers to read. None = default layers_to_share

        Returns:
            Dict mapping layer → hidden state tensor
        """
        layers = layers or self.layers_to_share
        source_agents = source_agents or [a for a in self._get_all_agents() if a != agent_id]

        result = {}
        for layer in layers:
            # Aggregate hidden states from all source agents (average them)
            states = []
            for source_agent in source_agents:
                key = (layer, source_agent)
                if key in self.shared_states:
                    states.append(self.shared_states[key])

            if states:
                # For now, just use most recent (in production, could average)
                result[layer] = states[-1]

            # Log read
            if agent_id not in self.read_history:
                self.read_history[agent_id] = []
            self.read_history[agent_id].append({
                "timestamp": datetime.utcnow().isoformat(),
                "layer": layer,
                "source_agents": source_agents,
                "found": len(states) > 0,
            })

        return result

    def write_hidden_states(self, agent_id: str, hidden_states_dict: Dict[int, Any]):
        """
        Write hidden states to working memory.

        Args:
            agent_id: Writing agent's ID
            hidden_states_dict: Dict mapping layer → hidden state tensor
        """
        for layer, state in hidden_states_dict.items():
            key = (layer, agent_id)
            self.shared_states[key] = state

        # Log write
        if agent_id not in self.write_history:
            self.write_history[agent_id] = []
        self.write_history[agent_id].append({
            "timestamp": datetime.utcnow().isoformat(),
            "layers": list(hidden_states_dict.keys()),
            "state_count": len(hidden_states_dict),
        })

    def get_state(self, layer: int, agent_id: str) -> Optional[Any]:
        """Get hidden state for specific layer + agent."""
        return self.shared_states.get((layer, agent_id), None)

    def clear_agent_states(self, agent_id: str):
        """Clear all states written by an agent."""
        keys_to_delete = [k for k in self.shared_states.keys() if k[1] == agent_id]
        for key in keys_to_delete:
            del self.shared_states[key]

    def clear_all(self):
        """Clear all latent states."""
        self.shared_states.clear()
        self.write_history.clear()
        self.read_history.clear()

    def _get_all_agents(self) -> List[str]:
        """Get list of all agents that have written states."""
        return list(set(agent_id for _, agent_id in self.shared_states.keys()))

    def metrics(self) -> Dict[str, Any]:
        """Return latent memory metrics."""
        all_agents = self._get_all_agents()
        return {
            "total_states_stored": len(self.shared_states),
            "active_agents": len(all_agents),
            "agent_ids": all_agents,
            "layers_shared": self.layers_to_share,
            "write_operations": sum(len(v) for v in self.write_history.values()),
            "read_operations": sum(len(v) for v in self.read_history.values()),
            "agents_with_reads": list(self.read_history.keys()),
        }

    def session_summary(self, agent_id: str) -> Dict[str, Any]:
        """Get summary of agent's memory interactions."""
        return {
            "agent_id": agent_id,
            "writes": self.write_history.get(agent_id, []),
            "reads": self.read_history.get(agent_id, []),
            "write_count": len(self.write_history.get(agent_id, [])),
            "read_count": len(self.read_history.get(agent_id, [])),
        }
