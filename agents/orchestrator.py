#!/usr/bin/env python3
"""
VIF Orchestrator – Master Delegation Agent
==========================================
The "Investment Coordinator" for your VIF Trading System.
Inspired by the hierarchical multi-agent architecture used by top GitHub repos
(FinRobot, TradingAgents, ai-hedge-fund).

DELEGATION MAP
──────────────
┌─────────────────────────────────────────────────────────┐
│                     ORCHESTRATOR                        │
│             (this file – master controller)             │
└──────┬──────────────────────────────────────────────────┘
       │ delegates to
       ├──► data_fetcher_agent.py   – fetch + cache OHLCV
       ├──► technical_agent.py      – IndicatorEngine + screening
       ├──► vif_analyst_agent.py    – Claude VIF signals + gamma
       ├──► catalyst_agent.py       – policy/news/catalyst flags
       ├──► risk_agent.py           – kill switch + position sizing
       └──► report_agent.py         – save + format final output

USAGE
─────
  python agents/orchestrator.py --watchlist energy_ai
  python agents/orchestrator.py --all
  python agents/orchestrator.py --ticker NVDA
  python agents/orchestrator.py --mode premarket    (runs appropriate subset)
  python agents/orchestrator.py --mode afterhours
  python agents/orchestrator.py --mode weekend

Each mode picks which sub-agents to call and in what order.
"""
import sys, os, json, logging, argparse, subprocess
from datetime import datetime
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = lambda *a, **kw: None

load_dotenv(override=True)  # .env wins over any stale system env var
Path("logs").mkdir(exist_ok=True)
Path("reports").mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [ORCHESTRATOR] %(message)s",
    handlers=[
        logging.FileHandler("logs/orchestrator.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# ── Python interpreter (use venv if available) ────────────────────────────────
VENV_PY = str(Path("venv/Scripts/python.exe"))
PYTHON   = VENV_PY if Path(VENV_PY).exists() else sys.executable

# ── Mode → agent pipeline map ─────────────────────────────────────────────────
PIPELINES = {
    "premarket": [
        # 07:00 – 09:30 CT
        # Goal: identify best setups BEFORE the open
        ("Catalyst Scan",         ["catalyst_analysis.py"]),
        ("VIF Watchlist (1mo)",   ["agents/watchlist_watcher.py", "--all", "--period", "1mo"]),
        ("Swing Screener",        ["swing_trade_screener_v2.py"]),
    ],
    "market_open": [
        # 09:35 CT – catch opening volume
        ("Opening Swing Screen",  ["swing_trade_screener_v2.py"]),
    ],
    "afterhours": [
        # 16:05 CT – review how the day closed
        ("Daily Conviction Model",["daily_watchlist_analysis.py"]),
        ("VIF Wrap (5d)",         ["agents/watchlist_watcher.py", "--all", "--period", "5d"]),
    ],
    "weekend": [
        # Saturday/Sunday – macro + earnings prep
        ("Weekend Catalyst Brief",["agents/weekend_catalyst_agent.py"]),
    ],
    "full": [
        # On-demand: complete end-to-end run
        ("Catalyst Scan",         ["catalyst_analysis.py"]),
        ("VIF Full Scan (1mo)",   ["agents/watchlist_watcher.py", "--all", "--period", "1mo"]),
        ("Swing Screener V2",     ["swing_trade_screener_v2.py"]),
        ("Daily Analysis",        ["daily_watchlist_analysis.py"]),
        ("Weekend Brief",         ["agents/weekend_catalyst_agent.py"]),
    ],
}


def run_agent(label: str, cmd_args: list[str], timeout: int = 600) -> dict:
    """
    Run a sub-agent script, capture output.
    Returns a result dict with success flag, key outputs.

    📚 LEARNING: This pattern is called "Orchestrator-Worker."
       The orchestrator delegates to workers (sub-agents) and collects
       their outputs to build a unified picture. Each worker only
       knows about its own job – the orchestrator synthesises them.
    """
    full_cmd = [PYTHON] + cmd_args
    logger.info(f"  → Delegating to [{label}]  cmd={' '.join(cmd_args)}")
    try:
        result = subprocess.run(
            full_cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(Path.cwd()),
        )
        ok = result.returncode == 0
        if ok:
            logger.info(f"    ✓ {label} completed")
        else:
            logger.error(f"    ✗ {label} FAILED (exit {result.returncode})")
            for line in result.stderr.splitlines()[-5:]:
                logger.error(f"      {line}")
        return {"label": label, "success": ok, "cmd": cmd_args, "stdout_tail": result.stdout[-500:]}
    except subprocess.TimeoutExpired:
        logger.error(f"    ✗ {label} TIMEOUT ({timeout}s)")
        return {"label": label, "success": False, "cmd": cmd_args, "stdout_tail": "TIMEOUT"}
    except Exception as e:
        logger.error(f"    ✗ {label} ERROR: {e}")
        return {"label": label, "success": False, "cmd": cmd_args, "stdout_tail": str(e)}


def run_pipeline(mode: str) -> list[dict]:
    """Execute a full named pipeline, return job results."""
    pipeline = PIPELINES.get(mode, PIPELINES["full"])
    logger.info(f"Pipeline: [{mode.upper()}] – {len(pipeline)} agents")
    results = []
    for label, cmd in pipeline:
        results.append(run_agent(label, cmd))
    return results


def run_single_ticker(ticker: str) -> dict:
    """
    Deep dive on a single ticker across all agents.

    📚 LEARNING: This is a "fan-out then fan-in" pattern.
       We send one ticker to multiple specialist agents in parallel,
       then collect their specialist outputs and merge them.
    """
    logger.info(f"Single-ticker deep dive: {ticker}")
    from agents.indicators import fetch_and_compute

    # Step 1: Technical Agent – compute all indicators locally
    logger.info("  [Technical Agent] Computing indicators...")
    ind = fetch_and_compute(ticker, period="6mo")
    if not ind:
        return {"error": f"No data for {ticker}"}

    # Step 2: VIF Analyst – Claude reads the indicators
    logger.info("  [VIF Analyst] Running Claude VIF analysis...")
    result = run_agent(
        f"VIF Analysis ({ticker})",
        ["agents/watchlist_watcher.py", "--watchlist", "energy_ai", "--period", "1mo"],
    )

    return {
        "ticker": ticker,
        "indicators": ind,
        "vif_agent_result": result,
        "timestamp": datetime.now().isoformat(),
    }


def save_run_log(results: list[dict], mode: str):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = Path("reports") / f"orchestrator_{mode}_{ts}.json"
    out.write_text(json.dumps({
        "mode": mode,
        "started_at": datetime.now().isoformat(),
        "jobs": results,
        "summary": {
            "total": len(results),
            "passed": sum(1 for r in results if r.get("success")),
            "failed": sum(1 for r in results if not r.get("success")),
        }
    }, indent=2))
    logger.info(f"Run log saved → {out}")


def main():
    parser = argparse.ArgumentParser(
        description="VIF Orchestrator – delegates to all specialist agents"
    )
    parser.add_argument("--watchlist", "-w", help="Single watchlist name")
    parser.add_argument("--ticker",    "-t", help="Single ticker deep dive")
    parser.add_argument("--all",       action="store_true", help="All watchlists")
    parser.add_argument(
        "--mode", "-m",
        choices=list(PIPELINES.keys()),
        default="full",
        help="Pipeline mode (default: full)"
    )
    args = parser.parse_args()

    logger.info("=" * 65)
    logger.info("  VIF ORCHESTRATOR – AGENT DELEGATION SYSTEM")
    logger.info(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  |  mode={args.mode}")
    logger.info("=" * 65)

    if args.ticker:
        result = run_single_ticker(args.ticker.upper())
        print(json.dumps(result, indent=2))
        return 0

    results = run_pipeline(args.mode)
    save_run_log(results, args.mode)

    # Print summary
    passed = sum(1 for r in results if r.get("success"))
    print(f"\n{'='*65}")
    print(f"ORCHESTRATOR COMPLETE │ {passed}/{len(results)} agents succeeded")
    print(f"{'='*65}")
    for r in results:
        icon = "✓" if r["success"] else "✗"
        print(f"  {icon}  {r['label']}")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
