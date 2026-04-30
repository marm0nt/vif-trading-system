# Skill: Computing Indicators
<!-- Shared engine. All agents import from agents/indicators.py -->

## Role
Compute a deterministic indicator set from OHLCV DataFrames.
One source of truth — if math changes here, all agents benefit automatically.

## Indicator reference (Python 3.14 compatible via `ta` library)

| Indicator | Period | VIF Use |
|---|---|---|
| RSI | 14 | Gamma regime + K1 kill switch |
| MACD | 12/26/9 | Trend direction confirmation |
| EMA | 9/21/50/200 | Trend structure + golden/death cross |
| Bollinger Bands | 20, 2σ | Volatility + squeeze detection |
| ATR | 14 | Stop placement (entry − 2×ATR) |
| Volume ratio | vs 20d avg | Signal strength filter |

## Quick usage
```python
from agents.indicators import fetch_and_compute, IndicatorEngine

# Single ticker (downloads + computes):
ind = fetch_and_compute("NVDA", period="6mo")

# From existing DataFrame:
ind = IndicatorEngine(df).compute()

# Key fields returned:
ind["rsi"]          # float, 0–100
ind["macd_cross"]   # "bullish" | "bearish"
ind["ema_trend"]    # "strong_uptrend" | "uptrend" | "mixed" | "downtrend"
ind["bb_squeeze"]   # bool – True = compression breakout pending
ind["atr_stop_2x"]  # float – suggested hard stop (2× ATR below price)
ind["vol_ratio"]    # float – today's vol / 20d avg
ind["vol_signal"]   # "strong" | "normal" | "weak"
ind["gamma_regime"] # "positive" | "negative" | "transition"
ind["kill_switches"]# list of active kill switch codes
```

## Validation feedback loop
```
After compute():
  → assert "rsi" in result and 0 <= result["rsi"] <= 100
  → assert result["gamma_regime"] in ("positive","negative","transition")
  → assert result["vol_ratio"] > 0
  → if any assertion fails: log ticker + skip (never crash the pipeline)
```

## Known Python 3.14 constraints
- `pandas-ta`: ❌ requires numba — not yet compatible with 3.14
- `TA-Lib`: ❌ C extension — no 3.14 wheel yet
- `ta`: ✅ pure-Python — full compatibility — same math
- When 3.14 wheels are released: swap `ta` → `pandas-ta` with zero code changes

## Performance checklist (review quarterly)
- [ ] All 8 indicator fields present in every output
- [ ] ATR stop never > 8% from entry (adjust 2× multiplier if needed)
- [ ] EMA 200 golden cross accuracy: track 20d forward return
- [ ] BB squeeze → check breakout rate 5d later (target > 60% directional)
