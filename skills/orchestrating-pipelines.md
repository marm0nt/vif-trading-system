# Skill: Orchestrating Pipelines
<!-- Agent: agents/orchestrator.py | Runs: every scheduled session -->

## Role
Coordinate all specialist agents. Delegate the right job to the right agent.
Never duplicate work an agent can do. Fail gracefully — one agent failure must not
stop the rest of the pipeline.

## Pipeline modes

| Mode | Agents called (in order) | When |
|---|---|---|
| `premarket` | catalyst → watchlist_watcher (1mo) → swing_screener | 08:45 CT |
| `market_open` | swing_screener | 09:35 CT |
| `afterhours` | daily_watchlist_analysis → watchlist_watcher (5d) | 16:05 CT |
| `weekend` | weekend_catalyst_agent | Sat 08:00 + Sun 18:00 |
| `full` | all of the above | On-demand |

## Delegation logic (decision tree)
```
User asks for:
  "premarket scan"           → --mode premarket
  "after close / end of day" → --mode afterhours
  "weekend / Monday prep"    → --mode weekend
  "deep dive NVDA"           → --ticker NVDA
  "full run"                 → --mode full
  "catalyst / policy"        → catalyst_analysis.py (direct)
```

## Error handling standard
```python
# Every agent call MUST use this pattern:
result = run_agent(label, cmd, timeout=600)
if not result["success"]:
    logger.error(f"{label} failed – continuing pipeline")
    # Do NOT sys.exit() – let remaining agents run
```

## Run log format (saved to reports/orchestrator_{mode}_{ts}.json)
```json
{
  "mode": "premarket",
  "started_at": "2026-04-29T07:00:00",
  "jobs": [
    {"label": "Catalyst Scan", "success": true, "cmd": ["catalyst_analysis.py"]},
    {"label": "VIF Watchlist", "success": true, "cmd": ["watchlist_watcher.py", "--all"]}
  ],
  "summary": {"total": 3, "passed": 3, "failed": 0}
}
```

## Feedback loop
```
After every pipeline run:
  1. Log pass/fail per agent to logs/orchestrator.log
  2. Append summary to logs/run_history.json (keep last 60 runs)
  3. If failed > 0: alert in console (bold red)
  4. Monthly: review run_history.json → which agent fails most? → fix first
```

## Performance improvement checklist (review monthly)
- [ ] Mean pipeline runtime < 10 minutes (if > 10min: parallelize fetches)
- [ ] Failed agent rate < 5% (if > 5%: check API credit balance + network)
- [ ] Premarket pipeline always completes before 09:30 CT (market open)
- [ ] Afterhours pipeline always completes before 17:00 CT (data freshness)
- [ ] Check run_history.json: any agent timing out consistently? → raise timeout
