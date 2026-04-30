# Skill: Monitoring Catalysts
<!-- Agent: catalyst_analysis.py | Time: 07:00 CT weekdays -->

## Role
Map tickers to upcoming policy, government, and fundamental catalysts.
Flag any catalyst that could cause gap moves > 5% within 5 trading days.

## Catalyst taxonomy
| Type | Examples | Risk level |
|---|---|---|
| **Policy** | Fed meeting, rate decision, FOMC minutes | HIGH |
| **Government** | CHIPS Act funding, DoD contracts, export controls | MED–HIGH |
| **Fundamental** | Earnings, guidance, revenue preannouncement | HIGH (K4) |
| **Sector** | ETF rebalance, index inclusion, sector ETF flows | MED |
| **Macro** | CPI, PPI, jobs report, GDP | MED–HIGH |

## Output format
```json
{
  "scan_date": "2026-04-29",
  "high_risk_catalysts": [
    {
      "ticker": "NVDA",
      "catalyst": "Earnings (Q1 2026)",
      "date": "2026-05-28",
      "days_away": 29,
      "risk": "HIGH",
      "action": "K4 kill switch if within 5 days"
    }
  ],
  "sector_themes": ["AI capex cycle", "nuclear power demand", "defense AI"],
  "macro_calendar": ["FOMC minutes (2026-05-21)", "CPI (2026-05-13)"]
}
```

## Catalyst → Kill Switch mapping
```
Earnings within 5 days        → K4 (do not take new positions)
Government contract < 24 hrs  → optional override (fast catalyst, can enter)
Export control announcement   → K2 if affects supply chain (NVDA, SMCI)
Fed rate surprise > 0.5%      → K1 market-wide (pause all new trades)
```

## Performance checklist (review monthly)
- [ ] Verify earnings dates against yfinance earningsTimestamp (can lag by 1-2 days)
- [ ] Update macro_calendar monthly (Fed, CPI, PPI schedule)
- [ ] Add new CHIPS Act funding rounds as they are announced
- [ ] If a catalyst is missed (untracked gap): add to catalyst DB immediately
- [ ] Compare flagged HIGH risk catalysts vs actual next-day moves > 5%
