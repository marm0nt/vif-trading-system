# Observability System - Complete Index

Everything you need to know about the three-tier observability system built for the VIF Trading System.

---

## 📚 Documentation Map

### 🟢 Start Here
- **[OBSERVABILITY_QUICK_START.md](./OBSERVABILITY_QUICK_START.md)** — 5-minute introduction
  - What you have
  - How to use it immediately
  - Common queries
  - Integration tips

### 🔵 Deep Dive
- **[OBSERVABILITY_GUIDE.md](./OBSERVABILITY_GUIDE.md)** — Complete reference (3000+ words)
  - Architecture overview
  - Tier 1 (Static Registry)
  - Tier 2 (Runtime Telemetry)
  - Tier 3 (Git & CI/CD)
  - Advanced examples
  - Monitoring setup

### 🟡 Industry Recommendations
- **[RECOMMENDATIONS_SUMMARY.md](./RECOMMENDATIONS_SUMMARY.md)** — Why this design + alternatives
  - Direct answers to your questions
  - What most users recommend
  - Comparison with other approaches
  - Evolution path as you scale

### 🟣 System Health
- **[SYSTEM_HEALTH.md](./SYSTEM_HEALTH.md)** — Dashboard template
  - Current status
  - Recent activity
  - Performance metrics
  - Known issues
  - Quick diagnostics

---

## 🛠️ Tools & Code

### Static Registry (Tier 1)
- **[SYSTEM_MANIFEST.md](../SYSTEM_MANIFEST.md)** ← Generated file
  - Auto-generated registry of all components
  - Human-readable markdown
  - Git-tracked for versioning

- **[SYSTEM_MANIFEST.json](../SYSTEM_MANIFEST.json)** ← Generated file
  - Same registry in machine-readable format
  - Easy to parse in scripts
  - Programmatic access

- **[scripts/generate_manifest.py](../scripts/generate_manifest.py)** ← Utility
  - Generates both SYSTEM_MANIFEST files
  - Scans agents/, skills/, scripts/, configs/, etc.
  - Includes git metadata
  - Run: `python scripts/generate_manifest.py`

### Telemetry System (Tier 2)
- **[utils/telemetry.py](../utils/telemetry.py)** ← Core library
  - Main telemetry class (`Telemetry`)
  - Event types and severity levels
  - Helper methods for different event types
  - JSON output to `logs/telemetry.jsonl`
  - Summary queries built-in

- **[logs/telemetry.jsonl](../logs/telemetry.jsonl)** ← Generated file
  - Continuously-growing event log
  - One JSON object per line (JSONL)
  - Timestamped events
  - Git state captured in each event

- **[examples/observability_examples.py](../examples/observability_examples.py)** ← Code examples
  - 10 real-world usage patterns
  - Copy-paste examples for your code
  - Shows integration in agents/scripts

---

## 📖 Reading Path by Use Case

### "I'm new to this project, show me what exists"
1. Read: [OBSERVABILITY_QUICK_START.md](./OBSERVABILITY_QUICK_START.md) (5 min)
2. Look at: [SYSTEM_MANIFEST.md](../SYSTEM_MANIFEST.md) (2 min)
3. Try: `cat SYSTEM_MANIFEST.md | head -100`

### "I want to understand why this design"
1. Read: [RECOMMENDATIONS_SUMMARY.md](./RECOMMENDATIONS_SUMMARY.md) (10 min)
2. See comparison table with other approaches
3. Understand industry best practices

### "I need to monitor a running system"
1. Quick reference: [OBSERVABILITY_QUICK_START.md](./OBSERVABILITY_QUICK_START.md) → "Common Queries" section
2. Open terminal: `tail -f logs/telemetry.jsonl | jq .`
3. Run your agent/script
4. Watch events stream in real-time

### "I want to integrate telemetry into my code"
1. Look at: [examples/observability_examples.py](../examples/observability_examples.py) (10 examples)
2. Copy pattern that matches your use case
3. Integrate into your agent/script
4. Run and verify events in `logs/telemetry.jsonl`

### "I need to troubleshoot an error"
1. Check: [SYSTEM_HEALTH.md](./SYSTEM_HEALTH.md) → "Recent Errors" section
2. Query telemetry: `grep '"severity": "error"' logs/telemetry.jsonl`
3. Get full context: `grep YOUR_COMPONENT logs/telemetry.jsonl | tail -10 | jq .`
4. See agent-specific logs: `tail -50 logs/YOUR_AGENT.log`

### "I want to analyze costs"
1. Quick query: `cat logs/telemetry.jsonl | jq 'select(.event_type == "api_call") | .metrics.total_tokens' | awk '{sum+=$1} END {print "Cost: $" (sum * 0.003 / 1000000)}'`
2. Full guide: [OBSERVABILITY_GUIDE.md](./OBSERVABILITY_GUIDE.md) → "Example: Monitoring a Run"
3. Script example: [examples/observability_examples.py](../examples/observability_examples.py) → "Example 9: Cost Analysis"

### "I'm setting up CI/CD or automation"
1. Read: [OBSERVABILITY_GUIDE.md](./OBSERVABILITY_GUIDE.md) → "Tools & Extensions"
2. Parse SYSTEM_MANIFEST.json in your CI script
3. Query telemetry.jsonl for metrics
4. Generate reports or alerts based on events

---

## 🚀 Quick Commands Reference

### Generate/Update System Manifest
```bash
python scripts/generate_manifest.py
```

### View System Structure
```bash
# See agents, skills, scripts
head -100 SYSTEM_MANIFEST.md

# As JSON
cat SYSTEM_MANIFEST.json | jq '.agents[].name'
```

### Monitor Live Telemetry
```bash
# Stream all events
tail -f logs/telemetry.jsonl | jq .

# Pretty format
tail -f logs/telemetry.jsonl | jq '{time: .timestamp, event: .event_type, component}'

# Filter by component
tail -f logs/telemetry.jsonl | jq 'select(.component == "watchlist_watcher")'

# Filter by severity
tail -f logs/telemetry.jsonl | jq 'select(.severity == "error")'
```

### Analyze Recent Activity
```bash
# Recent 10 events
tail -10 logs/telemetry.jsonl | jq .

# Count events by type
cat logs/telemetry.jsonl | jq -r '.event_type' | sort | uniq -c

# By component
cat logs/telemetry.jsonl | jq -r '.component' | sort | uniq -c

# Show errors
cat logs/telemetry.jsonl | jq 'select(.severity == "error")'
```

### Cost Analysis
```bash
# Total tokens (all time)
cat logs/telemetry.jsonl | jq '[select(.event_type == "api_call")] | map(.metrics.total_tokens) | add'

# Total cost
cat logs/telemetry.jsonl | jq 'select(.event_type == "api_call") | .metrics.total_tokens' | awk '{sum+=$1} END {print "Cost: $" (sum * 0.003 / 1000000)}'

# By component
cat logs/telemetry.jsonl | jq '[select(.event_type == "api_call")] | group_by(.component) | map({component: .[0].component, tokens: map(.metrics.total_tokens | select(. != null)) | add})'
```

### Performance Analysis
```bash
# Slowest agents
cat logs/telemetry.jsonl | jq 'select(.event_type == "agent_end") | {component, duration_sec}' | jq -s 'sort_by(-.duration_sec) | .[0:5]'

# Fastest agents
cat logs/telemetry.jsonl | jq 'select(.event_type == "agent_end") | {component, duration_sec}' | jq -s 'sort_by(.duration_sec) | .[0:5]'
```

### Python Analysis
```python
from utils.telemetry import get_telemetry

tel = get_telemetry()
summary = tel.get_telemetry_summary(hours=24)

print(f"Total events: {summary['total_events']}")
print(f"Errors: {len(summary['errors'])}")
print(f"By type: {summary['by_event_type']}")
```

### Run Examples
```bash
python examples/observability_examples.py
```

---

## 📊 Files Created/Modified

### New Files (What Was Built)
| File | Purpose | Type |
|------|---------|------|
| `utils/telemetry.py` | Telemetry library | Core |
| `scripts/generate_manifest.py` | Manifest generator | Utility |
| `logs/telemetry.jsonl` | Event log (created on first use) | Data |
| `SYSTEM_MANIFEST.md` | Component registry (auto-generated) | Reference |
| `SYSTEM_MANIFEST.json` | Registry as JSON (auto-generated) | Reference |
| `docs/OBSERVABILITY_QUICK_START.md` | 5-minute intro | Guide |
| `docs/OBSERVABILITY_GUIDE.md` | Complete reference | Guide |
| `docs/OBSERVABILITY_INDEX.md` | This file | Index |
| `docs/SYSTEM_HEALTH.md` | Health dashboard template | Dashboard |
| `docs/RECOMMENDATIONS_SUMMARY.md` | Why this design + industry context | Reference |
| `examples/observability_examples.py` | 10 usage patterns | Examples |

### Existing Files (Not Modified)
- `.claude/memory/` — Unchanged (for session continuity)
- `logs/*.log` — Existing structured logs (complementary)
- `.git/` — Existing git history (complementary)
- Code files — Unchanged (ready for telemetry integration)

---

## 🔄 How They Work Together

```
┌─────────────────────────────────────────────────────────┐
│ Your Code (agents, scripts)                              │
├─────────────────────────────────────────────────────────┤
│  ↓                                                        │
│  from utils.telemetry import get_telemetry               │
│  tel = get_telemetry()                                   │
│  tel.log_agent("my_agent", "start", ...)                 │
│  # ... work ...                                           │
│  tel.log_agent("my_agent", "end", duration_sec=45)       │
│  ↓                                                        │
├─────────────────────────────────────────────────────────┤
│ Telemetry System (utils/telemetry.py)                    │
├─────────────────────────────────────────────────────────┤
│  ↓                                                        │
│  Appends JSON events to logs/telemetry.jsonl              │
│  {timestamp, event_type, component, duration, metrics}   │
│  ↓                                                        │
├─────────────────────────────────────────────────────────┤
│ Observability Outputs                                    │
├─────────────────────────────────────────────────────────┤
│  • logs/telemetry.jsonl — Runtime events (Tier 2)        │
│  • SYSTEM_MANIFEST.md — Component registry (Tier 1)      │
│  • logs/*.log — Structured agent logs                    │
│  • .git/logs — Code history (Tier 3)                     │
│  ↓                                                        │
├─────────────────────────────────────────────────────────┤
│ Monitoring & Analysis                                    │
├─────────────────────────────────────────────────────────┤
│  • tail -f logs/telemetry.jsonl | jq .  (live stream)    │
│  • Parse telemetry.jsonl for metrics                     │
│  • Check SYSTEM_MANIFEST for dependencies                │
│  • Review git history for context                        │
│  • Generate reports/alerts                               │
│  ↓                                                        │
├─────────────────────────────────────────────────────────┤
│ Insights & Actions                                       │
├─────────────────────────────────────────────────────────┤
│  ✓ Understand system structure                           │
│  ✓ Track API costs in real-time                          │
│  ✓ Debug errors with full context                        │
│  ✓ Monitor performance trends                            │
│  ✓ Audit what changed and why                            │
└─────────────────────────────────────────────────────────┘
```

---

## 📋 Implementation Checklist

### Phase 1: Understand (Done ✅)
- [x] Read OBSERVABILITY_QUICK_START.md
- [x] See SYSTEM_MANIFEST.md
- [x] Understand three-tier architecture
- [x] Review examples in observability_examples.py

### Phase 2: Integrate (Next)
- [ ] Add telemetry to watchlist_watcher.py
- [ ] Add telemetry to orchestrator.py
- [ ] Add telemetry to swing_trade_screener_v2.py
- [ ] Add telemetry to catalyst_analysis.py
- [ ] Test with `tail -f logs/telemetry.jsonl`

### Phase 3: Automate (Week 1)
- [ ] Add manifest generation to git pre-commit hook
- [ ] Create daily cost report script
- [ ] Set up weekly health check
- [ ] Create monitoring dashboard (SYSTEM_HEALTH.md)

### Phase 4: Optimize (Month 1+)
- [ ] Analyze patterns in telemetry.jsonl
- [ ] Optimize slow components
- [ ] Forecast token budget
- [ ] Plan infrastructure upgrades

---

## 🎓 Key Concepts

| Term | Meaning | Example |
|------|---------|---------|
| **Event** | Something that happened in the system | "agent started", "API call made", "error occurred" |
| **Telemetry** | Collection of events over time | logs/telemetry.jsonl (all events appended) |
| **Manifest** | Registry of what exists | SYSTEM_MANIFEST.md (all agents, skills, etc.) |
| **Component** | A unit of the system | watchlist_watcher (agent), vif_config.yml (config) |
| **Severity** | How important an event is | info, warning, error, critical |
| **Metrics** | Numeric measurements | tokens (1650), latency_ms (2300), duration_sec (45.2) |
| **Context** | Surrounding state | git_branch ("main"), git_commit ("a3f9e2b") |

---

## ❓ FAQ

**Q: Where do I add telemetry to my code?**  
A: See [examples/observability_examples.py](../examples/observability_examples.py) for patterns. Copy the pattern that matches your use case.

**Q: How do I view events live?**  
A: `tail -f logs/telemetry.jsonl | jq .` while your code runs.

**Q: How much disk space will telemetry use?**  
A: ~1-2 KB per event, ~30-50 MB/month. Can be archived/deleted after 30 days.

**Q: Can I use this with GitHub Actions?**  
A: Yes! Parse SYSTEM_MANIFEST.json or telemetry.jsonl in your CI scripts.

**Q: What if I'm offline?**  
A: Telemetry is local files. Works offline. Sync when you come back online.

**Q: How does this compare to ELK/Datadog/Splunk?**  
A: This is for small-to-medium projects. Those tools are for enterprise scale (1M+ events/day). See evolution path in RECOMMENDATIONS_SUMMARY.md.

---

## 📞 Getting Help

1. **Quick question?** Check [OBSERVABILITY_QUICK_START.md](./OBSERVABILITY_QUICK_START.md)
2. **Need examples?** See [examples/observability_examples.py](../examples/observability_examples.py)
3. **Want details?** Read [OBSERVABILITY_GUIDE.md](./OBSERVABILITY_GUIDE.md)
4. **Comparing approaches?** See [RECOMMENDATIONS_SUMMARY.md](./RECOMMENDATIONS_SUMMARY.md)
5. **Checking health?** Look at [SYSTEM_HEALTH.md](./SYSTEM_HEALTH.md)

---

## 🎉 Summary

You now have:
1. ✅ **Tier 1 (Static)** — SYSTEM_MANIFEST.md shows what exists
2. ✅ **Tier 2 (Dynamic)** — telemetry.jsonl shows what happened
3. ✅ **Tier 3 (History)** — Git logs show why it changed

**Cost:** $0  
**Setup:** ~30 minutes  
**Value:** Hours of debugging saved + cost visibility + professional system understanding

**Start with:** [OBSERVABILITY_QUICK_START.md](./OBSERVABILITY_QUICK_START.md)  
**Go deep with:** [OBSERVABILITY_GUIDE.md](./OBSERVABILITY_GUIDE.md)

---

**Last Updated:** 2026-05-10  
**Files:** 11 new docs/tools  
**Status:** Ready to integrate and monitor
