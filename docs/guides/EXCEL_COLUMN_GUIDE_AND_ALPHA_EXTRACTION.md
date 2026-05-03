# Excel Report Column Guide & Alpha Extraction Strategy

**Document Version:** 1.0  
**Date:** May 2, 2026  
**Purpose:** Master reference for interpreting VIF Excel exports and extracting edge from the data

---

## 📊 Excel Spreadsheet Column Definitions

### **All Signals Sheet** (Main Data Table)

Each row represents one ticker analyzed. Columns are:

#### 1. **Ticker** 📍
- **What it is:** Stock symbol (e.g., NVDA, TSLA, AAPL)
- **Why it matters:** Identifies which security the signal applies to
- **Alpha insight:** Use with sector/industry knowledge. Concentrated exposure in one sector signals concentration risk

#### 2. **Signal** 🎯 **[KEY - Highest Priority]**
- **What it is:** Trading recommendation: **BUY | SELL | HOLD**
- **What each means:**
  - **BUY:** Positive gamma (bullish momentum) + strong volume + no kill switches
    - *Alpha trigger:* Position sizing: start at 2-3% allocation, scale up on confirmation
  - **SELL:** Negative gamma (bearish momentum) + kill switch active + technical breakdown
    - *Alpha trigger:* Short candidates or avoid longs; high-conviction shorts at 78%+ confidence
  - **HOLD:** Transition regime (neutral momentum) or mixed signals
    - *Alpha trigger:* Wait for clarity; don't force trades; reduce position bias
- **How to leverage:** Filter by Signal = "BUY" to find entry candidates; by "SELL" for exits or shorts

#### 3. **Confidence** 📈 **[KEY - Position Sizing]**
- **What it is:** 0-100 scale. Higher = more conviction behind the signal
- **Ranges:**
  - **70-100%:** High conviction (SELL signals typically here)
  - **50-70%:** Moderate conviction (mixed signals or positive momentum)
  - **30-50%:** Low conviction (transition regime, RSI=50, no edge)
  - **<30%:** Avoid (insufficient signal quality)
- **How to leverage ALPHA:**
  - **Confidence > 70%:** Full position size (3-5% allocation)
  - **Confidence 50-70%:** Half position (1.5-2.5%)
  - **Confidence < 50%:** No position (watch list only)
  - **Pro tip:** Combine confidence with kill switches (next column) for risk-adjusted sizing

#### 4. **Gamma Regime** 🔄 **[KEY - Market Context]**
- **What it is:** Market momentum state
- **Three regimes:**
  - **Positive:** RSI > 65 AND price > MA20
    - *Means:* Bullish bias, buy pressure dominant
    - *Alpha edge:* Look for pullbacks to MA20; long continuation trades, short weakness
  - **Negative:** RSI < 35 AND price < MA20
    - *Means:* Bearish bias, sell pressure dominant
    - *Alpha edge:* Avoid longs; short strength; look for capitulation bottoms
  - **Transition:** All other combinations
    - *Means:* No directional bias, consolidation, elevated uncertainty
    - *Alpha edge:* Wait for regime confirmation; don't force trades here; reduce risk
- **How to leverage:**
  - **Positive regime tickers:** 60% allocation to long bias
  - **Negative regime tickers:** 60% allocation to short bias / avoid longs
  - **Transition regime tickers:** 40% allocation / watch for breakout

#### 5. **Volume Signal** 📊 **[KEY - Confirmation]**
- **What it is:** Current volume vs 20-day average
- **Three levels:**
  - **STRONG:** Current vol > 1.5x average
    - *Means:* Conviction behind price move; participants backing trade
    - *Alpha edge:* Trust BUY signals more; shorts less likely to reverse
  - **NORMAL:** 0.8x to 1.5x average
    - *Means:* Average participation; inconclusive
    - *Alpha edge:* Require additional confirmation (technical setup, catalyst)
  - **WEAK:** < 0.8x average
    - *Means:* Lack of participation; move suspect, likely to reverse
    - *Alpha edge:* Avoid BUYs with weak volume; high-conviction SELL edge; wait for volume confirmation
- **How to leverage:**
  - **Never go long with WEAK volume** (reversal risk too high)
  - **STRONG volume on SELL signals** = highest conviction shorts
  - **STRONG volume on positive gamma** = momentum continuation play

#### 6. **Price** 💰
- **What it is:** Current market price at time of analysis
- **Why it matters:** Entry/exit reference point
- **Alpha insight:** 
  - Combine with MA20 (next column) for trend positioning
  - Track price relative to support/resistance levels
  - Use for position sizing by notional exposure (higher-priced stocks → smaller share count)

#### 7. **RSI** 📉 **[KEY - Momentum]**
- **What it is:** Relative Strength Index (0-100)
- **Interpretation:**
  - **RSI > 65:** Overbought, momentum strong but reversal risk
  - **RSI 50-65:** Moderately bullish, watch for pullback
  - **RSI 50:** Neutral, no directional edge
  - **RSI 35-50:** Moderately bearish, watch for bounce
  - **RSI < 35:** Oversold, momentum weak but bounce risk
- **How to leverage:**
  - **BUY signals with RSI 50-65:** Quality trade (momentum not yet overbought)
  - **SELL signals with RSI < 50:** Quality short (weakness not yet extreme)
  - **RSI > 75 on HOLD:** Overbought risk—consider taking profits
  - **RSI < 25 on HOLD:** Oversold—look for bounce confirmation

#### 8. **Kill Switch** ⚠️ **[KEY - Risk Override]**
- **What it is:** Safety override that negates BUY signals
- **Six kill switches:**
  - **K1:** RSI > 80 or RSI < 20 (extreme, reversal imminent)
  - **K2:** 5-day price range > 12% (extreme volatility, whipsaw risk)
  - **K3:** Current volume < 500k (illiquid, execution risk)
  - **K4:** Earnings within 5 days (binary event risk)
  - **K6:** Price < MA20 AND volume WEAK (technical breakdown, no confirmation)
  - **Null/None:** No kill switches active (safer signal)
- **Alpha leverage rules:**
  - **Never initiate BUY if K1, K2, K3, K4 active** (reversal/execution risk too high)
  - **K6 + Positive Gamma = Watch List** (potential breakout after consolidation, but wait for confirmation)
  - **K2 + SELL Signal = Highest conviction short** (extreme vol + bearish bias = momentum exhaustion)
  - **Sort by Kill Switch = None** to see safest signals
- **Pro tip:** Use kill switches as trade *scalp filters*—avoid multi-day holds, use only for quick entries/exits

#### 9. **Note** 📝
- **What it is:** Qualitative summary of signal reasoning
- **Examples:**
  - "K2 active; 5d range ~34%; strong vol but too risky" → Avoid BUY despite positive signals
  - "Below MA20, weak vol triggers K6" → Wait for price close above MA20 + volume surge
  - "Price above MA20 but RSI neutral; transition only" → Hold, don't add
- **How to leverage:** Quick qualitative check; confirms quantitative decision

---

## 🎯 Alpha Extraction Framework

### **High-Level Alpha Extraction Strategy**

Alpha = Return Above Benchmark. In this context:
- **Benchmark:** Buy-and-hold SPY (0.5-1% monthly return)
- **VIF Target:** 2-5% monthly return (200-500 bps alpha)
- **Method:** Signal-based position sizing + risk management

---

### **1. Signal Strength Scoring** (Combine columns for edge)

**Calculate a composite score:**

```
Signal Score = 
  (Confidence ÷ 100) × 40pts 
  + (Volume STRONG=1, NORMAL=0.5, WEAK=0) × 30pts 
  + (Gamma POSITIVE=1, TRANSITION=0.5, NEGATIVE=-0.5) × 20pts 
  + (Kill Switch NONE=1, else=0) × 10pts

Score Range: 0-100
Recommendation:
  80+: Highest conviction (FULL position, 3-5%)
  60-80: High conviction (2/3 position, 2-3%)
  40-60: Moderate conviction (1/2 position, 1-2%)
  <40: Low conviction (watch list, 0%)
```

**Example:**
- NVDA: Confidence 38%, STRONG vol, Transition gamma, K6 kill
- Score = (38/100)×40 + (1)×30 + (0.5)×20 + (0)×10 = 15.2 + 30 + 10 + 0 = 55.2
- Action: Moderate conviction → 1.5% position / watch list

---

### **2. Sector Rotation Edge** (Use multiple watchlists)

**VIF analyzes 3 watchlists:**
1. Vantage Portfolio (diversified)
2. AI Verticals (tech concentration)
3. Energy + AI (sector play)

**Alpha extraction:**
- If **AI Verticals** has more BUYs (>30% of portfolio) → Overweight tech allocation
- If **Energy + AI** has more SELLs (>50%) → Reduce energy exposure
- If **Vantage Portfolio** shift to HOLD → Reduce overall risk (go to cash or bonds)

**Pro tip:** Track sector signals week-by-week in a separate sheet. Momentum shifts 1-2 weeks before broad reversals.

---

### **3. Confidence Clustering** (Risk-Adjusted Position Sizing)

**Group by confidence bands:**

| Confidence Range | Action | Position Size | Risk/Reward |
|------------------|--------|---------------|-------------|
| 70-100% | **EXECUTE** | 3-5% | 1:3 (risk $100 to win $300) |
| 50-70% | **SCALE IN** | 1.5-2.5% | 1:2 |
| 40-50% | **WATCH LIST** | 0% | Monitor for confirmation |
| <40% | **IGNORE** | 0% | Too much noise |

**Alpha edge:** Concentrate capital on highest-conviction trades. Let low-conviction trades be homework for next week.

---

### **4. Kill Switch Risk Ladder** (When to deviate)

| Kill Switch | Severity | Action |
|-------------|----------|--------|
| **None** | Safe | Take full signal conviction |
| **K6 (Breakdown)** | Medium | Wait for breakdown confirmation (price close > MA20) |
| **K2 (Volatility)** | High | Short scalps only (5-min holds); avoid multi-day |
| **K1 (RSI Extreme)** | High | Avoid BUYs; scalp reversals only |
| **K3 (Illiquid)** | High | Skip entirely (execution risk > alpha potential) |

**Pro tip:** K2 + SELL = rare high-conviction short. This is your premium short setup.

---

## 📋 Optimized Daily Workflow for Alpha Extraction

### **Morning (Before Market Open - 8:45am)**

**Step 1: Load Yesterday's Sheets** (2 min)
- Open `VANTAGE_PORTFOLIO_ANALYSIS_*.xlsx`
- Open `AI_VERTICALS_ANALYSIS_*.xlsx`
- (Optional) Open `ENERGY_AI_ANALYSIS_*.xlsx`

**Step 2: Quick Scan (5 min)**
- Go to "SELL Signals" sheet
- Sort by Confidence (descending)
- **Top 3 SELLs = day's shorts** (focus here first)
- Any K2 + SELL = **premium setup**, take it

**Step 3: BUY Screening (3 min)**
- Go to "All Signals" sheet
- Filter: Signal = "BUY" AND Confidence > 60% AND Kill Switch = ""
- **These are the longs to watch**

**Step 4: Position Check (2 min)**
- If holding overnight positions: Check vs. yesterday's signals
- If SELL signal appeared on overnight hold: **exit on open** (capital preservation)
- If gamma flipped from Negative → Positive: **add to existing long**

**Total Time: 12 minutes**

---

### **Intraday (Throughout Day)**

**Momentum Trader (Fast scalps):**
- Monitor SELL signals with K2 active (extreme volatility = short scalp opportunities)
- Entry on breakdown below MA20 + volume surge
- Exit on first 30-min close above MA20 or 5-min profit target

**Position Trader (Hold 2-5 days):**
- Focus on Confidence 70%+ signals (ignore <60%)
- Enter on 5-min setup confirmation
- Hold through kill switch alerts (unless K1 triggers, then exit)
- Exit on opposite signal (SELL appears on HOLD) or when Confidence drops

---

### **End of Day (5:00pm)**

**Step 1: Position Tally** (1 min)
- Which positions matched VIF signals? (log wins)
- Which positions went against VIF? (log losses)
- This trains your intuition

**Step 2: Tomorrow's Plan** (2 min)
- Auto-generated sheets arrive at 5:00pm
- Skim the new "SELL Signals" sheet
- Flag any high-conviction shorts for tomorrow morning

**Total Time: 3 minutes**

---

## 🎯 Weekly Meta-Analysis (Fridays 4:00pm)

**Track system performance:**

| Metric | Target | Action |
|--------|--------|--------|
| **Win Rate** (signals correct) | >55% | If <50%: adjust confidence threshold upward |
| **Alpha Generated** | >50 bps/week | If <25 bps: reduce position sizes, increase selectivity |
| **Sector Concentration** | <40% single sector | If >50% in one sector: rebalance or reduce |
| **Avg Holding Period** | 2-5 days | If >7 days: you're holding losers too long |

---

## 🔑 Key Takeaways for Alpha Extraction

1. **Signal Quality > Signal Quantity**
   - Ignore <40% confidence signals entirely
   - Concentrate 80% of capital on 60%+ confidence trades
   - *Benefit:* Reduce noise, increase hit rate

2. **Volume + Gamma + Confidence = Edge**
   - Strong volume on positive gamma = momentum continuation (buy dips)
   - Weak volume on negative gamma = oversold shorts (cover risk)
   - *Benefit:* Compound multiple factors for higher probability

3. **Kill Switches are your Friend**
   - Use them as *trade filters*, not deal-breakers
   - K2 + SELL = rare, high-conviction short setup
   - K6 + BUY = wait for breakdown confirmation
   - *Benefit:* Reduce reversal risk, increase win rate

4. **Position Sizing > Trade Frequency**
   - Full position only on 70%+ confidence with no kills
   - Half positions on 50-70% confidence
   - Nothing on <50%
   - *Benefit:* Maximize alpha on best setups, minimize losses on weak ones

5. **Sector Rotation is Free Alpha**
   - Track sector concentration across 3 watchlists
   - Overweight sectors with 70%+ BUYs
   - Underweight sectors with 50%+ SELLs
   - *Benefit:* 1-2% additional monthly return from tactical allocation

---

## 📊 Sample Alpha Extraction Checklist

**Before every trade:**

- [ ] Signal = BUY or SELL? (Skip HOLD)
- [ ] Confidence ≥ 50%? (If <50%, skip)
- [ ] Kill Switch = None or K6 only? (If K1/K2/K3, skip or scalp only)
- [ ] Volume = STRONG or NORMAL? (If WEAK, avoid longs; SELL only)
- [ ] Gamma = Positive or Transition? (If Negative, short bias only)
- [ ] Position Size = (Confidence ÷ 60%) × 2%? (Scale to conviction)
- [ ] Entry Price = Near MA20 (if long) or Below MA20 (if short)
- [ ] Exit Plan = Opposite signal or 5-day hold max?

**If all checkboxes ✓: EXECUTE**

---

**Document Owner:** VIF Trading System  
**Last Updated:** May 2, 2026  
**Next Review:** May 9, 2026
