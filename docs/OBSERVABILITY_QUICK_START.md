# Observability Quick Start

You've just implemented a **three-tier observability system** for complete visibility into your VIF Trading System. Here's what you have and how to use it immediately.

---

## 🎯 What You Now Have

### Tier 1: SYSTEM_MANIFEST.md
**What:** Auto-generated registry of all files, agents, skills, scripts, configs
**Where:** `SYSTEM_MANIFEST.md` (root) and `SYSTEM_MANIFEST.json` (programmatic)
**Why:** Single source of truth—"what exists in my system?"

**Example uses:**
```bash
# See all agents
grep "^### " SYSTEM_MANIFEST.md | grep -v "Archived"

# See what changed recently
tail -20 SYSTEM_MANIFEST.md | grep "last_modified"

# Find a specific file
grep -A3 "swing_trade_screener"  SYSTEM_MANIFEST.md
```

### Tier 2: Telemetry System (NEW)
**What:** Real-time event logging of every significant system action
**Where:** `logs/telemetry.jsonl` (append-only JSONL file)
**Why:** "What happened? When? Did it work?"

**What gets logged:**
- Agent start/end (with duration)
- API calls (tokens, latency, cost)
- Pipeline stages
- Errors (with traceback)
- Reports generated
- Everything timestamped + git state

**Example events:**
```bash
# View last 5 events
tail -5 logs/telemetry.jsonl | jq .

# Stream live (while running a script)
tail -f logs/telemetry.jsonl | jq '{time: .timestamp, event: .event_type, component}'

# Find all errors
grep '"severity": "error"' logs/telemetry.jsonl

# Analyze token cost (last 24h)
cat logs/telemetry.jsonl | jq 'select(.event_type == "api_call") | .metrics.total_tokens' | awk '{sum+=$1} END {print "Total tokens:", sum}'
```

### Tier 3: Telemetry Library (NEW)
**What:** Python utility for agents/scripts to log events
**Where:** `utils/telemetry.py`
**Why:** Standardized logging across all components

**Quick integration:**
```python
from utils.telemetry import get_telemetry

tel = get_telemetry()

# Log agent lifecycle
tel.log_agent("my_agent", "start", "Processing watchlist")
# ... do work ...
tel.log_agent("my_agent", "end", duration_sec=45.2, metrics={"signals": 12})

# Log API calls
tel.log_api_call("vif_analysis", input_tokens=1200, output_tokens=450, latency_ms=2300)

# Log errors
tel.log_error("component_name", "ValueError", "Invalid ticker symbol")

# Get summary
summary = tel.get_telemetry_summary(hours=24)
```

---

## 📖 Documentation Files

| File | Purpose |
|------|---------|
| `docs/OBSERVABILITY_GUIDE.md` | **Complete reference** — all telemetry commands, examples, patterns |
| `docs/SYSTEM_HEALTH.md` | **Dashboard template** — status, recent activity, errors, performance |
| `scripts/generate_manifest.py` | **Manifest generator** — run to update SYSTEM_MANIFEST.md |
| `utils/telemetry.py` | **Telemetry library** — import and use in agents |

---

## 🚀 Get Started in 5 Minutes

### 1. View Your System Structure
```bash
# See everything that exists
cat SYSTEM_MANIFEST.md | head -100

# Or as JSON for scripting
cat SYSTEM_MANIFEST.json | jq '.agents[].name'
```

### 2. Monitor a Live Run
In one terminal, watch your system while running an agent:
```bash
# Watch real-time events
tail -f logs/telemetry.jsonl | jq '{time: .timestamp, event: .event_type, component, severity}'
```

In another, run an agent:
```bash
python agents/watchlist_watcher.py --watchlist vantage_portfolio
```

You'll see events stream in real-time showing:
- Agent start → API calls → Pipeline stages → Agent end
- Each with timing and token usage

### 3. Analyze Results
After the run completes:
```bash
# Summary of what happened
cat logs/telemetry.jsonl | jq 'select(.component == "watchlist_watcher") | {event: .event_type, duration: .duration_sec, tokens: .metrics}'

# Check for errors
cat logs/telemetry.jsonl | jq 'select(.severity == "error")'

# Token cost breakdown
cat logs/telemetry.jsonl | jq '[.event_type, .metrics.total_tokens] | @csv' | tail -20
```

### 4. Update Manifest (After Code Changes)
```bash
python scripts/generate_manifest.py
git add SYSTEM_MANIFEST.md SYSTEM_MANIFEST.json
git commit -m "Update system manifest"
```

---

## 📊 Common Queries

### "What ran in the last hour?"
```bash
python -c "
import json
from datetime import datetime, timedelta
cutoff = (datetime.now() - timedelta(hours=1)).isoformat()
with open('logs/telemetry.jsonl') as f:
    for line in f:
        event = json.loads(line)
        if event['timestamp'] > cutoff and event['event_type'] in ['agent_start', 'agent_end']:
            print(f\"{event['component']}: {event['event_type']} ({event.get('duration_sec', '-')}s)\")
"
```

### "How much did that run cost?"
```bash
cat logs/telemetry.jsonl | jq 'select(.event_type == "api_call") | .metrics.total_tokens' | awk '{sum+=$1} END {cost = sum * 0.003 / 1000000; print "Tokens:", sum, "Cost: $" cost}'
```

### "What errors happened today?"
```bash
grep '"severity": "error"' logs/telemetry.jsonl | jq '{time: .timestamp, component, error: .error, message: .message}'
```

### "Which agents are slowest?"
```bash
cat logs/telemetry.jsonl | jq 'select(.event_type == "agent_end") | {component, duration_sec}' | jq -s 'group_by(.component) | map({component: .[0].component, avg_duration: (map(.duration_sec) | add / length)})'
```

### "What's in today's generated reports?"
```bash
grep '"event_type": "report_generated"' logs/telemetry.jsonl | jq '{time: .timestamp, report: .component, type: .extra.report_type, path: .extra.file_path}'
```

---

## 🔧 Integration with Your Agents

To add telemetry to an existing agent, add these lines:

```python
# At top of file
from utils.telemetry import get_telemetry

# In your main function
tel = get_telemetry()

# At start
tel.log_agent("my_agent", "start", "Processing 50 tickers")

# During processing
tel.log_api_call("vif_analysis", input_tokens=1200, output_tokens=450, latency_ms=2300)

# Pipeline stage completion
tel.log_pipeline(
    pipeline_name="vif_analysis",
    action="end",
    stage="analysis",
    tickers_processed=50,
    tokens_used=1650,
    duration_sec=45.2
)

# If error occurs
try:
    # ... code ...
except Exception as e:
    tel.log_error("my_agent", type(e).__name__, str(e))
    raise

# At end
tel.log_agent("my_agent", "end", duration_sec=total_time, metrics={"signals_generated": 12})
```

---

## 📈 Dashboard Interpretation

### SYSTEM_MANIFEST.md
Shows what you have. Example:
```
Agents: 9
  ✓ watchlist_watcher.py (last modified: 2026-05-10)
  ✓ orchestrator.py
  ...

Skills: 12
Scripts: 14 (active) + 3 (archived)
```

**Answer:** "I have 9 agents doing 3 main jobs, with 14 active analysis scripts"

### logs/telemetry.jsonl
Shows what happened. Each line is one event:
```json
{"timestamp": "2026-05-10T14:32:15.123Z", "event_type": "agent_start", "component": "watchlist_watcher", "message": "Processing 85 tickers"}
{"timestamp": "2026-05-10T14:32:45.456Z", "event_type": "api_call", "metrics": {"total_tokens": 1650}, ...}
{"timestamp": "2026-05-10T14:33:00.789Z", "event_type": "agent_end", "duration_sec": 45.2}
```

**Answer:** "The watchlist_watcher ran for 45.2 seconds, used 1650 tokens, cost ~$0.005"

### SYSTEM_HEALTH.md
Manual snapshot. Example:
```
Overall Status: ✅ OPERATIONAL
Recent Activity (24h):
  - Agents: 4 runs, avg 42s
  - API Calls: 150 calls, 196K tokens
  - Signals: 8 BUY, 3 SELL, 2 HOLD
  - Errors: 0
```

**Answer:** "System is healthy, running on schedule, no issues"

---

## 🎓 Learning Path

1. **Start here:** Read this file (you are here)
2. **Quick reference:** Run the queries in "Common Queries" section
3. **Deep dive:** Read `docs/OBSERVABILITY_GUIDE.md` for everything
4. **Integration:** Add telemetry to your agents using the code example above
5. **Monitoring:** Set up periodic checks (daily/weekly/monthly tasks listed in the guide)

---

## 💡 Pro Tips

### Tip 1: Real-Time Monitoring During Development
```bash
# Terminal 1: Watch events live
tail -f logs/telemetry.jsonl | jq -c '{event: .event_type, component, duration: .duration_sec}'

# Terminal 2: Run your code
python agents/watchlist_watcher.py --watchlist ai_verticals
```

### Tip 2: Daily Cost Tracking
Create a script `daily_cost.sh`:
```bash
#!/bin/bash
DATE=$(date +%Y-%m-%d)
echo "Token usage for $DATE:"
grep "$DATE" logs/telemetry.jsonl | jq 'select(.event_type == "api_call") | .metrics.total_tokens' | awk '{sum+=$1} END {print "Tokens:", sum, "Cost: $" (sum * 0.003 / 1000000)}'
```

### Tip 3: Git Integration
```bash
# After running analysis, see what changed
git status
git diff SYSTEM_MANIFEST.md  # See if new agents added

# Commit with telemetry context
git log --oneline -5
# Pick the latest, then:
git commit -m "[watchlist_watcher] Add new VIF kill switch (from telemetry: 12 signals, 45s, 1650 tokens)"
```

### Tip 4: Automated Updates
Add to your cron (daily manifest update):
```bash
# .crontab
0 6 * * * cd /path/to/vif-trading-system && python scripts/generate_manifest.py && git add SYSTEM_MANIFEST.md && git commit -m "Daily manifest update"
```

---

## 🐛 Troubleshooting

### "No telemetry.jsonl file yet"
Telemetry only starts logging when you import and use it. Once you integrate `from utils.telemetry import get_telemetry()` into an agent, the file will be auto-created.

### "SYSTEM_MANIFEST.md is outdated"
Run the generator:
```bash
python scripts/generate_manifest.py
```

### "I want to clear old telemetry"
```bash
# Back up
cp logs/telemetry.jsonl logs/telemetry.jsonl.bak

# Clear
echo "" > logs/telemetry.jsonl

# Or archive old events
grep "2026-05-0[1-8]" logs/telemetry.jsonl.bak > logs/telemetry.jsonl.archive
```

### "How do I export to CSV for analysis?"
```bash
cat logs/telemetry.jsonl | jq -r '[.timestamp, .component, .event_type, .severity, (.metrics.total_tokens // ""), (.duration_sec // "")] | @csv' > telemetry.csv
# Now open in Excel/Sheets
```

---

## 📞 Next Steps

1. **Integrate telemetry into your agents** — Copy the code example into `watchlist_watcher.py` and other agents
2. **Set up monitoring scripts** — Create daily/weekly check scripts
3. **Read the full guide** — `docs/OBSERVABILITY_GUIDE.md` has everything
4. **Automate manifest updates** — Add to pre-commit hook or cron
5. **Track costs** — Use telemetry to forecast token budget

---

## Quick Command Reference

```bash
# View system structure
cat SYSTEM_MANIFEST.md | head

# Watch live telemetry
tail -f logs/telemetry.jsonl | jq .

# Summary of last 24h
python -c "from utils.telemetry import get_telemetry; import json; print(json.dumps(get_telemetry().get_telemetry_summary(24), indent=2))"

# Find errors
grep '"severity": "error"' logs/telemetry.jsonl

# Token cost (24h)
cat logs/telemetry.jsonl | jq 'select(.event_type == "api_call") | .metrics.total_tokens' | awk '{sum+=$1} END {print "Cost: $" (sum * 0.003 / 1000000)}'

# Update manifest
python scripts/generate_manifest.py

# Check agent-specific logs
tail -50 logs/watchlist_watcher.log
```

---

**You're all set! Start monitoring. 📊**
