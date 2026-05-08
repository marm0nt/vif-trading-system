#!/usr/bin/env python3
"""
VIF Trading System – Intelligent Daily Scheduler
================================================
Schedule (all times US Central):

WEEKDAYS
  07:00  Premarket Catalyst Scan       → catalyst_analysis.py
  08:45  Premarket VIF Watchlist Scan  → watchlist_watcher.py --all   (30-day data)
  09:35  Market-Open Swing Screener    → swing_trade_screener_v2.py    (top setups)
  16:05  After-Hours Analysis          → daily_watchlist_analysis.py   (conviction scores)

WEEKENDS
  Sat 08:00  Weekend Catalyst Briefing → agents/weekend_catalyst_agent.py
  Sun 18:00  Monday Morning Prep       → agents/weekend_catalyst_agent.py

Run:  python schedule_daily.py
Stop: Ctrl+C
"""

import subprocess
import time
import logging
import json
import os
from datetime import datetime
from pathlib import Path

import schedule

# ── Setup ─────────────────────────────────────────────────────────────────────
Path("logs").mkdir(exist_ok=True)
Path("reports").mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [SCHEDULER] %(levelname)s – %(message)s",
    handlers=[
        logging.FileHandler("logs/scheduler.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# ── Venv-aware python path ────────────────────────────────────────────────────
VENV_PYTHON = str(Path("venv") / "Scripts" / "python.exe")
PYTHON = VENV_PYTHON if Path(VENV_PYTHON).exists() else "python"


# ── Job runner ────────────────────────────────────────────────────────────────
def run_job(label: str, cmd: list[str], timeout: int = 600) -> bool:
    """Run a subprocess job, log output, return success flag."""
    # Prevent concurrent runs of same job via lock file
    lock_file = Path(f".claude/scheduled_tasks.lock")
    job_id = "_".join(cmd).replace("/", "_").replace("-", "_")[:40]
    lock_path = lock_file.parent / f"{job_id}.lock"

    # Check if job is already running
    if lock_path.exists():
        ts_lock = lock_path.read_text().strip()
        try:
            ts_start = datetime.fromisoformat(ts_lock)
            elapsed = (datetime.now() - ts_start).total_seconds()
            if elapsed < timeout:
                logger.warning(f"  ⊘ SKIPPED: {label} (already running, started {elapsed:.0f}s ago)")
                return False
        except:
            pass
        # Stale lock, remove it
        lock_path.unlink(missing_ok=True)

    ts = datetime.now().strftime("%H:%M:%S")
    logger.info(f"{'='*60}")
    logger.info(f"  STARTING: {label}  [{ts}]")
    logger.info(f"{'='*60}")
    try:
        # Write lock file
        lock_path.parent.mkdir(exist_ok=True)
        lock_path.write_text(datetime.now().isoformat())

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if result.returncode == 0:
            logger.info(f"  ✓ COMPLETED: {label}")
            # Tail last 15 lines of stdout
            lines = result.stdout.strip().splitlines()
            for line in lines[-15:]:
                logger.info(f"    {line}")
            return True
        else:
            logger.error(f"  ✗ FAILED: {label} (exit {result.returncode})")
            for line in result.stderr.strip().splitlines()[-10:]:
                logger.error(f"    {line}")
            return False
    except subprocess.TimeoutExpired:
        logger.error(f"  ✗ TIMEOUT: {label} exceeded {timeout}s")
        return False
    except Exception as e:
        logger.error(f"  ✗ ERROR in {label}: {e}")
        return False
    finally:
        # Clean up lock file
        lock_path.unlink(missing_ok=True)


def log_run_summary(jobs: list[dict]):
    """Append a JSON run-summary to logs/run_history.json."""
    history_file = Path("logs") / "run_history.json"
    history = []
    if history_file.exists():
        try:
            history = json.loads(history_file.read_text())
        except Exception:
            pass
    history.append({
        "date": datetime.now().isoformat(),
        "jobs": jobs,
    })
    history_file.write_text(json.dumps(history[-60:], indent=2))  # keep last 60 runs


# ── Individual job definitions ────────────────────────────────────────────────

def job_premarket_catalyst():
    """07:00 – Policy, government & fundamental catalyst scan."""
    run_job(
        "Premarket Catalyst Analysis",
        [PYTHON, "scripts/active/analysis/catalyst_analysis.py"],
        timeout=120,
    )

def job_premarket_vif_scan():
    """08:45 – Orchestrator premarket pipeline (catalyst + VIF + swing)."""
    run_job(
        "Premarket Pipeline [Orchestrator]",
        [PYTHON, "agents/orchestrator.py", "--mode", "premarket"],
        timeout=720,
    )

def job_market_open_swing():
    """09:35 – Orchestrator market-open pipeline (swing screener)."""
    run_job(
        "Market-Open Pipeline [Orchestrator]",
        [PYTHON, "agents/orchestrator.py", "--mode", "market_open"],
        timeout=600,
    )

def job_afterhours_analysis():
    """16:05 – Orchestrator after-hours pipeline (daily + 5d VIF)."""
    jobs_log = []
    ok1 = run_job(
        "After-Hours Pipeline [Orchestrator]",
        [PYTHON, "agents/orchestrator.py", "--mode", "afterhours"],
        timeout=720,
    )
    jobs_log.append({"label": "after_hours_orchestrator", "success": ok1})
    log_run_summary(jobs_log)

def job_weekend_catalyst():
    """Weekend – Orchestrator weekend pipeline (catalyst briefing)."""
    run_job(
        "Weekend Pipeline [Orchestrator]",
        [PYTHON, "agents/orchestrator.py", "--mode", "weekend"],
        timeout=600,
    )

def job_friday_close():
    """Fri 16:30 – Full end-of-week pipeline via orchestrator."""
    run_job(
        "Friday Full Pipeline [Orchestrator]",
        [PYTHON, "agents/orchestrator.py", "--mode", "full"],
        timeout=900,
    )


# ── Schedule builder ──────────────────────────────────────────────────────────

def build_schedule():
    """Register all jobs with the schedule library."""

    # ── Weekday jobs ──────────────────────────────────────────────────────────
    for day in ["monday", "tuesday", "wednesday", "thursday", "friday"]:
        getattr(schedule.every(), day).at("07:00").do(job_premarket_catalyst)
        getattr(schedule.every(), day).at("08:45").do(job_premarket_vif_scan)
        getattr(schedule.every(), day).at("09:35").do(job_market_open_swing)
        getattr(schedule.every(), day).at("16:05").do(job_afterhours_analysis)

    # ── Friday extra ─────────────────────────────────────────────────────────
    schedule.every().friday.at("16:30").do(job_friday_close)

    # ── Weekend jobs ─────────────────────────────────────────────────────────
    schedule.every().saturday.at("08:00").do(job_weekend_catalyst)
    schedule.every().sunday.at("18:00").do(job_weekend_catalyst)

    logger.info("Schedule registered:")
    logger.info("  Weekdays  07:00  Premarket Catalyst Scan")
    logger.info("  Weekdays  08:45  Premarket VIF Watchlist (1mo data)")
    logger.info("  Weekdays  09:35  Market-Open Swing Screener V2")
    logger.info("  Weekdays  16:05  After-Hours Analysis (daily + 5d VIF)")
    logger.info("  Fridays   16:30  End-of-Week Screener + Options Strategy")
    logger.info("  Saturday  08:00  Weekend Catalyst Briefing")
    logger.info("  Sunday    18:00  Monday Morning Prep")


# ── Main loop ─────────────────────────────────────────────────────────────────

def main():
    logger.info("=" * 60)
    logger.info("  VIF TRADING SYSTEM – INTELLIGENT SCHEDULER")
    logger.info(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)

    build_schedule()

    # Show next run times
    logger.info("\nNext scheduled runs:")
    for job in schedule.jobs:
        logger.info(f"  {job.next_run.strftime('%A %Y-%m-%d %H:%M')}  ->  {job.job_func.__name__}")

    logger.info("\nScheduler running. Press Ctrl+C to stop.\n")

    while True:
        schedule.run_pending()
        time.sleep(30)          # check every 30 seconds (was 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\nScheduler stopped by user.")
