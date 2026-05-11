# System Health Dashboard

**Last Updated:** [AUTO-GENERATED]

This dashboard provides a live snapshot of system health, recent activity, performance metrics, and any issues.

---

## 🟢 Overall Status: OPERATIONAL

| Component | Status | Last Check | Notes |
|-----------|--------|-----------|-------|
| API Connection | ✅ | - | Claude API functional |
| Scheduler | ✅ | - | cron/schedule daemon running |
| Data Cache | ✅ | - | 24-hour TTL working |
| Telemetry | ✅ | - | Event logging active |
| Test Suite | ✅ | - | All tests passing |

---

## 📊 Recent Activity (Last 24 Hours)

### Agents

| Agent | Runs | Avg Duration | Status | Last Run |
|-------|------|--------------|--------|----------|
| watchlist_watcher | - | - | - | - |
| weekend_catalyst_agent | - | - | - | - |
| orchestrator | - | - | - | - |
| claude_research_agent | - | - | - | - |

### Pipelines

| Pipeline | Executions | Success Rate | Avg Tokens | Avg Duration |
|----------|------------|--------------|-----------|--------------|
| premarket_analysis | - | - | - | - |
| swing_trade_screener | - | - | - | - |
| catalyst_analysis | - | - | - | - |
| daily_watchlist_analysis | - | - | - | - |

### Signals Generated

| Watchlist | BUY | SELL | HOLD | Avg Confidence |
|-----------|-----|------|------|-----------------|
| vantage_portfolio | - | - | - | - |
| ai_verticals | - | - | - | - |
| energy_ai | - | - | - | - |

---

## 💰 Token Usage

### Daily Budget

- **Total Daily Allocation:** ~13,000 tokens (~$0.13/day)
- **Used (Last 24h):** TBD
- **Remaining:** TBD
- **Trend:** TBD

### Breakdown by Component

| Component | Tokens | Cost | % of Budget |
|-----------|--------|------|------------|
| API Calls | - | - | - |
| Data Fetching | - | - | - |
| Analysis | - | - | - |
| Reports | - | - | - |

### Monthly Projection

- **Current Month Used:** TBD
- **Projected Month End:** TBD
- **Percentage of Monthly Budget ($20):** TBD

---

## 🚨 Recent Errors (Last 48h)

| Timestamp | Component | Error | Severity | Resolution |
|-----------|-----------|-------|----------|-----------|
| - | - | - | - | - |

**If errors exist:** Click component name to see full traceback and logs.

---

## 📈 Performance Metrics

### API Call Performance

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Avg Latency | - ms | < 3000ms | - |
| Error Rate | -% | < 1% | - |
| Cache Hit Rate | -% | > 70% | - |
| Avg Tokens/Call | - | < 2000 | - |

### Data Pipeline Performance

| Stage | Avg Time | Tickers/Min | Success Rate |
|-------|----------|------------|--------------|
| Parse | - | - | - |
| Fetch | - | - | - |
| Analyze | - | - | - |
| Report | - | - | - |

---

## 🔧 System Configuration

### Current Settings

```yaml
VIF Framework:
  - Gamma Threshold: 0.5
  - Volume Multiplier: 1.5x
  - Kill Switches: K1-K6 (all active)

API:
  - Model: claude-sonnet-4-6
  - Batch Size: 15 tickers
  - Cache TTL: 24 hours

Schedule:
  - Premarket: 07:00 weekdays
  - Market Open: 08:45 weekdays
  - Swing Screener: 09:35 weekdays
  - After Hours: 16:05 weekdays
  - Weekend: Friday 16:30, Saturday 08:00
```

### Environment

- Python: 3.10+
- OS: Linux/macOS/Windows
- Git Branch: `main`
- Git Commit: [AUTO-FILLED]

---

## 📋 Recent Test Results

### Unit Tests

| Test | Status | Coverage | Last Run |
|------|--------|----------|----------|
| test_api_key | ✅ | - | - |
| test_harness | ✅ | - | - |
| test_indicators | ✅ | - | - |

### Integration Tests

| Pipeline | Status | Tickers | Last Run |
|----------|--------|---------|----------|
| Full Premarket | - | - | - |
| Swing Screener | - | - | - |
| Catalyst Analysis | - | - | - |

---

## 📁 File System Health

| Path | Files | Size | Last Modified |
|------|-------|------|---------------|
| `reports/raw/` | - | - | - |
| `reports/daily/` | - | - | - |
| `logs/` | - | - | - |
| `data/cache/` | - | - | - |

---

## 🔗 Dependencies

### Python Packages

| Package | Version | Status |
|---------|---------|--------|
| anthropic | 0.97+ | ✅ Installed |
| yfinance | - | ✅ Installed |
| pandas | - | ✅ Installed |
| ta | - | ✅ Installed |
| pyyaml | - | ✅ Installed |

### External Services

| Service | Status | Last Check |
|---------|--------|-----------|
| Yahoo Finance API | - | - |
| Claude API | - | - |
| GitHub (for MCP) | - | - |
| Hugging Face (for MCP) | - | - |

---

## 🐛 Known Issues

### Open

- **None currently tracked** — See `issues/` directory or GitHub Issues

### Recently Resolved

| Issue | Resolution | Date |
|-------|-----------|------|
| - | - | - |

---

## 📅 Upcoming Maintenance

| Date | Task | Priority | Owner |
|------|------|----------|-------|
| - | - | - | - |

---

## 🔐 Security Checklist

- [ ] API key is in `.env` (not committed to git)
- [ ] No sensitive data in logs
- [ ] telemetry.jsonl does not contain PII
- [ ] All credentials rotated last month
- [ ] MCP credentials (GitHub, Hugging Face) are valid

---

## 📞 Support & Troubleshooting

### Quick Diagnostics

```bash
# Check API connectivity
python tests/test_api_key.py

# Run offline test (no API credits)
python tests/test_harness.py

# View recent telemetry
tail -f logs/telemetry.jsonl

# Check system manifest
less SYSTEM_MANIFEST.md

# View agent-specific logs
tail -f logs/watchlist_watcher.log
tail -f logs/orchestrator.log
```

### Common Issues

1. **API calls failing:** Check `.env` file and API key validity
2. **Data fetching slow:** May be cache miss; check yfinance rate limits
3. **Signals not generating:** Check kill switches in `config/vif_config.yml`
4. **Scheduler not running:** Verify cron job or `run_delayed_start.py`

### Where to Look

- **Code issues:** See `agents/` and `scripts/`
- **Config issues:** See `config/vif_config.yml`
- **Error logs:** See `logs/*.log` and `logs/telemetry.jsonl`
- **Docs:** See `docs/` directory
- **Test results:** Run `python tests/test_harness.py`

---

## 📝 Updating This Dashboard

This dashboard can be manually updated, or auto-generated by running:

```bash
# Generate system manifest + health snapshot
python scripts/generate_manifest.py
python scripts/generate_health_dashboard.py  # (when implemented)
```

To set up periodic updates, add to cron:

```bash
# Every morning at 6 AM
0 6 * * * cd /path/to/vif-trading-system && python scripts/generate_manifest.py
```

---

**Last Updated:** [AUTO-TIMESTAMP]
**Generated by:** `scripts/generate_manifest.py` or manual edit
**Next Update:** TBD

---

## 📊 Power BI Dashboard Project (NEW)

**Building a professional Power BI dashboard** to visualize system health, costs, and performance.

### Quick Links
- 📋 **[POWER_BI_DASHBOARD_ROADMAP.md](./POWER_BI_DASHBOARD_ROADMAP.md)** — Complete technical roadmap with code examples and SQL queries
- 🎨 **[POWER_BI_DASHBOARD_ROADMAP.html](./POWER_BI_DASHBOARD_ROADMAP.html)** — Visual HTML version (open in browser)

### Project Status
- **Status:** Planning & Design Phase
- **Timeline:** 2-4 weeks to completion
- **Skills Demonstrated:** ETL, SQL, Python, Power BI
- **Interview Value:** ⭐⭐⭐⭐⭐ Excellent portfolio piece

### What's Included
- ✅ Complete architecture (3 dashboards: System Health, Costs, Errors)
- ✅ ETL script (Python) with code examples
- ✅ Database schema (star schema design)
- ✅ SQL queries (all 5 queries provided)
- ✅ Power BI layouts (step-by-step build guide)
- ✅ Automation setup (scheduled ETL)
- ✅ Interview talking points

**Ready to build? Start with the roadmap!**
