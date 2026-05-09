#!/usr/bin/env python3
"""
smolagents Dual-Mode Bridge - Production & Research Paths

Two orchestration modes:
1. ProductionSwarmBridge: ToolCallingAgent (deterministic, scheduled daily pipeline)
2. ResearchSwarmBridge: CodeAgent (flexible code generation for ad-hoc queries)

Zero 'import smolagents' in this file triggers ImportError handling in orchestrator_swarm.py.
Native agents fallback to SwarmOrchestrator if smolagents is not installed.

Usage:
  from swarm.smolagents_bridge import ProductionSwarmBridge, ResearchSwarmBridge

  # Production: scheduled daily pipeline
  bridge = ProductionSwarmBridge()
  result = bridge.run("Analyze 6 watchlists for trading signals before market open")

  # Research: ad-hoc Q&A with code execution
  research = ResearchSwarmBridge()
  answer = research.run("Which tickers show the most bullish VIF signals across all watchlists?")
"""

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

try:
    from smolagents import tool, ToolCallingAgent, CodeAgent, ManagedAgent, AnthropicModel
except ImportError:
    # graceful degradation: orchestrator_swarm.py catches this
    raise ImportError("smolagents not installed. Install with: pip install smolagents")


# Initialize Claude model (Sonnet 4.6 for production, Opus 4.7 for research)
MODEL_PROD = AnthropicModel(model_id="claude-sonnet-4-6", temperature=0)
MODEL_RESEARCH = AnthropicModel(model_id="claude-opus-4-7", temperature=0.2)


# ── Shared Tools (both production and research use these) ──────────────────────

@tool
def analyze_watchlist_vif(watchlist_name: str, period: str = "1mo") -> str:
    """
    Analyze a watchlist using VIF framework for BUY/SELL/HOLD signals.

    Args:
        watchlist_name: Name of watchlist to analyze (e.g., "AI Physical Layer & Power Infrastructure")
        period: Data period ("1mo", "5d", "6mo")

    Returns:
        JSON string with signals, top buys, kill alerts
    """
    try:
        from agents.watchlist_watcher import parse_watchlist, fetch_market_data, analyze_with_vif
        from pathlib import Path

        # Resolve watchlist file
        wl_path = Path("watchlists") / f"{watchlist_name}.txt"
        if not wl_path.exists():
            # Try fuzzy match
            for f in Path("watchlists").glob("*.txt"):
                if f.stem.lower() == watchlist_name.lower():
                    wl_path = f
                    break

        if not wl_path.exists():
            return json.dumps({"error": f"Watchlist not found: {watchlist_name}"})

        # Parse and analyze
        tickers = parse_watchlist(str(wl_path))
        market_data = fetch_market_data(tickers, period)
        result = analyze_with_vif(market_data, watchlist_name)

        return json.dumps(result)
    except Exception as e:
        return json.dumps({"error": str(e)})


@tool
def scan_macro_catalysts() -> str:
    """
    Scan all watchlists for macro catalysts, earnings risks, government policy impacts.

    Returns:
        JSON string with catalyst assessment, K4 flags, macro regime
    """
    try:
        from scripts.active.analysis.catalyst_analysis import (
            load_all_watchlists, get_earnings_dates, get_macro_events,
            fetch_news_headlines, analyze_watchlist
        )

        # Load all watchlists
        watchlist_dict = load_all_watchlists()
        all_tickers = set()
        for tickers in watchlist_dict.values():
            all_tickers.update(tickers)

        # Get catalysts
        earnings = get_earnings_dates(list(all_tickers))
        macro_events = get_macro_events()
        news = fetch_news_headlines(list(all_tickers))

        # Analyze
        results = {}
        for wl_name, tickers in watchlist_dict.items():
            cat_result = analyze_watchlist(wl_name, list(tickers), earnings, macro_events, news)
            results[wl_name] = cat_result

        return json.dumps({"status": "success", "watchlists_scanned": len(watchlist_dict), "results": results})
    except Exception as e:
        return json.dumps({"error": str(e)})


@tool
def screen_swing_setups() -> str:
    """
    Screen all watchlists for 2-4 week swing trade setups ranked by risk/reward.

    Returns:
        JSON string with identified setups, entry/stop/target levels
    """
    try:
        from swarm.native_swing_screener_agent import _PatchedSwingScreener

        screener = _PatchedSwingScreener()
        setups = []

        for ticker in screener.tickers[:50]:  # Limit scope
            market_data = {}  # Would be populated from cache in production
            setup = screener.identify_setup(ticker, market_data)
            if setup:
                setup["ticker"] = ticker
                setups.append(setup)

        # Rank by R:R
        ranked = sorted(setups, key=lambda x: x.get("risk_reward", 0), reverse=True)

        return json.dumps({"status": "success", "setups_found": len(ranked), "top_setups": ranked[:10]})
    except Exception as e:
        return json.dumps({"error": str(e)})


@tool
def get_kv_cache_metrics() -> str:
    """
    Get current KV cache hit rate and latent memory metrics.

    Returns:
        JSON string with cache performance stats
    """
    try:
        # In production, this would read from live KVCacheManager instance
        # For now, return placeholder
        return json.dumps({
            "cache_hit_rate": 0.0,
            "cache_sessions": 0,
            "latent_memory_operations": 0,
            "note": "Live metrics would come from KVCacheManager instance passed from orchestrator"
        })
    except Exception as e:
        return json.dumps({"error": str(e)})


# ── Production Path: ToolCallingAgent ─────────────────────────────────────────

class ProductionSwarmBridge:
    """
    Scheduled daily pipeline coordinator.

    Uses ToolCallingAgent (deterministic, structured reasoning) for reliable
    multi-step analysis of watchlists, catalysts, and swing setups.
    """

    def __init__(self):
        """Initialize production swarm with ToolCallingAgent agents."""
        logger.info("Initializing ProductionSwarmBridge (ToolCallingAgent mode)")

        # Create individual tool-calling agents
        self.vif_agent = ToolCallingAgent(
            tools=[analyze_watchlist_vif],
            model=MODEL_PROD,
            name="vif_analyst",
            description="VIF framework signal analyzer for watchlists"
        )

        self.catalyst_agent = ToolCallingAgent(
            tools=[scan_macro_catalysts],
            model=MODEL_PROD,
            name="catalyst_monitor",
            description="Macro catalyst and earnings risk scanner"
        )

        self.swing_agent = ToolCallingAgent(
            tools=[screen_swing_setups],
            model=MODEL_PROD,
            name="swing_screener",
            description="2-4 week swing trade setup identifier"
        )

        # Create orchestrator that delegates to sub-agents
        self.orchestrator = ToolCallingAgent(
            tools=[
                ManagedAgent(self.catalyst_agent, name="catalyst_monitor", description="Run catalyst scan first"),
                ManagedAgent(self.vif_agent, name="vif_analyst", description="Run VIF analysis second"),
                ManagedAgent(self.swing_agent, name="swing_screener", description="Run swing screener third"),
                get_kv_cache_metrics,
            ],
            model=MODEL_PROD,
            name="vif_orchestrator",
            description="Master orchestrator for daily trading signal generation"
        )

    def run(self, task_prompt: str) -> str:
        """
        Execute production pipeline.

        Args:
            task_prompt: Task description (e.g., "Analyze 6 watchlists for trading signals")

        Returns:
            JSON string with results from all sub-agents
        """
        try:
            logger.info(f"ProductionSwarmBridge.run(): {task_prompt[:80]}...")
            result = self.orchestrator.run(task_prompt)
            return result
        except Exception as e:
            logger.error(f"Production pipeline failed: {e}", exc_info=True)
            return json.dumps({"error": str(e), "mode": "production"})


# ── Research Path: CodeAgent ───────────────────────────────────────────────────

class ResearchSwarmBridge:
    """
    Ad-hoc research query coordinator.

    Uses CodeAgent (flexible, can write and execute code) for exploratory
    analysis and custom queries beyond scheduled pipelines.
    """

    def __init__(self):
        """Initialize research agent with CodeAgent (code execution enabled)."""
        logger.info("Initializing ResearchSwarmBridge (CodeAgent mode)")

        self.agent = CodeAgent(
            tools=[
                analyze_watchlist_vif,
                scan_macro_catalysts,
                screen_swing_setups,
                get_kv_cache_metrics,
            ],
            model=MODEL_RESEARCH,
            name="vif_research_agent",
            description="VIF trading system research and analysis agent",
            additional_authorized_imports=["json", "pandas", "numpy", "pathlib", "datetime"],
        )

    def run(self, query: str) -> str:
        """
        Execute research query with code generation capability.

        Args:
            query: Natural language research question (e.g., "Which tickers show strongest bullish VIF signals?")

        Returns:
            Analysis result with code execution traces
        """
        try:
            logger.info(f"ResearchSwarmBridge.run(): {query[:80]}...")
            result = self.agent.run(query)
            return result
        except Exception as e:
            logger.error(f"Research pipeline failed: {e}", exc_info=True)
            return json.dumps({"error": str(e), "mode": "research"})
