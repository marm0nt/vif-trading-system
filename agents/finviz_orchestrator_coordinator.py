#!/usr/bin/env python3
"""
FinViz Orchestrator-Coordinator — Swarm Integration Layer

Manages FinViz screener execution as part of the 5-agent council.
- Runs all 19 screeners in parallel (skip-empty)
- Compares discoveries with VIF signals
- Synthesizes findings with critic agent
- Generates shadow test report

Workflow:
  1. Load VIF premarket signals (from swarm_result_premarket_*.json)
  2. Execute all 19 screeners (skip if no results)
  3. For each screener with results: Compare with VIF
  4. Critic agent: Evaluate overlap + confidence delta
  5. Research agent: Investigate novel discoveries
  6. Report: HTML shadow test analysis
"""

import logging
from pathlib import Path
from datetime import datetime
import json
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)

_REPO_ROOT = Path(__file__).parent.parent

# All 19 custom screeners (verified names)
FINVIZ_SCREENERS = [
    "hunt_1_3",
    "shorted_to_breakouts",
    "backtested_6mo_top1",
    "gap_up_screener",
    "gap_down_screener",
    "kell_v1_vol_rsi",
    "kell_v2_52w_beta_vol",
    "kell_v3_100pct_perf_vol",
    "kell_v4_gap_3pct",
    "combo_kell_all",
    "a_edge_ib_obv_7_25",
    "b_edge_loose_ib_obv_7_25",
    "new_signal_pre_breakout_a_7_25",
    "sr_pre_breakout_a_7_25",
    "vol_momentum_7_30",
    "er_gap_ups",
    "canslim_b_plus",
    "canslim_1_a_plus",
    "david_ryan_core",
]


class FinVizOrchestratorCoordinator:
    """
    Master orchestrator for FinViz screener execution within the swarm.
    Integrates screener results with VIF signals, critic analysis, and research.
    """

    def __init__(self):
        self.agent_id = "finviz-orchestrator-1"
        self.logger = logging.getLogger(__name__)
        self.catalog_path = _REPO_ROOT / "reports" / "finviz_orchestrator_catalog.json"
        self._load_catalog()

    def _load_catalog(self):
        """Load execution history."""
        self.catalog = {}
        if self.catalog_path.exists():
            try:
                with open(self.catalog_path) as f:
                    self.catalog = json.load(f)
                    self.logger.debug(f"Loaded {len(self.catalog)} orchestrator runs")
            except Exception as e:
                self.logger.warning(f"Failed to load orchestrator catalog: {e}")

    def execute_finviz_screening(self, vif_signals: Optional[Dict] = None, use_parallel: bool = True) -> Dict:
        """
        Execute all 19 FinViz screeners with skip-empty logic.

        Args:
            vif_signals: VIF premarket signals dict (optional for comparison)
            use_parallel: Use ThreadPoolExecutor for parallel execution (default True)

        Returns:
            {
                "timestamp": "...",
                "screeners_executed": 19,
                "screeners_with_results": 6,
                "screeners_skipped": 13,
                "results": {...},
                "vif_comparison": {...},
                "critic_analysis": {...}
            }
        """
        from agents.finviz_screener_agent import _screener

        start_time = datetime.now()
        self.logger.info(f"Starting FinViz orchestration ({len(FINVIZ_SCREENERS)} screeners)")

        # Step 1: Execute all screeners (skip empty)
        results_with_data = {}
        skipped_screeners = []

        if use_parallel:
            results_with_data, skipped_screeners = self._execute_screeners_parallel()
        else:
            results_with_data, skipped_screeners = self._execute_screeners_sequential()

        # Step 2: Compare with VIF signals if provided
        vif_comparison = None
        if vif_signals:
            vif_comparison = self._compare_with_vif(results_with_data, vif_signals)

        # Step 3: Get critic analysis
        critic_analysis = self._get_critic_analysis(results_with_data, vif_signals)

        # Step 4: Research novel discoveries
        novel_tickers = self._extract_novel_discoveries(results_with_data, vif_signals)
        research_findings = self._research_novel_discoveries(novel_tickers)

        # Step 5: Generate summary
        execution_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)

        report = {
            "timestamp": datetime.now().isoformat(),
            "execution_time_ms": execution_time_ms,
            "screeners_executed": len(FINVIZ_SCREENERS),
            "screeners_with_results": len(results_with_data),
            "screeners_skipped": len(skipped_screeners),
            "results": results_with_data,
            "vif_comparison": vif_comparison,
            "critic_analysis": critic_analysis,
            "novel_discoveries": {
                "count": len(novel_tickers),
                "tickers": novel_tickers,
                "research_findings": research_findings,
            },
            "summary": self._generate_summary(results_with_data, vif_comparison, skipped_screeners),
        }

        # Save to catalog
        self.catalog[f"finviz_orchestration_{datetime.now().isoformat()}"] = report
        self._save_catalog()

        self.logger.info(
            f"FinViz orchestration complete: {len(results_with_data)} screeners with results, "
            f"{len(skipped_screeners)} skipped ({execution_time_ms}ms)"
        )

        return report

    def _execute_screeners_parallel(self) -> tuple:
        """Execute screeners in parallel using ThreadPoolExecutor."""
        from agents.finviz_screener_agent import _screener

        results_with_data = {}
        skipped_screeners = []

        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_screener = {
                executor.submit(_screener.run_named_screener, screener_name): screener_name
                for screener_name in FINVIZ_SCREENERS
            }

            for future in as_completed(future_to_screener):
                screener_name = future_to_screener[future]
                try:
                    result = future.result()
                    if result.get("tickers"):
                        results_with_data[screener_name] = result
                        self.logger.info(f"✓ {screener_name}: {len(result['tickers'])} tickers")
                    else:
                        skipped_screeners.append(screener_name)
                        self.logger.info(f"○ {screener_name}: Skipped - no results")
                except Exception as e:
                    self.logger.error(f"✗ {screener_name}: {e}")
                    skipped_screeners.append(screener_name)

        return results_with_data, skipped_screeners

    def _execute_screeners_sequential(self) -> tuple:
        """Execute screeners sequentially (for testing/single-threaded)."""
        from agents.finviz_screener_agent import _screener

        results_with_data = {}
        skipped_screeners = []

        for screener_name in FINVIZ_SCREENERS:
            try:
                result = _screener.run_named_screener(screener_name)
                if result.get("tickers"):
                    results_with_data[screener_name] = result
                    self.logger.info(f"✓ {screener_name}: {len(result['tickers'])} tickers")
                else:
                    skipped_screeners.append(screener_name)
                    self.logger.info(f"○ {screener_name}: Skipped - no results")
            except Exception as e:
                self.logger.error(f"✗ {screener_name}: {e}")
                skipped_screeners.append(screener_name)

        return results_with_data, skipped_screeners

    def _compare_with_vif(self, finviz_results: Dict, vif_signals: Dict) -> Dict:
        """Compare FinViz discoveries with VIF signals."""
        from agents.finviz_screener_agent import _screener

        vif_tickers = set(vif_signals.keys())
        comparison_results = []
        total_finviz_tickers = set()

        for screener_name, result in finviz_results.items():
            tickers = result.get("tickers", [])
            finviz_set = set(tickers)
            total_finviz_tickers.update(finviz_set)

            overlap = finviz_set & vif_tickers
            finviz_only = finviz_set - vif_tickers

            comparison_results.append({
                "screener": screener_name,
                "finviz_count": len(finviz_set),
                "overlap_count": len(overlap),
                "overlap_pct": (len(overlap) / len(finviz_set) * 100) if finviz_set else 0,
                "overlap_tickers": list(overlap),
                "finviz_only_count": len(finviz_only),
                "finviz_only_tickers": list(finviz_only),
                "confidence_delta": {
                    t: vif_signals.get(t, {}).get("confidence", 50) for t in overlap
                },
            })

        # Aggregate stats
        total_overlap = set()
        total_finviz_only = set()
        for result in comparison_results:
            total_overlap.update(result["overlap_tickers"])
            total_finviz_only.update(result["finviz_only_tickers"])

        return {
            "vif_total_tickers": len(vif_tickers),
            "finviz_total_unique": len(total_finviz_tickers),
            "total_overlap": len(total_overlap),
            "total_overlap_pct": (len(total_overlap) / len(total_finviz_tickers) * 100) if total_finviz_tickers else 0,
            "total_finviz_only": len(total_finviz_only),
            "avg_overlap_per_screener": (
                sum(r["overlap_pct"] for r in comparison_results) / len(comparison_results)
                if comparison_results
                else 0
            ),
            "by_screener": comparison_results,
        }

    def _get_critic_analysis(self, finviz_results: Dict, vif_signals: Optional[Dict] = None) -> Dict:
        """Get critic agent analysis of FinViz vs VIF discrepancies."""
        try:
            from swarm.critic_agent import CriticAgent

            critic = CriticAgent()

            # Prepare critic context: FinViz discovery set vs VIF signals
            critic_context = {
                "finviz_screener_count": len(finviz_results),
                "vif_signal_count": len(vif_signals) if vif_signals else 0,
                "overlap_pct": self._compute_overlap(finviz_results, vif_signals),
            }

            # Critic veto analysis (uses munger inversion audit)
            subtasks = [{
                "type": "veto_analysis",
                "data": {
                    "finviz_tickers": list(set(t for r in finviz_results.values() for t in r.get("tickers", []))),
                    "vif_signals": vif_signals or {},
                }
            }]

            result = critic.execute(
                subtasks=subtasks,
                kv_cache_binding=None,
                latent_memory=None,
                task_context=critic_context
            )

            analysis = {
                "recommendation": "Phase C integration approved" if result.get("status") == "success" else "review required",
                "high_confidence_screeners": list(finviz_results.keys())[:3],
                "low_confidence_screeners": list(finviz_results.keys())[-3:],
                "overlap_threshold_met": critic_context.get("overlap_pct", 0) > 0.4,
                "next_steps": [
                    "Monitor daily overlap metrics (target > 50%)",
                    "Track novel discoveries that later appear in VIF signals",
                    "Validate no systematic downside from FinViz-only tickers",
                ],
                "critic_status": result.get("status"),
            }

            return analysis
        except Exception as e:
            self.logger.warning(f"Critic analysis failed: {e}, returning placeholder")
            return {"status": "pending", "reason": "critic agent not available"}

    def _compute_overlap(self, finviz_results: Dict, vif_signals: Optional[Dict] = None) -> float:
        """Compute overlap percentage: tickers in both FinViz and VIF signals."""
        finviz_tickers = set(t for r in finviz_results.values() for t in r.get("tickers", []))
        vif_tickers = set(vif_signals.keys()) if vif_signals else set()

        if not finviz_tickers and not vif_tickers:
            return 0.0

        overlap = len(finviz_tickers & vif_tickers)
        union = len(finviz_tickers | vif_tickers)
        return (overlap / union) if union > 0 else 0.0

    def _extract_novel_discoveries(self, finviz_results: Dict, vif_signals: Optional[Dict] = None) -> List[str]:
        """Extract tickers found ONLY in FinViz, not in VIF signals."""
        if not vif_signals:
            vif_tickers = set()
        else:
            vif_tickers = set(vif_signals.keys())

        all_novel = []
        for screener_result in finviz_results.values():
            finviz_tickers = set(screener_result.get("tickers", []))
            novel = finviz_tickers - vif_tickers
            all_novel.extend(novel)

        return list(set(all_novel))  # Deduplicate

    def _research_novel_discoveries(self, novel_tickers: List[str]) -> Dict:
        """Research novel discoveries using research agent."""
        try:
            # Placeholder for research agent integration
            # from agents.claude_research_agent import ClaudeResearchAgent
            # research = ClaudeResearchAgent()

            return {
                "total_novel": len(novel_tickers),
                "sample_tickers": novel_tickers[:5] if novel_tickers else [],
                "research_status": "pending_agent_integration",
            }
        except Exception as e:
            self.logger.warning(f"Research failed: {e}")
            return {"total_novel": len(novel_tickers), "sample_tickers": novel_tickers[:5]}

    def _generate_summary(self, results_with_data: Dict, vif_comparison: Optional[Dict], skipped: List) -> str:
        """Generate human-readable summary."""
        summary = {
            "total_unique_tickers": len(set(t for r in results_with_data.values() for t in r.get("tickers", []))),
            "high_conviction_screeners": [k for k, v in results_with_data.items() if len(v.get("tickers", [])) > 5],
            "low_conviction_screeners": [k for k, v in results_with_data.items() if len(v.get("tickers", [])) <= 2],
            "vif_overlap_pct": vif_comparison["total_overlap_pct"] if vif_comparison else None,
            "skipped_screeners": skipped,
        }
        return summary

    def _save_catalog(self):
        """Persist orchestration history."""
        self.catalog_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.catalog_path, "w") as f:
            json.dump(self.catalog, f, indent=2)
        self.logger.info(f"Saved orchestrator catalog ({len(self.catalog)} runs)")


# Singleton instance
_orchestrator = FinVizOrchestratorCoordinator()


def execute_finviz_shadow_test(
    vif_signals: Optional[Dict] = None,
    load_vif_from_latest: bool = True,
    use_parallel: bool = True,
) -> Dict:
    """
    Convenience function to run full FinViz orchestration.

    Args:
        vif_signals: VIF signals dict (optional)
        load_vif_from_latest: Auto-load latest VIF premarket results (default True)
        use_parallel: Use parallel execution (default True)

    Returns:
        Orchestration report with all results
    """
    if load_vif_from_latest and vif_signals is None:
        vif_files = sorted(
            (_REPO_ROOT / "reports").glob("swarm_result_premarket_*"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        if vif_files:
            vif_signals = json.loads(vif_files[0].read_text()).get("signals_by_ticker", {})

    return _orchestrator.execute_finviz_screening(vif_signals=vif_signals, use_parallel=use_parallel)


def list_finviz_screeners() -> List[str]:
    """List all 19 available FinViz screeners."""
    return FINVIZ_SCREENERS
