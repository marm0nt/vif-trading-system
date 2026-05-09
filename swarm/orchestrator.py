"""
Swarm Orchestrator - Hierarchical Task Decomposition & Coordination

Decomposes tasks via Tree of Thoughts, fans agents to subtasks,
manages KV cache + latent collaboration, resolves conflicts.
"""

from typing import Dict, List, Optional, Any, Coroutine
from datetime import datetime
import json
import uuid


class SwarmOrchestrator:
    """
    Hierarchical orchestrator for multi-agent task decomposition and execution.

    Implements:
    - Tree of Thoughts (ToT) task decomposition
    - Decentralized task routing via gossip protocol
    - KV cache binding for all agents
    - Latent working memory coordination
    - Confidence-weighted consensus for conflicts
    """

    def __init__(self, kv_cache_manager, latent_memory, agent_pool, gossip_router, consensus_resolver):
        """
        Initialize orchestrator.

        Args:
            kv_cache_manager: KVCacheManager instance
            latent_memory: LatentWorkingMemory instance
            agent_pool: Dict mapping agent_id → SpecialistAgent instance
            gossip_router: GossipRouter for decentralized task routing
            consensus_resolver: ConfidenceWeightedConsensus for conflict resolution
        """
        self.kv_cache = kv_cache_manager
        self.latent_memory = latent_memory
        self.agents = agent_pool
        self.gossip_router = gossip_router
        self.consensus = consensus_resolver

        # Execution tracking
        self.trace_id = None
        self.execution_history = []
        self.session_metrics = {}

    def orchestrate_task(self, task_prompt: str, task_context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Execute full swarm task coordination.

        Args:
            task_prompt: Task description (e.g., "Analyze 6 watchlists for trading signals")
            task_context: Optional context dict (e.g., {"watchlists": [...], "period": "1mo"})

        Returns:
            Consolidated result dict with signals, metrics, conflicts resolved
        """
        self.trace_id = str(uuid.uuid4())
        start_time = datetime.utcnow()

        # 1. Decompose via Tree of Thoughts
        decomposition = self._decompose_via_tot(task_prompt, task_context or {})

        # 2. Initialize shared KV cache session
        cache_binding = self.kv_cache.create_session(
            shared_backbone=True,
            per_agent_lora=True
        )

        # 3. Initialize latent working memory session
        self.latent_memory.clear_all()

        # 4. Route subtasks to agents via gossip protocol
        dispatch_map = self.gossip_router.route_tasks(
            subtasks=decomposition["subtasks"],
            agent_pool=self.agents
        )

        # 5. Execute all agents in parallel with cache + latent sharing
        results = self._execute_swarm(
            dispatch_map=dispatch_map,
            cache_binding=cache_binding,
            task_context=task_context or {}
        )

        # 6. Resolve conflicts via confidence-weighted consensus
        consensus_result = self._resolve_conflicts(results)

        # 7. Finalize session and collect metrics
        self.kv_cache.finalize_session(cache_binding)
        final_metrics = self._collect_metrics(start_time, results, consensus_result)

        return {
            "trace_id": self.trace_id,
            "consensus": consensus_result,
            "all_results": results,
            "decomposition": decomposition,
            "metrics": final_metrics,
        }

    def _decompose_via_tot(self, task_prompt: str, task_context: Dict) -> Dict[str, Any]:
        """
        Decompose task via Tree of Thoughts reasoning.

        Simple heuristic: map task type to standard subtask patterns.
        In production, this would call Claude with explicit ToT reasoning.
        """
        task_lower = task_prompt.lower()

        # Heuristic: if "watchlist" and "signal", decompose to multi-analyst + catalyst + swing screener
        if "watchlist" in task_lower and ("signal" in task_lower or "vif" in task_lower):
            watchlists = task_context.get("watchlists", [])
            return {
                "task_type": "vif_analysis",
                "master_plan": f"Fan {len(watchlists)} VIF analysts + catalyst monitor + swing screener",
                "subtasks": [
                    {
                        "agent_type": "vif-analyst",
                        "watchlist": wl,
                        "context": task_context
                    }
                    for wl in watchlists
                ] + [
                    {
                        "agent_type": "catalyst-monitor",
                        "scope": "all_watchlists",
                        "context": task_context
                    },
                    {
                        "agent_type": "swing-screener",
                        "scope": "all_watchlists",
                        "context": task_context
                    }
                ]
            }

        # Default: single agent
        return {
            "task_type": "generic",
            "master_plan": "Single agent execution",
            "subtasks": [{"agent_type": "generic", "context": task_context}]
        }

    def _execute_swarm(self, dispatch_map: Dict, cache_binding: Any, task_context: Dict) -> Dict[str, Any]:
        """
        Execute all agents in parallel with KV cache + latent sharing.

        Args:
            dispatch_map: {agent_id: [subtasks]}
            cache_binding: Shared KV cache binding
            task_context: Task-level context dict

        Returns:
            {agent_id: result}
        """
        results = {}

        # In production, use asyncio.gather() for true parallelism
        # For now, sequential (but agents share cache + latent state)
        for agent_id, subtasks in dispatch_map.items():
            if agent_id not in self.agents:
                continue

            agent = self.agents[agent_id]

            # Execute agent with cache binding + latent memory context
            try:
                result = agent.execute(
                    subtasks=subtasks,
                    kv_cache_binding=cache_binding,
                    latent_memory=self.latent_memory,
                    task_context=task_context
                )
                results[agent_id] = {
                    "status": "success",
                    "result": result,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            except Exception as e:
                results[agent_id] = {
                    "status": "failed",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat(),
                }

        return results

    def _resolve_conflicts(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve disagreements between agents via confidence-weighted consensus.

        Example: If VIF-Analyst-1 says NVDA=BUY (90% confidence) and
        VIF-Analyst-2 says NVDA=HOLD (70% confidence), use BUY (higher confidence).
        """
        # Extract signals from all results
        all_signals = {}
        for agent_id, agent_result in results.items():
            if agent_result["status"] != "success":
                continue

            result = agent_result.get("result", {})
            signals = result.get("signals", {})

            for ticker, signal_data in signals.items():
                if ticker not in all_signals:
                    all_signals[ticker] = []
                all_signals[ticker].append({
                    "agent_id": agent_id,
                    "signal": signal_data.get("signal"),
                    "confidence": signal_data.get("confidence", 50),
                })

        # Apply consensus logic
        consensus = {}
        conflicts = []
        for ticker, agent_signals in all_signals.items():
            best = max(agent_signals, key=lambda x: x["confidence"])
            consensus[ticker] = best

            # Log conflict if agents disagreed
            if len(set(s["signal"] for s in agent_signals)) > 1:
                conflicts.append({
                    "ticker": ticker,
                    "agents": agent_signals,
                    "consensus": best,
                })

        return {
            "consensus_signals": consensus,
            "conflicts": conflicts,
            "conflict_count": len(conflicts),
        }

    def _collect_metrics(self, start_time: datetime, results: Dict, consensus: Dict) -> Dict[str, Any]:
        """Collect execution metrics for observability."""
        end_time = datetime.utcnow()
        duration_ms = (end_time - start_time).total_seconds() * 1000

        successful_agents = sum(1 for r in results.values() if r["status"] == "success")
        total_agents = len(results)

        return {
            "trace_id": self.trace_id,
            "duration_ms": duration_ms,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "agents_executed": successful_agents,
            "agents_total": total_agents,
            "success_rate": successful_agents / total_agents if total_agents > 0 else 0,
            "kv_cache_hit_rate": self.kv_cache.global_hit_rate(),
            "consensus_conflicts": consensus.get("conflict_count", 0),
            "latent_memory_metrics": self.latent_memory.metrics(),
        }
