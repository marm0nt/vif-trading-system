# VIF Trading System

AI-powered TradingView watchlist monitoring with VIF (Volatility Imbalance Framework) analysis using Claude.

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt.txt
```

### 2. Set Up Environment
Copy `.env.example` to `.env` and add your Anthropic API key:
```bash
cp .env.example .env
# Edit .env with your CLAUDE_API_KEY
```

### 3. Run Watchlist Analysis
```bash
python agents/watchlist_watcher.py --watchlist vantage_portfolio
```

Output: JSON with BUY/SELL/HOLD signals, confidence scores, kill switch alerts.

## System Architecture

**3-Agent System:**
1. **Watchlist Parser** - Loads & validates TradingView exports
2. **Data Fetcher** - Pulls market data (Yahoo Finance)
3. **VIF Analyst** - Claude analyzes with VIF framework

See [AGENTS.md](AGENTS.md) for detailed architecture.

## Skills & Features

See [SKILLS.md](SKILLS.md) for:
- Watchlist parsing
- Market data fetching
- VIF framework analysis
- Token budget strategy

## Watchlists

Pre-configured watchlists in `watchlists/`:
- `vantage_portfolio.txt` - 85+ mixed holdings
- `ai_verticals.txt` - AI/semiconductor focus
- `energy_ai.txt` - Energy + AI convergence

Add new watchlists by exporting from TradingView Desktop.

## Configuration

Edit `config/vif_config.yml` to customize:
- VIF thresholds (gamma, volume, levels)
- Kill switch conditions
- Data periods & batch sizes
- API parameters

## Examples

### Analyze single watchlist
```bash
python agents/watchlist_watcher.py --watchlist vantage_portfolio
```

### Custom period (1 month)
```bash
python agents/watchlist_watcher.py --watchlist ai_verticals --period 1mo
```

### Batch analyze all watchlists
```bash
for wl in vantage_portfolio ai_verticals energy_ai; do
  python agents/watchlist_watcher.py --watchlist $wl
done
```

## Token Budget

- Per watchlist: ~1,200-1,500 tokens (~$0.01-0.02)
- 3 watchlists: ~4,500 tokens (~$0.04)
- Daily run: ~45,000 tokens (~$0.40/day, well under $20/month)

## Output

Analysis saved to `reports/` with JSON format:
```json
{
  "tickers": {
    "NASDAQ:NVDA": {
      "signal": "BUY",
      "confidence": 85,
      "gamma_regime": "positive",
      "level_type": "resistance",
      "volume_signal": "strong",
      "kill_switch": null,
      "reasoning": "..."
    }
  },
  "summary": "..."
}
```

## Future Enhancements

- [ ] Real-time TradingView webhook alerts
- [ ] Persistent storage (SQLite/PostgreSQL)
- [ ] Slack/Email notifications
- [ ] Multi-timeframe analysis
- [ ] Options chain integration (GEX, Gamma)
- [ ] Portfolio rebalancing suggestions
