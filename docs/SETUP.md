# VIF Trading System - Setup Guide

## ✓ System Status
- **Virtual Environment:** Created and activated
- **Dependencies:** Installed (anthropic, yfinance, pandas, numpy, pyyaml)
- **Watchlists:** 3 pre-configured (vantage_portfolio, ai_verticals, energy_ai)
- **Agents:** Ready (watchlist_watcher.py, test_harness.py)
- **Configuration:** VIF framework config ready (config/vif_config.yml)

## Quick Start

### 1. Activate Virtual Environment
```bash
cd c:/Users/marti/vif-trading-system
source venv/Scripts/activate  # Windows
# source venv/bin/activate      # Linux/Mac
```

### 2. Test Without API (No Credits Needed)
```bash
python agents/test_harness.py
```
Output: Mock VIF analysis showing the system structure. Results saved to `reports/test_analysis.json`.

### 3. Use Live Data (Requires API Credits)
First, add credits to your Anthropic account:
1. Go to https://console.anthropic.com/account/billing/overview
2. Purchase credits (even $5 allows hundreds of analyses)

Then run:
```bash
python agents/watchlist_watcher.py --watchlist energy_ai
python agents/watchlist_watcher.py --watchlist ai_verticals
python agents/watchlist_watcher.py --watchlist vantage_portfolio
```

### 4. Batch Analyze All Watchlists
```bash
python agents/watchlist_watcher.py --all
```

## System Architecture

### Three Components

**1. Watchlist Parser** (`watchlist_watcher.py`)
- Loads `.txt` files from `watchlists/` directory
- Cleans and deduplicates tickers
- Strips exchange prefixes (NASDAQ:, NYSE:, etc.)

**2. Data Fetcher** (`watchlist_watcher.py`)
- Fetches OHLCV data from Yahoo Finance
- Computes RSI, MA, volume indicators
- Caches locally to reduce API calls
- Falls back to mock data if API unavailable

**3. VIF Analyst** (Claude API)
- Analyzes market data with VIF framework
- Outputs BUY/SELL/HOLD signals with confidence
- Identifies gamma regime, structural levels, kill switches
- Returns JSON with full reasoning

## File Structure

```
vif-trading-system/
├── agents/
│   ├── watchlist_watcher.py      # Main agent (live data + Claude)
│   └── test_harness.py           # Local test (no API needed)
├── watchlists/
│   ├── vantage_portfolio.txt     # 85+ mixed holdings
│   ├── ai_verticals.txt          # 35+ AI/semiconductor
│   └── energy_ai.txt             # 13 energy+AI tickers
├── config/
│   └── vif_config.yml            # VIF parameters & kill switches
├── reports/
│   └── analysis_*.json           # Output reports (auto-generated)
├── data/
│   └── *.pkl                     # Cached market data (auto-generated)
├── .env                          # Your API key (KEEP SECRET)
├── .env.example                  # Template (safe to share)
└── venv/                         # Python virtual environment
```

## Configuration

Edit `config/vif_config.yml` to customize:

**VIF Thresholds:**
```yaml
vif_framework:
  gamma_regime:
    positive_threshold: 0.5       # Adjust gamma detection sensitivity
    negative_threshold: -0.5
  structural_levels:
    lookback_days: 20             # Historical window for support/resistance
  volume:
    ma_period: 20                 # Moving average period
    strong_threshold: 1.5         # 1.5x average = strong volume
```

**Kill Switches** (override conditions):
```yaml
kill_switches:
  k1: "Extreme Volatility (RSI > 80 or < 20)"
  k2: "Gap Risk (5-day range > 10%)"
  k3: "Low Liquidity (Volume < 1M)"
  k4: "News Risk (earnings within 5 days)"
  k5: "Correlation Risk (>0.8 with index)"
  k6: "Technical Breakdown (close below MA)"
```

**Data Fetching:**
```yaml
data_fetching:
  batch_size: 15                  # Tickers per Claude call (token control)
  period_default: "5d"            # Data lookback: 1d, 5d, 1mo, etc.
  cache_ttl_hours: 24             # Cache expiration
```

## Token Budget

**Per Watchlist Analysis:**
- Input: ~500 tokens (market data summary)
- Output: ~1000 tokens (JSON signals)
- Total: ~1,500 tokens per watchlist

**Pricing (Claude Opus 4.7):**
- Input: $5 per 1M tokens
- Output: $25 per 1M tokens
- Cost per watchlist: ~$0.02-0.03

**Usage Examples:**
- Daily (3 watchlists): 45,000 tokens = $0.40/day
- 50 days of daily analysis: $20 budget

## Troubleshooting

### "Your credit balance is too low"
**Solution:** Add credits at https://console.anthropic.com/account/billing/overview

### "No data for ticker X"
**Solution:** Yahoo Finance may not have data. Use `test_harness.py` instead or check ticker symbol.

### "Failed to import anthropic"
**Solution:** 
```bash
source venv/Scripts/activate
pip install anthropic
```

### "UnicodeEncodeError"
**Solution:** Already fixed in test_harness.py. Update your script.

## Next Steps

1. **Add Anthropic API Credits** → https://console.anthropic.com/account/billing/overview
2. **Run Test:** `python agents/test_harness.py` (verify system works)
3. **Run Live:** `python agents/watchlist_watcher.py --watchlist energy_ai`
4. **Schedule:** Set up daily cron/scheduler for automated analysis
5. **Integrate:** Export to Slack, email, or dashboard of choice

## Advanced Usage

### Custom Watchlist
1. Export from TradingView Desktop as `.txt`
2. Place in `watchlists/` directory
3. Run: `python agents/watchlist_watcher.py --watchlist mylist`

### Modify VIF Parameters
Edit `config/vif_config.yml` thresholds, then re-run analysis.

### Analyze Historical Period
```bash
python agents/watchlist_watcher.py --watchlist energy_ai --period 1mo
```

## Support

- **Claude:** Run `/help` to see available CLI tools
- **GitHub:** Check our examples in this repo
- **Docs:** See [AGENTS.md](AGENTS.md) and [SKILLS.md](SKILLS.md)
