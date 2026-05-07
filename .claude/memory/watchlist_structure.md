---
name: Institutional Watchlist Structure (2026-05-05)
description: 6 TradingView watchlists reorganized into 4-tier VIF institutional hierarchy; 170 tickers, 58 duplicates removed, files in watchlists/
type: project
originSessionId: 275d482b-9bda-41df-ac22-0d73fa9237a0
---
6 watchlists rebuilt with 4-tier section structure. Files ready for TradingView import from `watchlists/`.

**Why:** Reorganize flat watchlists into institutional VIF v4.0 hierarchy with regime/conviction/driver classification for faster scanning and cleaner signal generation.

**How to apply:** When VIF analysis references watchlist tickers, sections now indicate confidence tier: Vanguard = regime read, Primary = high-conviction entries, Scouts = setup confirmation needed, Waiting = monitor only.

## Watchlist Summary

| WL | Name | Tickers | Regime | Primary Driver |
|----|------|---------|--------|----------------|
| WL1 | AI Physical Layer & Power Infrastructure | 47 | Risk-On | Tape + CapEx |
| WL2 | AI Verticals (Supply Chain) | 31 | Risk-On | CapEx + Tape |
| WL3 | Core Growth & Macro Indices | 56 | Both | Earnings + Macro |
| WL4 | Energy & AI (Power Convergence) | 13 | Risk-On | Contract + CapEx |
| WL5 | Speculative & High-Beta | 10 | Risk-On ONLY | Momentum |
| WL6 | Trump Admin: Onshoring | 13 | Risk-On | Contract + Macro |

## 4-Tier Structure (applies to all 6 lists)
- `###01_MACRO_VANGUARD` — 2–9 regime instruments; check first before any entry
- `###02_PRIMARY_CONVICTION` — 60–70% capital; passes all VIF checks
- `###03_SPECULATIVE_SCOUTS` — 20–30% capital; requires setup confirmation
- `###04_WAITING_LIST` — monitoring only; no active positions

## Key Duplicate Resolutions
- BE → WL4 only (was in all 6)
- FCEL → WL4 only (was in 5)
- WULF/IREN → WL3 + WL5 (removed from WL1, WL4)
- VX1!/ASHR → WL3/WL2 only (removed from WL1)
- WL3 AI BOTTLENECKS section stripped; large-caps promoted to Primary Conviction

## Report
Full HTML report with ticker metadata, alpha triggers, VIF variants, and import instructions:
`C:\Users\marti\vif-trading-system\reports\watchlist_institutional_structure.html`
