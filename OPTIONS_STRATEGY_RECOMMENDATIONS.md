# OPTIONS STRATEGY FOR $335 CAPITAL
**Capital Available:** $335  
**Strategy Type:** Single-leg options (no spreads allowed)  
**Time Horizon:** 2-4 weeks (aligns with swing trade thesis)  
**Analysis Date:** 2026-04-28

---

## BEST OPTIONS STRATEGY: DLR LONG CALL

### **Primary Recommendation**

**Ticker:** DLR (Digital Realty Trust)  
**Strategy:** LONG CALL (Bullish)  
**Status:** ✓ OPTIMAL FOR YOUR CAPITAL & THESIS

---

## EXECUTION DETAILS

### **Entry Setup**
```
Underlying: DLR
Current Price: $193.84
Your Entry Target: $190.66 (MA20 support)
Target Price: $208.14

CALL OPTION:
Contract Strike:        $200.00
Expiration Date:        2026-05-22 (24 days out)
Call Premium:           $3.17 per share
Total Cost (1 contract): $317.50
Remaining Capital:      $17.50 (keep as buffer)
```

### **Position Metrics**

| Metric | Value |
|--------|-------|
| **Max Loss (if DLR <$200 at expiry)** | -$317.50 (100% of premium) |
| **Break-Even Price** | $203.17 ($200 strike + $3.17 premium) |
| **Max Profit (if DLR >$208 at expiry)** | +$496.50 |
| **Risk/Reward Ratio** | 1.56x (good for 24-day trade) |
| **Profit If Target Hit** | +$496.50 (+148% return) |

---

## WHY DLR LONG CALL?

### **1. Strike Price Rationale**
- **$200 strike** = near-the-money (NTM)
- Current price $193.84 → strike $200 = 3.2% OTM (out-of-money)
- **Why OTM:** Less expensive premium ($3.17 vs $5+ for ATM), gives room for pullback

### **2. Expiration Selection**
- **May 22, 2026** = 24 days (perfect 2-4 week swing trade window)
- **Why 24 days:** Enough time for thesis to play out, avoids theta decay cliff
- **Theta impact:** ~25-35% premium decay by expiry (acceptable loss)

### **3. DLR Thesis (Why This Works)**
- **Current:** $193.84 (trading near MA20 support at $190.66)
- **Entry Zone:** Buy call when DLR hits $190.66 (your swing trade entry)
- **Target:** $208.14 (upside target from swing trade analysis)
- **Setup:** Pullback to MA20 + bullish structure = 40%+ historical win rate
- **Sector:** Data center infrastructure (AI capex beneficiary)

### **4. Capital Efficiency**
- **Cost:** $317.50 (uses 95% of capital, leaves $17.50 buffer)
- **Leverage:** 1 contract = exposure to 100 shares = $19,384 notional value
- **Leverage Ratio:** 61:1 (significant leverage with defined risk)

---

## TRADE EXECUTION PLAN

### **Step 1: Entry Trigger (WAIT for this)**
```
Watch DLR on TradingView
Entry Zone: $189.50 - $191.50 (around MA20 support at $190.66)

When DLR drops to $190.66:
→ BUY 1 $200 call contract
→ Cost: $317.50
→ Entry time: Within 5-10 minutes of price touch
```

### **Step 2: Order Placement**
```
Order Type: Limit Buy
Call Strike: $200.00
Expiration: May 22, 2026
Quantity: 1 contract
Limit Price: $3.17 (or lower if possible - aim for $3.00-$3.15)
Duration: Day order

Use Interactive Brokers, TD Ameritrade, or E*TRADE
(Must support options trading)
```

### **Step 3: Management (Hold Period)**
```
If DLR breaks above $200 (strike):
→ Your call goes in-the-money (ITM)
→ Starts gaining intrinsic value
→ Risk becoming assignment (convert to 100 DLR shares)

To avoid assignment (if you don't want shares):
→ Close the call 2-3 days before expiry
→ Lock in profit (even if $200 not hit)
```

### **Step 4: Exit Triggers**

#### **Target (Profit-Taking)**
```
IF DLR reaches $208.14 (your swing trade target):
→ SELL the call immediately
→ Profit: ~$496.50 (148% return)
→ Time: ~10-15 trading days
→ Action: Limit sell order at $8.14+ premium
```

#### **Stop Loss (Downside Protection)**
```
IF DLR closes BELOW $190.66 (entry zone support):
→ SELL the call immediately
→ Limit loss: Keep it under $317.50
→ Exit strategy: Take 50% loss if this breaks

Example: If DLR drops to $188:
→ Call value drops to ~$1.50-$2.00
→ Sell and cut losses to ~$150-$170 (vs $317 max)
```

#### **Time Decay (If Stalled)**
```
IF DLR stalls at $195-$198 (near breakeven):
→ Monitor closely with 5 days left to expiry
→ If no movement likely: Close call at 70% of cost
→ Accept $95 loss, preserve capital for next setup
→ Reason: Theta decay accelerates final week
```

---

## PROFIT/LOSS SCENARIOS

### **Scenario 1: TARGET HIT (DLR = $208.14)**
```
Entry:              DLR $190.66 (via call at $200 strike)
Exit:               DLR $208.14 (swing target achieved)
Call Value at Exit: ~$8.14 premium + intrinsic = $8.14+ 
Profit:             $8.14 - $3.17 = $4.97 per share
Total Profit:       $4.97 × 100 = +$497 (148% return)
Capital Deployed:   $317.50
Final Account:      $335 - $317.50 + $497 = $514.50
Time Frame:         ~15 trading days
```

### **Scenario 2: STOPPED OUT (DLR = $188 at breakeven)**
```
Entry:              DLR $190.66
Exit:               DLR $188 (breaks below support)
Call Value at Exit: ~$0.80 (intrinsic + time value)
Loss:               $3.17 - $0.80 = $2.37 per share
Total Loss:         $2.37 × 100 = -$237
Capital Deployed:   $317.50
Final Account:      $335 - $237 = $98 remaining
Time Frame:         ~5 trading days
(Cut losses early to preserve capital)
```

### **Scenario 3: THETA DECAY (DLR = $198, expires worthless)**
```
Entry:              DLR $190.66
Exit:               DLR $198 (near resistance, 5 days to expiry)
Call Value:         ~$0.50 (mostly time value gone)
Loss:               $3.17 - $0.50 = $2.67
Total Loss:         $2.67 × 100 = -$267
Capital Deployed:   $317.50
Final Account:      $335 - $267 = $68 remaining
Time Frame:         ~19 days
(Close before final week to avoid full decay)
```

### **Scenario 4: MODEST GAIN (DLR = $204)**
```
Entry:              DLR $190.66
Exit:               DLR $204 (between entry and target)
Call Value:         ~$4.00 ($4 intrinsic + $0.50 time)
Profit:             $4.00 - $3.17 = $0.83 per share
Total Profit:       $0.83 × 100 = +$83 (26% return)
Capital Deployed:   $317.50
Final Account:      $335 + $83 = $418
Time Frame:         ~12 trading days
(Take profits when you can - don't get greedy)
```

---

## ALTERNATIVE: UPS LONG CALL (Secondary Option)

If DLR doesn't trigger entry, UPS is your backup:

```
Ticker:             UPS (United Parcel Service)
Current Price:      $104.75
Entry Target:       $101.96 (MA20 support)
Target Price:       $108.52

CALL OPTION:
Strike:             $104.00 (ATM - near current price)
Expiry:             2026-05-22 (24 days)
Premium:            $3.30 per share
Total Cost:         $330.00 (1 contract)
Max Loss:           $330.00
Breakeven:          $107.30
```

**Why UPS is #2:**
- ✓ **Strongest volume (1.80x)** — best liquidity among top 5
- ✓ **Lowest price** — tightest stops available
- ⚠ Lower upside to target (4.3% vs DLR 4.1%) = lower profit potential
- ⚠ At-the-money (ATM) strike = higher premium, less room for pullback

**Use UPS if:**
- DLR doesn't hit entry zone
- You prefer logistics/supply chain exposure
- You want tighter technical setup (cleaner volume)

---

## KEY OPTION RISKS & MANAGEMENT

### **Theta Decay (Time Works Against You)**
- Each day, your call loses ~$10-15 in time value
- **Critical window:** Days 15-21 (sharp decay begins)
- **Fix:** Exit with 3-5 days to expiry (don't let time kill position)

### **Implied Volatility (Option Price Sensitivity)**
- If DLR IV drops → call premium falls (even if price stable)
- If DLR IV rises → call premium rises (helps your position)
- **Current IV estimate:** Normal (50-60 IV rank) = moderate decay

### **Gap Risk (Overnight Moves)**
- Earnings, macro data could gap DLR past your stop
- **Mitigation:** Set alert at $190 (2% above stop), be ready to close

### **Assignment Risk (Call Goes In-The-Money)**
- If DLR > $200 at expiry, you could be assigned (own 100 shares)
- **Not ideal with $335 capital** — you can't afford the stock
- **Fix:** Close the call 2-3 days before expiry (avoid assignment)

### **Liquidity Risk (Wide Bid-Ask Spread)**
- If DLR May $200 calls have wide spread → hard to exit profitably
- **Check:** Before buying, verify bid-ask spread <$0.20
- **Example:** Bid $3.10, Ask $3.25 = $0.15 spread = tight ✓

---

## BROKER REQUIREMENTS

**You'll need:**
- ✓ Options approval Level 1 or 2 (for long calls)
- ✓ Account minimum $2,000+ (most brokers)
- ✓ Options-enabled brokerage

**Recommended Brokers:**
- **Interactive Brokers** — lowest fees, best options tools
- **TD Ameritrade** — ThinkorSwim platform (excellent charts)
- **E*TRADE** — competitive options pricing
- **Tastytrade** — options specialists (best education)

**Do NOT use:**
- Robinhood (poor options education, wide spreads)
- Webull (limited options selection)
- Fidelity (slower platform for day trading)

---

## QUICK REFERENCE CARD

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PRIMARY TRADE: DLR LONG CALL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ENTRY TRIGGER:      DLR price = $190.66 (on chart, watch MA20)
BUY:                1 × DLR May 22 $200 Call
COST:               $3.17/share × 100 = $317.50 total
EXPIRY:             May 22, 2026 (24 days)

EXIT - PROFIT:      DLR = $208.14 (target) → Sell call → +$497
EXIT - STOP LOSS:   DLR < $190.66 → Sell call → -$237
EXIT - TIME DECAY:  5 days to expiry → Close (avoid last-minute decay)

BREAKEVEN:          $203.17 (strike + premium)
MAX LOSS:           $317.50 (if DLR < $200 at expiry)
MAX PROFIT:         $496.50 (if DLR > $208 at expiry)
RISK/REWARD:        1.56x (good for 24-day swing)

BACKUP TRADE:       UPS May 22 $104 Call ($330 cost)
                    
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## STEP-BY-STEP CHECKLIST

**Before Entry:**
- [ ] Open brokerage account with options approval
- [ ] Fund account with $335+
- [ ] Add DLR to watchlist on TradingView
- [ ] Set alert at $190.66 (entry zone)
- [ ] Verify May 22 $200 calls exist (bid-ask spread <$0.20)

**At Entry ($190.66 trigger):**
- [ ] Place limit buy order: 1 DLR May 22 $200 Call @ $3.17
- [ ] Order fills → you own 1 contract
- [ ] Cost: $317.50 (leaves $17.50 buffer)
- [ ] Note entry price and time in journal

**During Hold (5-20 days):**
- [ ] Monitor DLR price daily
- [ ] Set exit alerts at $208.14 (profit) and $190 (stop)
- [ ] Track Greeks: Delta, Theta (Vega if possible)

**Before Expiry (2-3 days before May 22):**
- [ ] CLOSE THE CALL (don't let time kill it)
- [ ] Lock in profit or cut losses
- [ ] Note exit price, time, and P&L

**After Exit:**
- [ ] Record trade in journal: entry, exit, P&L, reason
- [ ] Wait for next swing setup
- [ ] Rerun `swing_trade_screener_v2.py` (weekly)

---

## FINAL RECOMMENDATION

**Go with DLR Long Call** because:

1. ✓ **Perfect capital fit** ($317.50 uses 95% efficiently)
2. ✓ **Best risk/reward** (1.56x for 24-day trade)
3. ✓ **Strong thesis** (Data center + AI capex)
4. ✓ **Clean technical** (Pullback to MA20 support)
5. ✓ **Liquidity** (DLR liquid at $194 price level)
6. ✓ **Expiry timing** (May 22 = perfect 2-4 week window)

**Expected outcome:**
- **Best case:** +$497 profit (148% return) if target hit
- **Base case:** +$83-150 profit (25-45% return) if partial move
- **Worst case:** -$237 loss (if stopped early, cut losses)

**Time frame:** 10-20 trading days  
**Win probability:** 40%+ (based on pullback-to-MA20 backtest)

---

## FINAL WARNING ⚠️

**Options are leverage instruments:**
- You can lose 100% of your capital ($335) quickly
- Theta decay + gap moves can destroy positions overnight
- **Only trade what you can afford to lose**
- **Exit discipline is critical** (don't hold hoping it comes back)
- **Track every trade** in journal (validate vs backtest)

---

**Ready to execute?** 
1. Open brokerage + options account (today)
2. Wait for DLR to hit $190.66 entry zone
3. Buy 1 DLR May 22 $200 call
4. Manage position using exit triggers above
5. Record results for future iterations

**Questions?** Let me know which broker you'll use, and I can walk you through the specific order placement.
