#!/usr/bin/env python3
"""
Swarm Intelligence Orchestrator - Phase 3 Integration

Replaces sequential subprocess orchestration with intelligent multi-agent swarm.
Uses KV cache sharing + latent collaboration + gossip routing + consensus.

Usage:
  python agents/orchestrator_swarm.py --mode premarket
  python agents/orchestrator_swarm.py --mode afterhours
  python agents/orchestrator_swarm.py --mode full
"""

import sys
import os
import json
import logging
import argparse
import uuid
from datetime import datetime
from pathlib import Path

# Ensure repo is in path for swarm module imports
sys.path.insert(0, str(Path(__file__).parent.parent))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = lambda *a, **kw: None

load_dotenv(override=True)
Path("logs").mkdir(exist_ok=True)
Path("reports").mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [SWARM-ORCHESTRATOR] %(message)s",
    handlers=[
        logging.FileHandler("logs/orchestrator_swarm.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# Import swarm framework
try:
    from swarm import (
        SwarmOrchestrator,
        KVCacheManager,
        LatentWorkingMemory,
        GossipRouter,
        ConfidenceWeightedConsensus,
        NativeCatalystMonitorAgent,
        NativeVIFAnalystAgent,
        NativeFinVizScreenerAgent,
        CriticAgent,
        NativeSwingScreenerAgent,
        NativeVectorBTAgent,
        NativeAutoResearchAgent,
        NativeSignalVerifierAgent,
        RiskAgent,
    )
except ImportError as e:
    logger.error(f"Swarm framework import failed: {e}. Falling back to subprocess orchestrator.")
    import subprocess
    sys.exit(subprocess.run([sys.executable, "agents/orchestrator.py"] + sys.argv[1:]).returncode)


# ── Watchlists ────────────────────────────────────────────────────────────────
WATCHLISTS = [
    "AI Physical Layer & Power Infrastructure",
    "AI Verticals (Supply Chain)",
    "Core Growth & Macro Indices (Large-Cap Anchors)",
    "Energy & AI (Power Convergence)",
    "Speculative _ High-Beta",
    "Trump Admin_ Onshoring",
]

# ── Task decomposition by mode ─────────────────────────────────────────────────
PIPELINES = {
    "premarket": {
        "description": "07:00 – 09:30 CT: Premarket catalyst + VIF + swing screener",
        "task_prompt": "Analyze 6 watchlists for trading signals and opportunities before market open",
        "task_context": {
            "watchlists": WATCHLISTS,
            "period": "1mo",
            "focus": ["catalyst_scan", "vif_analysis", "swing_setups"],
        }
    },
    "market_open": {
        "description": "09:35 CT: Swing screener for opening volume",
        "task_prompt": "Screen for swing trade setups at market open",
        "task_context": {
            "watchlists": WATCHLISTS,
            "period": "5d",
            "focus": ["swing_setups"],
        }
    },
    "afterhours": {
        "description": "16:05 CT: Daily conviction model + 5d VIF wrap",
        "task_prompt": "Review daily market close and 5-day trend analysis",
        "task_context": {
            "watchlists": WATCHLISTS,
            "period": "5d",
            "focus": ["daily_conviction", "vif_5d"],
        }
    },
    "weekend": {
        "description": "Weekend: Catalyst briefing and macro analysis",
        "task_prompt": "Scan macro catalysts, earnings dates, sector rotation for week ahead",
        "task_context": {
            "watchlists": WATCHLISTS,
            "period": "1mo",
            "focus": ["catalyst_scan"],
        }
    },
    "full": {
        "description": "Full end-to-end analysis: all modes combined",
        "task_prompt": "Complete analysis: catalysts, VIF signals, swing setups, daily conviction",
        "task_context": {
            "watchlists": WATCHLISTS,
            "period": "1mo",
            "focus": ["catalyst_scan", "vif_analysis", "swing_setups", "daily_conviction"],
        }
    },
    "finviz_screen": {
        "description": "07:30 CT: Independent FinViz discovery scan (separate from VIF watchlists)",
        "task_prompt": "Run 19 institutional screeners: Hunt, CANSLIM, Kell variants, earnings-driven. Compare results with VIF signals for overlap analysis.",
        "task_context": {
            "mode": "finviz_screen",
            "screener_groups": ["daily_screeners", "tactical_screeners"],
            "focus": ["finviz_discovery"],
            "compare_with_vif": True,
            "output_format": "html",
        }
    },
}


def initialize_swarm():
    """Initialize swarm framework components."""
    logger.info("Initializing swarm intelligence framework...")

    # ── AGENT ONBOARDING PROTOCOL ────────────────────────────────────────────
    # To add a new agent to the VIF council, follow ALL 4 steps:
    #  1. Create swarm/native_<name>_agent.py — implement execute() with the
    #     standard swarm signature: execute(subtasks, kv_cache_binding,
    #     latent_memory, task_context) -> Dict
    #  2. Export from swarm/__init__.py (add to import + __all__ list)
    #  3. Add @tool wrapper in swarm/smolagents_bridge.py (both Production
    #     and Research bridges) so the primary smolagents path can call it
    #  4. Add to agent_pool dict below with a string key
    # SwarmOrchestrator is the lead agent — all execution must flow through it.
    # ─────────────────────────────────────────────────────────────────────────

    # Create framework components
    kv_cache = KVCacheManager(max_cache_mb=500, max_recompute_layers=3)
    latent_memory = LatentWorkingMemory(layers_to_share=[8, 16, 24, 32, 40])
    gossip_router = GossipRouter(gossip_timeout_ms=500, max_agents_per_subtask=2)
    consensus = ConfidenceWeightedConsensus(
        signal_priority={"BUY": 3, "SELL": 2, "HOLD": 1}
    )

    # Create agent pool (order defined in SwarmOrchestrator.AGENT_EXECUTION_ORDER)
    # 1. Catalyst monitor — writes K4 tickers to layer-2 LoRA cache
    # 2. VIF analyst — reads K4, outputs signals → task_context["vif_signals"]
    # 3. Critic agent — vetoes/downgrades → task_context["critic_signals"]
    # 4. VectorBT backtester — validates post-critic signals via 6mo Sharpe/drawdown (layer 32)
    # 5. Signal verifier — 4-gate PUBLISH/DOWNGRADE/REJECT → task_context["verified_signals"]
    # 6. Swing screener — reuses market data from VIF's KV cache layer-1
    # 7. FinViz screener — local discovery (0 tokens), compares with VIF signals
    # 8. Autoresearch agent — iterative research synthesis (layer 40), signal validation
    # 9. Risk agent (final) — circuit breaker (-5% drawdown) + risk mitigation
    agent_pool = {
        "catalyst-monitor": NativeCatalystMonitorAgent("catalyst-monitor"),
        "vif-analyst-1": NativeVIFAnalystAgent("vif-analyst-1"),
        "critic": CriticAgent("critic"),
        "vectorbt-backtester": NativeVectorBTAgent("vectorbt-backtester"),
        "signal-verifier": NativeSignalVerifierAgent("signal-verifier"),
        "swing-screener": NativeSwingScreenerAgent("swing-screener"),
        "finviz-screener": NativeFinVizScreenerAgent("finviz-screener"),
        "autoresearch": NativeAutoResearchAgent("autoresearch"),
        "risk-agent": RiskAgent("risk-agent"),
    }

    # Initialize orchestrator
    orchestrator = SwarmOrchestrator(
        kv_cache_manager=kv_cache,
        latent_memory=latent_memory,
        agent_pool=agent_pool,
        gossip_router=gossip_router,
        consensus_resolver=consensus,
    )

    logger.info(f"  ✓ KV Cache Manager initialized (500MB, 3-layer recomputation)")
    logger.info(f"  ✓ Latent Working Memory initialized (layers: 8, 16, 24, 32, 40)")
    logger.info(f"  ✓ Gossip Router initialized (500ms timeout, 2 agents/subtask)")
    logger.info(f"  ✓ Consensus Resolver initialized (BUY=3, SELL=2, HOLD=1)")
    logger.info(f"  ✓ Agent Pool initialized ({len(agent_pool)} native specialist agents)")
    logger.info(f"    Phase 1: Catalyst → VIF → Critic (Planner-Critic-Executor)")
    logger.info(f"    Phase 2: VectorBT → SignalVerifier (4-gate: Vol/Fund/Sent/Macro) → SwingScreener → FinViz")
    logger.info(f"    Phase 3: Autoresearch (iterative synthesis, layer 40) → Risk (Circuit Breaker)")

    return orchestrator, kv_cache, latent_memory, consensus


def _run_finviz_pipeline(pipeline_cfg: dict):
    """Run FinViz discovery scan in-process via NativeFinVizScreenerAgent."""
    import time

    logger.info(f"{'='*65}")
    logger.info(f"  FINVIZ DISCOVERY SCREENER: {pipeline_cfg['description']}")
    logger.info(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"{'='*65}")

    start_time = time.time()
    trace_id = str(uuid.uuid4())
    logger.info(f"\nTrace-ID: {trace_id}")

    try:
        from swarm.native_finviz_screener_agent import execute_finviz_screening

        logger.info("Executing FinViz discovery scan (in-process, 0 tokens)...")
        finviz_output = execute_finviz_screening(use_parallel=True)

        duration_ms = int((time.time() - start_time) * 1000)

        # Aggregate unique tickers
        total_tickers = set()
        for screener_result in finviz_output.get("results", {}).values():
            total_tickers.update(screener_result.get("tickers", []))

        logger.info(f"\n{'='*65}")
        logger.info(f"  FINVIZ SCAN COMPLETE")
        logger.info(f"{'='*65}")
        logger.info(f"Duration: {duration_ms}ms | Cache hit: {finviz_output.get('cache_hit', False)}")
        logger.info(f"Screeners with results: {finviz_output.get('screeners_with_results', 0)}/{finviz_output.get('screeners_executed', 19)}")
        logger.info(f"Unique Tickers: {len(total_tickers)} | Token cost: 0")
        logger.info(f"Top Discoveries: {sorted(list(total_tickers))[:10]}")

        output_file = Path("reports") / f"finviz_screen_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        envelope = {
            "mode": "finviz_screen",
            "trace_id": trace_id,
            "timestamp": datetime.now().isoformat(),
            "duration_ms": duration_ms,
            "finviz_results": finviz_output,
            "unique_tickers": sorted(list(total_tickers)),
            "discovery_count": len(total_tickers),
        }
        output_file.write_text(json.dumps(envelope, indent=2, default=str))
        logger.info(f"\nResults saved -> {output_file}")

        try:
            from scripts.active.reporting.finviz_screen_html import write_finviz_screen_html

            html_path = write_finviz_screen_html(output_file, envelope)
            logger.info(f"HTML report saved -> {html_path}")
        except Exception as e:
            logger.warning(f"FinViz HTML report skipped: {e}")

        return 0

    except Exception as e:
        logger.error(f"Finviz pipeline failed: {e}", exc_info=True)
        return 1


def run_pipeline(mode: str):
    """Execute pipeline via SwarmOrchestrator or specialized agent."""
    if mode not in PIPELINES:
        logger.error(f"Unknown mode: {mode}. Valid modes: {list(PIPELINES.keys())}")
        return 1

    pipeline_cfg = PIPELINES[mode]

    # Special handling for finviz_screen (independent discovery, not swarm-orchestrated)
    if mode == "finviz_screen":
        return _run_finviz_pipeline(pipeline_cfg)

    logger.info(f"{'='*65}")
    logger.info(f"  SWARM ORCHESTRATOR: {pipeline_cfg['description']}")
    logger.info(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"{'='*65}")

    # Initialize swarm
    orchestrator, kv_cache, latent_memory, consensus = initialize_swarm()

    # Generate trace ID
    trace_id = str(uuid.uuid4())
    logger.info(f"\nTrace-ID: {trace_id}")

    # Inject FinViz discoveries from today's cached scan into task_context
    # Enables critic agent to reference FinViz tickers during Munger audit
    finviz_reports = sorted(Path("reports").glob("finviz_screen_*.json"))
    if finviz_reports:
        try:
            fv = json.loads(finviz_reports[-1].read_text())
            pipeline_cfg["task_context"]["finviz_tickers_from_vif"] = fv.get("unique_tickers", [])
            logger.info(f"  FinViz context loaded: {len(fv.get('unique_tickers', []))} tickers from {finviz_reports[-1].name}")
        except Exception as e:
            logger.warning(f"  Could not load FinViz context: {e}")

    # Execute swarm task
    logger.info(f"\nExecuting task: {pipeline_cfg['task_prompt']}")
    logger.info(f"Context: {len(pipeline_cfg['task_context'].get('watchlists', []))} watchlists")

    try:
        # Try smolagents bridge first (richer multi-step reasoning + retry)
        try:
            from swarm.smolagents_bridge import ProductionSwarmBridge
            logger.info("Using smolagents ProductionSwarmBridge for orchestration")
            bridge = ProductionSwarmBridge()
            raw_result = bridge.run(pipeline_cfg['task_prompt'])

            # Parse raw JSON output from bridge
            if isinstance(raw_result, str):
                result_data = json.loads(raw_result) if raw_result.startswith('{') else {"raw": raw_result}
            else:
                result_data = raw_result

            # Extract consensus signals from smolagents output
            consensus_signals = result_data.get("consensus_signals", {})
            conflicts = result_data.get("conflicts", [])
            metrics = result_data.get("metrics", {})

        except ImportError:
            # smolagents not installed — fall back to native SwarmOrchestrator
            logger.info("smolagents not available, using native SwarmOrchestrator")
            result = orchestrator.orchestrate_task(
                task_prompt=pipeline_cfg['task_prompt'],
                task_context=pipeline_cfg['task_context']
            )

            # Extract results
            consensus_signals = result.get("consensus", {}).get("consensus_signals", {})
            conflicts = result.get("consensus", {}).get("conflicts", [])
            metrics = result.get("metrics", {})

        # Log summary
        logger.info(f"\n{'='*65}")
        logger.info(f"  SWARM EXECUTION COMPLETE")
        logger.info(f"{'='*65}")
        logger.info(f"Duration: {metrics.get('duration_ms', 0):.0f}ms")
        logger.info(f"Agents: {metrics.get('agents_executed', 0)}/{metrics.get('agents_total', 0)} succeeded")
        logger.info(f"KV Cache Hit Rate: {metrics.get('kv_cache_hit_rate', 0):.1%}")
        logger.info(f"Consensus Conflicts: {metrics.get('consensus_conflicts', 0)}")

        # Count signal types
        buy_count = sum(1 for s in consensus_signals.values() if s.get("signal") == "BUY")
        sell_count = sum(1 for s in consensus_signals.values() if s.get("signal") == "SELL")
        hold_count = sum(1 for s in consensus_signals.values() if s.get("signal") == "HOLD")

        logger.info(f"Signals: {buy_count} BUY, {sell_count} SELL, {hold_count} HOLD")

        # Save results (JSON)
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = Path("reports") / f"swarm_result_{mode}_{ts}.json"
        output_file.write_text(json.dumps({
            "mode": mode,
            "trace_id": trace_id,
            "timestamp": datetime.now().isoformat(),
            "consensus_signals": consensus_signals,
            "conflicts": conflicts,
            "metrics": metrics,
        }, indent=2))
        logger.info(f"\nResults saved -> {output_file}")

        # Save HTML report (includes Greeks/IV% table if options data available)
        try:
            from scripts.active.reporting.html_report_generator import (
                create_html_template, build_greeks_table, save_html_report
            )

            buy_signals  = {t: s for t, s in consensus_signals.items() if s.get("signal") == "BUY"}
            sell_signals = {t: s for t, s in consensus_signals.items() if s.get("signal") == "SELL"}
            hold_signals = {t: s for t, s in consensus_signals.items() if s.get("signal") == "HOLD"}

            def _signal_table(sigs):
                if not sigs:
                    return "<p>No signals.</p>"
                rows = "".join(
                    f"<tr><td><strong>{t}</strong></td>"
                    f"<td>{s.get('signal','—')}</td>"
                    f"<td>{s.get('confidence','—')}%</td>"
                    f"<td>{s.get('iv_pct','—')}</td>"
                    f"<td>{s.get('delta','—')}</td>"
                    f"<td>{s.get('gamma_regime','—')}</td>"
                    f"<td>{s.get('verifier_verdict', s.get('note','—'))}</td></tr>"
                    for t, s in sorted(sigs.items(), key=lambda x: x[1].get("confidence", 0), reverse=True)
                )
                return f"""<table><thead><tr>
                    <th>Ticker</th><th>Signal</th><th>Confidence</th>
                    <th>IV%</th><th>Delta</th><th>Gamma Regime</th><th>Note</th>
                </tr></thead><tbody>{rows}</tbody></table>"""

            sections = [
                {"heading": f"SELL Signals ({sell_count})", "html": _signal_table(sell_signals)},
                {"heading": f"BUY Signals ({buy_count})",  "html": _signal_table(buy_signals)},
                {"heading": f"HOLD ({hold_count})",        "html": _signal_table(hold_signals)},
                {"heading": "Options Greeks & IV%",         "html": build_greeks_table(consensus_signals)},
            ]

            html = create_html_template(
                title=f"VIF Swarm Report — {mode.upper()} — {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                content_sections=sections,
                metadata={"author": "VIF Swarm Orchestrator", "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')},
            )
            html_path = save_html_report(f"swarm_{mode}_{ts}", html)
            logger.info(f"HTML report saved -> {html_path}")
        except Exception as e:
            logger.warning(f"HTML report generation skipped: {e}")

        return 0 if metrics.get("agents_executed", 0) == metrics.get("agents_total", 0) else 1

    except Exception as e:
        logger.error(f"Swarm execution failed: {e}", exc_info=True)
        return 1


def main():
    parser = argparse.ArgumentParser(
        description="Swarm Intelligence Orchestrator – Multi-agent coordination with KV cache + latent collaboration"
    )
    parser.add_argument(
        "--mode", "-m",
        choices=list(PIPELINES.keys()),
        default="full",
        help="Pipeline mode (default: full)"
    )
    args = parser.parse_args()

    return run_pipeline(args.mode)


if __name__ == "__main__":
    sys.exit(main())
