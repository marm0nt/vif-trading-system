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
            agent_id="swarm-orchestrator",
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

    # Canonical execution order — agents run sequentially so each can read prior results
    AGENT_EXECUTION_ORDER = [
        "catalyst-monitor",   # 1. K4 kill-switch flags → LoRA cache layer 2
        "vif-analyst-1",      # 2. Signals → task_context["vif_signals"] + KV layer 1
        "critic",             # 3. Reads vif_signals, vetoes/downgrades → task_context["critic_signals"]
        "vectorbt-backtester",# 4. Backtests critic-passed signals → flags poor Sharpe/drawdown
        "signal-verifier",    # 5. 4-gate PUBLISH/DOWNGRADE/REJECT → task_context["verified_signals"]
        "swing-screener",     # 6. Reuses KV layer 1 market data
        "finviz-screener",    # 7. Local discovery (0 tokens)
        "autoresearch",       # 8. Iterative synthesis for low-confidence signals
        "risk-agent",         # 9. Circuit breaker + risk mitigation (final gate)
    ]

    def _execute_swarm(self, dispatch_map: Dict, cache_binding: Any, task_context: Dict) -> Dict[str, Any]:
        """
        Execute agents sequentially in AGENT_EXECUTION_ORDER so each agent
        can read prior agents' results via task_context injection.

        Args:
            dispatch_map: {agent_id: [subtasks]} from gossip router
            cache_binding: Shared KV cache binding
            task_context: Task-level context dict (mutated in-place with agent outputs)

        Returns:
            {agent_id: result}
        """
        results = {}
        live_context = dict(task_context)  # mutable copy — accumulates inter-agent signals

        for agent_id in self.AGENT_EXECUTION_ORDER:
            if agent_id not in self.agents:
                continue
            subtasks = dispatch_map.get(agent_id, [{}])

            agent = self.agents[agent_id]
            try:
                result = agent.execute(
                    subtasks=subtasks,
                    kv_cache_binding=cache_binding,
                    latent_memory=self.latent_memory,
                    task_context=live_context,
                )
                results[agent_id] = {
                    "status": "success",
                    "result": result,
                    "timestamp": datetime.utcnow().isoformat(),
                }
                # Inject this agent's signals into live_context for downstream agents
                if isinstance(result, dict) and result.get("signals"):
                    if agent_id == "vif-analyst-1":
                        live_context["vif_signals"] = result["signals"]
                    elif agent_id == "critic":
                        live_context["critic_signals"] = result["signals"]
                    elif agent_id == "signal-verifier":
                        live_context["verified_signals"] = result["signals"]
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
