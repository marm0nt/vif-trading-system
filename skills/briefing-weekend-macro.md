# Skill: Briefing Weekend Macro
<!-- Agent: agents/weekend_catalyst_agent.py | Times: Sat 08:00 + Sun 18:00 CT -->

## Role
Produce a Monday Morning Briefing: macro themes, top setups, earnings watch,
sector rotation, and a 3-bullet Monday game plan. Concise. No filler.

## Prompt template (XML-structured)

```xml
<context>
  You are a VIF macro strategist preparing a Monday Morning Briefing.
  Your output feeds directly into the trader's pre-market checklist.
  Date: {DATE} | Tickers scanned: {N} | Weekend mode: {SAT|SUN}
</context>

<weekly_data>
{MARKET_DATA_JSON}
</weekly_data>

<upcoming_events>
{EVENTS_JSON}
</upcoming_events>

<macro_themes_to_scan>
  Fed policy signals | CHIPS Act / AI capex | Geopolitical risk
  Energy prices | Crypto regulatory news | Earnings season themes
</macro_themes_to_scan>

<task>
Return ONLY this JSON. No markdown. No extra keys.
{
  "briefing_date": "{DATE}",
  "macro_themes": ["theme1 (evidence)", "theme2 (evidence)"],
  "top_long_setups": [
    {"ticker": "X", "reason": "one sentence", "entry_zone": "$XX-$YY", "risk": "LOW|MED|HIGH"}
  ],
  "top_short_watch": [
    {"ticker": "X", "reason": "one sentence"}
  ],
  "earnings_watch": [
    {"ticker": "X", "date": "YYYY-MM-DD", "bias": "bullish|bearish|neutral", "key_metric": "what to watch"}
  ],
  "kill_switch_alerts": [
    {"ticker": "X", "switch": "K4", "reason": "one sentence"}
  ],
  "sector_rotation": "one paragraph – where money is moving and why",
  "monday_game_plan": ["bullet 1", "bullet 2", "bullet 3"]
}
</task>
```

## Selection rules for top_long_setups
```
Include if ALL:
  - RSI < 70 (not overextended)
  - vol_ratio > 1.0 (at least average volume week)
  - week_chg > -2% (not in freefall)
  - no K1, K2, or K3 kill switches

Max 5 tickers. Rank by |week_chg| × vol_ratio (most active + healthy).
```

## Feedback loop
```
Step 1: Validate JSON parse
Step 2: Verify all tickers in top_long_setups exist in weekly_data
Step 3: Verify earnings_watch dates are within ±7 days
Step 4: Save to reports/weekend_briefing_{timestamp}.json
Step 5: Print compact summary to console (Monday game plan + top 3 longs)
```

## Performance improvement checklist (review every 4 weeks)
- [ ] Track Monday open performance of top_long_setups → did they gap up?
- [ ] Track earnings_watch bias accuracy → bullish called correctly?
- [ ] If macro_themes repeat 3 weeks: check if catalyst DB needs refresh
- [ ] If sector_rotation is always "AI capex": expand dataset to energy_ai watchlist
- [ ] Saturday vs Sunday briefing: which has more accurate Monday open calls?
