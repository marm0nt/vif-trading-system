---
name: monitoring-catalysts
description: Run or interpret catalyst scan results from scripts/catalyst_analysis.py. Use when analyzing catalyst risk, checking K4 kill switch status, reviewing sector themes, or interpreting earnings calendar data. Agent uses live Claude analysis + real yfinance earnings dates + recent news headlines.
---

# Skill: Monitoring Catalysts

## Agent file
`scripts/catalyst_analysis.py` | Pipeline slot: premarket (first) | Model: claude-sonnet-4-6

## What this agent does (live as of May 2026)
Every run it:
1. Loads all tickers from all 3 watchlists (deduplicates across watchlists)
2. Fetches real earnings dates via `yfinance.Ticker.calendar` (authoritative)
3. Fetches recent news headlines via `yfinance.Ticker.get_news()` (last 48-72h)
4. Detects K4 kill switch: earnings within 5 days → do not trade
5. Calls Claude with earnings + news + FOMC calendar to reason about catalysts
6. Outputs structured JSON to `reports/catalyst_analysis_<timestamp>.json`

## Run commands
```bash
python scripts/catalyst_analysis.py              # all 3 watchlists, top 15 each
python scripts/catalyst_analysis.py --watchlist vantage_portfolio
python scripts/catalyst_analysis.py --top 20    # expand to 20 tickers per watchlist
```

## Output schema
```json
{
  "analysis_date": "2026-05-02 17:07:27",
  "model": "claude-sonnet-4-6",
  "catalyst_themes": {
    "AI Chip Demand": ["MU", "AVGO", "MRVL"],
    "Fed Policy Impact": ["AAPL", "MSFT"]
  },
  "k4_kill_switches": {
    "NVDA": {"switch": "K4", "earnings_date": "2026-05-20", "days_away": 17, "action": "Do not initiate new positions"}
  },
  "earnings_calendar": {
    "MRVL": {"date": "2026-05-28", "days_away": 25, "k4_active": false},
    "NVDA": {"date": "2026-05-20", "days_away": 17, "k4_active": false}
  },
  "watchlist_analyses": {
    "VANTAGE_PORTFOLIO": {
      "macro_regime": {
        "fed_stance": "hawkish hold",
        "rate_trajectory": "neutral",
        "risk_appetite": "risk-on",
        "key_theme": "AI capex driving semiconductor demand"
      },
      "sector_themes": [
        {"theme": "AI Chip Demand", "tickers": ["MU","AVGO"], "catalyst_strength": "HIGH", "time_horizon": "5-30d"}
      ],
      "macro_calendar": [
        {"event": "FOMC Meeting", "date": "2026-06-17", "days_away": 46, "impact": "HIGH"}
      ],
      "ticker_catalysts": [
        {
          "ticker": "MU",
          "catalyst_type": "fundamental",
          "catalyst": "Q3 earnings beat expected on HBM demand",
          "catalyst_strength": "HIGH",
          "time_horizon": "5-30d",
          "key_risk": "China export controls",
          "kill_switch": null
        }
      ],
      "high_risk_catalysts": [
        {"ticker": "NVDA", "catalyst": "Q1 2026 earnings", "date": "2026-05-20",
         "days_away": 17, "risk": "HIGH", "action": "K4 kill switch"}
      ],
      "top_5_opportunity_tickers": ["MU", "AVGO", "MRVL", "WULF", "RDDT"],
      "top_3_risk_tickers": ["NVDA", "SMCI", "TSM"]
    }
  }
}
```

## Catalyst taxonomy
| Type | Examples | Risk level |
|---|---|---|
| **Policy** | Fed meeting, rate decision, FOMC minutes | HIGH |
| **Government** | CHIPS Act funding, DoD contracts, export controls | MED-HIGH |
| **Fundamental** | Earnings, guidance, revenue preannouncement | HIGH (K4) |
| **Sector** | ETF rebalance, index inclusion, capital flows | MED |
| **Macro** | CPI, PPI, jobs report, PCE | MED-HIGH |

## Catalyst → Kill Switch mapping
```
Earnings within 5 days        → K4 (do not take new positions)
Government contract < 24 hrs  → optional override (fast catalyst, can enter)
Export control announcement   → K2 if affects supply chain (NVDA, SMCI, TSM)
Fed rate surprise > 0.5%      → K1 market-wide (pause all new trades)
```

## Interpreting results — priority order
1. `k4_kill_switches` — check FIRST before any new position
2. `macro_regime.risk_appetite` — lean long (risk-on) or short (risk-off) as baseline
3. `top_5_opportunity_tickers` — Claude's highest-conviction catalyst plays this cycle
4. `sector_themes[].catalyst_strength = HIGH` — potential 10%+ movers
5. `earnings_calendar` sorted by `days_away` — upcoming binary events to respect

## FOMC dates 2026 (hardcoded in agent)
Jan 28, Mar 18, Apr 29, Jun 17, Jul 29, Sep 16, Oct 28, Dec 9

## Token cost
~2,500-4,000 tokens per full run (3 watchlists × 15 tickers, 1 Claude call each batch)
~$0.003-0.005 per run at Sonnet 4.6 pricing

## Performance checklist (review monthly)
- [ ] Verify K4 alerts matched actual earnings dates (yfinance can lag 1-2 days)
- [ ] Compare `top_5_opportunity_tickers` vs actual 2-week performance
- [ ] Check if `macro_regime.key_theme` matched market narrative that week
- [ ] If catalyst gap missed (untracked move > 5%): investigate and note
- [ ] Update FOMC_2026 list in script when Fed publishes next year's schedule
