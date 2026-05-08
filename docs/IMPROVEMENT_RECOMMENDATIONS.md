# Project Improvement Opportunities

**High-Impact, Low-Risk improvements identified through meta-tools analysis.**

---

## Priority 1: Organize scripts/ Directory (Use file-organizer)

**Current State:**
- 14 Python files (7 active + 7 archived)
- 374KB total
- No organization by function

**Recommended Structure:**
```
scripts/
├── active/
│   ├── analysis/
│   │   ├── catalyst_analysis.py      (30KB — K4 flags, macro events)
│   │   ├── swing_trade_screener_v2.py (16KB — 5 setup types)
│   │   └── daily_watchlist_analysis.py (24KB — conviction scoring)
│   ├── reporting/
│   │   ├── generate_vif_master_report.py (44KB — best HTML generator)
│   │   ├── html_report_generator.py   (36KB — simpler fallback)
│   │   └── json_to_excel_exporter.py  (optional Excel output)
│   └── utilities/
│       └── check_usage.py (cost tracking)
├── meta_tools/                       (already exists, keep as-is)
│   ├── file-organizer/
│   └── skill-creator/
└── archive/                          (already exists, keep as-is)
```

**Expected Benefit:**
- ✅ Faster navigation when adding new analysis scripts
- ✅ Clear separation between load-bearing pipeline code and utilities
- ✅ Easy to identify which scripts run in schedule_daily.py vs manual-only

**How to Execute:**
```
In Claude Code, ask:
"Organize scripts/ directory. Separate into:
- scripts/active/analysis/ (catalyst_analysis.py, swing_trade_screener_v2.py, daily_watchlist_analysis.py)
- scripts/active/reporting/ (generate_vif_master_report.py, html_report_generator.py, json_to_excel_exporter.py)
- scripts/active/utilities/ (check_usage.py)
- Leave scripts/meta_tools/ and scripts/archive/ as-is"
```

**Effort:** 5 minutes (file-organizer does the work)

---

## Priority 2: Clean reports/ Directory (Use file-organizer)

**Current State:**
- 5.2MB of HTML reports
- Many old copies (May 2-7, duplicates)
- 15+ files with similar names

**Recommendation:**
```
Keep only:
- Last 3 days of pipeline_premarket_*.html
- Last 3 days of pipeline_market_open_*.html
- Last 1 month of VIF_MASTER_DASHBOARD_*.html

Archive to:
reports/archive/historical/YYYY-MM/
```

**Expected Benefit:**
- ✅ Reduces reports/ from 5.2MB to <1.5MB
- ✅ Git operations faster (smaller repo)
- ✅ Easier to find recent reports
- ✅ Old reports still available in archive/ if needed

**How to Execute:**
```
In Claude Code, ask:
"Clean reports/ directory. Keep:
- Last 3 premarket reports
- Last 3 market_open reports  
- All VIF_MASTER_DASHBOARD files
- Move older files to reports/archive/historical/<date>/"
```

**Effort:** 3 minutes

---

## Priority 3: Consolidate Duplicate Validation Logic (Use skill-creator)

**Current State:**
- `daily_watchlist_analysis.py` duplicates VIF logic from `agents/watchlist_watcher.py`
- Both compute RSI, MACD, Bollinger Bands independently
- Both produce signals (different scoring)

**Analysis:**
- `daily_watchlist_analysis.py`: 24KB, 200+ lines, class-based, proprietary conviction scoring
- `agents/watchlist_watcher.py`: primary VIF pipeline, batch mode, production
- Overlap: RSI, EMA, technical analysis, signal generation

**Recommendation:**
Instead of merging (risky), create a **"vif-signal-validator" skill** that:
1. Takes raw VIF signals from orchestrator
2. Cross-validates with daily_watchlist_analysis confidence scores
3. Flags divergences (e.g., VIF=BUY but confidence=LOW)
4. Outputs enhanced confidence levels

**Expected Benefit:**
- ✅ Leverages both analysis methods without merging
- ✅ Confidence scoring becomes discoverable (other Claude instances can use it)
- ✅ No risk to production pipeline
- ✅ Provides secondary validation layer
- ✅ Reusable for swing-trade-screener confidence tuning

**How to Execute:**
```bash
# Step 1: Initialize skill template
python scripts/meta_tools/skill-creator/init_skill.py vif-signal-validator --path .claude/skills/

# Step 2: Move validation logic to scripts/
cp scripts/daily_watchlist_analysis.py scripts/meta_tools/vif-signal-validator/scripts/

# Step 3: Edit .claude/skills/vif-signal-validator.md
# - Document when to use (after vif-analyst, before report-builder)
# - Reference scripts/daily_watchlist_analysis.py
# - Show input: VIF JSON signals
# - Show output: signals with confidence modifiers

# Step 4: Package
python scripts/meta_tools/skill-creator/package_skill.py .claude/skills/vif-signal-validator/
```

**Effort:** 30 minutes

---

## Priority 4: Wire generate_vif_master_report.py Into Report Pipeline

**Current State:**
- `generate_vif_master_report.py` (44KB) is the **best HTML generator** in the project
- Not wired into schedule_daily.py or orchestrator.py
- Smaller `html_report_generator.py` is used instead

**Recommendation:**
Update `orchestrator.py` to use `generate_vif_master_report.py` for all HTML output:
```python
# In report-builder stage:
from scripts.generate_vif_master_report import create_dashboard
html = create_dashboard(json_data)  # Instead of html_report_generator.py
```

**Expected Benefit:**
- ✅ Professional dashboards (gradient headers, tabs, interactive tables)
- ✅ Consistent styling across all reports
- ✅ Better visual differentiation of signal confidence

**Risk Level:** Low (backward compatible, both generators produce HTML)

**Effort:** 10 minutes

---

## Priority 5: Identify Code Duplication in Indicators

**Current State:**
- `agents/indicators.py`: shared indicator engine (RSI, MACD, Bollinger Bands, etc.)
- `agents/watchlist_watcher.py`: uses indicators.py
- `scripts/daily_watchlist_analysis.py`: **recomputes** RSI, MACD inline (doesn't import indicators.py)

**Finding:** `daily_watchlist_analysis.py` bypasses the shared indicator engine.

**Recommendation:**
Create a **"indicator-validator" skill** that:
1. Compares indicators.py vs daily_watchlist_analysis.py implementations
2. Identifies divergences (RSI calculation differences)
3. Validates which version is correct against yfinance TA-Lib

**Expected Benefit:**
- ✅ Ensures consistent indicator math across all analysis
- ✅ Catches subtle bugs (e.g., RSI period differences)
- ✅ Builds confidence in signal reliability

**Effort:** 45 minutes

---

## Summary: What to Do This Week

| Priority | Task | Tool | Effort | Benefit |
|----------|------|------|--------|---------|
| 1 | Organize scripts/ | file-organizer | 5 min | Faster navigation |
| 2 | Clean reports/ | file-organizer | 3 min | 3.7MB saved |
| 3 | Create vif-signal-validator skill | skill-creator | 30 min | Better signal confidence |
| 4 | Wire generate_vif_master_report.py | Manual edit | 10 min | Better dashboards |
| 5 | Create indicator-validator skill | skill-creator | 45 min | Consistency check |

**Total effort:** ~90 minutes
**Total benefit:** 3.7MB saved + consistent validation + better dashboards

---

## What NOT to Change

❌ Don't merge daily_watchlist_analysis.py into watchlist_watcher.py
- Risk of breaking production pipeline
- Different architectures (class vs functional)
- Better to run in parallel as validator

❌ Don't consolidate catalyst_analysis.py
- Standalone utility, not critical path
- Clean separation of concerns
- Keep as-is

❌ Don't touch .claude/agents/ or .claude/skills/ directory structure
- Already well-organized
- Production-critical files
- Leave alone

---

## Next Steps

1. **This session:** Use file-organizer on scripts/ and reports/
2. **Next session:** Create vif-signal-validator skill
3. **Follow-up:** Wire generate_vif_master_report.py into orchestrator
4. **Optional:** Create indicator-validator skill if code drift detected
