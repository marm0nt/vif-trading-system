# Skill: Parsing Watchlists
<!-- Agent: agents/watchlist_watcher.py (parser stage) -->

## Role
Load, validate, and deduplicate TradingView watchlist exports. Output a clean ticker list.

## Watchlist files
| File | Tickers | Focus |
|---|---|---|
| `watchlists/vantage_portfolio.txt` | ~85 | Core holdings + swing candidates |
| `watchlists/ai_verticals.txt` | ~35 | AI infrastructure, semis, cloud |
| `watchlists/energy_ai.txt` | ~13 | Energy, nuclear, AI power |

## Normalization rules
```python
# Strip exchange prefix: "NASDAQ:NVDA" → "NVDA"
ticker = raw.strip().split(":")[-1]

# Skip comment lines starting with ###
if ticker.startswith("###"): continue

# Skip empty / whitespace-only
if not ticker: continue

# Deduplicate: use set() before returning
return sorted(set(cleaned_tickers))
```

## Validation checklist
- [ ] File exists → FileNotFoundError caught, warn and continue
- [ ] No ticker is > 6 characters (flag long strings as likely malformed)
- [ ] At least 1 ticker loaded (if 0: fail with clear error message)
- [ ] Log ticker count per watchlist on every run

## Performance improvement checklist (review when watchlists change)
- [ ] Review watchlists every quarter — remove delisted / merged tickers
- [ ] Add new AI/energy tickers from sector ETF holdings (XLK, XLE)
- [ ] Ensure no duplicate tickers across watchlists (use `--all` to catch)
