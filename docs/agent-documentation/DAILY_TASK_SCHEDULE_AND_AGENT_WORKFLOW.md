# Daily Task Schedule & Agent Workflow Documentation

**Document Version:** 1.0  
**Date:** May 2, 2026  
**Purpose:** Complete reference for automated tasks, agent roles, and continuous improvement workflow

---

## 📅 Daily Task Schedule (Automated Execution)

### **Weekday Schedule**

All times are **local timezone** (executed by `schedule_daily.py`)

#### **07:00 — Catalyst Scan Agent** 🎯
- **Task:** Scan for macro catalysts, earnings announcements, sector rotation
- **Executed by:** `agents/weekend_catalyst_agent.py`
- **Inputs:**
  - Earnings calendar (API: Yahoo Finance)
  - Macro events (Fed announcements, economic data releases)
  - News feeds (sector sentiment)
  - Watchlist tickers
- **Outputs:**
  - Catalyst bulletin (who's reporting, when)
  - Sector rotation signals
  - High-risk earnings dates for next 5 days
- **Files Generated:**
  - `reports/catalyst_scan_YYYYMMDD.json`
  - `reports/CATALYST_SCAN_YYYYMMDD.html`
- **Why it matters:** Earnings = binary events = kill switch K4 activated. Knowing which tickers have events helps avoid surprises.
- **What to do with it:** Before trading any ticker in report—check if earnings in next 5 days. If yes, tighten stops (volatility risk).

---

#### **08:45 — Premarket VIF Analysis** 📊
- **Task:** Full 1-month technical analysis on all watchlist tickers
- **Executed by:** `agents/watchlist_watcher.py --watchlist all --period 1mo`
- **Inputs:**
  - 73 tickers from Vantage Portfolio
  - 1-month OHLCV data (yfinance)
  - Technical indicators: RSI, MACD, Bollinger Bands, EMA20, ATR
  - Kill switch conditions (K1-K6)
- **Processing:**
  - Batched: 12 tickers per Claude API call (7 calls total)
  - Model routing: Simple → Haiku 4.5 ($1/MTok) | Complex → Sonnet 4.6 ($3/MTok)
  - Prompt caching: System prompt cached across all 7 calls (saves $0.012/day)
- **Outputs:**
  - Raw JSON: `reports/analysis_20260502_*.json`
  - Excel spreadsheet: `reports/VANTAGE_PORTFOLIO_ANALYSIS_*.xlsx`
  - HTML report: `reports/VANTAGE_PORTFOLIO_ANALYSIS_*.html`
- **Signal generation:**
  - BUY: Positive gamma + strong volume + no kills
  - SELL: Negative gamma + kill switch active
  - HOLD: Everything else (transition regime)
- **Files Generated:** 3 formats (JSON, Excel, HTML) for flexibility
- **What to do with it:** This is your **primary morning signal source**. Review at 8:50am before market open (10am ET).

---

#### **09:35 — Swing Trade Screener** 🎢
- **Task:** Identify 2-4 week swing trade setups (higher timeframe, medium-term holds)
- **Executed by:** `scripts/swing_trade_screener_v2.py`
- **Inputs:**
  - 2-4 week OHLCV data
  - Support/resistance levels (20/50/200-day moving averages)
  - Volatility clustering (ATR, Bollinger Band width)
  - Volume profile (where does big volume sit?)
- **Setup types identified:**
  - **Breakout:** Price above resistance + volume surge → long bias
  - **Breakdown:** Price below support + volume surge → short bias
  - **Consolidation Play:** Tight range, waiting for breakout → scalp or wait for confirm
  - **Reversal:** Oversold bounce (RSI <25 + V-shape recovery) or overbought fades
  - **Momentum:** Continuation from prior week's strong move
- **Ranking:** By risk/reward ratio (targets 2:1 or better)
- **Files Generated:**
  - `reports/SWING_SCREENER_*.xlsx` (ranked by R:R)
  - `reports/SWING_SCREENER_*.html`
- **What to do with it:** Find 2-3 best setups, add to watchlist, enter on breakout confirmation.

---

#### **16:05 — After-Hours Conviction Update** 🌙
- **Task:** Score existing positions for overnight hold conviction
- **Executed by:** `scripts/daily_watchlist_analysis.py`
- **Inputs:**
  - End-of-day price, volume, RSI
  - What was today's signal?
  - Did price action confirm or contradict the signal?
- **Outputs:**
  - Hold/reduce decision for each position
  - Overnight risk assessment (gaps, futures moves, earnings risk)
  - Conviction score: Should you hold or close?
- **Files Generated:**
  - `reports/CONVICTION_UPDATE_*.xlsx`
  - `reports/CONVICTION_UPDATE_*.html`
- **What to do with it:** Before you leave market, check this. If conviction drops to <30%, consider closing position overnight.

---

#### **17:00 — Daily Reports Generation** 📋
- **Task:** Auto-generate three daily reports at end of business day
- **Executed by:** Cron job calling:
  - `scripts/daily_changelog_generator.py`
  - `scripts/daily_news_monitor.py`
  - `scripts/autonomous_improvements.py`
- **Reports generated:**

**1. Daily Changelog** (`DAILY_CHANGELOG_YYYYMMDD.html`)
- System improvements completed today
- Analysis results (tickers analyzed, signals generated, kills triggered)
- Cost analysis (daily spend, projected monthly, savings)
- Scheduled jobs summary
- In-progress work items
- **Purpose:** Track system health & improvement velocity
- **Use case:** Weekly review to ensure system optimizations are delivering value

**2. Daily Summary Report** (`DAILY_SUMMARY_YYYYMMDD.html`)
- System updates (new features, fixes)
- API news (Anthropic updates, deprecations, new models)
- Analysis insights (market regime, key findings, signal breakdown)
- Market alerts (top SELL signals, technical breakdowns, sector rotations)
- Performance metrics (cost/day, cache hit rate, API calls, tickers analyzed)
- **Purpose:** Holistic view of market + system state
- **Use case:** Morning briefing next day (shows what happened yesterday)

**3. Improvements Tracker** (`IMPROVEMENTS_TRACKER_YYYYMMDD.html`)
- Phase 1 progress (Week 1 quick wins)
- Phase 2 roadmap (Week 2-3 medium-term improvements)
- Cost savings summary (current vs optimized costs)
- Implementation schedule (what's next)
- **Purpose:** Track roadmap execution
- **Use case:** Monthly review to gauge improvement velocity & ROI

---

### **Weekend Schedule**

#### **Friday 16:30 — End-of-Week Sweep** 📈
- Full analysis of all 3 watchlists
- Sector concentration report (which sectors over/underweight)
- Week recap: Win rate, alpha generated, adjustments needed
- **File:** `reports/WEEKLY_RECAP_*.html`

#### **Saturday 08:00 — Weekend Macro Briefing** 🌍
- Major economic data (jobs, inflation, central bank decisions)
- Earnings calendar (next week)
- Geopolitical risks
- Expected volatility shifts
- **File:** `reports/WEEKEND_MACRO_*.html`

#### **Sunday 18:00 — Monday Morning Prep** 🎯
- Pre-market gaps (if US futures available)
- Sector momentum shifts observed over weekend
- Monday setup guide (top buys/sells to watch)
- **File:** `reports/MONDAY_PREP_*.html`

---

## 🤖 Agent Architecture & Roles

### **Agent 1: Watchlist Watcher** (Primary)
**File:** `agents/watchlist_watcher.py`

**Responsibilities:**
- Parse TradingView watchlist exports (remove duplicates, normalize tickers)
- Fetch market data from yfinance (OHLCV + indicators)
- Cache data locally (24-hour TTL, 100% hit rate on repeat runs)
- Run VIF framework analysis via Claude API
- Generate BUY/SELL/HOLD signals with confidence scores

**How it works:**
1. **Parse Stage:** Read `watchlists/vantage_portfolio.txt` → extract 73 tickers
2. **Fetch Stage:** yfinance → RSI, MACD, MA20, ATR, volume (cached)
3. **Batch Stage:** Split 73 tickers into 6-7 batches of 12 tickers
4. **Route Stage:** Categorize complexity → simple to Haiku, complex to Sonnet
5. **Analyze Stage:** Claude processes each batch → returns BUY/SELL/HOLD
6. **Merge Stage:** Combine batch results into single portfolio analysis
7. **Export Stage:** Save to JSON + auto-convert to Excel + HTML

**Optimizations applied:**
- ✅ Prompt caching (system prompt cached across 7 calls, -$0.012/day)
- ✅ Hybrid routing (Haiku for simple, Sonnet for complex, -$0.05/day)
- ✅ Batching (12 tickers/call vs. 73 in one mega-call)

**Future optimizations in pipeline:**
- 🔄 Structured outputs (eliminate JSON parsing errors)
- 🔄 TA Library integration (replace hand-rolled indicators)
- 🔄 TradingAgents debate mechanism (reduce false signals 10-15%)

---

### **Agent 2: Weekend Catalyst Agent** (Macro Context)
**File:** `agents/weekend_catalyst_agent.py`

**Responsibilities:**
- Monitor earnings calendar (5-day forward look)
- Track macro events (Fed, employment, inflation data)
- Identify sector rotation signals
- Flag binary event risks (K4 kill switch trigger)

**How it works:**
1. Fetch earnings dates from multiple APIs
2. Match against watchlist tickers (which ones reporting soon?)
3. Assess volatility impact (tech earnings = higher vol than utilities)
4. Cross-reference with sector performance trends

**Output:**
- Daily catalyst report with risk/reward by sector
- K4 alerts (avoid longs 5 days before earnings)

**Usage:** Before trading any pre-earnings ticker, this tells you risk/reward is skewed (binary event).

---

### **Agent 3: Orchestrator** (Meta-Coordinator)
**File:** `agents/orchestrator.py`

**Responsibilities:**
- Coordinate multi-agent pipelines
- Route requests to correct agent (watchlist → watcher, macro → catalyst agent)
- Support focused analysis (single ticker deep-dive or specific watchlist)
- Combine outputs from multiple agents

**Modes:**
- `--mode premarket` — Quick BUY/SELL signals (8:45 job)
- `--mode full` — Complete analysis with catalyst context
- `--ticker NVDA` — Deep analysis of one stock (technical + options + catalysts)

---

### **Agent 4: Research Agent** (Ad-Hoc Q&A)
**File:** `agents/claude_research_agent.py`

**Responsibilities:**
- Answer ad-hoc trading questions
- Explain VIF framework concepts
- Interactive analysis (not scheduled)

**Example queries:**
- "What's the gamma flip point for NVDA?"
- "Why was TSLA marked SELL yesterday?"
- "Compare APE and AMC using VIF framework"

**Usage:** `python agents/claude_research_agent.py --query "your question"`

---

### **Agent 5: Report UI Agent** (Formatting)
**File:** `agents/report_ui_agent.py`

**Responsibilities:**
- Convert raw JSON analysis to human-readable Markdown/HTML
- Create summary narratives
- Format tables and charts

---

## 🔄 Continuous Improvement Workflow

### **How Agents Improve the System**

**Week 1: Rapid Deployment** ✅
1. **Monday-Tuesday (May 1-2):** Deploy quick wins
   - Prompt caching (-$0.012/day) ✅ DONE
   - Hybrid routing (-$0.05/day) ✅ DONE
   - Structured outputs 🔄 IN PROGRESS
2. **Measurement:** Track daily cost, API call times, error rates

**Week 2: Code Improvement** 🔄
1. **Monday-Wednesday (May 6-8):**
   - TA Library integration (replace hand-rolled indicators)
   - Backtesting.py setup (weekly validation)
2. **Measurement:** Validate indicator accuracy, measure Sharpe ratio of signal subset

**Week 3: Signal Enhancement** 🔄
1. **Monday-Friday (May 13-17):**
   - TradingAgents debate mechanism (multi-agent validation)
   - PyBroker Numba acceleration (8x faster compute)
2. **Measurement:** Compare before/after false signal rate, compute speed

**Week 4+: Strategic Features** 🔄
1. **May 20+:** AgenticTrading (self-improving agents with memory)
2. **Measurement:** Track learn-ability (does system improve after observing past errors?)

---

### **Agent Self-Improvement Loop**

```
Day 1: Signal Generated
  ↓ (analysis_20260502_140330.json created)
↓
Day 1 EOD: Report Generated
  ↓ (daily_summary shows signals + market context)
↓
Day 2: Outcome Observed
  ↓ (price moved; did VIF signal call the direction?)
↓
Week 1 EOD: Performance Reviewed
  ↓ (win rate calculated; high-confidence signals assessed)
↓
Week 2: Improvements Applied
  ↓ (adjust thresholds, fine-tune kill switches, add new indicators)
↓
Week 3+: Backtesting Validates
  ↓ (Backtesting.py shows Sharpe impact of changes)
↓
Month 1: Cycle Repeats
  ↓ (system becomes incrementally better)
```

**Concrete improvements made automatically:**

1. **Confidence Calibration**
   - Track: Which confidence scores were most accurate?
   - Example: If 60-70% confidence signals win 60%, bump threshold to 65%
   - Effect: Fewer false positives

2. **Kill Switch Tuning**
   - Track: Did K2 (high volatility) filter out losers or winners?
   - Example: If K2 trades still win 55%, relax threshold from 12% to 14%
   - Effect: Fewer skipped opportunities

3. **Indicator Weighting**
   - Track: Which indicator (RSI vs volume vs gamma) predicted direction best?
   - Example: If volume outperforms gamma in short timeframes, increase weight
   - Effect: Better signal quality

---

## 📊 System Monitoring Dashboard

### **Daily Metrics Tracked**

| Metric | Current | Target | Action If Below |
|--------|---------|--------|-----------------|
| **Cost/Day** | $0.068 | <$0.15 | Reduce batch size or add more caching |
| **API Calls/Day** | 6-7 | <8 | Combine adjacent calls or increase cache TTL |
| **Cache Hit Rate** | 100% | >95% | Increase cache TTL from 24h |
| **JSON Parse Success** | 100% | >99% | Implement structured outputs |
| **Analysis Time** | ~7 min | <5 min | Deploy PyBroker acceleration |
| **Signal Confidence Avg** | ~45% | >55% | Tighten filters (raise minimum from 30%) |

---

### **Weekly Performance Review** (Friday 4pm)

| Metric | How to Calculate | Action |
|--------|------------------|--------|
| **Win Rate** | (Winning signals / Total signals) × 100 | If <55%: adjust thresholds |
| **Alpha Generated** | (VIF returns - SPY returns) | If <50bps/week: reduce noise |
| **Sector Concentration** | Largest sector % of total capital | If >50%: rebalance |
| **Avg Hold Duration** | Average days held per trade | If >7d: reduce winners; exit faster |
| **Sharpe Ratio** | Return ÷ volatility of returns | If <1.0: too much volatility |

---

## 🎯 Agent Communication Flow

```
┌─────────────────────────────────────────────────────────────┐
│                   schedule_daily.py                         │
│              (Master Orchestrator - Cron Job)               │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
    07:00 │          08:45 │         09:35 │
         │               │               │
    ┌────▼──┐       ┌────▼──┐       ┌────▼──┐
    │Catalyst│      │ Watcher│      │Screener│
    │ Agent  │      │ Agent  │      │ Agent  │
    └────┬───┘      └────┬───┘      └────┬───┘
         │               │               │
         │ earnings.json │ analysis.json │
         │               │ + excel export│
         │               │               │
         └───────────────┼───────────────┘
                         │
                    16:05 │
                         │
                    ┌────▼──────────┐
                    │ Conviction     │
                    │ Update Agent   │
                    └────┬───────────┘
                         │
                         │ conviction.json
                         │
                    17:00 │
                         │
         ┌───────────────┼───────────────┐
         │               │               │
    ┌────▼──┐       ┌────▼──┐       ┌────▼──┐
    │Changelog│      │Summary │      │Tracker│
    │Generator │      │Monitor │      │Agent  │
    └────┬────┘      └────┬───┘      └────┬───┘
         │                │               │
         │ changelog.html │ summary.html  │
         │                │ improvements  │
         │                │ tracker.html  │
         │                │               │
         └────────────────┴───────────────┘
                    │
              📊 Reports Ready
              (User Reviews)
```

---

## 🔐 Data Quality Assurance

**How agents validate their own work:**

1. **JSON validation** (after each analysis)
   - Check: All required fields present (signal, confidence, price, etc.)
   - Check: Confidence is 0-100 integer
   - Check: Signal is BUY/SELL/HOLD
   - Fix: If invalid, re-run or flag for manual review

2. **Signal consistency** (weekly)
   - Check: If RSI=50 and price=MA20, signal should be HOLD (not BUY/SELL)
   - Check: Negative gamma + kill switch should be SELL (not HOLD)
   - Fix: Adjust weighting in VIF framework

3. **Performance validation** (monthly)
   - Check: Do high-confidence signals outperform low-confidence?
   - Check: Is kill switch filtering working? (skipped losers?)
   - Fix: Calibrate thresholds or adjust kill switch conditions

---

## 📝 Quick Reference

### **What runs every day:**
- 07:00 → Catalyst scan
- 08:45 → VIF analysis (73 tickers, 3 formats: JSON/Excel/HTML)
- 09:35 → Swing screener
- 16:05 → Conviction update
- 17:00 → 3 daily reports (changelog, summary, tracker)

### **What agents do:**
- **Watcher:** Signal generation (BUY/SELL/HOLD)
- **Catalyst:** Risk/catalyst flagging
- **Screener:** Multi-week setup identification
- **Orchestrator:** Coordination
- **Research:** Ad-hoc analysis

### **How they improve:**
- Weekly performance review
- Monthly threshold calibration
- Quarterly architecture upgrade

---

**Document Owner:** VIF Trading System  
**Last Updated:** May 2, 2026  
**Next Review:** May 9, 2026
