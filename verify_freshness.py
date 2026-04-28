#!/usr/bin/env python3
"""Verify data freshness for identified setups"""
import yfinance as yf
from datetime import datetime

tickers = ['TSEM', 'DLR', 'UPS', 'LITE', 'NBIS', 'AMAT', 'COHR', 'LRCX', 'POET', 'RDDT']

print("="*80)
print("DATA FRESHNESS VERIFICATION - IDENTIFIED SWING TRADE SETUPS")
print("="*80)
print()

for ticker in tickers:
    try:
        df = yf.download(ticker, period='5d', progress=False)
        if df is not None and len(df) > 0:
            latest_date = df.index[-1]
            latest_close = df['Close'].iloc[-1]
            days_old = (datetime.now() - latest_date).days
            status = "✓ FRESH" if days_old == 0 else f"({days_old}d old)"
            print(f"{ticker:8} | Latest: {latest_date.strftime('%Y-%m-%d')} | Close: ${latest_close:.2f} | {status}")
    except:
        print(f"{ticker:8} | ERROR fetching data")

print()
print(f"Current UTC Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
print(f"Scan Timestamp: 2026-04-28 14:10 UTC")
