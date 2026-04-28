#!/usr/bin/env python3
"""Quick FPS (First Solar) analysis with real market data."""
import json
import pandas as pd
import yfinance as yf
from datetime import datetime

def analyze_single_ticker(ticker):
    """Analyze a single ticker with real data."""
    print(f"\nFetching real market data for {ticker}...")

    try:
        df = yf.download(ticker, period="1mo", progress=False)

        if df is None or len(df) < 2:
            print(f"No data available for {ticker}")
            return None

        # Handle multi-index columns from yfinance
        if isinstance(df.columns, pd.MultiIndex):
            close_col = ('Close', ticker)
            vol_col = ('Volume', ticker)
        else:
            close_col = 'Close'
            vol_col = 'Volume'

        df = df.dropna()
        if len(df) < 2:
            return None

        latest_close = float(df[close_col].iloc[-1])
        latest_vol = float(df[vol_col].iloc[-1])
        first_close = float(df[close_col].iloc[0])

        # Calculate indicators
        close_series = df[close_col]
        vol_series = df[vol_col]
        ma_20 = float(close_series.tail(20).mean()) if len(df) >= 20 else float(close_series.mean())
        vol_avg = float(vol_series.tail(20).mean()) if len(df) >= 20 else float(vol_series.mean())

        # Simple RSI
        closes = df[close_col].values
        deltas = [closes[i] - closes[i-1] for i in range(1, len(closes))]
        gains = sum([d for d in deltas[-14:] if d > 0]) / 14 if len(deltas) >= 14 else 0
        losses = -sum([d for d in deltas[-14:] if d < 0]) / 14 if len(deltas) >= 14 else 0
        rsi = 100 - (100 / (1 + (gains / losses if losses > 0 else 1))) if losses > 0 else 50

        price = latest_close
        change_pct = ((latest_close - first_close) / first_close * 100) if first_close > 0 else 0
        vol_ratio = latest_vol / vol_avg if vol_avg > 0 else 0

        # VIF Analysis Logic
        if rsi < 30 and vol_ratio > 1.2:
            signal = "BUY"
            confidence = 85
            reasoning = f"Oversold RSI {rsi:.1f}, strong volume {vol_ratio:.1f}x"
        elif rsi > 70 and change_pct > 5:
            signal = "SELL"
            confidence = 75
            reasoning = f"Overbought RSI {rsi:.1f}, strong rally {change_pct:.1f}%"
        else:
            signal = "HOLD"
            confidence = 50
            reasoning = f"Neutral: RSI {rsi:.1f}, vol {vol_ratio:.1f}x, change {change_pct:.1f}%"

        gamma = "positive" if rsi > 50 else "negative"
        level = "resistance" if change_pct > 0 else "support"
        vol_signal = "strong" if vol_ratio > 1.5 else "weak"
        kill_switch = None
        if rsi > 85 or rsi < 15:
            kill_switch = "K1"
        elif abs(change_pct) > 10:
            kill_switch = "K2"

        return {
            "ticker": ticker,
            "price": round(price, 2),
            "signal": signal,
            "confidence": confidence,
            "gamma_regime": gamma,
            "level_type": level,
            "volume_signal": vol_signal,
            "kill_switch": kill_switch,
            "rsi": round(rsi, 1),
            "ma_20": round(float(ma_20), 2),
            "change_pct": round(change_pct, 2),
            "vol_ratio": round(vol_ratio, 2),
            "reasoning": reasoning,
            "data_points": len(df)
        }

    except Exception as e:
        print(f"Error analyzing {ticker}: {e}")
        return None

if __name__ == "__main__":
    print("="*80)
    print("FPS (FIRST SOLAR) - REAL MARKET DATA ANALYSIS")
    print("="*80)

    analysis = analyze_single_ticker("FPS")

    if analysis:
        print("\n" + json.dumps(analysis, indent=2))
        print("\n" + "="*80)
        print(f"Signal: {analysis['signal']} (confidence {analysis['confidence']}%)")
        print(f"Reasoning: {analysis['reasoning']}")
        print(f"Kill Switch: {analysis['kill_switch'] if analysis['kill_switch'] else 'NONE'}")
        print("="*80)
    else:
        print("Failed to analyze FPS")
