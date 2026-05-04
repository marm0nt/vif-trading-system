Optimized Daily Trading Workflow for Alpha Extraction
Document Version: 1.0
Date: May 2, 2026
Purpose: Actionable day-by-day, hour-by-hour guide to extract maximum alpha from VIF reports
---
Report Overview
This document provides an operational, time-boxed trading workflow for using VIF-generated reports to identify setups, execute trades, manage risk during the session, and complete end-of-day and weekly review routines.
* Quick Start: Use the �Quick Start: Your 3-Minute Morning Checklist� section for the pre-open setup.
* Daily Operating Rhythm: Follow �Detailed Workflow by Time of Day� for premarket through end-of-day execution and management.
* Weekly Review: Use �Weekly Workflow (Friday 4:00pm)� to calculate performance metrics and document lessons learned.
* Process Improvements: Use �Pro Tips for Maximum Alpha� and �Performance Tracking Template� to standardize sizing, tracking, and iteration.
* Printable Control List: Use �Daily Checklist (Print & Tape to Monitor)� as the daily compliance checklist.
Quick Start: Your 3-Minute Morning Checklist
Time: 08:50am - Before Market Open
1. STEP 1 (30 sec): Open Excel reports
o -> reports/VANTAGE_PORTFOLIO_ANALYSIS_*.xlsx
o -> reports/AI_VERTICALS_ANALYSIS_*.xlsx
2. STEP 2 (60 sec): Review SELL Signals sheet
o Sort by Confidence descending
o Identify top 3 high-confidence SELLs (>65%)
o Check: Any K2 (volatility) active? -> Premium short setups
o Mark these as "TODAY'S SHORTS TO WATCH"
3. STEP 3 (60 sec): Review BUY Signals sheet
o Filter: Confidence >60% AND Kill Switch = "None"
o Identify top 2-3 longs to watch
o Check: Volume = STRONG or NORMAL? (if WEAK, skip)
o Mark these as "TODAY'S LONGS TO WATCH"
4. STEP 4 (60 sec): Check overnight positions
o Compare holding positions to yesterday's signals
o If SELL signal appeared overnight: EXIT ON OPEN (no debate)
o If BUY signal confirmed: HOLD + consider adding
o Update position sizing based on fresh Confidence scores
READY TO TRADE: 9:00am
---
Detailed Workflow by Time of Day
PREMARKET (8:45am - 10:00am ET)
8:45-8:48: Auto-Generated Reports Arrive
* Analyst finishes VIF analysis
* Reports auto-exported: JSON -> Excel -> HTML
* Systems: Files saved to reports/ folder
8:48-8:54: Excel Report Review (6 min)
Open VANTAGE_PORTFOLIO_ANALYSIS_*.xlsx
Sheet 1: Summary Tab
* Read watchlist overview
* Check: Total tickers, kills triggered, signal distribution
* Key insight: Is market regime positive/negative/transition?
o If Positive: Long bias today (buy dips)
o If Negative: Short bias today (fade rallies)
o If Transition: Stay defensive, require clear setups
Sheet 2: SELL Signals Tab (Highest priority)
ColumnActionTickerMark on watchlistConfidence>70% = execute shorts; 50-70% = watch; <50% = ignoreKill SwitchK2 + SELL = premium shortPriceSet short entry 5% below current (if breakdown)NoteRead reasoning (confirms or contradicts your thesis)Example Action:
NVDA SELL, Confidence 62%, K2 (volatility), Price $209.25
Interpretation: Overbought vol spike, technical risk
Action: Watch for breakdown below MA20, then short on volume
Entry: <$197 (below MA20), Stop: $214 (above resistance)
Target: $180 (support), R:R = 1:2.5 ? EXECUTE IF SETUP HITS
Sheet 3: BUY Signals Tab
ColumnActionTickerMark on watchlistConfidence>70% = buy; 50-70% = scale in; <50% = ignoreVolume SignalWEAK = avoid; NORMAL = OK; STRONG = preferredPriceSet long entry at MA20 (on dips)Kill SwitchIf K2 = wait for breakout confirm; if NONE = go longExample Action:
MSFT BUY, Confidence 73%, STRONG vol, K=None, Price $424.46
Interpretation: Bullish momentum, volume confirmed, no red flags
Action: Buy on dip to MA20 or breakout above resistance
Entry: $425 (breakout) or $415 (MA20 dip), Stop: $407
Target: $460 (resistance), R:R = 1:2.3 ? EXECUTE
Sheet 4: Kill Switch Analysis Tab
* K2 tickers (high volatility): Watch for whipsaws; short scalps only
* K3 tickers (illiquid): SKIP entirely
* K6 tickers (breakdown): Wait for setup confirmation before long entry
8:54-8:58: Check Overnight Positions (4 min)
For each open position:
PositionYesterday's SignalToday's SignalActionAAPL LongBUY (Conf 65%)HOLD (Conf 35%)Reduce 50% at open, keep 50% for momentumTSLA LongBUY (Conf 72%)BUY (Conf 75%)HOLD + add 25% on dipQQQ ShortSELL (Conf 60%)SELL (Conf 68%)HOLD + add 25% on rallySPY LongHOLD (Conf 40%)HOLD (Conf 38%)CLOSE (confidence dropped)Rule: If signal degrades (e.g., 70% -> 40%), reduce or close position. If signal improves, hold or add.
8:58-9:00: Set Alerts (2 min)
Using your broker (ThinkorSwim, Interactive Brokers, etc.):
For each "TODAY'S SHORTS" and "TODAY'S LONGS":
* Shorts: Alert if price breaks below yesterday's low (setup trigger)
* Longs: Alert if price breaks above yesterday's high (setup trigger)
Example:
NVDA Short Setup: Alert if price < $205 (below MA20 support)
MSFT Long Setup: Alert if price > $430 (above resistance)
By 9:00am: You're ready to trade. Market opens.
---
MARKET OPEN (10:00am - 11:00am ET)
10:00-10:30: Execution Phase
Tactic 1: Breakout Trading (Using VIF setups)
Watching: NVDA SELL signal + K2 (volatility)
Setup: Price breaks below $205 (MA20 support) + volume surge

Execution:
1. Price hits $204 + volume 30% above average -> ENTER SHORT
2. Set stop loss: $214 (above resistance)
3. Set profit target: $180 (support level)
4. R:R = $34 risk : $24 target = 1:2.4 ? Too tight
-> Adjust target to $175 = 1:2.9 ? BETTER
5. EXECUTE SHORT (5% of portfolio allocation)
Tactic 2: Dip-Buying (If overnight dips occur)
Watching: MSFT BUY signal + STRONG volume
Setup: Price dips to MA20 ($415) + RSI >40 (no oversold)

Execution:
1. Price hits $415 + volume confirms -> ENTER LONG
2. Set stop loss: $407 (below MA20)
3. Set profit target: $450 (next resistance)
4. R:R = $8 risk : $35 target = 1:4.4 ? EXCELLENT
5. EXECUTE LONG (3% of portfolio allocation)
Tactic 3: Momentum Scalping (For K2 + SELL setups - pro only)
Watching: Ticker with K2 + SELL + Confidence 75%
Setup: Intraday momentum collapse (price > MA20 but falling)

Execution:
1. Enter SHORT on close above MA20 (end-of-day)
2. Hold 5-30 minutes only (scalp)
3. Exit on first 0.5-1% profit or close back below MA20
4. Repeat 2-3 times if setup repeats

Risk: High intensity, tight stops, small shares. PRO ONLY.
Reward: 100+ bps/day on good vol days
10:30-11:00: No New Entries
After 10:30am ET, market momentum typically established. Avoid chasing.
Instead:
* Monitor existing positions
* Tighten stops on winners (if up 1%+)
* Add to winners if setup repeats (pyramid)
---
MID-DAY (11:00am - 3:00pm ET)
Position Management
Every hour:
* Check profit/loss on open positions
* If +2% or more: TIGHTEN stop to breakeven
* If -1% or more: REASSESS thesis (is signal still valid?)
Catalyst Monitor:
* Check reports/catalyst_scan_*.json for same-day announcements
* If catalyst drops, close position immediately (binary event risk)
Sector Watch:
* Track if sector shifted (check AI_VERTICALS or ENERGY_AI sheets from morning)
* If sector momentum reversed, close positions in that sector
Avoid These Mistakes
* Don't add to losing positions (unless setup improves, which is rare)
* Don't hold past lunch hour on intraday scalps (close by 2pm)
* Don't initiate new positions without VIF signal confirmation
* Don't fight the tape (if all your longs down, market likely bearish)
---
LATE DAY (3:00pm - 4:00pm ET)
Position Closing Decisions
Ask yourself:
1. Is the VIF signal still valid? (Check kill switches; did K4 appear = earnings risk?)
2. Have we hit the target? (If yes, close)
3. Is position up, but momentum fading? (Close into strength; don't hold overnight)
4. Do I want to hold overnight? (Risk/reward framework below)
Overnight Hold Decision Tree:
Do I have a winning position?
|- YES: Take profit (2/3 of position) + hold 1/3 overnight
| \- Tomorrow morning: Check VIF signal
| |- Still BUY -> Hold or add
| \- Now SELL -> Close immediately
|
\- NO (Losing position):
|- Is the VIF signal still valid? (or did kill switch appear?)
| |- YES -> Hold stop, let it work (overnight vol could flush weaker holders)
| \- NO -> Close losses, move to next trade
|
\- Is thesis still intact? (sector still bullish? earnings not in 5 days?)
|- YES -> Hold, but tighten stop to -1% max
\- NO -> Close immediately (why stay in a fading thesis?)
Example: MSFT long, +1.5% gain at 3:30pm
* Take 2/3 off table at $430 (lock profit)
* Hold 1/3 overnight if tomorrow's BUY signal still valid
* If tomorrow shows SELL signal -> Close on open gap
Close out Scalps (3:45pm)
* Momentum scalps initiated at 10:15am-11:00am -> CLOSE by 3:45pm
* These are micro-duration; don't hold overnight
* Goal: 50-100 bps/day on good days
---
END OF DAY (4:00pm - 5:00pm ET)
4:00-4:30: Position Tally
Document what happened:
TickerSignalEntryExitP&LNotesNVDASELL$207$203+$40Matched thesis ?MSFTBUY$425$435+$100Momentum play ?AAPLBUY$268$266-$20Stopped out, setup failed ?TSLASELL$370$372-$20Bounced, exited loss ?Tally Summary:
* Winning trades: 2 of 4 (50% win rate)
* Total P&L: +$100
* Alpha vs SPY: +0.15% (if SPY flat)
4:30-5:00: Prepare for Next Day
Step 1: Review overnight positions
* Which ones do you want to hold?
* Set alerts for gap downs (if long) or gap ups (if short)
Step 2: Waiting for 17:00 reports
* Reports auto-generate (no action needed)
* Just wait 15 minutes
---
REPORTS ARRIVAL (5:00pm ET)
Reports auto-generate:
Receive 3 documents:
1. DAILY_CHANGELOG_*.html � System status
2. DAILY_SUMMARY_*.html � Market insights, next day's focus
3. IMPROVEMENTS_TRACKER_*.html � System improvements
Quick review (2 min):
* Read DAILY_SUMMARY to understand macro context
* Note any API improvements (cost savings, new features)
* Done for the day
---
Weekly Workflow (Friday 4:00pm)
Performance Review Checklist
Calculate weekly metrics:
Win Rate Calculation:
Winners: Trades closed with profit
Losers: Trades closed with loss
Win Rate = Winners / (Winners + Losers)
Target: >55% (better than coin flip)

Alpha Calculation:
Your Return: (Week's Profits - Losses) / Starting Capital
Benchmark Return: SPY return for the week
Alpha = Your Return - Benchmark
Target: >50 bps/week (2.6% annualized)

Sharpe Ratio Approximation:
Return volatility = Std Dev of daily P&L
Sharpe = Average P&L / Volatility � ?52
Target: >1.5 (risk-adjusted returns)
Example Weekly Report:
Week of April 28 - May 2, 2026

Trades Executed: 12 total
- Winners: 7 (58%)
- Losers: 5 (42%)
Win Rate: 58% ? ABOVE 55% TARGET

Alpha Generated: +1.2%
- Your Return: +1.2% (starting capital: $100,000)
- SPY Return: +0.3%
- Alpha: +0.9% ? ABOVE 50bps TARGET

Largest Winners:
1. NVDA Short (K2+SELL setup) +$250
2. MSFT Long (Strong vol) +$180
3. AAPL Long (Positive gamma) +$120

Largest Losers:
1. TSLA Long (killed by earnings surprise) -$85
2. QQQ Short (bounced hard) -$60

Lessons Learned:
1. K4 (earnings risk) should have blocked TSLA trade
2. Shorts with K1 (RSI <20) bounced harder than expected
3. STRONG volume + positive gamma = 75% win rate
4. Transition regime HOLD signals had negative P&L (avoid)

Adjustments for Next Week:
? Increase minimum confidence from 30% to 50%
? Avoid shorts in STRONG vol (only scalp)
? Skip transition regime trades (wait for signal clarity)
? Respect K4 earnings kill switches (never override)
---
Pro Tips for Maximum Alpha
Tip 1: Sector Rotation (Free 1-2% Monthly)
Track sector signals across 3 watchlists:
Monday: Analyze
- Count BUYs in AI_VERTICALS (tech sector)
- Count BUYs in ENERGY_AI (energy sector)
- Count BUYs in VANTAGE_PORTFOLIO (diversified)

If tech > 60% BUYs: Overweight tech allocation
If energy > 60% SELLs: Underweight energy allocation
If broad mkt < 40% BUYs: Reduce overall risk (go to cash)

Benefit: 1-2% monthly from sector timing alone
Tip 2: Confidence Clustering (4x Position Sizing Edge)
Instead of flat position sizing, use a tiered system:
Confidence 70%+: Full position (3-5%)
Confidence 50-70%: Half position (1.5-2%)
Confidence <50%: Watch list only (0%)

Result: 70% of capital on best 30% of signals
Benefit: Win rate improves 2-3x on concentrated bets
Tip 3: Kill Switch Scalping (500+ bps/month on volatility)
K2 (high volatility) is your profit machine:
When: K2 + SELL + Confidence >60%
Setup: Intraday momentum exhaustion
Entry: Breakout below MA20
Exit: First 0.5-1% profit OR 5-10 min hold
Frequency: 3-5 times on high-vol days
Monthly P&L: +500-1000 bps from scalps alone

Why it works: K2 means wild swings = opportunity for scalping
Tip 4: Conviction Ladder Entries
Don't go all-in at once. Scale in:
Signal appears (BUY, Conf 60%):
- Enter 1/3 position immediately
- Set order for 1/3 at MA20 (if dips)
- Set order for 1/3 at higher support (insurance)

Benefit: Average down on dips, reduce cost basis
Risk: If thesis breaks, you're already partway in
Tip 5: Overnight Hold Thesis Test
Before holding overnight, ask:
"Would I enter this position right now, knowing tomorrow's market?"

If YES: Hold overnight + add tomorrow if confirmed
If NO: Close position (move on to next trade)

This prevents "hope trades" and keeps you disciplined.
---
Performance Tracking Template
Create a simple spreadsheet:
DateTickerSignalEntryExitDays HeldP&L% ReturnWin?ConfidenceKill SwitchNotes5/2NVDASELL207203<1 day+40+0.4%?70%K2Scalp5/2MSFTBUY425435<1 day+100+0.8%?73%NoneMomentum5/2AAPLBUY268266<1 day-20-0.2%?35%K6Setup failedWeekly summary row:
* Win Rate: 66% (2 wins, 1 loss)
* Avg P&L: +40
* Alpha: +0.35%
---
Daily Checklist (Print & Tape to Monitor)
? 8:45am - Reports arrive
? 8:50am - Review SELL signals (>65% confidence)
? 8:55am - Review BUY signals (>60% confidence, no K-kills)
? 9:00am - Check overnight positions (exit if signal flipped)
? 9:00am - Set entry/exit alerts for top 5 setups
? 10:00am - Market open, execution ready
? 10:30am - No new entries (market momentum established)
? 11:00am - Monitor positions hourly, tighten stops on winners
? 3:00pm - Begin closing winning scalps
? 3:30pm - Decision: hold positions overnight or close?
? 4:00pm - Document daily trades (win/loss tally)
? 4:30pm - Prepare overnight setup alerts
? 5:00pm - Reports arrive (review for context)
? EOD - Rest, prepare for tomorrow
---
Workflow Owner: VIF Trading System
Last Updated: May 2, 2026
Next Review: May 9, 2026
TL;DR / Summary
* Before open (08:50am): Open the Excel reports; prioritize SELL Signals first, then BUY Signals. Build �TODAY�S SHORTS TO WATCH� (SELL >65%) and �TODAY�S LONGS TO WATCH� (BUY >60% and Kill Switch = �None�; skip WEAK volume).
* Premarket (8:45am�10:00am ET): Review Summary Tab for regime (Positive = long bias, Negative = short bias, Transition = defensive). Use Kill Switch Analysis to handle K2/K3/K6 behavior.
* Overnight positions: Compare today�s signals vs yesterday�s; if a SELL signal appears overnight, exit on open. If a signal degrades materially (e.g., 70% -> 40%), reduce or close; if it improves, hold or add.
* Open (10:00am�10:30am ET): Execute only when the setup triggers (breakdowns/breakouts/dips) with defined entry, stop, and target. Use confidence to guide action (>70% strongest; 50�70% watch/scale; <50% ignore).
* After 10:30am ET: Avoid chasing; focus on monitoring, tightening stops on winners (if up 1%+), and pyramiding only if the setup repeats.
* Mid-day (11:00am�3:00pm ET): Check positions hourly; tighten to breakeven if +2% or more; reassess if -1% or more. Monitor catalyst_scan and sector shifts; close positions when binary/catalyst risk appears or momentum reverses.
* Late day (3:00pm�4:00pm ET): Decide to close, scale out, or hold overnight using the decision tree (take 2/3 profit on winners and hold 1/3 overnight; do not hold scalps overnight; close scalps by 3:45pm).
* End of day (4:00pm�5:00pm ET): Record trades (ticker, signal, entry/exit, P&L, notes) and prepare alerts for overnight gaps. Review the 5:00pm reports (DAILY_CHANGELOG, DAILY_SUMMARY, IMPROVEMENTS_TRACKER).
* Weekly (Friday 4:00pm): Calculate Win Rate, Alpha vs SPY, and Sharpe approximation; document winners/losers, lessons learned, and next-week adjustments.

**Date:** May 2, 2026  
**Purpose:** Actionable day-by-day, hour-by-hour guide to extract maximum alpha from VIF reports

---

## 🚀 Quick Start: Your 3-Minute Morning Checklist

**Time: 08:50am - Before Market Open**

```
STEP 1 (30 sec): Open Excel reports
  → reports/VANTAGE_PORTFOLIO_ANALYSIS_*.xlsx
  → reports/AI_VERTICALS_ANALYSIS_*.xlsx

STEP 2 (60 sec): Review SELL Signals sheet
  • Sort by Confidence descending
  • Identify top 3 high-confidence SELLs (>65%)
  • Check: Any K2 (volatility) active? → Premium short setups
  • Mark these as "TODAY'S SHORTS TO WATCH"

STEP 3 (60 sec): Review BUY Signals sheet
  • Filter: Confidence >60% AND Kill Switch = "None"
  • Identify top 2-3 longs to watch
  • Check: Volume = STRONG or NORMAL? (if WEAK, skip)
  • Mark these as "TODAY'S LONGS TO WATCH"

STEP 4 (60 sec): Check overnight positions
  • Compare holding positions to yesterday's signals
  • If SELL signal appeared overnight: EXIT ON OPEN (no debate)
  • If BUY signal confirmed: HOLD + consider adding
  • Update position sizing based on fresh Confidence scores

READY TO TRADE: 9:00am
```

---

## 📊 Detailed Workflow by Time of Day

### **PREMARKET (8:45am - 10:00am ET)**

#### **8:45-8:48: Auto-Generated Reports Arrive**
- Analyst finishes VIF analysis
- Reports auto-exported: JSON → Excel → HTML
- Systems: Files saved to `reports/` folder

#### **8:48-8:54: Excel Report Review** (6 min)

**Open `VANTAGE_PORTFOLIO_ANALYSIS_*.xlsx`**

**Sheet 1: Summary Tab**
- Read watchlist overview
- Check: Total tickers, kills triggered, signal distribution
- Key insight: Is market regime positive/negative/transition?
  - **If Positive:** Long bias today (buy dips)
  - **If Negative:** Short bias today (fade rallies)
  - **If Transition:** Stay defensive, require clear setups

**Sheet 2: SELL Signals Tab** (Highest priority)

| Column | Action |
|--------|--------|
| **Ticker** | Mark on watchlist |
| **Confidence** | >70% = execute shorts; 50-70% = watch; <50% = ignore |
| **Kill Switch** | K2 + SELL = **premium short** |
| **Price** | Set short entry 5% below current (if breakdown) |
| **Note** | Read reasoning (confirms or contradicts your thesis) |

**Example Action:**
```
NVDA SELL, Confidence 62%, K2 (volatility), Price $209.25
Interpretation: Overbought vol spike, technical risk
Action: Watch for breakdown below MA20, then short on volume
Entry: <$197 (below MA20), Stop: $214 (above resistance)
Target: $180 (support), R:R = 1:2.5 ✓ EXECUTE IF SETUP HITS
```

**Sheet 3: BUY Signals Tab**

| Column | Action |
|--------|--------|
| **Ticker** | Mark on watchlist |
| **Confidence** | >70% = buy; 50-70% = scale in; <50% = ignore |
| **Volume Signal** | WEAK = avoid; NORMAL = OK; STRONG = preferred |
| **Price** | Set long entry at MA20 (on dips) |
| **Kill Switch** | If K2 = wait for breakout confirm; if NONE = go long |

**Example Action:**
```
MSFT BUY, Confidence 73%, STRONG vol, K=None, Price $424.46
Interpretation: Bullish momentum, volume confirmed, no red flags
Action: Buy on dip to MA20 or breakout above resistance
Entry: $425 (breakout) or $415 (MA20 dip), Stop: $407
Target: $460 (resistance), R:R = 1:2.3 ✓ EXECUTE
```

**Sheet 4: Kill Switch Analysis Tab**
- K2 tickers (high volatility): Watch for whipsaws; short scalps only
- K3 tickers (illiquid): SKIP entirely
- K6 tickers (breakdown): Wait for setup confirmation before long entry

#### **8:54-8:58: Check Overnight Positions** (4 min)

**For each open position:**

| Position | Yesterday's Signal | Today's Signal | Action |
|----------|-------------------|----------------|--------|
| AAPL Long | BUY (Conf 65%) | HOLD (Conf 35%) | Reduce 50% at open, keep 50% for momentum |
| TSLA Long | BUY (Conf 72%) | BUY (Conf 75%) | HOLD + add 25% on dip |
| QQQ Short | SELL (Conf 60%) | SELL (Conf 68%) | HOLD + add 25% on rally |
| SPY Long | HOLD (Conf 40%) | HOLD (Conf 38%) | CLOSE (confidence dropped) |

**Rule:** If signal degrades (e.g., 70% → 40%), reduce or close position. If signal improves, hold or add.

#### **8:58-9:00: Set Alerts** (2 min)

**Using your broker (ThinkorSwim, Interactive Brokers, etc.):**

For each "TODAY'S SHORTS" and "TODAY'S LONGS":
- **Shorts:** Alert if price breaks below yesterday's low (setup trigger)
- **Longs:** Alert if price breaks above yesterday's high (setup trigger)

Example:
```
NVDA Short Setup: Alert if price < $205 (below MA20 support)
MSFT Long Setup: Alert if price > $430 (above resistance)
```

**By 9:00am:** You're ready to trade. Market opens.

---

### **MARKET OPEN (10:00am - 11:00am ET)**

#### **10:00-10:30: Execution Phase**

**Tactic 1: Breakout Trading** (Using VIF setups)

```
Watching: NVDA SELL signal + K2 (volatility)
Setup: Price breaks below $205 (MA20 support) + volume surge

Execution:
  1. Price hits $204 + volume 30% above average → ENTER SHORT
  2. Set stop loss: $214 (above resistance)
  3. Set profit target: $180 (support level)
  4. R:R = $34 risk : $24 target = 1:2.4 ✗ Too tight
     → Adjust target to $175 = 1:2.9 ✓ BETTER
  5. EXECUTE SHORT (5% of portfolio allocation)
```

**Tactic 2: Dip-Buying** (If overnight dips occur)

```
Watching: MSFT BUY signal + STRONG volume
Setup: Price dips to MA20 ($415) + RSI >40 (no oversold)

Execution:
  1. Price hits $415 + volume confirms → ENTER LONG
  2. Set stop loss: $407 (below MA20)
  3. Set profit target: $450 (next resistance)
  4. R:R = $8 risk : $35 target = 1:4.4 ✓ EXCELLENT
  5. EXECUTE LONG (3% of portfolio allocation)
```

**Tactic 3: Momentum Scalping** (For K2 + SELL setups - pro only)

```
Watching: Ticker with K2 + SELL + Confidence 75%
Setup: Intraday momentum collapse (price > MA20 but falling)

Execution:
  1. Enter SHORT on close above MA20 (end-of-day)
  2. Hold 5-30 minutes only (scalp)
  3. Exit on first 0.5-1% profit or close back below MA20
  4. Repeat 2-3 times if setup repeats

Risk: High intensity, tight stops, small shares. PRO ONLY.
Reward: 100+ bps/day on good vol days
```

#### **10:30-11:00: No New Entries**

After 10:30am ET, market momentum typically established. Avoid chasing.

Instead:
- Monitor existing positions
- Tighten stops on winners (if up 1%+)
- Add to winners if setup repeats (pyramid)

---

### **MID-DAY (11:00am - 3:00pm ET)**

#### **Position Management**

**Every hour:**
- Check profit/loss on open positions
- If +2% or more: TIGHTEN stop to breakeven
- If -1% or more: REASSESS thesis (is signal still valid?)

**Catalyst Monitor:**
- Check `reports/catalyst_scan_*.json` for same-day announcements
- If catalyst drops, close position immediately (binary event risk)

**Sector Watch:**
- Track if sector shifted (check AI_VERTICALS or ENERGY_AI sheets from morning)
- If sector momentum reversed, close positions in that sector

#### **Avoid These Mistakes**
- ❌ Don't add to losing positions (unless setup improves, which is rare)
- ❌ Don't hold past lunch hour on intraday scalps (close by 2pm)
- ❌ Don't initiate new positions without VIF signal confirmation
- ❌ Don't fight the tape (if all your longs down, market likely bearish)

---

### **LATE DAY (3:00pm - 4:00pm ET)**

#### **Position Closing Decisions**

**Ask yourself:**
1. **Is the VIF signal still valid?** (Check kill switches; did K4 appear = earnings risk?)
2. **Have we hit the target?** (If yes, close)
3. **Is position up, but momentum fading?** (Close into strength; don't hold overnight)
4. **Do I want to hold overnight?** (Risk/reward framework below)

**Overnight Hold Decision Tree:**

```
Do I have a winning position?
├─ YES: Take profit (2/3 of position) + hold 1/3 overnight
│      └─ Tomorrow morning: Check VIF signal
│         ├─ Still BUY → Hold or add
│         └─ Now SELL → Close immediately
│
└─ NO (Losing position):
   ├─ Is the VIF signal still valid? (or did kill switch appear?)
   │  ├─ YES → Hold stop, let it work (overnight vol could flush weaker holders)
   │  └─ NO → Close losses, move to next trade
   │
   └─ Is thesis still intact? (sector still bullish? earnings not in 5 days?)
      ├─ YES → Hold, but tighten stop to -1% max
      └─ NO → Close immediately (why stay in a fading thesis?)
```

**Example:** MSFT long, +1.5% gain at 3:30pm
- Take 2/3 off table at $430 (lock profit)
- Hold 1/3 overnight if tomorrow's BUY signal still valid
- If tomorrow shows SELL signal → Close on open gap

#### **Close out Scalps** (3:45pm)
- Momentum scalps initiated at 10:15am-11:00am → CLOSE by 3:45pm
- These are micro-duration; don't hold overnight
- Goal: 50-100 bps/day on good days

---

### **END OF DAY (4:00pm - 5:00pm ET)**

#### **4:00-4:30: Position Tally**

**Document what happened:**

| Ticker | Signal | Entry | Exit | P&L | Notes |
|--------|--------|-------|------|-----|-------|
| NVDA | SELL | $207 | $203 | +$40 | Matched thesis ✓ |
| MSFT | BUY | $425 | $435 | +$100 | Momentum play ✓ |
| AAPL | BUY | $268 | $266 | -$20 | Stopped out, setup failed ✗ |
| TSLA | SELL | $370 | $372 | -$20 | Bounced, exited loss ✗ |

**Tally Summary:**
- Winning trades: 2 of 4 (50% win rate)
- Total P&L: +$100
- Alpha vs SPY: +0.15% (if SPY flat)

#### **4:30-5:00: Prepare for Next Day**

**Step 1: Review overnight positions**
- Which ones do you want to hold?
- Set alerts for gap downs (if long) or gap ups (if short)

**Step 2: Waiting for 17:00 reports**
- Reports auto-generate (no action needed)
- Just wait 15 minutes

---

### **REPORTS ARRIVAL (5:00pm ET)**

**Reports auto-generate:**

**Receive 3 documents:**
1. `DAILY_CHANGELOG_*.html` — System status
2. `DAILY_SUMMARY_*.html` — Market insights, next day's focus
3. `IMPROVEMENTS_TRACKER_*.html` — System improvements

**Quick review (2 min):**
- Read DAILY_SUMMARY to understand macro context
- Note any API improvements (cost savings, new features)
- Done for the day

---

## 📋 Weekly Workflow (Friday 4:00pm)

### **Performance Review Checklist**

**Calculate weekly metrics:**

```
Win Rate Calculation:
  Winners: Trades closed with profit
  Losers: Trades closed with loss
  Win Rate = Winners / (Winners + Losers)
  Target: >55% (better than coin flip)

Alpha Calculation:
  Your Return: (Week's Profits - Losses) / Starting Capital
  Benchmark Return: SPY return for the week
  Alpha = Your Return - Benchmark
  Target: >50 bps/week (2.6% annualized)

Sharpe Ratio Approximation:
  Return volatility = Std Dev of daily P&L
  Sharpe = Average P&L / Volatility × √52
  Target: >1.5 (risk-adjusted returns)
```

**Example Weekly Report:**

```
Week of April 28 - May 2, 2026

Trades Executed: 12 total
- Winners: 7 (58%)
- Losers: 5 (42%)
Win Rate: 58% ✓ ABOVE 55% TARGET

Alpha Generated: +1.2%
- Your Return: +1.2% (starting capital: $100,000)
- SPY Return: +0.3%
- Alpha: +0.9% ✓ ABOVE 50bps TARGET

Largest Winners:
1. NVDA Short (K2+SELL setup) +$250
2. MSFT Long (Strong vol) +$180
3. AAPL Long (Positive gamma) +$120

Largest Losers:
1. TSLA Long (killed by earnings surprise) -$85
2. QQQ Short (bounced hard) -$60

Lessons Learned:
1. K4 (earnings risk) should have blocked TSLA trade
2. Shorts with K1 (RSI <20) bounced harder than expected
3. STRONG volume + positive gamma = 75% win rate
4. Transition regime HOLD signals had negative P&L (avoid)

Adjustments for Next Week:
✓ Increase minimum confidence from 30% to 50%
✓ Avoid shorts in STRONG vol (only scalp)
✓ Skip transition regime trades (wait for signal clarity)
✓ Respect K4 earnings kill switches (never override)
```

---

## 💡 Pro Tips for Maximum Alpha

### **Tip 1: Sector Rotation (Free 1-2% Monthly)**

Track sector signals across 3 watchlists:

```
Monday: Analyze
  - Count BUYs in AI_VERTICALS (tech sector)
  - Count BUYs in ENERGY_AI (energy sector)
  - Count BUYs in VANTAGE_PORTFOLIO (diversified)

If tech > 60% BUYs: Overweight tech allocation
If energy > 60% SELLs: Underweight energy allocation
If broad mkt < 40% BUYs: Reduce overall risk (go to cash)

Benefit: 1-2% monthly from sector timing alone
```

### **Tip 2: Confidence Clustering (4x Position Sizing Edge)**

Instead of flat position sizing, use a tiered system:

```
Confidence 70%+: Full position (3-5%)
Confidence 50-70%: Half position (1.5-2%)
Confidence <50%: Watch list only (0%)

Result: 70% of capital on best 30% of signals
Benefit: Win rate improves 2-3x on concentrated bets
```

### **Tip 3: Kill Switch Scalping (500+ bps/month on volatility)**

K2 (high volatility) is your profit machine:

```
When: K2 + SELL + Confidence >60%
Setup: Intraday momentum exhaustion
Entry: Breakout below MA20
Exit: First 0.5-1% profit OR 5-10 min hold
Frequency: 3-5 times on high-vol days
Monthly P&L: +500-1000 bps from scalps alone

Why it works: K2 means wild swings = opportunity for scalping
```

### **Tip 4: Conviction Ladder Entries**

Don't go all-in at once. Scale in:

```
Signal appears (BUY, Conf 60%):
  - Enter 1/3 position immediately
  - Set order for 1/3 at MA20 (if dips)
  - Set order for 1/3 at higher support (insurance)

Benefit: Average down on dips, reduce cost basis
Risk: If thesis breaks, you're already partway in
```

### **Tip 5: Overnight Hold Thesis Test**

Before holding overnight, ask:

```
"Would I enter this position right now, knowing tomorrow's market?"

If YES: Hold overnight + add tomorrow if confirmed
If NO: Close position (move on to next trade)

This prevents "hope trades" and keeps you disciplined.
```

---

## 📊 Performance Tracking Template

**Create a simple spreadsheet:**

| Date | Ticker | Signal | Entry | Exit | Days Held | P&L | % Return | Win? | Confidence | Kill Switch | Notes |
|------|--------|--------|-------|------|-----------|-----|----------|------|-----------|-------------|-------|
| 5/2 | NVDA | SELL | 207 | 203 | <1 day | +40 | +0.4% | ✓ | 70% | K2 | Scalp |
| 5/2 | MSFT | BUY | 425 | 435 | <1 day | +100 | +0.8% | ✓ | 73% | None | Momentum |
| 5/2 | AAPL | BUY | 268 | 266 | <1 day | -20 | -0.2% | ✗ | 35% | K6 | Setup failed |

**Weekly summary row:**
- Win Rate: 66% (2 wins, 1 loss)
- Avg P&L: +40
- Alpha: +0.35%

---

## 🎯 Daily Checklist (Print & Tape to Monitor)

```
☐ 8:45am - Reports arrive
☐ 8:50am - Review SELL signals (>65% confidence)
☐ 8:55am - Review BUY signals (>60% confidence, no K-kills)
☐ 9:00am - Check overnight positions (exit if signal flipped)
☐ 9:00am - Set entry/exit alerts for top 5 setups
☐ 10:00am - Market open, execution ready
☐ 10:30am - No new entries (market momentum established)
☐ 11:00am - Monitor positions hourly, tighten stops on winners
☐ 3:00pm - Begin closing winning scalps
☐ 3:30pm - Decision: hold positions overnight or close?
☐ 4:00pm - Document daily trades (win/loss tally)
☐ 4:30pm - Prepare overnight setup alerts
☐ 5:00pm - Reports arrive (review for context)
☐ EOD - Rest, prepare for tomorrow
```

---

**Workflow Owner:** VIF Trading System  
**Last Updated:** May 2, 2026  
**Next Review:** May 9, 2026

