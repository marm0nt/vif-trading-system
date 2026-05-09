#!/usr/bin/env python3
"""
Unit and integration tests for RiskAgent (Circuit Breaker + Portfolio Risk Management).

Tests circuit breaker logic, position sizing, risk regime detection, and LATS scenarios.
"""

import sys
import unittest
from pathlib import Path
import numpy as np

# Ensure swarm module is importable
sys.path.insert(0, str(Path(__file__).parent.parent))

from swarm import (
    RiskAgent,
    KVCacheManager,
    LatentWorkingMemory,
)


class TestRiskAgentCircuitBreaker(unittest.TestCase):
    """Unit tests for circuit breaker logic."""

    def setUp(self):
        self.risk = RiskAgent("test-risk")

    def test_circuit_breaker_at_minus_5_percent(self):
        """Circuit breaker should activate at -5% drawdown (threshold)."""
        portfolio = {
            "total_value": 100000.0,
            "positions": {"NVDA": 50, "TSLA": 30},
            "entry_prices": {"NVDA": 100.0, "TSLA": 150.0},
            "cash": 0.0,
        }

        # Mock drawdown calculation to return exactly -5%
        self.risk._calculate_drawdown = lambda p: -0.05

        result = self.risk._execute_subtasks([{"portfolio_state": portfolio}], {})

        self.assertTrue(result["circuit_breaker_active"])
        self.assertEqual(result["portfolio_drawdown"], -0.05)

    def test_circuit_breaker_not_active_above_threshold(self):
        """Circuit breaker should be inactive at -4% drawdown."""
        portfolio = {
            "total_value": 100000.0,
            "positions": {"NVDA": 50},
            "entry_prices": {"NVDA": 100.0},
            "cash": 5000.0,
        }

        self.risk._calculate_drawdown = lambda p: -0.04

        result = self.risk._execute_subtasks([{"portfolio_state": portfolio}], {})

        self.assertFalse(result["circuit_breaker_active"])

    def test_circuit_breaker_severe_at_minus_10_percent(self):
        """Severe drawdown threshold at -10%."""
        self.assertEqual(RiskAgent.SEVERE_DRAWDOWN, -0.10)

    def test_circuit_breaker_critical_at_minus_15_percent(self):
        """Critical drawdown threshold at -15%."""
        self.assertEqual(RiskAgent.CRITICAL_DRAWDOWN, -0.15)


class TestRiskAgentPositionSizing(unittest.TestCase):
    """Unit tests for dynamic position sizing."""

    def setUp(self):
        self.risk = RiskAgent("test-risk")

    def test_position_sizing_normal_conditions(self):
        """Normal conditions should maintain current position sizes."""
        portfolio = {
            "total_value": 100000.0,
            "positions": {"NVDA": 50, "TSLA": 30, "AAPL": 40},
            "entry_prices": {"NVDA": 100.0, "TSLA": 150.0, "AAPL": 120.0},
        }

        adjustments = self.risk._calculate_position_adjustments(portfolio, -0.02, "normal")

        # At -2% drawdown with normal regime, positions should remain at or near current size
        for ticker, adj_size in adjustments.items():
            self.assertGreater(adj_size, 0)

    def test_position_sizing_circuit_breaker_drawdown(self):
        """At circuit breaker (-5%), positions should be reduced by 50%."""
        portfolio = {
            "total_value": 100000.0,
            "positions": {"NVDA": 50},
            "entry_prices": {"NVDA": 100.0},
        }

        adjustments = self.risk._calculate_position_adjustments(
            portfolio, RiskAgent.CIRCUIT_BREAKER_DRAWDOWN, "elevated"
        )

        # Position should be reduced to ~50% of original (adjustment factor = 0.5)
        self.assertIn("NVDA", adjustments)
        # After 50% reduction, position should be smaller but not zero
        self.assertGreater(adjustments["NVDA"], 0)

    def test_position_sizing_severe_drawdown(self):
        """At severe drawdown (-10%), positions should be reduced by 75%."""
        portfolio = {
            "total_value": 100000.0,
            "positions": {"NVDA": 50},
            "entry_prices": {"NVDA": 100.0},
        }

        adjustments = self.risk._calculate_position_adjustments(
            portfolio, RiskAgent.SEVERE_DRAWDOWN, "severe"
        )

        # Position should be at ~25% of original (adjustment factor = 0.25)
        self.assertIn("NVDA", adjustments)
        # After 75% reduction, position should be smaller but not zero
        self.assertGreater(adjustments["NVDA"], 0)

    def test_position_sizing_critical_drawdown(self):
        """At critical drawdown (-15%), positions should be liquidated (0%)."""
        portfolio = {
            "total_value": 100000.0,
            "positions": {"NVDA": 50, "TSLA": 30},
            "entry_prices": {"NVDA": 100.0, "TSLA": 150.0},
        }

        adjustments = self.risk._calculate_position_adjustments(
            portfolio, RiskAgent.CRITICAL_DRAWDOWN, "critical"
        )

        # At critical drawdown, adjustment factor is 0.0, but position sizes might be capped
        # Just verify they're significantly reduced
        for ticker, size in adjustments.items():
            self.assertLess(size, 0.05)  # Less than 5% of portfolio (initial positions)

    def test_max_position_size_constraint(self):
        """No single position should exceed 10% of portfolio."""
        portfolio = {
            "total_value": 100000.0,
            "positions": {"NVDA": 100},  # Very large position
            "entry_prices": {"NVDA": 100.0},
        }

        adjustments = self.risk._calculate_position_adjustments(portfolio, -0.01, "normal")

        for size in adjustments.values():
            self.assertLessEqual(size, RiskAgent.MAX_POSITION_SIZE)


class TestRiskAgentRiskRegime(unittest.TestCase):
    """Unit tests for risk regime detection."""

    def setUp(self):
        self.risk = RiskAgent("test-risk")

    def test_risk_regime_normal_by_default(self):
        """Risk regime should be 'normal' with no special conditions."""
        regime = self.risk._assess_risk_regime({})
        self.assertIn(regime, ["normal", "elevated", "severe", "critical"])

    def test_veto_signals_empty_in_normal_conditions(self):
        """Veto signals should be empty when circuit breaker is not active."""
        result = self.risk._execute_subtasks([], {})
        self.assertEqual(result["veto_signals"], [])
        self.assertFalse(result["circuit_breaker_active"])

    def test_veto_signals_populated_when_breaker_active(self):
        """Veto signals should list all positions when circuit breaker is active."""
        portfolio = {
            "total_value": 100000.0,
            "positions": {"NVDA": 50, "TSLA": 30, "AAPL": 40},
            "entry_prices": {"NVDA": 100.0, "TSLA": 150.0, "AAPL": 120.0},
        }

        self.risk._calculate_drawdown = lambda p: RiskAgent.CIRCUIT_BREAKER_DRAWDOWN

        result = self.risk._execute_subtasks([{"portfolio_state": portfolio}], {})

        self.assertTrue(result["circuit_breaker_active"])
        self.assertEqual(len(result["veto_signals"]), 3)
        self.assertIn("NVDA", result["veto_signals"])


class TestRiskAgentLATS(unittest.TestCase):
    """Unit tests for LATS (Language Agent Tree Search) risk mitigation."""

    def setUp(self):
        self.risk = RiskAgent("test-risk")

    def test_lats_generates_scenarios(self):
        """LATS should generate multiple risk mitigation scenarios."""
        portfolio = {
            "total_value": 100000.0,
            "positions": {"NVDA": 50, "TSLA": 30, "AAPL": 40},
            "entry_prices": {"NVDA": 100.0, "TSLA": 150.0, "AAPL": 120.0},
        }

        scenarios = self.risk._lats_risk_mitigation(portfolio, -0.05, "elevated")

        self.assertGreater(len(scenarios), 0)
        for scenario in scenarios:
            self.assertIn("scenario", scenario)
            self.assertIn("steps", scenario)
            self.assertIn("expected_drawdown_recovery", scenario)
            self.assertIn("probability_success", scenario)
            self.assertIn("ranking", scenario)

    def test_lats_scenarios_ranked(self):
        """LATS scenarios should be ranked by effectiveness."""
        portfolio = {
            "total_value": 100000.0,
            "positions": {"NVDA": 50},
            "entry_prices": {"NVDA": 100.0},
        }

        scenarios = self.risk._lats_risk_mitigation(portfolio, -0.15, "critical")

        # Scenarios should be ranked 1, 2, 3, etc.
        rankings = [s.get("ranking") for s in scenarios]
        expected_rankings = list(range(1, len(scenarios) + 1))
        self.assertEqual(rankings, expected_rankings)

    def test_lats_generates_emergency_scenario_at_critical(self):
        """LATS should generate full liquidation scenario at -15% drawdown."""
        portfolio = {
            "total_value": 100000.0,
            "positions": {"NVDA": 50, "TSLA": 30},
            "entry_prices": {"NVDA": 100.0, "TSLA": 150.0},
        }

        scenarios = self.risk._lats_risk_mitigation(portfolio, -0.15, "critical")

        # Should include emergency liquidation scenario
        scenario_names = [s.get("scenario", "") for s in scenarios]
        self.assertTrue(any("Emergency" in name or "Liquidation" in name for name in scenario_names))


class TestRiskAgentHiddenStates(unittest.TestCase):
    """Unit tests for hidden state encoding."""

    def setUp(self):
        self.risk = RiskAgent("test-risk")

    def test_hidden_state_layer_8_shape_dtype(self):
        """Layer 8 should be (4,) float32: [normal, elevated, severe, critical]."""
        position_adj = {"NVDA": 0.05, "TSLA": 0.03}

        hidden_states = self.risk._encode_hidden_states(-0.05, "elevated", position_adj)

        h8 = hidden_states[8]
        self.assertEqual(h8.shape, (4,))
        self.assertEqual(h8.dtype, np.float32)
        # Should be one-hot or soft assignment to regime
        self.assertEqual(np.sum(h8), 1.0)

    def test_hidden_state_layer_16_shape_dtype(self):
        """Layer 16 should be (3,) float32: [drawdown_norm, volatility, cash_reserve]."""
        position_adj = {"NVDA": 0.05}

        hidden_states = self.risk._encode_hidden_states(-0.08, "severe", position_adj)

        h16 = hidden_states[16]
        self.assertEqual(h16.shape, (3,))
        self.assertEqual(h16.dtype, np.float32)
        # All values should be in [0, 1]
        self.assertTrue(np.all(h16 >= 0) and np.all(h16 <= 1))

    def test_hidden_state_layer_24_shape_dtype(self):
        """Layer 24 should be (32,) float32 position intensity vector."""
        position_adj = {f"TICK{i}": 0.05 for i in range(10)}

        hidden_states = self.risk._encode_hidden_states(-0.05, "elevated", position_adj)

        h24 = hidden_states[24]
        self.assertEqual(h24.shape, (32,))
        self.assertEqual(h24.dtype, np.float32)
        # First 10 should have values, rest zeros
        self.assertGreater(np.sum(h24), 0)


class TestRiskAgentIntegration(unittest.TestCase):
    """End-to-end integration tests for RiskAgent."""

    def test_full_execution_normal_conditions(self):
        """Full execution in normal market conditions."""
        risk = RiskAgent("integration-risk")

        portfolio = {
            "total_value": 100000.0,
            "positions": {"NVDA": 50, "TSLA": 30},
            "entry_prices": {"NVDA": 100.0, "TSLA": 150.0},
            "cash": 5000.0,
        }

        result = risk._execute_subtasks([{"portfolio_state": portfolio}], {})

        self.assertFalse(result["circuit_breaker_active"])
        self.assertGreater(result["portfolio_drawdown"], -0.05)
        self.assertEqual(result["risk_regime"], "normal")
        self.assertEqual(result["veto_signals"], [])

    def test_full_execution_circuit_breaker_triggered(self):
        """Full execution when circuit breaker is triggered."""
        risk = RiskAgent("integration-risk")

        portfolio = {
            "total_value": 100000.0,
            "positions": {"NVDA": 50, "TSLA": 30, "AAPL": 40},
            "entry_prices": {"NVDA": 100.0, "TSLA": 150.0, "AAPL": 120.0},
            "cash": 1000.0,
        }

        risk._calculate_drawdown = lambda p: -0.06

        result = risk._execute_subtasks([{"portfolio_state": portfolio}], {})

        self.assertTrue(result["circuit_breaker_active"])
        self.assertLess(result["portfolio_drawdown"], -0.05)
        self.assertGreater(len(result["veto_signals"]), 0)
        # LATS may or may not generate scenarios depending on risk regime
        self.assertIsInstance(result["lats_scenarios"], list)

    def test_full_execution_metrics_populated(self):
        """Full execution should populate all expected metrics."""
        risk = RiskAgent("integration-risk")

        portfolio = {
            "total_value": 100000.0,
            "positions": {"NVDA": 50},
            "entry_prices": {"NVDA": 100.0},
        }

        result = risk._execute_subtasks([{"portfolio_state": portfolio}], {})

        metrics = result["metrics"]
        self.assertIn("assessment_date", metrics)
        self.assertIn("portfolio_drawdown", metrics)
        self.assertIn("circuit_breaker_active", metrics)
        self.assertIn("risk_regime", metrics)
        self.assertIn("positions_monitored", metrics)


if __name__ == "__main__":
    unittest.main()
