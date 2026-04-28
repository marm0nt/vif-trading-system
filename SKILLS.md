# VIF Trading System - Skills

## Skill 1: Watchlist Parsing
**What it does:** Loads TradingView exported watchlist files, validates tickers, deduplicates.

**Triggers on:**
- New watchlist file added to `watchlists/` directory
- Manual invocation: `python agents/watchlist_watcher.py --watchlist {name}`

**Input:** Raw CSV/TXT from TradingView
**Output:** Cleaned, deduplicated ticker list

**Example:**
```bash
python agents/watchlist_watcher.py --watchlist vantage_portfolio
```

---

## Skill 2: Market Data Fetching
**What it does:** Pulls OHLCV data from yfinance, computes RSI/MA indicators, caches locally.

**Triggers on:**
- Watchlist analysis starts
- Daily at 9 AM (optional scheduler)

**Data Sources:**
- Yahoo Finance (free, no API key)
- Caches in `./data/` to minimize API calls

**Optimization:**
- Limits to first 15 tickers per run (cost control)
- 5-day lookback by default (adjust with `--period`)

---

## Skill 3: VIF Analysis
**What it does:** Claude analyzes market data against VIF framework, outputs signals.

**VIF Framework:**
- **Gamma Regime:** Positive (calls ITM), negative (puts ITM), transition
- **Structural Levels:** Support/resistance from recent highs/lows
- **Volume Confirmation:** Above/below 20-day average
- **Kill Switches:** K1-K6 override conditions

**Output Signals:**
- BUY (confidence 0-100)
- SELL (confidence 0-100)
- HOLD (confidence 0-100)

**Cost Control:**
- Batches 10-15 tickers per Claude call
- Uses summaries, not raw candle data
- ~$2-4 per full watchlist analysis (Opus 4.7)

---

## Usage Examples

### Single Watchlist
```bash
python agents/watchlist_watcher.py --watchlist vantage_portfolio
```

### Custom Period
```bash
python agents/watchlist_watcher.py --watchlist ai_verticals --period 1mo
```

### Batch All Watchlists
```bash
for wl in vantage_portfolio ai_verticals energy_ai; do
  python agents/watchlist_watcher.py --watchlist $wl
done
```

---

## Token Budget
- **Per watchlist:** ~1,200-1,500 tokens (input: market data + prompt, output: JSON analysis)
- **3 watchlists:** ~4,500 tokens (~$0.04 at Opus pricing)
- **Daily run:** 30 calls = ~45,000 tokens (~$0.40/day)

**Under $20 budget:** Sustainable for ~50 days of daily full-watchlist analysis.

---

## Configuration
Edit `config/vif_config.yml` to customize:
- VIF regime thresholds
- Kill switch conditions
- Indicator periods (RSI, MA)
- Batch sizes for token control
