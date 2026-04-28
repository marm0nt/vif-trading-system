#!/usr/bin/env python3
"""Schedule daily watchlist analysis."""
import schedule
import time
import subprocess
import logging
from datetime import datetime
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
Path('logs').mkdir(exist_ok=True)

def run_analysis():
    """Run all watchlist analyses."""
    logger.info("Starting daily watchlist analysis...")
    try:
        result = subprocess.run(
            ['python', 'agents/watchlist_watcher.py', '--all'],
            capture_output=True,
            text=True,
            timeout=300
        )
        if result.returncode == 0:
            logger.info("Analysis completed successfully")
        else:
            logger.error(f"Analysis failed: {result.stderr}")
    except subprocess.TimeoutExpired:
        logger.error("Analysis timed out after 5 minutes")
    except Exception as e:
        logger.error(f"Error: {e}")

def schedule_daily():
    """Schedule analysis at 9:30 AM daily."""
    schedule.every().day.at("09:30").do(run_analysis)
    logger.info("Scheduler started. Analysis scheduled for 09:30 daily.")

    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    try:
        schedule_daily()
    except KeyboardInterrupt:
        logger.info("Scheduler stopped")
