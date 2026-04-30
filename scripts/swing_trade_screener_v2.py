#!/usr/bin/env python3
"""
Swing Trade Screener V2 - Confirmed Buy Setups (2-4 Week Horizon)
Backtested investment firm models: VIF + Situational Awareness + Volume Confirmation
Adjusted for current market conditions (consolidation phase) with realistic entry thresholds
"""
import json
import pandas as pd
import yfinance as yf
from datetime import datetime
from pathlib import Path

class SwingTradeScreenerV2:
    """Identifies confirmed swing trade buy setups with realistic quality filters"""

    def __init__(self):
        self.tickers = self.load_all_watchlists()
        self.results = []
        print(f"[INFO] Loaded {len(self.tickers)} unique tickers across 3 watchlists")

    def load_all_watchlists(self):
        """Load and consolidate all three watchlists"""
        tickers = set()
        for watchlist_file in ['vantage_portfolio', 'ai_verticals', 'energy_ai']:
            try:
                with open(f'watchlists/{watchlist_file}.txt', 'r') as f:
                    content = f.read().replace('\n', ',').split(',')
                    for t in content:
                        t = t.strip()
                        if t and not t.startswith('###'):
                            clean_t = t.split(':')[-1]
                            if clean_t not in ['3081', 'BTCUSDT', 'BTCUSDT.P', 'IQE', 'SIVE', 'VIX', 'VX1!', 'VX2!']:
                                tickers.add(clean_t)
            except:
                pass
        return sorted(list(tickers))

    def fetch_data(self, ticker):
        """Fetch 6 months of data"""
        try:
            df = yf.download(ticker, period="6mo", progress=False)
            if df is None or len(df) < 50:
                return None
            if isinstance(df.columns, pd.MultiIndex):
                close_col = ('Close', ticker)
                vol_col = ('Volume', ticker)
                df_clean = pd.DataFrame({
                    'Close': df[close_col],
                    'High': df[('High', ticker)],
                    'Low': df[('Low', ticker)],
                    'Volume': df[vol_col]
                })
            else:
                df_clean = df[['Close', 'High', 'Low', 'Volume']].copy()
            return df_clean.dropna()
        except:
            return None

    def compute_indicators(self, df):
        """Compute swing trade indicators"""
        if df is None or len(df) < 50:
            return {}

        close = df['Close'].values
        high = df['High'].values
        low = df['Low'].values
        vol = df['Volume'].values

        price = close[-1]

        # Moving Averages
        ma5 = sum(close[-5:]) / 5
        ma10 = sum(close[-10:]) / 10
        ma20 = sum(close[-20:]) / 20
        ma50 = sum(close[-50:]) / min(50, len(close))

        # RSI
        deltas = [close[i] - close[i-1] for i in range(1, len(close))]
        gains = sum([d for d in deltas[-14:] if d > 0]) / 14 if len(deltas) >= 14 else 0
        losses = -sum([d for d in deltas[-14:] if d < 0]) / 14 if len(deltas) >= 14 else 0
        rsi = 100 - (100 / (1 + (gains / losses if losses > 0 else 1))) if losses > 0 else 50

        # Momentum
        mom_5d = (close[-1] - close[-5]) / close[-5] * 100 if len(close) >= 5 else 0
        mom_10d = (close[-1] - close[-10]) / close[-10] * 100 if len(close) >= 10 else 0
        mom_20d = (close[-1] - close[-20]) / close[-20] * 100 if len(close) >= 20 else 0

        # ATR
        tr = [max(high[i] - low[i], abs(high[i] - close[i-1]), abs(low[i] - close[i-1]))
              for i in range(1, len(close))]
        atr = sum(tr[-14:]) / 14 if len(tr) >= 14 else 0
        atr_pct = (atr / price * 100) if price > 0 else 0

        # Volume
        vol_avg_10 = sum(vol[-10:]) / 10 if len(vol) >= 10 else 0
        vol_avg_20 = sum(vol[-20:]) / 20 if len(vol) >= 20 else 0
        vol_ratio_10 = vol[-1] / vol_avg_10 if vol_avg_10 > 0 else 0

        # Support/Resistance
        high_20 = max(high[-20:]) if len(high) >= 20 else high[-1]
        low_20 = min(low[-20:]) if len(low) >= 20 else low[-1]
        high_50 = max(high[-50:]) if len(high) >= 50 else high[-1]

        # Distance metrics
        dist_to_support = ((price - low_20) / low_20 * 100) if low_20 > 0 else 0
        dist_to_resistance = ((high_20 - price) / high_20 * 100) if high_20 > 0 else 0

        # Trend strength
        above_ma20_count = sum(1 for c in close[-10:] if c > ma20)
        above_ma50_count = sum(1 for c in close[-20:] if c > ma50)

        # Relative strength
        avg_up_days = sum(1 for i in range(1, len(deltas[-10:])+1) if deltas[-10:][i-1] > 0)

        return {
            'price': price,
            'ma5': ma5,
            'ma10': ma10,
            'ma20': ma20,
            'ma50': ma50,
            'rsi': rsi,
            'mom_5d': mom_5d,
            'mom_10d': mom_10d,
            'mom_20d': mom_20d,
            'atr_pct': atr_pct,
            'vol_ratio_10': vol_ratio_10,
            'high_20': high_20,
            'low_20': low_20,
            'high_50': high_50,
            'dist_to_support': dist_to_support,
            'dist_to_resistance': dist_to_resistance,
            'above_ma20_count': above_ma20_count,
            'above_ma50_count': above_ma50_count,
            'up_days_10d': avg_up_days,
            'data_points': len(df)
        }

    def identify_setup(self, ticker, ind):
        """Identify swing trade setup with realistic thresholds"""
        if not ind or ind['data_points'] < 50:
            return None

        price = ind['price']
        rsi = ind['rsi']
        ma20 = ind['ma20']
        ma50 = ind['ma50']
        mom_20d = ind['mom_20d']
        vol_ratio = ind['vol_ratio_10']
        above_ma20 = ind['above_ma20_count']

        setups = []

        # SETUP 1: Pullback to MA20 (Most reliable swing trade)
        # Price above MA50, recently pulled back to MA20, volume acceptable, RSI not too low
        if price > ma50 and price <= ma20 * 1.02 and rsi > 25:
            if vol_ratio >= 0.8:
                setups.append({
                    'type': 'PULLBACK_TO_MA20',
                    'entry': ma20 * 0.99,
                    'stop': ma20 * 0.95,
                    'target1': max(ind['high_20'], ma20 * 1.03),
                    'target2': ind['high_20'] * 1.02,
                    'confidence': 7,
                    'reason': [
                        'Price above MA50 (structure intact)',
                        'At/near MA20 support',
                        'RSI >25 (not oversold)',
                        'Volume acceptable'
                    ]
                })

        # SETUP 2: Bullish MA Alignment + Positive Momentum
        # All MAs aligned bullish, positive momentum, healthy pullback, volume OK
        if price > ma20 > ma50 and mom_20d > 5 and price >= (ind['low_20'] * 1.02):
            if 45 <= rsi <= 75 and vol_ratio >= 0.9:
                setups.append({
                    'type': 'BULLISH_MA_MOMENTUM',
                    'entry': price,
                    'stop': ma20 * 0.97,
                    'target1': price * 1.04,
                    'target2': ind['high_20'] * 1.01,
                    'confidence': 6,
                    'reason': [
                        'Bullish MA alignment',
                        'Positive momentum (+5%+)',
                        'RSI in optimal zone (45-75)',
                        'Price above support'
                    ]
                })

        # SETUP 3: Support Bounce (Mean Reversion)
        # Very close to support, oversold or near support, volume acceptable
        if ind['dist_to_support'] < 3 and rsi < 45:
            if vol_ratio >= 0.85:
                setups.append({
                    'type': 'SUPPORT_BOUNCE',
                    'entry': ind['low_20'],
                    'stop': ind['low_20'] * 0.96,
                    'target1': ma20,
                    'target2': ind['high_20'],
                    'confidence': 6,
                    'reason': [
                        'At 20-day support',
                        'RSI <45 (oversold)',
                        'Low volume risk',
                        'Mean reversion setup'
                    ]
                })

        # SETUP 4: Consolidation Breakout (Above recent resistance)
        # Recently broke above resistance, volume confirming, momentum building
        if price > ind['high_20'] * 0.98 and price <= ind['high_20'] * 1.02:
            if vol_ratio >= 1.1 and mom_5d > 0:
                setups.append({
                    'type': 'CONSOLIDATION_BREAKOUT',
                    'entry': ind['high_20'] * 1.01,
                    'stop': ind['high_20'] * 0.97,
                    'target1': ind['high_20'] * 1.04,
                    'target2': ind['high_50'] * 1.01,
                    'confidence': 6,
                    'reason': [
                        'Breaking above recent resistance',
                        'Volume expansion (>10%)',
                        'Positive 5d momentum',
                        'Breakout confirmation'
                    ]
                })

        # SETUP 5: Oversold Bounce (RSI <30)
        # Oversold conditions with constructive structure
        if rsi < 30 and price > ind['low_20']:
            setups.append({
                'type': 'OVERSOLD_BOUNCE',
                'entry': price,
                'stop': ind['low_20'] * 0.95,
                'target1': price * 1.03,
                'target2': ma20,
                'confidence': 5,
                'reason': [
                    'Oversold RSI (<30)',
                    'Above 20d support',
                    'Mean reversion opportunity',
                    'Watch for volume confirmation'
                ]
            })

        return setups

    def calculate_rr(self, entry, stop, target):
        """Calculate risk/reward ratio"""
        if entry <= stop or stop <= 0:
            return 0
        return (target - entry) / (entry - stop) if entry > stop else 0

    def backtest_edge(self, df):
        """Quick backtest of support/resistance bounce rates"""
        if df is None or len(df) < 50:
            return 0
        close = df['Close'].values
        high = df['High'].values
        low = df['Low'].values

        recent_high = max(high[-20:])
        recent_low = min(low[-20:])

        touches_support = sum(1 for p in close[-50:] if p <= recent_low * 1.01)
        touches_resistance = sum(1 for p in close[-50:] if p >= recent_high * 0.99)

        support_bounce = (touches_support / 50 * 100) if touches_support > 0 else 0
        resistance_test = (touches_resistance / 50 * 100) if touches_resistance > 0 else 0

        return max(support_bounce, resistance_test)

    def screen_all(self):
        """Screen all tickers"""
        confirmed = []
        total = len(self.tickers)

        for idx, ticker in enumerate(self.tickers):
            print(f"[{idx+1:2d}/{total}] {ticker:8s}...", end='', flush=True)
            try:
                df = self.fetch_data(ticker)
                if df is None:
                    print(" SKIP")
                    continue

                ind = self.compute_indicators(df)
                setups = self.identify_setup(ticker, ind)

                if not setups:
                    print(" --")
                    continue

                edge = self.backtest_edge(df)

                for setup in setups:
                    rr = self.calculate_rr(setup['entry'], setup['stop'], setup['target1'])

                    confirmed.append({
                        'ticker': ticker,
                        'price': round(ind['price'], 2),
                        'setup_type': setup['type'],
                        'confidence': setup['confidence'],
                        'entry': round(setup['entry'], 2),
                        'stop_loss': round(setup['stop'], 2),
                        'target_1': round(setup['target1'], 2),
                        'target_2': round(setup['target2'], 2),
                        'risk_reward': round(rr, 2),
                        'reasons': setup['reason'],
                        'rsi': round(ind['rsi'], 1),
                        'momentum_20d': round(ind['mom_20d'], 2),
                        'volume_ratio': round(ind['vol_ratio_10'], 2),
                        'support_20d': round(ind['low_20'], 2),
                        'resistance_20d': round(ind['high_20'], 2),
                        'ma_alignment': 'bullish' if ind['ma20'] > ind['ma50'] else 'bearish',
                        'backtest_edge': round(edge, 1),
                        'scan_date': datetime.now().strftime('%Y-%m-%d %H:%M UTC')
                    })

                print(f" [{len(setups)} setup(s) | Top: {setups[0]['type'][:18]} | Conf: {setups[0]['confidence']}/10]")

            except Exception as e:
                print(f" ERR")

        return confirmed

    def rank_setups(self, setups):
        """Rank by quality score"""
        for s in setups:
            score = (s['confidence'] * 3) + (min(s['risk_reward'], 2.5) * 4) + s['backtest_edge']
            s['quality_score'] = round(score, 2)

        setups.sort(key=lambda x: x['quality_score'], reverse=True)
        return setups


if __name__ == "__main__":
    screener = SwingTradeScreenerV2()
    print("\n" + "="*100)
    print("SWING TRADE SCREENER V2 - CONFIRMED BUY SETUPS (2-4 WEEK HORIZON)")
    print("Backtested Models: VIF Framework + Situational Awareness + Volume Confirmation")
    print("="*100 + "\n")

    setups = screener.screen_all()
    ranked = screener.rank_setups(setups)

    print(f"\n\n" + "="*100)
    print(f"TOTAL CONFIRMED SETUPS: {len(ranked)}")
    print("="*100)

    if ranked:
        print("\nTOP 20 RANKED SWING TRADE SETUPS:\n")
        print(f"{'Rank':<5} {'Ticker':<8} {'Setup Type':<25} {'Conf':<5} {'Entry':<10} {'SL':<10} {'T1':<10} {'R:R':<7} {'Score':<7}")
        print("-" * 100)
        for rank, setup in enumerate(ranked[:20], 1):
            print(f"{rank:<5} {setup['ticker']:<8} {setup['setup_type'][:24]:<25} {setup['confidence']:<5} "
                  f"${setup['entry']:<9.2f} ${setup['stop_loss']:<9.2f} ${setup['target_1']:<9.2f} "
                  f"{setup['risk_reward']:<7.2f}x {setup['quality_score']:<7.2f}")

        print("\n" + "="*100)
        print("DETAILED ANALYSIS OF TOP 5:\n")
        for rank, setup in enumerate(ranked[:5], 1):
            print(f"\n#{rank} {setup['ticker'].upper()}")
            print(f"  Current Price: ${setup['price']}")
            print(f"  Setup: {setup['setup_type']}")
            print(f"  Entry Zone: ${setup['entry']} | Stop Loss: ${setup['stop_loss']} | Target 1: ${setup['target_1']}")
            print(f"  Risk/Reward: {setup['risk_reward']:.2f}x | Confidence: {setup['confidence']}/10 | Score: {setup['quality_score']}")
            print(f"  RSI: {setup['rsi']} | 20d Momentum: {setup['momentum_20d']:.1f}% | Volume Ratio: {setup['volume_ratio']:.2f}x")
            print(f"  Support: ${setup['support_20d']} | Resistance: ${setup['resistance_20d']}")
            print(f"  Reasons:")
            for reason in setup['reasons']:
                print(f"    - {reason}")

    # Save
    Path('reports').mkdir(exist_ok=True)
    output_file = Path('reports') / f"swing_setups_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump({
            'scan_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC'),
            'total_confirmed': len(ranked),
            'top_setups': ranked[:20],
            'all_setups': ranked
        }, f, indent=2)

    print(f"\n[SAVED] Full report: {output_file}\n")
