---
name: K4 Earnings Calendar — Confirmed Dates May-July 2026
description: Confirmed and estimated earnings dates for watchlist tickers, used for K4 kill switch flagging
type: project
---

Confirmed/high-confidence earnings dates as of 2026-05-08:

| Ticker | Date | Status | Days Away | K4 Active (<=5d) |
|--------|------|--------|-----------|------------------|
| POWL   | 2026-05-05 | REPORTED (beat orders, missed EPS slightly) | -3 | NO (past) |
| ANET   | 2026-05-05 | REPORTED (beat, stock -13% on valuation) | -3 | NO (past) |
| RDDT   | 2026-04-30 | REPORTED (beat, +69% rev YoY) | -8 | NO (past) |
| HOOD   | Q1 reported | REPORTED (miss vs est, $1.07B rev) | past | NO |
| CRWV   | 2026-05-13 | ESTIMATED | +5 | YES — K4 ACTIVE |
| AMAT   | 2026-05-14 | CONFIRMED | +6 | APPROACHING — monitor |
| NVDA   | 2026-05-20 | CONFIRMED | +12 | NO (yet) |
| MRVL   | 2026-05-27 | CONFIRMED | +19 | NO |
| AVGO   | 2026-06-03 | CONFIRMED | +26 | NO |
| MU     | ~2026-06-25 | ESTIMATED | ~+48 | NO |
| TSM    | 2026-07-16 | UNCONFIRMED | ~+69 | NO |

**Why:** K4 threshold is 5 days per config/vif_config.yml (K4_THRESHOLD_DAYS = 5).

**How to apply:** CRWV crosses K4 threshold on or before May 13. Flag AMAT for K4 watch starting May 9 (5 days before May 14). NVDA is the highest-impact upcoming event — not K4 yet but drives sector-wide sentiment.
