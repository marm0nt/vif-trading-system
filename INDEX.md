# VIF Trading System - Complete Index

## 📋 Start Here

1. **New to the system?** → Read [QUICKSTART.md](QUICKSTART.md) (2 minutes)
2. **Full setup?** → Read [SETUP.md](SETUP.md) (comprehensive guide)
3. **Project overview?** → Read [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)
4. **Deployment status?** → Check [DEPLOYMENT_STATUS.txt](DEPLOYMENT_STATUS.txt)

---

## 📁 File Structure

### Core Agents
- **[agents/watchlist_watcher.py](agents/watchlist_watcher.py)** - MAIN agent
  - Loads watchlists
  - Fetches market data
  - Analyzes with Claude
  - Returns BUY/SELL/HOLD signals

- **[agents/test_harness.py](agents/test_harness.py)** - DEMO agent
  - Local testing (no API credits needed)
  - Mock VIF analysis
  - JSON output validation

- **[agents/claude_research_agent.py](agents/claude_research_agent.py)** - Reference
  - Original research agent
  - VIF framework expert prompt

### Watchlists
- **[watchlists/vantage_portfolio.txt](watchlists/vantage_portfolio.txt)** - 85 tickers
  - Mixed sectors & indices
  - Large cap focus

- **[watchlists/ai_verticals.txt](watchlists/ai_verticals.txt)** - 35 tickers
  - AI & semiconductor focus
  - Chipmakers, software

- **[watchlists/energy_ai.txt](watchlists/energy_ai.txt)** - 13 tickers
  - Energy + AI convergence
  - Power & infrastructure

### Configuration
- **[config/vif_config.yml](config/vif_config.yml)** - VIF settings
  - Gamma thresholds
  - Kill switches (K1-K6)
  - Volume parameters
  - Data fetch options

### Tools & Utilities
- **[schedule_daily.py](schedule_daily.py)** - Daily scheduler
  - Runs at 9:30 AM
  - Analyzes all watchlists
  - Logs to `logs/scheduler.log`

---

## 📚 Documentation

| File | Purpose |
|------|---------|
| [QUICKSTART.md](QUICKSTART.md) | 2-minute quick start |
| [SETUP.md](SETUP.md) | Complete setup & troubleshooting |
| [README.md](README.md) | Features & usage examples |
| [AGENTS.md](AGENTS.md) | 3-agent architecture |
| [SKILLS.md](SKILLS.md) | Detailed skill descriptions |
| [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) | Full project overview |
| [DEPLOYMENT_STATUS.txt](DEPLOYMENT_STATUS.txt) | Deployment checklist |
| [INDEX.md](INDEX.md) | This file |

---

## 🚀 Usage

### Test (No API Credits)
```bash
python agents/test_harness.py
```
Output: Mock VIF analysis → `reports/test_analysis.json`

### Live Analysis
```bash
# Single watchlist
python agents/watchlist_watcher.py --watchlist energy_ai

# All watchlists
python agents/watchlist_watcher.py --all

# Custom period (1 month)
python agents/watchlist_watcher.py --watchlist ai_verticals --period 1mo
```

### Schedule Daily at 9:30 AM
```bash
python schedule_daily.py
```

---

## 📊 Output Format

Analysis results saved as JSON in `reports/` directory:

```json
{
  "analysis_date": "2026-04-28 09:30:00",
  "watchlist": "energy_ai",
  "tickers_analyzed": 13,
  "signals": {
    "NASDAQ:BE": {
      "signal": "BUY|SELL|HOLD",
      "confidence": 0-100,
      "gamma_regime": "positive|negative|transition",
      "level_type": "support|resistance",
      "volume_signal": "strong|weak",
      "kill_switch": "K1|K2|...|null",
      "price": 245.60,
      "rsi": 32.1,
      "reasoning": "RSI 32, vol 2.1x, change 2.3%"
    }
  },
  "summary": "BUY 4, SELL 2, HOLD 7"
}
```

---

## 💰 Token Budget

- **Per watchlist:** 1,500 tokens (~$0.02)
- **Daily (3 watchlists):** 45,000 tokens (~$0.40)
- **Monthly:** 1.35M tokens (~$12)
- ✓ Well under $20/month

---

## 🔐 Security

✓ `.env` with API key → in `.gitignore`
✓ `.env.example` template → safe to share
✓ Git history cleaned of credentials
✓ Mock fallback if API unavailable

---

## ⚙️ Configuration

**Edit VIF thresholds:**
```bash
# config/vif_config.yml
vif_framework:
  gamma_regime:
    positive_threshold: 0.5
  volume:
    strong_threshold: 1.5
```

**Add custom watchlist:**
1. Export from TradingView Desktop
2. Save to `watchlists/mylist.txt`
3. Run: `python agents/watchlist_watcher.py --watchlist mylist`

---

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| "Credit balance too low" | Add credits: https://console.anthropic.com/account/billing/overview |
| "No data for ticker" | Use `test_harness.py` or verify ticker symbol |
| "Import error" | `source venv/Scripts/activate && pip install -r requirements.txt.txt` |
| "UnicodeEncodeError" | Already fixed in test_harness.py |

---

## 📦 Dependencies

```
anthropic>=0.24.0       # Claude API
yfinance>=0.2.30        # Market data
pandas>=2.0.0           # Data analysis
numpy>=1.24.0           # Numerical computing
pyyaml>=6.0             # Config files
python-dotenv>=1.0.0    # Environment variables
schedule>=1.1.0         # Daily scheduler
pytest>=7.4.0           # Testing (optional)
```

---

## 🎯 Next Steps

1. **Test:** `python agents/test_harness.py`
2. **Add API credits:** https://console.anthropic.com/account/billing/overview
3. **Run live:** `python agents/watchlist_watcher.py --watchlist energy_ai`
4. **Check output:** `reports/analysis_*.json`
5. **Schedule (optional):** `python schedule_daily.py`

---

## 📞 Support

- **Claude Help:** Run `/help` for CLI tool documentation
- **Issues:** Check [SETUP.md](SETUP.md) troubleshooting section
- **Customization:** Edit [config/vif_config.yml](config/vif_config.yml)

---

**System Ready.** Add API credits and run your first analysis now!
