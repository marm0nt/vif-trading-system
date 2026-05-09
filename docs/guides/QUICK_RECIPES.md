# Quick Recipes: Copy-Paste Workflows

**Ready-to-run commands and workflows for common trading tasks.**

---

## Recipe 1: Daily Premarket (Run Every Morning 08:30)

### Command
```bash
cd C:\Users\marti\vif-trading-system
python agents/orchestrator.py --mode premarket --watchlist vantage_portfolio
```

### Expected Output
- `reports/premarket_2026-05-09.html` (open in browser)
- JSON data in `reports/raw/premarket_YYYY-MM-DD.json`

### What to Look For
1. **Top Tier 1 signals** (high confidence, BUY/SELL):
   - Click on ticker name to see structural levels
   - Check R:R ratio (should be > 2:1)
   
2. **K4 Kill Switches** (red flags):
   - If ticker is flagged, skip it (earnings risk, gap risk, etc.)
   
3. **Swing Setup Ranks**:
   - Ranks 1–3 are tradeable
   - Ranks 4–5 skip (better setups coming)

### Next Step
- Set price alerts on top 3 on your broker
- Plan entry/exit zones based on structural levels
- Check K4 veto list before entering

---

## Recipe 2: Monday Morning Macro Brief (Run Sunday 18:00)

### Command
```bash
cd C:\Users\marti\vif-trading-system
python agents/orchestrator.py --mode weekend
```

### Expected Output
- `reports/weekend_macro_2026-05-09.html`
- Earnings calendar, sector momentum, macro catalysts

### What to Look For
1. **Monday Open Bias**:
   - Is the report saying "Energy likely to lead" or "Tech under pressure"?
   
2. **Earnings Calendar**:
   - Any mega-cap earnings Mon–Tue? (NVDA, TSLA, etc.)
   - These will be K4 flagged tomorrow
   
3. **Sector Rotation**:
   - Are there winners/losers identified?
   - Example: "Banks outperform on rising rates"

### Next Step
- Read brief with morning coffee
- Adjust watchlist for Monday (add rotation tickers)
- Use Monday market open to find aligned setups

---

## Recipe 3: Find Your Best Swing Setups (Run Anytime)

### Command
```bash
cd C:\Users\marti\vif-trading-system
python scripts/swing_trade_screener_v2.py --watchlist ai_verticals --period 2w
```

### Expected Output
- `reports/swing_setups_2026-05-09.json`
- Ranked list of 30–50 2-week setups

### What to Look For
1. **Top 5 Setups**:
   - Ticker, setup type (PULLBACK, BREAKOUT, etc.), R:R ratio
   - If R:R < 2:1, skip it
   
2. **Volume Confirmation**:
   - Is current volume > 20-day MA?
   - If NO, skip (hard exit)

### Next Step
- Open TradingView for top 3 tickers
- Verify chart matches the setup description
- Set entry alert at support level
- Calculate stop/target based on R:R

---

## Recipe 4: Deep Dive on One Ticker (High Conviction)

### Command (Multi-Timeframe Check)
```bash
cd C:\Users\marti\vif-trading-system

# Get daily signal
python agents/orchestrator.py --ticker NVDA --period 1d

# Get weekly signal
python agents/orchestrator.py --ticker NVDA --period 1w

# Get monthly signal
python agents/orchestrator.py --ticker NVDA --period 1mo
```

### Expected Output
Three JSON files with confidence scores for each timeframe.

### Decision Matrix
```
Daily BUY + Weekly BUY + Monthly BUY 
  → Tier 1 (100% position size)

Daily BUY + Weekly BUY (Monthly HOLD/SELL)
  → Tier 2 (50% position size)

Daily BUY only
  → Tier 3 (skip or 25% for research)
```

### Next Step
1. Open TradingView chart (daily + weekly + monthly)
2. Mark structural levels from output
3. Identify entry zone (at support, not euphoric)
4. Check catalyst-monitor for K4 risk
5. Set alerts and enter with size matching tier

---

## Recipe 5: Check Overnight Gaps (Run 09:35)

### Command
```bash
cd C:\Users\marti\vif-trading-system
python agents/orchestrator.py --mode market_open
```

### Expected Output
- `reports/market_open_2026-05-09.html`
- Flags tickers with gap > 3%

### What to Look For
1. **Gapped Tickers**:
   - Are they on K4 veto list? (Earnings expected?)
   - If gapped > 5% unexpectedly: May revert (short opportunity) or continue (trend)
   
2. **Swing Screens Updated**:
   - Some setups may have changed post-gap
   - Ranks may have shifted

### Next Step
- Skip K4-flagged gaps (they're priced in)
- Watch for reversals on smaller timeframes
- Use updated swing screens for fresh entries

---

## Recipe 6: End-of-Day Conviction Update (Run 16:05)

### Command
```bash
cd C:\Users\marti\vif-trading-system
python agents/orchestrator.py --mode afterhours
```

### Expected Output
- `reports/afterhours_2026-05-09.html`
- Conviction scores, 5-day momentum, EOD summary

### What to Look For
1. **Conviction Scores**:
   - Which holdings are still high conviction EOD?
   - Which are fading (consensus dropping)?
   
2. **5-Day Momentum**:
   - Should help identify next week setups
   
3. **EOD Summary**:
   - Win/loss tally for the day
   - Tomorrow's macro context

### Next Step
- Update positions if conviction faded
- Plan next morning entries based on 5-day read
- Log any lessons from today

---

## Recipe 7: Monitor Earnings Risk (Run Anytime)

### Command
```bash
cd C:\Users\marti\vif-trading-system
python scripts/catalyst_analysis.py --watchlist vantage_portfolio
```

### Expected Output
- `reports/catalyst_2026-05-09.json`
- Earnings calendar, K4 risk flags, macro events

### What to Look For
1. **Earnings within 5 days** = K4 flagged
   - These will skip automatically in vif-analyst
   
2. **Macro Events** (FOMC, CPI, etc.):
   - Can cause sector-wide moves
   - Check if your correlations will be affected

### Next Step
- Cross-reference K4 list with your positions
- Tighten stops if K4 active and you're holding through it
- Wait for post-earnings move to settle before re-entering

---

## Recipe 8: Check System Health (Run Weekly)

### Command
```bash
cd C:\Users\marti\vif-trading-system

# Check last 10 days of logs
tail -100 logs/vif_trading.log

# Check API cost (if tracking)
python scripts/check_usage.py

# Check config is valid
python -c "import yaml; yaml.safe_load(open('config/vif_config.yml'))" && echo "Config OK"
```

### What to Look For
1. **Logs**:
   - Any ERROR or WARNING lines?
   - Last run timestamp (is scheduler alive?)
   
2. **API Cost**:
   - Running under $20/month?
   - Any spike indicates inefficiency
   
3. **Config**:
   - If "Config OK" prints, you're good

### Next Step
- If errors, check vif_config.yml and watchlist files
- If cost spike, investigate which agent ran excessive API calls
- If scheduler dead, restart: `python schedule_daily.py`

---

## Recipe 9: Manual Market Research (Ad-Hoc)

### Command
```bash
cd C:\Users\marti\vif-trading-system
python agents/claude_research_agent.py --query "Why is NVDA gapping up?" --model sonnet
```

### Expected Output
- Detailed analysis from Claude with:
  - Recent news, earnings, technical setup
  - Macro context (sector rotation, rate expectations)
  - Probability of continuation vs reversal

### Use Cases
- Understand unexpected gaps
- Research new ticker (not in watchlist)
- Understand sector headwinds
- Deep analysis on thesis before large position

### Next Step
- Use findings to inform position sizing
- Check if finding aligns with your signals
- If disagreement, use research to override signal (manual judgment)

---

## Recipe 10: Setup Your Environment (One-Time)

### Prerequisites
```bash
# Python 3.11+
python --version

# Install dependencies
pip install -r requirements.txt

# Copy .env.example to .env and add your API key
cp .env.example .env
# Edit .env with your ANTHROPIC_API_KEY
```

### Create Required Directories
```bash
mkdir -p reports/raw reports/daily reports/options
mkdir -p data logs
```

### Initialize Watchlists
Place your TradingView watchlist exports in `watchlists/`:
```
watchlists/vantage_portfolio.txt
watchlists/ai_verticals.txt
watchlists/energy_ai.txt
```

Each file: one ticker per line (no headers).

### Test the System
```bash
# Test API key
python tests/test_api_key.py

# Test offline (no API calls)
python tests/test_harness.py

# Run a small analysis
python agents/watchlist_watcher.py --watchlist vantage_portfolio --period 1mo
```

### Next Step
- Run `python schedule_daily.py` to start daily pipeline
- Check `reports/` for output HTML files
- Adjust `config/vif_config.yml` if needed

---

## Troubleshooting Quick Fixes

### "Module not found: yfinance"
```bash
pip install yfinance
```

### "API key invalid"
```bash
# Check your .env file
cat .env | grep ANTHROPIC_API_KEY

# Should print your key (not blank)
# If blank, add it: ANTHROPIC_API_KEY=sk-ant-...
```

### "No such file: watchlists/vantage_portfolio.txt"
```bash
# Create empty watchlist with a few tickers
echo "NVDA" > watchlists/vantage_portfolio.txt
echo "TSLA" >> watchlists/vantage_portfolio.txt
echo "AAPL" >> watchlists/vantage_portfolio.txt
```

### "Reports folder empty"
```bash
# Check if orchestrator actually ran
tail -20 logs/vif_trading.log

# If no logs, start it manually
python agents/orchestrator.py --mode premarket --watchlist vantage_portfolio
```

### "K4 kill switches not working"
```bash
# Verify config is loaded
python -c "import yaml; c = yaml.safe_load(open('config/vif_config.yml')); print(c['kill_switches'])"

# Should print all 6 K1–K6 thresholds
```

---

## Cheat Sheet: Commands by Time

| Time | Command | Output |
|------|---------|--------|
| 07:00 | `catalyst_analysis.py` | Earnings + K4 flags |
| 08:30 | `orchestrator --mode premarket` | Signals + setups |
| 09:35 | `orchestrator --mode market_open` | Gap alerts |
| 16:05 | `orchestrator --mode afterhours` | EOD convictions |
| 16:30 (Fri) | `orchestrator --mode full` | All of above |
| Sun 18:00 | `orchestrator --mode weekend` | Monday brief |
| Anytime | `swing_trade_screener_v2.py` | Ranked setups |
| Anytime | `claude_research_agent.py` | Deep research |

---

**Last Updated:** 2026-05-09

See **LEVERAGE_GUIDE.md** for backtested patterns and decision frameworks.
