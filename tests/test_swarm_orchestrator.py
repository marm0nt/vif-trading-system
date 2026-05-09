#!/usr/bin/env python3
"""
Test Swarm Orchestrator - Validate Phase 3 integration

Quick validation of swarm framework before production deployment.
Run: python tests/test_swarm_orchestrator.py
"""

import sys
import json
from pathlib import Path

# Add repo to path
sys.path.insert(0, str(Path.cwd()))


def test_imports():
    """Test that all swarm components can be imported."""
    print("Test 1: Swarm Framework Imports")
    try:
        from swarm import (
            SwarmOrchestrator,
            KVCacheManager,
            LatentWorkingMemory,
            GossipRouter,
            ConfidenceWeightedConsensus,
            VIFAnalystAgent,
            CatalystMonitorAgent,
            SwingScreenerAgent,
            SpecialistAgent,
        )
        print("  ✓ All swarm components imported successfully")
        return True
    except ImportError as e:
        print(f"  ✗ Import failed: {e}")
        return False


def test_kv_cache():
    """Test KV cache manager."""
    print("\nTest 2: KV Cache Manager")
    try:
        from swarm import KVCacheManager

        cache_mgr = KVCacheManager(max_cache_mb=100)
        binding = cache_mgr.create_session("test-agent-1")

        # Test put/get
        binding.put(layer=8, value="test_tensor_8", shared=True)
        binding.put(layer=16, value="test_tensor_16", shared=False)

        val_8 = binding.get(layer=8)
        val_16 = binding.get(layer=16)

        assert val_8 == "test_tensor_8", "Shared cache get failed"
        assert val_16 == "test_tensor_16", "LoRA cache get failed"

        print(f"  ✓ KV cache binding works (hit_rate: {binding.hit_rate():.1%})")

        cache_mgr.finalize_session(binding)
        metrics = cache_mgr.metrics()
        print(f"  ✓ Cache metrics: sessions={metrics['sessions_created']}, hit_rate={metrics['global_hit_rate']:.1%}")
        return True
    except Exception as e:
        print(f"  ✗ KV cache test failed: {e}")
        return False


def test_latent_memory():
    """Test latent working memory."""
    print("\nTest 3: Latent Working Memory")
    try:
        from swarm import LatentWorkingMemory

        latent = LatentWorkingMemory(layers_to_share=[8, 16, 24])

        # Agent 1 writes states
        latent.write_hidden_states("agent-1", {
            8: "agent1_layer8_tensor",
            16: "agent1_layer16_tensor",
            24: "agent1_layer24_tensor",
        })

        # Agent 2 reads states
        states = latent.read_hidden_states("agent-2", source_agents=["agent-1"])

        assert 8 in states, "Layer 8 not found in read states"
        assert states[8] == "agent1_layer8_tensor", "Layer 8 tensor mismatch"

        print(f"  ✓ Latent state write/read works")

        metrics = latent.metrics()
        print(f"  ✓ Latent metrics: stored={metrics['total_states_stored']}, agents={metrics['active_agents']}")
        return True
    except Exception as e:
        print(f"  ✗ Latent memory test failed: {e}")
        return False


def test_consensus():
    """Test confidence-weighted consensus."""
    print("\nTest 4: Confidence-Weighted Consensus")
    try:
        from swarm import ConfidenceWeightedConsensus

        consensus = ConfidenceWeightedConsensus()

        # Simulate 3 agents disagreeing on NVDA
        agent_signals = {
            "NVDA": [
                {"agent_id": "agent-1", "signal": "BUY", "confidence": 85},
                {"agent_id": "agent-2", "signal": "HOLD", "confidence": 70},
                {"agent_id": "agent-3", "signal": "BUY", "confidence": 90},
            ]
        }

        result = consensus.resolve(agent_signals)
        consensus_signal = result["consensus_signals"]["NVDA"]

        assert consensus_signal["signal"] == "BUY", "Should resolve to BUY (highest confidence)"
        assert consensus_signal["confidence"] == 90, "Should use agent-3's confidence"
        assert result["conflict_count"] == 1, "Should detect conflict"

        print(f"  ✓ Consensus resolution works")
        print(f"  ✓ Conflicts logged: {result['conflict_count']}")
        return True
    except Exception as e:
        print(f"  ✗ Consensus test failed: {e}")
        return False


def test_gossip_router():
    """Test gossip-based task routing."""
    print("\nTest 5: Gossip Router")
    try:
        from swarm import GossipRouter, SpecialistAgent

        router = GossipRouter()

        # Create mock agent pool
        class MockAgent(SpecialistAgent):
            def _execute_subtasks(self, subtasks, latent_context):
                return {"signals": {}, "metrics": {}, "hidden_states": {}}

        agent_pool = {
            "vif-analyst-1": MockAgent("vif-analyst-1", "vif-analyst", "Test VIF Agent"),
            "catalyst-monitor": MockAgent("catalyst-monitor", "catalyst-monitor", "Test Catalyst Agent"),
        }

        # Create subtasks
        subtasks = [
            {"agent_type": "vif-analyst", "watchlist": "test_1"},
            {"agent_type": "catalyst-monitor", "scope": "all"},
        ]

        # Route tasks
        dispatch = router.route_tasks(subtasks, agent_pool)

        assert isinstance(dispatch, dict), "Dispatch map should be dict"
        assert len(dispatch) > 0, "Should have routing results"

        print(f"  ✓ Gossip router routing works")

        metrics = router.metrics()
        print(f"  ✓ Router metrics: gossip_events={metrics['total_gossip_events']}, acceptance_rate={metrics['acceptance_rate']:.1%}")
        return True
    except Exception as e:
        print(f"  ✗ Gossip router test failed: {e}")
        return False


def test_specialist_agents():
    """Test specialist agent wrappers."""
    print("\nTest 6: Specialist Agents")
    try:
        from swarm import VIFAnalystAgent, CatalystMonitorAgent, SwingScreenerAgent

        agents = [
            VIFAnalystAgent("vif-analyst-1"),
            CatalystMonitorAgent("catalyst-monitor"),
            SwingScreenerAgent("swing-screener"),
        ]

        for agent in agents:
            assert agent.agent_id, f"Agent {agent} has no ID"
            assert agent.agent_type, f"Agent {agent} has no type"
            health = agent.health_check()
            assert "agent_id" in health, "Health check missing agent_id"

        print(f"  ✓ All {len(agents)} specialist agents initialized")
        return True
    except Exception as e:
        print(f"  ✗ Specialist agents test failed: {e}")
        return False


def test_orchestrator():
    """Test SwarmOrchestrator initialization."""
    print("\nTest 7: SwarmOrchestrator")
    try:
        from swarm import (
            SwarmOrchestrator,
            KVCacheManager,
            LatentWorkingMemory,
            GossipRouter,
            ConfidenceWeightedConsensus,
            VIFAnalystAgent,
            CatalystMonitorAgent,
            SwingScreenerAgent,
        )

        kv_cache = KVCacheManager(max_cache_mb=100)
        latent = LatentWorkingMemory()
        router = GossipRouter()
        consensus = ConfidenceWeightedConsensus()

        agent_pool = {
            "vif-analyst-1": VIFAnalystAgent("vif-analyst-1"),
            "catalyst-monitor": CatalystMonitorAgent("catalyst-monitor"),
            "swing-screener": SwingScreenerAgent("swing-screener"),
        }

        orchestrator = SwarmOrchestrator(
            kv_cache_manager=kv_cache,
            latent_memory=latent,
            agent_pool=agent_pool,
            gossip_router=router,
            consensus_resolver=consensus,
        )

        assert orchestrator.agents, "Orchestrator has no agents"
        assert orchestrator.kv_cache, "Orchestrator has no KV cache"

        print(f"  ✓ SwarmOrchestrator initialized with {len(agent_pool)} agents")
        return True
    except Exception as e:
        print(f"  ✗ SwarmOrchestrator test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("SWARM ORCHESTRATOR - PHASE 3 INTEGRATION TESTS")
    print("=" * 60)

    tests = [
        test_imports,
        test_kv_cache,
        test_latent_memory,
        test_consensus,
        test_gossip_router,
        test_specialist_agents,
        test_orchestrator,
    ]

    results = [test() for test in tests]

    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"RESULTS: {passed}/{total} tests passed")
    print("=" * 60)

    if passed == total:
        print("\n✓ All tests passed! Swarm framework is ready for production.")
        print("  Next: Run 'python agents/orchestrator_swarm.py --mode premarket'")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed. Check logs above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
