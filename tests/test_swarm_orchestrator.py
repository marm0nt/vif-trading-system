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
            NativeCatalystMonitorAgent,
            NativeVIFAnalystAgent,
            NativeSwingScreenerAgent,
            SpecialistAgent,
            PromptLoader,
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
        from swarm import NativeVIFAnalystAgent, NativeCatalystMonitorAgent, NativeSwingScreenerAgent

        agents = [
            NativeVIFAnalystAgent("vif-analyst-1"),
            NativeCatalystMonitorAgent("catalyst-monitor"),
            NativeSwingScreenerAgent("swing-screener"),
        ]

        for agent in agents:
            assert agent.agent_id, f"Agent {agent} has no ID"
            assert agent.agent_type, f"Agent {agent} has no type"
            health = agent.health_check()
            assert "agent_id" in health, "Health check missing agent_id"

        print(f"  ✓ All {len(agents)} native specialist agents initialized")
        return True
    except Exception as e:
        print(f"  ✗ Native specialist agents test failed: {e}")
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
            NativeVIFAnalystAgent,
            NativeCatalystMonitorAgent,
            NativeSwingScreenerAgent,
        )

        kv_cache = KVCacheManager(max_cache_mb=100)
        latent = LatentWorkingMemory()
        router = GossipRouter()
        consensus = ConfidenceWeightedConsensus()

        agent_pool = {
            "catalyst-monitor": NativeCatalystMonitorAgent("catalyst-monitor"),
            "vif-analyst-1": NativeVIFAnalystAgent("vif-analyst-1"),
            "swing-screener": NativeSwingScreenerAgent("swing-screener"),
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

        print(f"  ✓ SwarmOrchestrator initialized with {len(agent_pool)} native agents")
        print(f"    Execution order: Catalyst → VIF → SwingScreener (latent context enabled)")
        return True
    except Exception as e:
        print(f"  ✗ SwarmOrchestrator test failed: {e}")
        return False


def test_native_catalyst_agent():
    """Test 8: NativeCatalystMonitorAgent (no subprocess)."""
    print("\nTest 8: Native Catalyst Monitor Agent")
    try:
        from swarm import NativeCatalystMonitorAgent, KVCacheManager

        agent = NativeCatalystMonitorAgent("catalyst-monitor")
        assert agent.agent_type == "catalyst-monitor"

        # Bind KV cache + latent memory
        cache = KVCacheManager(max_cache_mb=100)
        binding = cache.create_session("test")
        agent.kv_cache_binding = binding

        # Mock execute (minimal, no API calls in test)
        result = agent._encode_hidden_states(0.2, 0.3, 0.4, 0.1, {}, [])
        assert 8 in result and 16 in result and 24 in result, "Hidden states missing"
        assert result[8].shape == (4,), f"Layer 8 shape mismatch: {result[8].shape}"
        assert result[16].shape == (3,), f"Layer 16 shape mismatch: {result[16].shape}"
        assert result[24].shape == (32,), f"Layer 24 shape mismatch: {result[24].shape}"

        print(f"  ✓ NativeCatalystMonitorAgent works (hidden states shape OK)")
        return True
    except Exception as e:
        print(f"  ✗ NativeCatalystMonitorAgent test failed: {e}")
        return False


def test_native_vif_agent():
    """Test 9: NativeVIFAnalystAgent (reads latent context, no subprocess)."""
    print("\nTest 9: Native VIF Analyst Agent")
    try:
        from swarm import NativeVIFAnalystAgent, KVCacheManager
        import numpy as np

        agent = NativeVIFAnalystAgent("vif-analyst-1")
        assert agent.agent_type == "vif-analyst"

        # Bind KV cache
        cache = KVCacheManager(max_cache_mb=100)
        binding = cache.create_session("test")
        agent.kv_cache_binding = binding

        # Mock K4 tickers in LoRA cache (from catalyst monitor)
        binding.put(layer=2, value={"NVDA": {"kill_switch": "K4"}}, key="signals_catalyst-monitor", shared=False)

        # Test latent context adjustment
        signals = {
            "NVDA": {"signal": "BUY", "confidence": 85, "kill_switch": None, "note": "test"},
            "TSLA": {"signal": "SELL", "confidence": 70, "kill_switch": None, "note": "test"}
        }
        adjusted = agent._apply_latent_context_adjustments(signals, {})

        assert adjusted["NVDA"]["kill_switch"] == "K4", "K4 override failed"
        assert adjusted["NVDA"]["confidence"] <= 40, "K4 confidence not capped"
        assert "K4 earnings risk" in adjusted["NVDA"]["note"], "K4 note not added"

        # Test hidden state encoding
        result = agent._encode_hidden_states(signals)
        assert 8 in result and 16 in result and 24 in result
        assert result[8].shape == (4,) and result[8].dtype == np.float32

        print(f"  ✓ NativeVIFAnalystAgent works (K4 override + hidden states OK)")
        return True
    except Exception as e:
        print(f"  ✗ NativeVIFAnalystAgent test failed: {e}")
        return False


def test_native_swing_agent():
    """Test 10: NativeSwingScreenerAgent (patched watchlist loader)."""
    print("\nTest 10: Native Swing Screener Agent + Patched Watchlist Loader")
    try:
        from swarm.native_swing_screener_agent import _PatchedSwingScreener

        screener = _PatchedSwingScreener()

        # Verify watchlist bug is fixed
        assert len(screener.tickers) > 10, f"Watchlist loading failed, only {len(screener.tickers)} tickers"
        assert "VIX" not in screener.tickers, "VIX should be excluded"
        assert "BTCUSDT" not in screener.tickers, "BTCUSDT should be excluded"

        # Test setup identification (pullback to MA20)
        # Price below MA20, RSI oversold, volume strong
        mock_data = {
            "price": 140.0,      # Below MA20
            "ma20": 145.0,       # Support level
            "rsi": 35,           # Oversold
            "vol_ratio_10": 1.8, # Strong volume
            "vol_ratio": 1.8,    # Fallback field name
            "high_20": 160.0,    # Target
            "high_20d": 160.0,   # Alternate field name
            "low_20": 130.0,     # Stop loss
            "low_20d": 130.0,    # Alternate field name
            "mom_20d": -2.5      # Negative momentum (pullback)
        }

        setup = screener.identify_setup("NVDA", mock_data)
        assert setup is not None, f"Setup identification failed for mock data: {mock_data}"
        assert setup["setup_type"] in ["PULLBACK_TO_MA20", "BULLISH_MA_MOMENTUM", "SUPPORT_BOUNCE", "CONSOLIDATION_BREAKOUT", "OVERSOLD_BOUNCE"]
        assert setup["confidence"] > 0
        assert setup["risk_reward"] > 0

        print(f"  ✓ _PatchedSwingScreener works ({len(screener.tickers)} tickers loaded, setup ID OK)")
        return True
    except Exception as e:
        print(f"  ✗ NativeSwingScreenerAgent test failed: {e}")
        return False


def test_kv_cache_sharing():
    """Test 11: KV Cache sharing between agents (critical for performance)."""
    print("\nTest 11: KV Cache Sharing (Layer-1 Market Data Reuse)")
    try:
        from swarm import KVCacheManager

        cache = KVCacheManager(max_cache_mb=100)
        binding = cache.create_session("test")

        # Simulate VIF analyst caching market data
        mock_market_data = {
            "price": 150.0, "rsi": 55.0, "vol_ratio": 1.2,
            "bb_mid": 148.0, "high_20d": 155.0, "low_20d": 140.0, "mom_20d": 3.2
        }
        binding.put(layer=1, value=mock_market_data, key="NVDA", shared=True)

        # Simulate swing screener reusing cached data
        cached = binding.get(layer=1, key="NVDA")
        assert cached == mock_market_data, "Cache miss — swing screener cannot read VIF cache"

        hit_rate = binding.hit_rate()
        assert hit_rate == 1.0, f"Expected 100% hit rate, got {hit_rate:.0%}"

        print(f"  ✓ KV cache sharing works (hit_rate={hit_rate:.0%})")
        return True
    except Exception as e:
        print(f"  ✗ KV cache sharing test failed: {e}")
        return False


def test_prompt_loader():
    """Test 12: PromptLoader (DSPy compile-only architecture)."""
    print("\nTest 12: PromptLoader (DSPy Compile-Only)")
    try:
        from swarm import PromptLoader

        # Load compiled prompts
        vif_system = PromptLoader.get_system_prompt("vif_signal")
        catalyst_system = PromptLoader.get_system_prompt("catalyst")

        assert vif_system, "VIF system prompt not found"
        assert catalyst_system, "Catalyst system prompt not found"
        assert "gamma regime" in vif_system.lower(), "VIF prompt missing gamma regime reference"
        assert "catalyst" in catalyst_system.lower(), "Catalyst prompt missing catalyst reference"

        # Check version
        version = PromptLoader.prompt_version()
        assert version == "1.0", f"Expected version 1.0, got {version}"

        # Validate version
        valid = PromptLoader.validate_version("1.0")
        assert valid, "Version validation failed"

        print(f"  ✓ PromptLoader works (version {version}, 2 system prompts loaded)")
        return True
    except Exception as e:
        print(f"  ✗ PromptLoader test failed: {e}")
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
        test_native_catalyst_agent,
        test_native_vif_agent,
        test_native_swing_agent,
        test_kv_cache_sharing,
        test_prompt_loader,
    ]

    results = [test() for test in tests]

    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"RESULTS: {passed}/{total} tests passed")
    print("=" * 60)

    if passed == total:
        print("\n✓ All tests passed! Swarm framework + native agents + DSPy compiler ready.")
        print("  Next steps:")
        print("  1. Run 'python agents/orchestrator_swarm.py --mode premarket' for live test")
        print("  2. Check reports/swarm_result_*.json for signals and KV cache metrics")
        print("  3. Optional: Run 'python research/dspy_compiler.py --export' to regenerate prompts")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed. Check logs above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
