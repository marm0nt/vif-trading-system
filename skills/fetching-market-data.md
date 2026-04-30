# Skill: Fetching Market Data
<!-- Agent: agents/watchlist_watcher.py (fetcher) + agents/indicators.py -->

## Role
Pull OHLCV data from Yahoo Finance, cache locally, compute indicators.
Minimize API calls. Never re-download data that is < 4 hours old.

## Data source
- **Provider:** Yahoo Finance via `yfinance` (free, no API key)
- **Cache:** `data/{TICKER}_{PERIOD}.pkl` (pickle files)
- **Cache TTL:** 4 hours for intraday, 24 hours for daily OHLCV

## Period guide
| Period | Use case | Indicators reliable from |
|---|---|---|
| `5d` | After-hours quick wrap | RSI, vol ratio only |
| `1mo` | Premarket full scan | All indicators |
| `3mo` | Single-ticker deep dive | All indicators + EMA200 |
| `6mo` | IndicatorEngine default | Most accurate EMA200 |

## Cache logic
```python
cache_path = Path(f"data/{ticker}_{period}.pkl")
if cache_path.exists():
    age_hours = (time.time() - cache_path.stat().st_mtime) / 3600
    if age_hours < 4:
        return pickle.load(open(cache_path, "rb"))  # use cache
# else: download fresh
df = yf.download(ticker, period=period, progress=False)
pickle.dump(df, open(cache_path, "wb"))
```

## MultiIndex flattening (yfinance 1.x returns MultiIndex columns for single tickers)
```python
if isinstance(df.columns, pd.MultiIndex):
    df = pd.DataFrame({
        "Close":  df[("Close",  ticker)],
        "High":   df[("High",   ticker)],
        "Low":    df[("Low",    ticker)],
        "Volume": df[("Volume", ticker)],
    })
```

## Performance checklist (review monthly)
- [ ] Cache hit rate > 70% on repeat runs (if low: check TTL or cache path)
- [ ] No ticker fails with KeyError on MultiIndex (yfinance version compat)
- [ ] data/ directory size < 500 MB (purge caches older than 7 days weekly)
- [ ] Download rate < 2 requests/second (avoid Yahoo throttling)
