#!/usr/bin/env python3
"""
Unit and integration tests for CriticAgent (Planner-Critic-Executor pattern).

Tests veto logic, downgrade rules, hidden state encoding, and latent context propagation.
"""

import sys
import unittest
from pathlib import Path
import numpy as np

# Ensure swarm module is importable
sys.path.insert(0, str(Path(__file__).parent.parent))

from swarm import (
    CriticAgent,
    KVCacheManager,
    LatentWorkingMemory,
)


class TestCriticVetoLogic(unittest.TestCase):
    """Unit tests for CriticAgent._veto_logic() method."""

    def setUp(self):
        self.critic = CriticAgent("test-critic")

    def test_veto_k4_earnings_risk(self):
        """VETO condition: K4 earnings risk."""
        signal = {
            "signal": "BUY",
            "confidence": 85,
            "rsi": 60,
            "volume_signal": "normal",
            "kill_switch": None,
        }
        result = self.critic._veto_logic("TSLA", signal, k4_tickers={"TSLA"})

        self.assertTrue(result["veto"])
        self.assertFalse(result["downgrade"])
        self.assertIn("K4 earnings risk", result["reason"])

    def test_veto_rsi_extreme_overbought(self):
        """VETO condition: RSI >85 on BUY signal."""
        signal = {
            "signal": "BUY",
            "confidence": 85,
            "rsi": 88,
            "volume_signal": "normal",
            "kill_switch": None,
        }
        result = self.critic._veto_logic("NVDA", signal, k4_tickers=set())

        self.assertTrue(result["veto"])
        self.assertFalse(result["downgrade"])
        self.assertIn("RSI >85", result["reason"])

    def test_veto_weak_volume_on_buy(self):
        """VETO condition: Weak volume on BUY signal."""
        signal = {
            "signal": "BUY",
            "confidence": 75,
            "rsi": 60,
            "volume_signal": "weak",
            "kill_switch": None,
        }
        result = self.critic._veto_logic("AAPL", signal, k4_tickers=set())

        self.assertTrue(result["veto"])
        self.assertFalse(result["downgrade"])
        self.assertIn("Weak volume", result["reason"])

    def test_veto_kill_switch_active(self):
        """VETO condition: Any existing kill switch."""
        signal = {
            "signal": "SELL",
            "confidence": 70,
            "rsi": 40,
            "volume_signal": "normal",
            "kill_switch": "K2",
        }
        result = self.critic._veto_logic("MSFT", signal, k4_tickers=set())

        self.assertTrue(result["veto"])
        self.assertFalse(result["downgrade"])
        self.assertIn("Kill switch K2", result["reason"])

    def test_downgrade_rsi_moderate_overbought(self):
        """DOWNGRADE condition: RSI 75–85 on high-confidence BUY."""
        signal = {
            "signal": "BUY",
            "confidence": 80,
            "rsi": 77,
            "volume_signal": "normal",
            "kill_switch": None,
        }
        result = self.critic._veto_logic("META", signal, k4_tickers=set())

        self.assertFalse(result["veto"])
        self.assertTrue(result["downgrade"])
        self.assertIn("RSI >75", result["reason"])

    def test_downgrade_rsi_extreme_oversold_on_sell(self):
        """DOWNGRADE condition: RSI <20 on SELL (extreme oversold, potential bounce)."""
        signal = {
            "signal": "SELL",
            "confidence": 75,
            "rsi": 15,
            "volume_signal": "normal",
            "kill_switch": None,
        }
        result = self.critic._veto_logic("AMD", signal, k4_tickers=set())

        self.assertFalse(result["veto"])
        self.assertTrue(result["downgrade"])
        self.assertIn("RSI <20", result["reason"])

    def test_downgrade_strong_volume_on_sell(self):
        """DOWNGRADE condition: Strong volume on SELL (bullish reversal signal)."""
        signal = {
            "signal": "SELL",
            "confidence": 70,
            "rsi": 50,
            "volume_signal": "strong",
            "kill_switch": None,
        }
        result = self.critic._veto_logic("GOOGL", signal, k4_tickers=set())

        self.assertFalse(result["veto"])
        self.assertTrue(result["downgrade"])
        self.assertIn("Strong volume", result["reason"])

    def test_pass_normal_conditions(self):
        """PASS condition: No veto or downgrade triggers."""
        signal = {
            "signal": "BUY",
            "confidence": 75,
            "rsi": 65,
            "volume_signal": "normal",
            "kill_switch": None,
        }
        result = self.critic._veto_logic("NFLX", signal, k4_tickers=set())

        self.assertFalse(result["veto"])
        self.assertFalse(result["downgrade"])
        self.assertIn("Passed critic review", result["reason"])


class TestCriticDowngrade(unittest.TestCase):
    """Unit tests for CriticAgent._apply_downgrade() method."""

    def setUp(self):
        self.critic = CriticAgent("test-critic")

    def test_downgrade_reduces_confidence_25_percent(self):
        """Downgrade should reduce confidence by 25% (multiply by 0.75)."""
        signal = {
            "signal": "BUY",
            "confidence": 80,
            "rsi": 60,
        }
        downgraded = self.critic._apply_downgrade(signal, "RSI >75 (overbought) — downgrade to 60%")

        self.assertEqual(downgraded["original_confidence"], 80)
        self.assertEqual(downgraded["confidence"], 60)  # 80 * 0.75
        self.assertIn("RSI >75", downgraded["veto_reason"])

    def test_downgrade_preserves_other_fields(self):
        """Downgrade should preserve all original signal fields."""
        signal = {
            "signal": "SELL",
            "confidence": 70,
            "rsi": 15,
            "price": 150.0,
            "note": "Support failure",
        }
        downgraded = self.critic._apply_downgrade(signal, "RSI <20")

        self.assertEqual(downgraded["signal"], "SELL")
        self.assertEqual(downgraded["price"], 150.0)
        self.assertEqual(downgraded["note"], "Support failure")


class TestCriticHiddenStates(unittest.TestCase):
    """Unit tests for CriticAgent._encode_hidden_states() method."""

    def setUp(self):
        self.critic = CriticAgent("test-critic")

    def test_hidden_state_layer_8_shape_and_dtype(self):
        """Layer 8 should be (4,) float32: [vetoed_frac, downgraded_frac, passed_frac, k4_overlap]."""
        vetoed = {"TSLA": {}, "META": {}}
        downgraded = {"NVDA": {}}
        passed = {"AAPL": {}, "MSFT": {}, "GOOGL": {}}

        hidden_states = self.critic._encode_hidden_states(vetoed, downgraded, passed)

        h8 = hidden_states[8]
        self.assertEqual(h8.shape, (4,))
        self.assertEqual(h8.dtype, np.float32)
        # Check fractions sum to 1.0 (approximately)
        self.assertAlmostEqual(h8[0] + h8[1] + h8[2], 1.0, places=5)

    def test_hidden_state_layer_16_shape_and_dtype(self):
        """Layer 16 should be (3,) float32: [avg_orig_conf, avg_downgraded_conf, veto_rate]."""
        vetoed = {"TSLA": {}}
        downgraded = {"NVDA": {"confidence": 60, "original_confidence": 80}}
        passed = {"AAPL": {"confidence": 75}, "MSFT": {"confidence": 85}}

        hidden_states = self.critic._encode_hidden_states(vetoed, downgraded, passed)

        h16 = hidden_states[16]
        self.assertEqual(h16.shape, (3,))
        self.assertEqual(h16.dtype, np.float32)
        # All values should be in [0, 1]
        self.assertTrue(np.all(h16 >= 0) and np.all(h16 <= 1))

    def test_hidden_state_layer_24_shape_and_dtype(self):
        """Layer 24 should be (32,) float32 zero-padded veto intensity vector."""
        vetoed = {f"TICK{i}": {} for i in range(50)}
        downgraded = {}
        passed = {}

        hidden_states = self.critic._encode_hidden_states(vetoed, downgraded, passed)

        h24 = hidden_states[24]
        self.assertEqual(h24.shape, (32,))
        self.assertEqual(h24.dtype, np.float32)
        # First 32 should be 1.0 (marked as vetoed), rest zeros
        self.assertEqual(np.sum(h24), 32.0)

    def test_hidden_states_all_present(self):
        """All three layers (8, 16, 24) must be present in output."""
        vetoed, downgraded, passed = {}, {}, {}
        hidden_states = self.critic._encode_hidden_states(vetoed, downgraded, passed)

        self.assertIn(8, hidden_states)
        self.assertIn(16, hidden_states)
        self.assertIn(24, hidden_states)


class TestCriticExecution(unittest.TestCase):
    """Integration tests for CriticAgent._execute_subtasks() method."""

    def setUp(self):
        self.critic = CriticAgent("test-critic")
        self.kv_cache = KVCacheManager(max_cache_mb=100)
        self.latent_memory = LatentWorkingMemory(layers_to_share=[8, 16, 24])
        self.cache_binding = self.kv_cache.create_session("test-critic")

    def test_execute_with_vif_signals(self):
        """Full execution: review simulated VIF signals, apply veto logic, encode hidden states."""
        vif_signals = {
            "NVDA": {
                "signal": "BUY",
                "confidence": 85,
                "rsi": 88,  # Extreme overbought
                "volume_signal": "normal",
                "kill_switch": None,
            },
            "TSLA": {
                "signal": "SELL",
                "confidence": 70,
                "rsi": 15,  # Extreme oversold
                "volume_signal": "normal",
                "kill_switch": None,
            },
            "AAPL": {
                "signal": "BUY",
                "confidence": 75,
                "rsi": 65,  # Normal
                "volume_signal": "normal",
                "kill_switch": None,
            },
        }

        subtasks = [{"signals": vif_signals}]
        result = self.critic._execute_subtasks(subtasks, latent_context={})

        # Validate result structure
        self.assertIn("signals", result)
        self.assertIn("metrics", result)
        self.assertIn("hidden_states", result)

        # Check metrics
        metrics = result["metrics"]
        self.assertEqual(metrics["signals_reviewed"], 3)
        self.assertGreater(metrics["signals_vetoed"], 0)
        self.assertGreater(metrics["signals_downgraded"], 0)

    def test_execute_with_k4_override(self):
        """Execute with K4 K4 tickers in KV cache (LoRA layer 2)."""
        vif_signals = {
            "TSLA": {
                "signal": "BUY",
                "confidence": 85,
                "rsi": 70,
                "volume_signal": "normal",
                "kill_switch": None,
            },
        }

        # Write K4 tickers to KV cache (what catalyst monitor would do)
        k4_signals = {"TSLA": {"kill_switch": "K4"}}
        self.cache_binding.put(layer=2, value=k4_signals, key="signals_catalyst-monitor", shared=False)

        # Execute critic with cache binding
        self.critic.kv_cache_binding = self.cache_binding
        subtasks = [{"signals": vif_signals}]
        result = self.critic._execute_subtasks(subtasks, latent_context={})

        # TSLA should be vetoed due to K4
        self.assertEqual(result["metrics"]["signals_vetoed"], 1)

    def test_execute_writes_latent_memory(self):
        """Execute should write hidden states to latent memory."""
        vif_signals = {
            "NVDA": {"signal": "BUY", "confidence": 75, "rsi": 60, "volume_signal": "normal", "kill_switch": None},
        }

        self.critic.latent_memory = self.latent_memory
        subtasks = [{"signals": vif_signals}]
        result = self.critic._execute_subtasks(subtasks, latent_context={})

        # Check that hidden states were written
        self.assertIn("hidden_states", result)
        self.assertIn(8, result["hidden_states"])
        self.assertIn(16, result["hidden_states"])
        self.assertIn(24, result["hidden_states"])


class TestCriticIntegration(unittest.TestCase):
    """End-to-end integration tests for Planner-Critic-Executor pattern."""

    def test_critic_reduces_false_signals(self):
        """Critic should reduce false signals (realistic scenario: 3 BUY signals → 1 passed, 1 downgraded, 1 vetoed)."""
        critic = CriticAgent("critic")

        # Simulated VIF output: 3 BUY signals with varying quality
        vif_signals = {
            "TSLA": {  # High-quality BUY
                "signal": "BUY",
                "confidence": 85,
                "rsi": 60,
                "volume_signal": "strong",
                "kill_switch": None,
            },
            "NVDA": {  # Overbought BUY (should be downgraded)
                "signal": "BUY",
                "confidence": 80,
                "rsi": 78,
                "volume_signal": "normal",
                "kill_switch": None,
            },
            "META": {  # Extreme overbought BUY (should be vetoed)
                "signal": "BUY",
                "confidence": 75,
                "rsi": 88,
                "volume_signal": "weak",
                "kill_switch": None,
            },
        }

        subtasks = [{"signals": vif_signals}]
        result = critic._execute_subtasks(subtasks, latent_context={})

        metrics = result["metrics"]

        # Expected: 1 passed, 1 downgraded, 1 vetoed
        self.assertEqual(metrics["signals_reviewed"], 3)
        self.assertEqual(metrics["signals_vetoed"], 1)  # META (extreme overbought)
        self.assertEqual(metrics["signals_downgraded"], 1)  # NVDA (moderate overbought)
        self.assertEqual(metrics["signals_passed"], 1)  # TSLA (high quality)

        # Veto rate should be 33% (1/3)
        self.assertAlmostEqual(metrics["veto_rate"], 1 / 3, places=2)


if __name__ == "__main__":
    unittest.main()
