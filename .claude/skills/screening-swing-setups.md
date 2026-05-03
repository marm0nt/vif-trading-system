# Skill: Screening Swing Setups
<!-- Agent: swing_trade_screener_v2.py | Time: 09:35 CT weekdays -->

## Role
Find the highest-quality 2–4 week swing trade setups, ranked by risk:reward.
Output is a ranked list — the top of the list is the highest-conviction actionable setup.

## 5 setup types (backtested, proven in Freqtrade community strategies)

| Setup | Entry Condition | Target | Stop |
|---|---|---|---|
| **Breakout** | Price > 20d high + vol > 1.5× avg | +8–12% | 20d high − 1×ATR |
| **Pullback to EMA21** | RSI cools to 45–55, price tests EMA21 | +6–10% | EMA21 − 1.5×ATR |
| **BB Squeeze Expansion** | BB width < 0.04, then candle breaks upper band | +8–15% | Lower band |
| **MACD Bullish Cross** | MACD crosses above signal + vol confirms | +5–8% | Entry − 2×ATR |
| **Oversold Bounce** | RSI < 35, K1 not active, vol > 1.2× avg | +5–10% | Recent swing low |

## Quality scoring (0–100)
```
score = 0
+ RSI in 45–65 range:          +20   (momentum not exhausted)
+ MACD cross = bullish:         +20   (trend confirmation)
+ vol_ratio > 1.3:              +20   (conviction)
+ price > EMA50:                +20   (structural uptrend)
+ bb_squeeze just resolved:     +20   (compressed energy)

Kill switch penalty:
- K1 active:  −50  (do not trade)
- K2 active:  −30  (reduce size or skip)
- K3 active:  −40  (liquidity risk)
- K4 active:  −40  (binary event)
- K6 active:  −30  (distribution)

Min score to show: 50  (below = skip)
```

## Output format
```json
{
  "screened_at": "2026-04-29 09:35:00",
  "top_setups": [
    {
      "ticker": "NVDA",
      "setup_type": "Breakout",
      "quality_score": 84,
      "entry": 213.50,
      "target": 234.85,
      "stop": 205.20,
      "rr_ratio": 2.6,
      "reasoning": "15-word max summary of why this setup qualifies"
    }
  ],
  "skipped": ["WULF", "NBIS"],
  "skip_reasons": {"WULF": "K3 low volume", "NBIS": "K4 earnings 2d"}
}
```

## Feedback loop
```
Step 1: Compute indicators (IndicatorEngine)
Step 2: Score each ticker
Step 3: Filter score < 50 → move to skipped list
Step 4: Sort remaining by rr_ratio descending
Step 5: Log top 5 to console + save full list to reports/swing_{timestamp}.json
```

## Performance improvement checklist (review monthly)
- [ ] Track each flagged setup → 5d, 10d, 20d actual return
- [ ] If quality_score 50–60 underperforms: raise minimum to 60
- [ ] If Breakout setups hit target < 40%: check vol_ratio threshold (raise to 1.7×)
- [ ] If pullback setups overperform: add EMA21 setups to premarket scan
- [ ] Compare Friday-flagged setups vs Monday-flagged setups for best entry day
