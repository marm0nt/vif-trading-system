"""
Gossip Router - Decentralized Task Routing Protocol

Instead of orchestrator assigning tasks, agents gossip "task accepted" to neighbors.
Task gets assigned to first agent to accept (no central bottleneck).
"""

from typing import Dict, List, Any
from datetime import datetime
import random


class GossipRouter:
    """
    Decentralized task routing via gossip protocol.

    Agents autonomously decide if they can handle a subtask based on:
    - Role match (agent_type matches subtask agent_type)
    - Current load (not overloaded)
    - Capacity (can take on more work)

    Tasks get assigned to first agent to accept, reducing orchestrator bottleneck.
    """

    def __init__(self, gossip_timeout_ms: int = 500, max_agents_per_subtask: int = 3):
        """
        Initialize gossip router.

        Args:
            gossip_timeout_ms: Max time to wait for agent acceptance (default 500ms)
            max_agents_per_subtask: Max agents that can accept same subtask (load balancing)
        """
        self.gossip_timeout_ms = gossip_timeout_ms
        self.max_agents_per_subtask = max_agents_per_subtask
        self.routing_history = []

    def route_tasks(self, subtasks: List[Dict], agent_pool: Dict[str, Any]) -> Dict[str, List[Dict]]:
        """
        Route subtasks to agents via gossip protocol.

        Args:
            subtasks: List of subtasks to route
            agent_pool: Dict mapping agent_id → SpecialistAgent instance

        Returns:
            {agent_id: [subtasks]} dispatch map
        """
        dispatch_map = {agent_id: [] for agent_id in agent_pool.keys()}
        acceptance_count = {}  # Track how many agents accepted each subtask

        # For each subtask, gossip to matching agents
        for subtask in subtasks:
            subtask_id = subtask.get("agent_type") + "_" + str(subtasks.index(subtask))
            acceptance_count[subtask_id] = 0

            # Get agents matching subtask type
            matching_agents = self._get_matching_agents(subtask, agent_pool)

            # Gossip: ask agents in order if they can accept
            for agent in matching_agents:
                if acceptance_count[subtask_id] >= self.max_agents_per_subtask:
                    break  # Enough agents accepted this subtask

                # Check if agent can accept
                if self._can_agent_accept(agent, subtask):
                    dispatch_map[agent.agent_id].append(subtask)
                    acceptance_count[subtask_id] += 1

                    # Log gossip event
                    self.routing_history.append({
                        "timestamp": datetime.utcnow().isoformat(),
                        "subtask_type": subtask.get("agent_type"),
                        "agent_id": agent.agent_id,
                        "action": "accepted",
                    })

            # If no agent accepted, assign to fallback (first matching agent)
            if acceptance_count[subtask_id] == 0 and matching_agents:
                fallback = matching_agents[0]
                dispatch_map[fallback.agent_id].append(subtask)
                self.routing_history.append({
                    "timestamp": datetime.utcnow().isoformat(),
                    "subtask_type": subtask.get("agent_type"),
                    "agent_id": fallback.agent_id,
                    "action": "fallback_assigned",
                })

        return dispatch_map

    def _get_matching_agents(self, subtask: Dict, agent_pool: Dict[str, Any]) -> List[Any]:
        """
        Get agents whose type matches subtask agent_type.

        Shuffles to avoid always assigning to same agent (load balancing).
        """
        subtask_type = subtask.get("agent_type")
        matching = [
            agent for agent_id, agent in agent_pool.items()
            if agent.agent_type == subtask_type
        ]
        random.shuffle(matching)
        return matching

    def _can_agent_accept(self, agent: Any, subtask: Dict) -> bool:
        """
        Heuristic: can agent accept this subtask?

        Simple checks:
        - Agent must have matching type
        - Agent must not be overloaded (execution_count < threshold)
        """
        # Type already matched by caller
        if not hasattr(agent, "agent_type"):
            return False

        # Check overload: if agent has executed >5 times without reset, probably overloaded
        overload_threshold = 5
        if hasattr(agent, "execution_count") and agent.execution_count >= overload_threshold:
            return False

        return True

    def metrics(self) -> Dict[str, Any]:
        """Return routing metrics."""
        if not self.routing_history:
            return {"total_gossip_events": 0}

        accepted = sum(1 for h in self.routing_history if h["action"] == "accepted")
        fallback = sum(1 for h in self.routing_history if h["action"] == "fallback_assigned")

        return {
            "total_gossip_events": len(self.routing_history),
            "accepted_events": accepted,
            "fallback_assignments": fallback,
            "acceptance_rate": accepted / len(self.routing_history) if self.routing_history else 0,
        }
