# VIF Trading System

AI-powered watchlist monitoring with VIF (Volatility Imbalance Framework) analysis using Claude.

## Quick Start

### 1. Install & Configure
```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your ANTHROPIC_API_KEY
```

### 2. Verify API Key
```bash
python tests/test_api_key.py
```

### 3. Test Live Analysis
```bash
python agents/watchlist_watcher.py --watchlist vantage_portfolio
```

Or test offline (no API credits):
```bash
python tests/test_harness.py
```

## Project Structure

```
vif-trading-system/
├── agents/              # Core AI agents
│   ├── watchlist_watcher.py     # VIF signal engine
│   ├── weekend_catalyst_agent.py# Macro/earnings briefing
│   ├── orchestrator.py          # Pipeline orchestrator
│   ├── indicators.py            # Shared indicator library
│   ├── claude_research_agent.py  # Ad-hoc research queries
│   └── report_ui_agent.py       # JSON→Markdown converter
├── scripts/             # Analysis scripts
│   ├── catalyst_analysis.py
│   ├── swing_trade_screener_v2.py
│   ├── advanced_analysis.py
│   └── daily_watchlist_analysis.py
├── tests/               # Testing utilities
│   ├── test_harness.py          # Offline mock testing
│   └── test_api_key.py          # API key verification
├── config/
│   └── vif_config.yml           # VIF thresholds, kill switches
├── watchlists/          # Ticker lists (TradingView exports)
├── reports/             # Output reports (JSON + Markdown)
├── logs/                # Scheduler logs
├── docs/                # Reference documentation
├── schedule_daily.py    # Master scheduler (main entry point)
├── run_delayed_start.py # Scheduler launcher utility
├── .env.example         # Environment template
├── requirements.txt     # Python dependencies
└── DEPLOYMENT_STATUS.txt# Operational reference
```

## Core Features

### Agents
- **Watchlist Watcher** - Monitors 3 watchlists (85+ tickers) for VIF signals
- **Weekend Catalyst Agent** - Scans macro events & earnings for Monday prep
- **Orchestrator** - Hierarchical multi-agent pipeline coordinator
- **Research Agent** - Interactive Q&A for VIF analysis

### Analysis Scripts
- **Catalyst Analysis** - Government/policy catalyst database
- **Swing Trade Screener** - Technical setup detection (5 types, ranked)
- **Advanced Analysis** - Multi-framework technical analysis
- **Daily Watchlist** - Conviction scoring + narrative summaries

### Configuration
- **VIF Config** (`config/vif_config.yml`) - All framework parameters:
  - Gamma regime thresholds
  - Kill switch conditions (K1–K6)
  - Volume & structural level detection
  - API model selection

## Watchlists

Pre-configured in `watchlists/`:
- `vantage_portfolio.txt` — 85 mixed holdings
- `ai_verticals.txt` — AI & semiconductor focus
- `energy_ai.txt` — Energy + AI convergence

## Usage

### Single Watchlist
```bash
python agents/watchlist_watcher.py --watchlist vantage_portfolio
```

### Custom Period
```bash
python agents/watchlist_watcher.py --watchlist ai_verticals --period 1mo
```

### Full Scheduler (automated daily)
```bash
python schedule_daily.py
```

Runs automatically:
- **Weekdays 07:00** → Catalyst scan
- **Weekdays 08:45** → Premarket VIF (1-month data)
- **Weekdays 09:35** → Market-open swing screener
- **Weekdays 16:05** → After-hours conviction + 5-day VIF
- **Friday 16:30** → End-of-week full sweep
- **Saturdays 08:00** → Weekend macro briefing
- **Sundays 18:00** → Monday morning prep

## Token Budget

- Daily total: ~13,000 tokens (~$0.13)
- Monthly: ~390,000 tokens (~$3.90)
- Well under $20/month

## Output

Reports saved to `reports/`:
- **Raw JSON** (`reports/raw/`) — Structured analysis data
- **Daily Markdown** (`reports/daily/`) — Human-readable summaries
- **Options Reports** (`reports/options/`) — Strategy analysis

## Documentation

- [AGENTS.md](docs/AGENTS.md) — Agent architecture details
- [SETUP.md](docs/SETUP.md) — Installation & configuration
- [QUICKSTART.md](docs/QUICKSTART.md) — Getting started guide
- [SKILLS.md](docs/SKILLS.md) — Framework skill descriptions

## Development

### Test without API credits
```bash
python tests/test_harness.py  # Offline mock VIF analysis
```

### Debug a specific script
```bash
python scripts/catalyst_analysis.py
python scripts/swing_trade_screener_v2.py
```

### Check API key status
```bash
python tests/test_api_key.py
```

## Future Enhancements

- [ ] Real-time TradingView webhook alerts
- [ ] Persistent storage (SQLite)
- [ ] Slack/Email notifications
- [ ] Multi-timeframe analysis
- [ ] Portfolio rebalancing suggestions
