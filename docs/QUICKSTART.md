# Quick Start - 2 Minutes

## Step 1: Test (No Credits Needed)
```bash
cd c:/Users/marti/vif-trading-system
source venv/Scripts/activate
python agents/test_harness.py
```

Expected output: JSON with BUY/SELL/HOLD signals for sample tickers.

## Step 2: Add API Credits (Optional)
Visit https://console.anthropic.com/account/billing/overview and add credits.

## Step 3: Run Live Analysis
```bash
python agents/watchlist_watcher.py --watchlist energy_ai
```

Expected output: Real market data analyzed with VIF framework.

## That's It!

**What's Running:**
- ✓ 3 watchlists pre-configured
- ✓ Claude Opus 4.7 analysis ready
- ✓ Caching & fallback support
- ✓ Kill switch detection
- ✓ JSON report output

**Next:**
- Edit `config/vif_config.yml` to customize thresholds
- Run `--all` flag to analyze all watchlists at once
- Schedule daily analysis with cron/Windows Task Scheduler
