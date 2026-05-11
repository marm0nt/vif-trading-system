# Observability & System Tracking Guide

This guide explains the complete observability stack for the VIF Trading System—how to see what's happening, what worked, what failed, and why.

---

## Overview: Three-Tier Observability Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Observability Stack                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Tier 1: STATIC REGISTRY                                         │
│  ├─ SYSTEM_MANIFEST.md (auto-generated)                          │
│  ├─ SYSTEM_MANIFEST.json (programmatic access)                   │
│  └─ Catalogs: agents, skills, scripts, configs, watchlists       │
│                                                                   │
│  Tier 2: RUNTIME TELEMETRY                                       │
│  ├─ logs/telemetry.jsonl (all events: start/end/api/error)       │
│  ├─ logs/*.log (agent-specific structured logs)                  │
│  └─ reports/* (output artifacts)                                 │
│                                                                   │
│  Tier 3: GIT & CI/CD                                             │
│  ├─ .git/logs (commit history, blame)                            │
│  ├─ GitHub Actions (automated tests, deploys)                    │
│  └─ Pull requests (change tracking, code review)                 │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Tier 1: Static Registry (SYSTEM_MANIFEST.md)

### What It Is

A **machine-generated markdown file** that catalogues everything in your project at a point in time.

### What It Contains

```
Agents:
  ✓ watchlist_watcher.py
  ✓ orchestrator.py
  ✓ weekend_catalyst_agent.py
  ✓ claude_research_agent.py

Skills:
  ✓ computing-indicators.md
  ✓ screening-swing-setups.md
  ✓ ...

Scripts:
  Active:
    ✓ swing_trade_screener_v2.py
    ✓ catalyst_analysis.py
    ✓ daily_watchlist_analysis.py
  Archived:
    ✓ advanced_analysis.py

Configs:
  ✓ vif_config.yml
  ✓ cache_config.yml

Watchlists:
  ✓ vantage_portfolio.txt (85 tickers)
  ✓ ai_verticals.txt (35 tickers)
  ✓ energy_ai.txt (13 tickers)

Utilities:
  ✓ structured_logging.py
  ✓ telemetry.py
  ✓ error_recovery.py
  ✓ usage_tracker.py

Docs:
  ✓ README.md
  ✓ SETUP.md
  ✓ QUICKSTART.md
  ✓ AGENTS.md
  ✓ SKILLS.md
```

### How to Generate It

```bash
python scripts/generate_manifest.py
```

This scans your entire project and creates:
- `SYSTEM_MANIFEST.md` — Human-readable registry
- `SYSTEM_MANIFEST.json` — Machine-readable (for scripts)

### How to Use It

1. **Find a component:** Grep for a name
   ```bash
   grep -n "swing_trade_screener" SYSTEM_MANIFEST.md
   ```

2. **See dependencies:** Read the manifest and check which agents call which scripts

3. **Check recent changes:** See git commit hash and last modified date for each file

4. **Understand structure:** Reference for onboarding or understanding the system

### Keep It Updated

Add to your git pre-commit hook:

```bash
# .git/hooks/pre-commit
python scripts/generate_manifest.py
git add SYSTEM_MANIFEST.md SYSTEM_MANIFEST.json
```

Or run manually before committing:

```bash
python scripts/generate_manifest.py && git add SYSTEM_MANIFEST.md SYSTEM_MANIFEST.json
```

---

## Tier 2: Runtime Telemetry (logs/telemetry.jsonl)

### What It Is

A **continuously-growing event log** that captures every significant system event.

One JSON object per line (JSONL format), making it both human-readable and easy to parse programmatically.

### What Gets Logged

- **Agent lifecycle:** Start, end, duration, success/error
- **API calls:** Tokens, latency, model, operation, error
- **Pipelines:** Stages, tickers processed, total tokens
- **Skills invoked:** Which agent called it, success
- **Reports generated:** Type, sections, output path
- **Errors:** Component, type, message, traceback, git state
- **Workflow runs:** Total steps, completion %, duration

### Example Events

```json
{"timestamp": "2026-05-10T14:32:15.123Z", "event_type": "agent_start", "component": "watchlist_watcher", "message": "Starting analysis of 85 tickers", "severity": "info", "context": {"git_branch": "main", "git_commit": "a3f9e2b", "python_version": "3.11.2"}}

{"timestamp": "2026-05-10T14:32:45.456Z", "event_type": "api_call", "component": "claude-api", "message": "API call: vif_analysis", "severity": "info", "metrics": {"input_tokens": 1200, "output_tokens": 450, "total_tokens": 1650, "latency_ms": 2340}, "tags": ["api", "claude-sonnet-4-6"]}

{"timestamp": "2026-05-10T14:33:00.789Z", "event_type": "pipeline_end", "component": "vif_analysis", "message": "Pipeline end (stage: analysis)", "severity": "info", "duration_sec": 45.23, "metrics": {"tickers": 85, "tokens": 1650}, "tags": ["pipeline", "analysis"]}

{"timestamp": "2026-05-10T14:33:05.012Z", "event_type": "error_occurred", "component": "swing_screener", "message": "Failed to fetch data for NVDA", "severity": "error", "error": "API_TIMEOUT", "tags": ["error", "API_TIMEOUT"], "traceback": "..."}

{"timestamp": "2026-05-10T14:34:20.345Z", "event_type": "agent_end", "component": "watchlist_watcher", "message": "Analysis complete", "severity": "info", "duration_sec": 125.4, "metrics": {"signals_generated": 12, "buy_signals": 4, "sell_signals": 3}, "tags": ["watchlist_watcher"]}
```

### How to Use Telemetry

#### View Recent Events (Last 10 events)

```bash
tail -10 logs/telemetry.jsonl
```

#### View Real-Time Stream

```bash
tail -f logs/telemetry.jsonl
```

#### Filter by Component

```bash
grep '"component": "watchlist_watcher"' logs/telemetry.jsonl | tail -5
```

#### Filter by Event Type

```bash
grep '"event_type": "error_occurred"' logs/telemetry.jsonl
```

#### Pretty-Print Recent Event

```bash
tail -1 logs/telemetry.jsonl | jq .
```

#### Count Events by Type

```bash
cat logs/telemetry.jsonl | jq -r '.event_type' | sort | uniq -c
```

#### Analyze Token Usage (Last 24h)

```bash
cat logs/telemetry.jsonl | jq 'select(.event_type == "api_call") | .metrics.total_tokens' | awk '{sum+=$1} END {print "Total tokens:", sum, "Cost: $" (sum * 0.003 / 1000000)}'
```

#### Find All Errors

```bash
cat logs/telemetry.jsonl | jq 'select(.severity == "error")'
```

#### Get Workflow Summary

```bash
# Show all agent lifecycle events (start/end pairs)
grep '"event_type": "agent_' logs/telemetry.jsonl | jq '{timestamp, component, message: .event_type, duration: .duration_sec}'
```

### Integrate with Your Code

When creating agents/scripts, import and use telemetry:

```python
from utils.telemetry import get_telemetry, EventType

tel = get_telemetry()

# Agent start
tel.log_agent("my_agent", "start", "Processing 50 tickers")

# API call
tel.log_api_call(
    operation="vif_analysis",
    input_tokens=1200,
    output_tokens=450,
    latency_ms=2300
)

# Pipeline stage
tel.log_pipeline(
    pipeline_name="vif_analysis",
    action="end",
    stage="analysis",
    tickers_processed=50,
    tokens_used=1650,
    duration_sec=45.2
)

# Report generated
tel.log_report_generated(
    report_name="swing_recommendations",
    report_type="markdown",
    file_path="reports/daily/swing.md",
    sections=5
)

# Agent end
tel.log_agent(
    "my_agent", "end",
    "Processing complete",
    duration_sec=125.4,
    metrics={"signals_generated": 12}
)
```

### Get Telemetry Summary Programmatically

```python
from utils.telemetry import get_telemetry

tel = get_telemetry()

# Get summary of last 24 hours
summary = tel.get_telemetry_summary(hours=24)

print(f"Total events: {summary['total_events']}")
print(f"By event type: {summary['by_event_type']}")
print(f"By component: {summary['by_component']}")
print(f"Errors: {summary['errors']}")
print(f"Recent API calls: {summary['recent_api_calls']}")
```

---

## Tier 3: Git & Code Tracking

### Git History

See what code changed and when:

```bash
# View commit history with file changes
git log --oneline --stat

# See specific file's history
git log --oneline -- agents/watchlist_watcher.py

# View blame for a specific line
git blame agents/watchlist_watcher.py | head -20

# See what changed in last commit
git show HEAD

# Compare branches
git diff main feature/experiment
```

### GitHub Features (If Using GitHub)

1. **Actions:** Automated testing, linting, deployment logs
2. **Issues:** Track bugs, feature requests, discussions
3. **Pull Requests:** Code review history, change tracking
4. **Releases:** Changelog, version history
5. **Discussions:** Archive of decisions and context

### Best Practices for Commit Messages

```
Format: [COMPONENT] Brief description

Examples:
[watchlist_watcher] Fix kill switch K2 detection
[swing_screener] Add support for 4-week lookback
[config] Update gamma threshold to 0.55
[docs] Document new catalyst analysis pipeline
[telemetry] Add API call latency tracking
```

---

## Tier 1.5: System Health Dashboard (SYSTEM_HEALTH.md)

### What It Is

A human-readable **dashboard snapshot** showing:
- Current system status (all green/red)
- Recent activity (agents run, signals generated, errors)
- Performance metrics (token usage, latency)
- Test results
- Known issues

### How to Generate It

```bash
python scripts/generate_health_dashboard.py  # (not implemented yet)
```

For now, manually update `docs/SYSTEM_HEALTH.md` using telemetry data:

```bash
# Parse telemetry and fill in the dashboard
python -c "
from utils.telemetry import get_telemetry
summary = get_telemetry().get_telemetry_summary(hours=24)
print('Events last 24h:', summary['total_events'])
print('By type:', summary['by_event_type'])
print('Errors:', len(summary['errors']))
"
```

---

## Complete Example: Monitoring a Run

Here's how to observe a complete watchlist analysis run:

### Before Run

```bash
# Check system health
python tests/test_api_key.py

# Look at manifest
cat SYSTEM_MANIFEST.md | head -50

# Current telemetry state
wc -l logs/telemetry.jsonl
```

### During Run

```bash
# Watch live telemetry stream
tail -f logs/telemetry.jsonl | jq '{timestamp, event: .event_type, component, message}'

# In another terminal, watch agent log
tail -f logs/watchlist_watcher.log
```

### After Run

```bash
# Count events
grep '"component": "watchlist_watcher"' logs/telemetry.jsonl | wc -l

# Get summary
cat logs/telemetry.jsonl | jq 'select(.component == "watchlist_watcher") | {event: .event_type, duration_sec: .duration_sec, tokens: .metrics.total_tokens}'

# Check for errors
cat logs/telemetry.jsonl | jq 'select(.severity == "error")'

# See generated reports
ls -la reports/daily/
```

---

## Recommended Monitoring Setup

### Daily Checklist

```bash
#!/bin/bash
# Daily observability check

echo "=== SYSTEM HEALTH ===" 
python tests/test_api_key.py

echo "=== RECENT EVENTS (last 5) ==="
tail -5 logs/telemetry.jsonl | jq '{event: .event_type, component, severity}'

echo "=== TODAY'S ERRORS ==="
grep '"severity": "error"' logs/telemetry.jsonl | jq -r '.message' | tail -10

echo "=== TOKEN USAGE (24h) ==="
cat logs/telemetry.jsonl | jq 'select(.event_type == "api_call") | .metrics.total_tokens' | awk '{sum+=$1} END {print "Total:", sum, "Cost: $" (sum * 0.003 / 1000000)}'

echo "=== MANIFEST AGE ==="
stat -f "%Sm" SYSTEM_MANIFEST.md 2>/dev/null || stat -c "%y" SYSTEM_MANIFEST.md
```

### Weekly Tasks

1. **Update manifest:** `python scripts/generate_manifest.py`
2. **Review health dashboard:** `cat docs/SYSTEM_HEALTH.md`
3. **Analyze token trends:** Check telemetry for cost anomalies
4. **Test recovery:** Run `python tests/test_harness.py`
5. **Review errors:** Filter for new error patterns in telemetry

### Monthly Tasks

1. **Archive old logs:** Move `logs/` files > 30 days old to `logs/archive/`
2. **Update CLAUDE.md:** Reflect any architectural changes
3. **Review git history:** Summarize month's commits
4. **Forecast token usage:** Project next month's costs
5. **Update documentation:** Fix any stale sections in `docs/`

---

## Querying Telemetry Programmatically

### Python Script to Analyze Yesterday's Run

```python
import json
from datetime import datetime, timedelta
from pathlib import Path

tel_file = Path("logs/telemetry.jsonl")
yesterday = datetime.now() - timedelta(days=1)

stats = {
    "total_events": 0,
    "agents": {},
    "api_calls": 0,
    "total_tokens": 0,
    "errors": 0,
    "duration": 0,
}

with open(tel_file) as f:
    for line in f:
        event = json.loads(line)
        event_time = datetime.fromisoformat(event['timestamp'])
        
        if event_time.date() != yesterday.date():
            continue
        
        stats["total_events"] += 1
        
        if event['event_type'] in ['agent_start', 'agent_end']:
            component = event['component']
            stats["agents"][component] = stats["agents"].get(component, 0) + 1
        
        if event['event_type'] == 'api_call':
            stats["api_calls"] += 1
            stats["total_tokens"] += event['metrics']['total_tokens']
        
        if event['severity'] == 'error':
            stats["errors"] += 1
        
        if event.get('duration_sec'):
            stats["duration"] += event['duration_sec']

print(f"Yesterday's Summary:")
print(f"  Events: {stats['total_events']}")
print(f"  API Calls: {stats['api_calls']}")
print(f"  Tokens: {stats['total_tokens']} (${stats['total_tokens'] * 0.003 / 1000000:.2f})")
print(f"  Errors: {stats['errors']}")
print(f"  Total Duration: {stats['duration']:.1f}s")
print(f"  By Agent: {stats['agents']}")
```

---

## Tools & Extensions

### CLI Tools to Pair with Telemetry

```bash
# Real-time JSON parsing
cat logs/telemetry.jsonl | jq

# CSV export for spreadsheet analysis
cat logs/telemetry.jsonl | jq -r '[.timestamp, .component, .event_type, .severity] | @csv' > telemetry.csv

# Flamegraph of component call stack
cat logs/telemetry.jsonl | jq '.component' | sort | uniq -c | sort -rn
```

### Future Enhancements

- [ ] Elasticsearch/Logstash for searchable telemetry
- [ ] Grafana dashboard for real-time metrics
- [ ] Slack alerts on errors
- [ ] Auto-generated health reports emailed daily
- [ ] Telemetry-based cost optimization dashboard

---

## Summary

| Tier | What | Where | How Often | Purpose |
|------|------|-------|-----------|---------|
| 1 | Static Registry | `SYSTEM_MANIFEST.md` | After each code commit | "What exists?" |
| 2 | Runtime Events | `logs/telemetry.jsonl` | Continuous (appended) | "What happened?" |
| 3 | Code History | `.git/logs`, GitHub | On commit | "Why changed?" |

Use them together:
- **Manifest** to understand structure
- **Telemetry** to debug issues and monitor performance
- **Git** to see what code changed

---

**Related Docs:**
- [SYSTEM_MANIFEST.md](../SYSTEM_MANIFEST.md) — Component registry
- [SYSTEM_HEALTH.md](./SYSTEM_HEALTH.md) — Health dashboard
- [utils/telemetry.py](../utils/telemetry.py) — Telemetry library
- [DEPLOYMENT_STATUS.md](./DEPLOYMENT_STATUS.md) — Operational checklist
