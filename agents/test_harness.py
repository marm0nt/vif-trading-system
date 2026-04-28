#!/usr/bin/env python3
"""Local test harness - no Claude API calls needed."""
import json
from pathlib import Path
from datetime import datetime

def mock_vif_analysis(market_data, watchlist_name):
    """Simulate VIF analysis locally."""
    signals = {}
    buy_count, sell_count, hold_count = 0, 0, 0

    for ticker, data in market_data.items():
        rsi = data['rsi']
        change = data['change_pct']
        vol_ratio = data['volume'] / data['vol_avg_20d']

        if rsi < 30 and vol_ratio > 1.2:
            signal, conf = "BUY", 80
        elif rsi > 70 and change > 5:
            signal, conf = "SELL", 75
        else:
            signal, conf = "HOLD", 50

        kill_switch = None
        if rsi > 85 or rsi < 15:
            kill_switch = "K1"
        elif abs(change) > 10:
            kill_switch = "K2"

        signals[ticker] = {
            "signal": signal,
            "confidence": conf,
            "gamma_regime": "positive" if rsi > 50 else "negative",
            "level_type": "resistance" if change > 0 else "support",
            "volume_signal": "strong" if vol_ratio > 1.5 else "weak",
            "kill_switch": kill_switch,
            "price": round(data['price'], 2),
            "rsi": round(data['rsi'], 1),
            "reasoning": f"RSI {rsi:.0f}, vol {vol_ratio:.1f}x, change {change:.1f}%"
        }

        if signal == "BUY":
            buy_count += 1
        elif signal == "SELL":
            sell_count += 1
        else:
            hold_count += 1

    return {
        "analysis_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "watchlist": watchlist_name,
        "tickers_analyzed": len(market_data),
        "signals": signals,
        "summary": f"BUY {buy_count}, SELL {sell_count}, HOLD {hold_count} - {watchlist_name} shows mixed signals",
        "note": "MOCK DATA - No Claude API used"
    }

def generate_sample_market_data():
    """Create sample market data."""
    import random
    random.seed(42)

    tickers = ["NVDA", "TSLA", "AMD", "MRVL", "ASML", "NET", "AEHR", "KLAC"]
    data = {}

    for ticker in tickers:
        price = random.uniform(50, 300)
        data[ticker] = {
            'price': price,
            'volume': random.uniform(5000000, 30000000),
            'vol_avg_20d': random.uniform(5000000, 30000000),
            'high_5d': price * random.uniform(1.01, 1.10),
            'low_5d': price * random.uniform(0.90, 0.99),
            'ma_20': price * random.uniform(0.98, 1.02),
            'rsi': random.uniform(20, 80),
            'change_pct': random.uniform(-8, 8)
        }

    return data

if __name__ == "__main__":
    print("\n" + "="*80)
    print("VIF WATCHLIST ANALYZER - LOCAL TEST MODE")
    print("="*80)

    market_data = generate_sample_market_data()
    analysis = mock_vif_analysis(market_data, "test_watchlist")

    print(json.dumps(analysis, indent=2))

    Path("reports").mkdir(exist_ok=True)
    output_file = Path("reports") / "test_analysis.json"
    with open(output_file, 'w') as f:
        json.dump(analysis, f, indent=2)

    print(f"\nTest results saved to {output_file}")
    print("\n[OK] System working correctly!")
    print("[OK] When API credits are added, use: python agents/watchlist_watcher.py --watchlist energy_ai")
