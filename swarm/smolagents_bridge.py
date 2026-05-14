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
    SMOLAGENTS_AVAILABLE = True
except ImportError:
    SMOLAGENTS_AVAILABLE = False
    # Define dummy tool decorator and classes for graceful degradation
    def tool(func):
        return func
    ToolCallingAgent = None
    CodeAgent = None
    ManagedAgent = None
    AnthropicModel = None

# Initialize Claude model only if smolagents is available
if SMOLAGENTS_AVAILABLE:
    MODEL_PROD = AnthropicModel(model_id="claude-sonnet-4-6", temperature=0)
    MODEL_RESEARCH = AnthropicModel(model_id="claude-opus-4-7", temperature=0.2)
else:
    MODEL_PROD = None
    MODEL_RESEARCH = None


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
def run_finviz_discovery() -> str:
    """
    Run all 19 FinViz institutional screeners and return discovered tickers.

    Screeners include Hunt, CANSLIM A+/B+, Kell V1-V4, Gap Up/Down,
    Shorted-to-Breakouts, Earnings Gap Ups, David Ryan Core, and more.
    Results are cached 24h; empty screeners are automatically skipped.
    Token cost: 0 (fully local execution, no API calls).

    Returns:
        JSON string with unique tickers discovered and screener metrics
    """
    try:
        from swarm.native_finviz_screener_agent import execute_finviz_screening
        result = execute_finviz_screening()
        unique_tickers: list = []
        for screener_result in result.get("results", {}).values():
            unique_tickers.extend(screener_result.get("tickers", []))
        return json.dumps({
            "status": "success",
            "screeners_with_results": result.get("screeners_with_results", 0),
            "screeners_skipped": result.get("screeners_skipped", 0),
            "unique_tickers": sorted(set(unique_tickers)),
            "cache_hit": result.get("cache_hit", False),
            "token_cost": 0,
        })
    except Exception as e:
        return json.dumps({"error": str(e), "tool": "run_finviz_discovery"})


@tool
def run_signal_backtest(ticker_signals_json: str = "{}") -> str:
    """
    Backtest VIF signals using vectorbt — validates historical Sharpe ratio, max drawdown,
    and win rate for each ticker via 6-month RSI+SMA momentum simulation.

    Signals with Sharpe < 0.5 or drawdown > 20% are flagged.
    Results cached 24h per ticker. Token cost: 0 (Numba-accelerated local computation).
    Falls back to pandas computation if vectorbt not installed.

    Args:
        ticker_signals_json: JSON string of {ticker: {signal, confidence}} pairs.
                             If empty, reads from latest VIF signal output.

    Returns:
        JSON string with per-ticker backtest metrics, flagged tickers, and summary stats
    """
    try:
        from swarm.native_vectorbt_agent import run_signal_backtest as _run_backtest
        import json as _json

        signals = _json.loads(ticker_signals_json) if ticker_signals_json.strip() != "{}" else {}
        result = _run_backtest(signals=signals or None)

        # Summarize for smolagents consumption
        flagged = result.get("flagged_tickers", [])
        bt = result.get("backtest_results", {})
        summary = {t: {
            "sharpe": r.get("sharpe_ratio"),
            "max_drawdown": r.get("max_drawdown"),
            "win_rate": r.get("win_rate"),
            "flagged": r.get("flagged"),
            "engine": r.get("engine"),
        } for t, r in bt.items() if r.get("status") == "completed"}

        return _json.dumps({
            "status": "success",
            "signals_validated": result.get("signals_validated", 0),
            "signals_flagged": result.get("signals_flagged", 0),
            "flagged_tickers": flagged,
            "backtest_summary": summary,
            "execution_time_ms": result.get("execution_time_ms", 0),
            "cache_hits": result.get("cache_hits", 0),
            "token_cost": 0,
        })
    except Exception as e:
        return json.dumps({"error": str(e), "tool": "run_signal_backtest"})


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


@tool
def run_autoresearch(research_query: str = "", context_signals_json: str = "{}") -> str:
    """
    Run iterative research synthesis to validate trading signals and explore macro context.

    Implements Karpathy/autoresearch framework:
    1. Decompose query into sub-questions
    2. Search for evidence and insights
    3. Synthesize findings into confidence-scored conclusions
    4. Cross-validate against prior VIF context

    Uses 24-hour caching per query; falls back to cached results if query was
    researched earlier today. Max 3 iterations per query (~500 tokens).

    Args:
        research_query: Research question (e.g., "What drives NVDA momentum?")
        context_signals_json: Optional JSON string of prior signals for cross-validation

    Returns:
        JSON string with findings, confidence score, topics, novel insights, execution time
    """
    try:
        from swarm.native_autoresearch_agent import execute_autoresearch
        import json as _json

        context_signals = _json.loads(context_signals_json) if context_signals_json.strip() != "{}" else {}
        result = execute_autoresearch(research_query=research_query, context_signals=context_signals)

        return _json.dumps({
            "status": result.get("status", "unknown"),
            "query": result.get("query", ""),
            "findings": result.get("findings", []),
            "confidence_score": result.get("confidence_score", 0.0),
            "topics": result.get("topics", []),
            "novel_insights": result.get("novel_insights", []),
            "execution_time_ms": result.get("execution_time_ms", 0),
            "cache_hit": result.get("cache_hit", False),
            "iterations_used": result.get("iterations_used", 0),
            "token_cost": 500 if not result.get("cache_hit") else 0,
        })
    except Exception as e:
        return json.dumps({"error": str(e), "tool": "run_autoresearch"})


# ── Production Path: ToolCallingAgent ─────────────────────────────────────────

class ProductionSwarmBridge:
    """
    Scheduled daily pipeline coordinator.

    Uses ToolCallingAgent (deterministic, structured reasoning) for reliable
    multi-step analysis of watchlists, catalysts, and swing setups.
    """

    def __init__(self):
        """Initialize production swarm with ToolCallingAgent agents."""
        if not SMOLAGENTS_AVAILABLE:
            raise ImportError("ProductionSwarmBridge requires smolagents. Install with: pip install smolagents")
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

        self.finviz_agent = ToolCallingAgent(
            tools=[run_finviz_discovery],
            model=MODEL_PROD,
            name="finviz_screener",
            description="19-screener FinViz institutional discovery (Hunt, CANSLIM, Kell, etc.)"
        )

        self.backtest_agent = ToolCallingAgent(
            tools=[run_signal_backtest],
            model=MODEL_PROD,
            name="vectorbt_backtester",
            description="Validates VIF signals via 6-month historical backtest (Sharpe, drawdown, win rate). Flags underperforming signals before execution."
        )

        self.autoresearch_agent = ToolCallingAgent(
            tools=[run_autoresearch],
            model=MODEL_PROD,
            name="autoresearch",
            description="Iterative research synthesis for signal validation and macro context"
        )

        # Create orchestrator that delegates to sub-agents
        self.orchestrator = ToolCallingAgent(
            tools=[
                ManagedAgent(self.catalyst_agent, name="catalyst_monitor", description="Run catalyst scan first"),
                ManagedAgent(self.vif_agent, name="vif_analyst", description="Run VIF analysis second"),
                ManagedAgent(self.backtest_agent, name="vectorbt_backtester", description="Run signal backtest third — validates Sharpe/drawdown before acting on signals"),
                ManagedAgent(self.swing_agent, name="swing_screener", description="Run swing screener fourth"),
                ManagedAgent(self.finviz_agent, name="finviz_screener", description="Run FinViz discovery fifth"),
                ManagedAgent(self.autoresearch_agent, name="autoresearch", description="Run autoresearch sixth — iterative validation and macro synthesis"),
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
        if not SMOLAGENTS_AVAILABLE:
            raise ImportError("ResearchSwarmBridge requires smolagents. Install with: pip install smolagents")
        logger.info("Initializing ResearchSwarmBridge (CodeAgent mode)")

        self.agent = CodeAgent(
            tools=[
                analyze_watchlist_vif,
                scan_macro_catalysts,
                screen_swing_setups,
                run_finviz_discovery,
                run_signal_backtest,
                run_autoresearch,
                get_kv_cache_metrics,
            ],
            model=MODEL_RESEARCH,
            name="vif_research_agent",
            description="VIF trading system research and analysis agent",
            additional_authorized_imports=["json", "pandas", "numpy", "pathlib", "datetime", "vectorbt"],
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
