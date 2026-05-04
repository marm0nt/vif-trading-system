# Friday Prep for Monday Trading: Quick Reference

**Last Updated:** May 2, 2026  
**Purpose:** Where to look to prep for Monday execution

---

## 🎯 TOP 3 FOLDERS YOU'LL USE 90% OF THE TIME

### 1. **`reports/premarket/`** — Your Daily Trading Signals
**What's here:** HTML reports with BUY/SELL/HOLD signals for all tickers  
**File pattern:** `pipeline_premarket_YYYYMMDD_HHMMSS.html`  
**Latest:** [`reports/premarket/pipeline_premarket_20260502_210910.html`](../../reports/premarket/pipeline_premarket_20260502_210910.html)  
**Why:** This is your main decision tool. Open in browser, click tabs to see:
- **Catalysts Tab** — Earnings, K4 alerts, macro events
- **VIF Analysis Tab** — All tickers with RSI, MACD, Bollinger Bands, ATR, gamma regime, kill switches
- **Swing Setups Tab** — 2-4 week opportunities (pullback, consolidation, oversold bounce)

**Action for Monday prep:** Open latest HTML report Friday evening, review which tickers have active signals for Monday morning.

---

### 2. **`reports/catalysts/`** — Risk Alerts & Macro Context
**What's here:** JSON files with earnings dates, news, K4 kill switches  
**File pattern:** `catalyst_analysis_YYYYMMDD_HHMMSS.json`  
**Latest:** `reports/catalysts/catalyst_analysis_20260502_210622.json`  
**Key JSON fields:**
- `k4_kill_switches` — Tickers with earnings ≤5 days (DO NOT TRADE these)
- `macro_regime` — Current market condition (positive/negative/transition)
- `sector_themes` — Which sectors are hot
- `ticker_catalysts` — Per-ticker news, earnings, events

**Action for Monday prep:** Check K4 alerts. Any ticker you're considering should NOT be in K4 list.

---

### 3. **`reports/swing-trades/`** — Your 2-4 Week Opportunity List
**What's here:** Swing trade screener results (JSON + analysis files)  
**File pattern:** `swing_setups_YYYYMMDD_HHMMSS.json`  
**Latest:** `reports/swing-trades/swing_setups_20260502_210910.json`  
**Key data:**
- **5 setup types ranked by risk/reward:**
  1. PULLBACK_TO_MA20 (safest)
  2. BULLISH_MA_MOMENTUM
  3. SUPPORT_BOUNCE
  4. CONSOLIDATION_BREAKOUT
  5. OVERSOLD_BOUNCE

**Action for Monday prep:** Filter by setup type. PULLBACK_TO_MA20 is lowest risk for weekly execution.

---

## 📊 SECONDARY FOLDERS (Reference Only)

| Folder | Purpose | When to Check |
|--------|---------|---|
| `reports/weekend/` | Macro briefing from Friday evening | Monday morning (strategic context) |
| `reports/raw/` | Intermediate JSON data | Only for debugging signal issues |
| `reports/archive/` | Old reports >30 days | Rarely needed |
| `logs/orchestrator.log` | Pipeline execution status | If reports fail to generate |
| `config/vif_config.yml` | Kill switches, thresholds | Only if modifying framework |

---

## 🚀 YOUR MONDAY EXECUTION WORKFLOW

### **Friday Evening (Right Now)**
1. ✅ Open latest `reports/premarket/pipeline_premarket_*.html` in browser
2. ✅ Scan **Catalysts Tab** for K4 alerts (earnings ≤5 days)
3. ✅ Review **VIF Analysis Tab** for BUY signals (confidence >70)
4. ✅ Check **Swing Setups Tab** for 2-4 week opportunities
5. ✅ Open `reports/catalysts/catalyst_analysis_*.json` in VS Code
6. ✅ Note `macro_regime` (positive/negative affects signal reliability)
7. ✅ Mark 3-5 tickers as "candidates for Monday"

### **Monday Morning (07:00-09:00)**
1. ✅ System runs premarket pipeline automatically (07:00)
2. ✅ Check latest `reports/premarket/pipeline_premarket_*.html` (new report by 08:30)
3. ✅ Compare Friday's candidates vs Monday morning signals (any changes?)
4. ✅ For each candidate ticker:
   - **Is K4 active?** → SKIP (earnings risk)
   - **Is RSI >80 or <20?** → SKIP (K1 kill switch)
   - **Is BB squeeze + low volume?** → SKIP (K6 kill switch)
   - **Is macro_regime positive?** → GOOD (higher confidence)
   - **Is golden_cross active?** → GOOD (trend structure)
5. ✅ Execute orders on approved tickers

---

## 📂 FOLDER STRUCTURE AT A GLANCE

```
vif-trading-system/
│
├── reports/                          ← YOUR MAIN WORKSPACE
│   ├── premarket/                    ← Daily signals (MOST IMPORTANT)
│   │   └── pipeline_premarket_*.html ← OPEN THIS IN BROWSER
│   ├── swing-trades/                 ← 2-4 week setups
│   │   └── swing_setups_*.json
│   ├── catalysts/                    ← K4 alerts, macro context
│   │   └── catalyst_analysis_*.json
│   ├── weekend/                      ← Monday briefing
│   └── archive/                      ← Old reports >30 days
│
├── docs/                             ← REFERENCE DOCS
│   ├── FOLDER_OPERATIONS_CHECKLIST.md ← Daily ops guide
│   ├── MARKET_DATA_SOURCE_ANALYSIS.md ← Why we use yfinance
│   ├── TA_LIBRARY_INTEGRATION_COMPLETE.md ← What just improved
│   └── QUICK_START_FRIDAY_PREP.md    ← THIS FILE
│
├── config/                           ← CONFIGURATION
│   └── vif_config.yml                ← Kill switches, thresholds
│
├── agents/                           ← EXECUTION CODE (don't edit)
│   ├── indicators.py                 ← RSI, MACD, BB, ATR, EMA
│   ├── orchestrator.py               ← Runs all agents
│   ├── watchlist_watcher.py          ← VIF analysis
│   └── weekend_catalyst_agent.py     ← Macro briefing
│
├── scripts/                          ← ANALYSIS SCRIPTS
│   ├── catalyst_analysis.py          ← K4 detection, macro
│   └── swing_trade_screener_v2.py    ← Swing setup screener
│
└── logs/                             ← DEBUG INFO
    └── orchestrator.log              ← Pipeline execution logs
```

---

## 🎯 WHAT TO LOOK AT FOR MONDAY EXECUTION

### **Tier 1: MUST REVIEW** (10 min)
- [ ] Latest premarket HTML report (BUY/SELL/HOLD signals)
- [ ] K4 alerts in catalyst JSON (which tickers to skip)
- [ ] Macro regime (positive = higher signal confidence)

### **Tier 2: SHOULD REVIEW** (5 min)
- [ ] Golden cross status (EMA50 > EMA200? = bullish structure)
- [ ] Swing setup type (PULLBACK_TO_MA20 = safest)
- [ ] Volume signal (strong/normal/weak affects entry conviction)

### **Tier 3: OPTIONAL** (deep dives only)
- [ ] Raw JSON analysis (for debugging failed signals)
- [ ] Historical logs (understanding why a signal fired)
- [ ] Configuration review (only if changing kill switch thresholds)

---

## ⚡ QUICK CHECKLIST FOR MONDAY

**Before 9:35 AM market open:**

- [ ] Premarket report generated? (check `reports/premarket/` folder)
- [ ] Pick 3-5 candidates with BUY signals (confidence >70)
- [ ] Cross-check against K4 list (earnings within 5 days?)
- [ ] Verify macro_regime is positive or transition (not negative)
- [ ] Check RSI (not >80 or <20 = K1 not triggered)
- [ ] Verify volume signal is normal or strong
- [ ] For swing trades: pick PULLBACK_TO_MA20 setup (lowest risk)
- [ ] Execute on first 30 min after market open (liquidity confirmation)

---

## 📌 KEY KILL SWITCHES TO REMEMBER

| K# | Name | Trigger | Action |
|----|------|---------|--------|
| **K1** | Extreme RSI | RSI >80 or <20 | SKIP ticker |
| **K2** | Volatility Gap | 5-day range >12% | SKIP ticker |
| **K3** | Low Liquidity | Volume <500k | SKIP ticker |
| **K4** | Earnings Risk | Earnings ≤5 days | **MUST SKIP** |
| **K6** | Breakdown | BB squeeze + low vol | SKIP ticker |

---

## 🔗 DIRECT FILE PATHS FOR QUICK ACCESS

**Open these files directly in browser/editor for Monday prep:**

1. **Latest Premarket HTML:**  
   `C:\Users\marti\vif-trading-system\reports\premarket\pipeline_premarket_20260502_210910.html`  
   ⏱️ Fastest way: Right-click → Open with → Chrome

2. **Latest Catalyst JSON:**  
   `C:\Users\marti\vif-trading-system\reports\catalysts\catalyst_analysis_20260502_210622.json`  
   ⏱️ Open in VS Code for easy parsing

3. **Latest Swing Setups JSON:**  
   `C:\Users\marti\vif-trading-system\reports\swing-trades\swing_setups_20260502_210910.json`  
   ⏱️ Quick reference for 2-4 week opportunities

---

## 💡 FRIDAY → MONDAY WORKFLOW SUMMARY

**Friday Evening (30 min):**
1. Open premarket HTML → scan BUY signals
2. Open catalyst JSON → check K4 list, macro regime
3. Mark 3-5 candidates
4. Sleep soundly 😴

**Monday 08:30 AM (10 min):**
1. Check if new premarket report ready
2. Verify candidates still valid
3. Execute approved trades

**That's it.** The system handles the heavy lifting.

---

## ❓ IF SOMETHING GOES WRONG

| Problem | Solution |
|---------|----------|
| No premarket HTML? | Check `logs/orchestrator.log` for errors |
| JSON file missing? | System may still be running (check timestamps) |
| K4 list empty? | Probably means no earnings this week (good!) |
| RSI showing 50? | Insufficient data (needs 14+ bars) |
| Macro regime "negative"? | Market headwind; lower conviction, fewer BUY signals |

---

## 📞 STILL OVERWHELMED?

You don't need to understand everything. For Monday execution, focus on:

1. **Which tickers have BUY signals?** (premarket HTML)
2. **Which have K4 alerts?** (catalyst JSON)
3. **Is macro positive?** (catalyst JSON)
4. **Is volume normal or strong?** (premarket HTML)

That's literally all you need to trade confidently. The system does the rest.

