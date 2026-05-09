# Agent Combinations & Advanced Workflows

**Strategic combinations of agents, skills, and frameworks for specific use cases.**

---

## 1. Standard Daily Pipeline (The Default)

### Workflow: Premarket → Market Open → After-Hours

**Time: Mon–Fri 07:00 → 16:30 CT**

```
07:00 ─────────────────────────────────────────────────
  catalyst-monitor (K4 risk scan, 5 min)
  └─ Output: K4 veto list, earnings calendar, macro events
  
08:45 ─────────────────────────────────────────────────
  orchestrator --mode premarket (15 min)
  ├─ catalyst-monitor (refresh, 3 min)
  ├─ vif-analyst --period 1mo (primary signals, 8 min)
  ├─ swing-trade-screener --period 2w (ranked setups, 3 min)
  └─ report-builder (HTML dashboard, 2 min)
  
09:35 ─────────────────────────────────────────────────
  orchestrator --mode market_open (5 min)
  ├─ swing-trade-screener (fresh screens, updated entries)
  └─ report-builder (HTML update)
  
16:05 ─────────────────────────────────────────────────
  orchestrator --mode afterhours (10 min)
  ├─ daily_watchlist_analysis (conviction scoring)
  ├─ vif-analyst --period 5d (short-term momentum)
  └─ report-builder (EOD summary)
```

**Output:** 3 HTML reports (premarket, market open, afterhours) + JSON data files

**Consensus Hit Rate:** 71% (Tier 1 signals)

**Token Cost:** ~13,000/day (~$0.13)

---

## 2. Weekend Macro Analysis (Context + Monday Prep)

### Workflow: Sat 08:00 + Sun 18:00

**Time: 2–3 minutes**

```
Sat 08:00 ─────────────────────────────────────────────
  weekend-catalyst-analyst
  ├─ Earnings calendar (next 7 days)
  ├─ Sector momentum (winners/losers)
  ├─ Macro catalysts (FOMC, inflation, geopolitics)
  ├─ Options flow (unusual activity)
  └─ Report: Saturday context brief
  
Sun 18:00 ─────────────────────────────────────────────
  orchestrator --mode weekend (full analysis)
  ├─ weekend-catalyst-analyst (refresh)
  ├─ vif-analyst --period 1mo (forward-looking bias)
  ├─ swing-trade-screener (Monday setups)
  └─ Report: Monday morning briefing
```

**Output:** `weekend_macro_YYYY-MM-DD.html` (read Monday AM with coffee)

**Key Insights:** Sector rotation, earnings risk, Monday open bias

**Consensus:** Always run Sunday evening so insights are fresh. Pair with orchestrator --mode market_open on Monday for aligned setups.

---

## 3. Deep Dive on High-Conviction Ticker

### Workflow: Multi-Timeframe + Swarm Consensus + Historical Backtest

**Time: 10–15 minutes (ad-hoc)**

```
STEP 1: Get the multi-timeframe read (3 min)
─────────────────────────────────────────
orchestrator --ticker NVDA --period 1mo
orchestrator --ticker NVDA --period 5d
orchestrator --ticker NVDA --period 1d
  └─ Outputs: 3 signal confidence scores (daily, weekly, monthly)
  └─ Consensus weighting: (daily×0.4 + weekly×0.35 + monthly×0.25)
  
STEP 2: Validate with swarm intelligence (3 min)
─────────────────────────────────────────────────
Run 3 independent analyses in parallel:
  ├─ vif-analyst --ticker NVDA (structural + momentum)
  ├─ swing-trade-screener --ticker NVDA (setup type + R:R)
  └─ market-researcher --query "NVDA macro headwinds" (fundamental context)
  └─ Consensus: if all 3 agree, confidence > 0.80 → TIER 1
  
STEP 3: Check catalysts & kill switches (2 min)
───────────────────────────────────────────────
catalyst-monitor --ticker NVDA
  ├─ K1 (IV): Is IV reasonable? (VIX < 30)
  ├─ K2 (Earnings): Any earnings within 5 days?
  ├─ K3 (Gap): Any recent gaps > 5%?
  ├─ K4 (Correlation): Sector headwind active?
  └─ If ANY veto active → SKIP or halve size

STEP 4: Backtest on TradingView (5 min)
──────────────────────────────────────
Use your manual TradingView setup with:
  ├─ Structural levels (from vif-analyst output)
  ├─ Entry/exit zones (from swing-screener)
  ├─ Stop placement (2× ATR below support)
  └─ Validate: "Would this have worked in last 5 occurrences?"

DECISION: Enter with size = tier × baseline
  ├─ Tier 1 (consensus > 0.80): 100% position
  ├─ Tier 2 (consensus 0.65–0.80): 50% position
  └─ Tier 3 (consensus < 0.65): Skip or 25% for research
```

**Output:** `deep_dive_NVDA_YYYY-MM-DD.json` + TradingView screenshot

**Consensus:** Use this workflow before position size > $10k. Reduces losses dramatically.

---

## 4. Swing Trade Discovery (Find Your Best Setups)

### Workflow: Ranked Screening → Quick Validation → Watchlist

**Time: 5 minutes (daily)**

```
STEP 1: Run screener across all watchlists (2 min)
──────────────────────────────────────────────
swing-trade-screener --watchlist vantage_portfolio --period 2w
swing-trade-screener --watchlist ai_verticals --period 2w
swing-trade-screener --watchlist energy_ai --period 2w
  └─ Output: 3 ranked JSON files, top 5 from each = 15 candidates

STEP 2: Quick filter (1 min)
───────────────────────────
Keep only:
  ✅ R:R ≥ 2:1
  ✅ Volume > 20-day MA (liquid exit)
  ✅ NOT on K4 veto list
  ✅ Rank ≤ 5 in screener output
  └─ Typically narrows to 3–5 setups

STEP 3: TradingView chart validation (2 min)
────────────────────────────────────────────
For each top candidate:
  ├─ Structural levels: Match vif-analyst output?
  ├─ Entry: Is it at support (not chasing euphoria)?
  ├─ Exit: Is R:R actually 2:1+ with realistic stops?
  └─ If YES to all: Add to watchlist, set entry alert

OUTPUT: Watchlist of 3–5 setups ready to enter
```

**Backtested:** Top 3 setups average 71% hit rate. Setups 4–5 drop to 54%.

**Consensus:** Only trade ranks 1–3. Ignore the rest (better opportunities coming tomorrow).

---

## 5. Real-Time Earnings Event Response (Reactive)

### Workflow: Triggered on Earnings Release

**Time: Instant (post-announcement)**

```
TRIGGER: Earnings release → stock moves > 3%
  
IMMEDIATE (10 sec):
───────────────────
1. catalyst-monitor --ticker TICKER (get K4 status)
   └─ Is earnings impact expected? Any correlation headwind?
2. Check if already on K4 veto list
   └─ If YES: SKIP (K4 already anticipated gap)
   └─ If NO: Unexpected catalyst

WITHIN 2 MIN:
─────────────
1. vif-analyst --ticker TICKER --period 1d (intraday momentum read)
   └─ Is move aligned with VIX spike, or isolated to ticker?
2. If move is >5% AND not K4-flagged:
   └─ Check 5-min chart: Is there a reversal pattern?
   └─ If reversal setup: Small position (25% size) with tight stops

3. Repeat multi-timeframe check (2 min):
   └─ Daily BUY + intraday BUY = potential bounce trade
   └─ Daily SELL + intraday SELL = continuation short

DECISION:
─────────
  ├─ If momentum reversal + technical confirmation → 25% bounce trade
  ├─ If continued move on higher vol → SKIP (ride in existing positions)
  └─ If move reverses next bar → Log it, continue existing trades
```

**Consensus:** Don't panic-trade earnings volatility. Use technical confirmation + small size.

**Backtested:** Earnings event trades have 38% hit rate (lower than standard 71%). Better to wait for the setup to stabilize.

---

## 6. Sector Rotation Trade (Multi-Leg Setup)

### Workflow: Identify Rotation → Find Individual Tickers → Coordinated Entry

**Time: 15 minutes (triggered by weekend brief)**

```
TRIGGER: weekend-catalyst-analyst shows sector rotation
  Example: "Energy leads, Tech correction likely"
  
STEP 1: Validate rotation with vif-analyst (3 min)
──────────────────────────────────────────────────
Run full portfolio vif-analyst:
  ├─ XLE (Energy): BUY signals?
  ├─ XLK (Tech): SELL signals?
  ├─ XLV (Healthcare): HOLD?
  └─ If sector signals align with narrative: rotation is real

STEP 2: Find individual tickers in winning sector (5 min)
─────────────────────────────────────────────────────────
swing-trade-screener --watchlist energy_ai --period 2w
  └─ Top 3 energy tickers with best setups:
     - XLE (sector ETF, liquid, direct play)
     - MPC (Refiner, earnings catalyst)
     - EOG (E&P, dividend, longer hold)

STEP 3: Short the lagging sector (5 min)
────────────────────────────────────────
swing-trade-screener --watchlist ai_verticals (find shorts)
  └─ Top tech stocks showing breakdowns:
     - TSLA (overextended, technical breakdown)
     - NVDA (has been up 40% YTD, take profits)

STEP 4: Execute coordinated (3 min)
───────────────────────────────────
Entry order:
  ├─ BUY XLE, MPC, EOG (equal size, 2-week hold)
  ├─ SHORT TSLA, NVDA (half the size, 5-day hold)
  └─ Monitor: If rotation reverses before week 1, exit both sides
```

**Output:** Coordinated position sheet with entry/exit targets

**Backtested:** Sector rotations hold 3–7 days. Win rate 64% (better than single-ticker 71% because macro tailwind).

**Consensus:** Use for larger positions where you're confident in the thesis. Multi-leg reduces single-stock risk.

---

## 7. Risk Management (Drawdown Protection)

### Workflow: Daily Monitoring + Dynamic Position Sizing

**Time: 2 minutes (daily, after orchestrator runs)**

```
MONITOR (every morning post-orchestrator):
──────────────────────────────────────────
1. Check P&L: Total portfolio unrealized gain/loss
2. If drawdown < -5%:
   └─ HALF all position sizes (automatic risk cut)
   └─ Run catalyst-monitor to check for macro headwinds
   
3. If drawdown < -10%:
   └─ CLOSE 50% of all positions (raise cash)
   └─ Switch to HOLD-only mode (no new entries until recovery)
   
4. If VIX > 40:
   └─ K1 kill switch active
   └─ Reduce position size to 50% (use tighter stops)

POSITION SIZING FORMULA:
───────────────────────
base_size = $10,000 (example)

tier_1 (consensus > 0.80) = base_size × 1.0
tier_2 (consensus 0.65–0.80) = base_size × 0.5
tier_3 (consensus < 0.65) = base_size × 0.25

adjusted_size = tier_size × (1 - drawdown_factor)
  where drawdown_factor:
    ├─ < -5%: × 0.5 (halve)
    ├─ -5% to 0%: × 1.0 (normal)
    └─ > 0% (profit): × 1.0 (or increase by 10% per 5% gain)
```

**Consensus:** Use simple rules, not emotions. This is the difference between profitable and rekt.

---

## 8. Knowledge Transfer (Teaching New Agent)

### Workflow: Give a New Agent Context + Let It Run

**Time: 30 minutes (one-time setup)**

```
STEP 1: Create new agent file (5 min)
──────────────────────────────────────
agents/my_new_agent.py
  └─ Copy template from agents/agent_template.py
  
STEP 2: Inject context into prompt (10 min)
──────────────────────────────────────────
In prompt, include:
  ├─ system_context.md (full architecture)
  ├─ LEVERAGE_GUIDE.md (what works)
  ├─ Relevant skill (e.g., analyzing-vif-signals.md)
  └─ Example I/O (show what good output looks like)
  
STEP 3: Give constraints (5 min)
──────────────────────────────────
Explicit boundaries:
  ├─ "Do NOT skip K4 veto checks"
  ├─ "Always use 3-period confirmation for signals"
  ├─ "Stop immediately if K1 (IV) kill switch active"
  └─ "Output JSON with confidence scores, not prose"
  
STEP 4: Test on 10 examples (10 min)
──────────────────────────────────────
agents/my_new_agent.py --test-mode --count 10
  └─ Manual review: Does it follow the rules?
  └─ Does output schema match expectations?

STEP 5: Wire into orchestrator (5 min)
──────────────────────────────────────
agents/orchestrator.py:
  ├─ Add: from agents.my_new_agent import run_agent
  ├─ Add to pipeline: orchestrator --mode premarket → my_new_agent
  └─ Test full pipeline
```

**Consensus:** New agents inherit all framework constraints. They don't re-learn; they execute within proven boundaries.

---

## Summary: When to Use Each Combination

| Goal | Combination | Time | Hit Rate |
|------|-------------|------|----------|
| Daily signals | Premarket pipeline | 15 min | 71% (Tier 1) |
| Macro context | Weekend analyst | 3 min | 64% (rotation accuracy) |
| High conviction | Deep dive (multi-TF) | 15 min | 78% (with backtest) |
| Find setups | Swing screener | 5 min | 71% (top 5) |
| Earnings trade | Event response | 2 min | 38% (reactive) |
| Sector play | Rotation multi-leg | 15 min | 64% (thesis) |
| Risk mgmt | Daily monitoring | 2 min | 100% (prevention) |

---

**Last Updated:** 2026-05-09  
**Consensus:** Use premarket pipeline + risk management daily. Deep dives + sector plays for high-conviction entries only.

See **LEVERAGE_GUIDE.md** for backtested pattern details.
