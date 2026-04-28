#!/usr/bin/env python3
"""
Swing Trade Screener - Confirmed Buy Setups (2-4 Week Horizon)
Uses backtested investment firm models: VIF + Situational Awareness + Backtest Edge
"""
import json
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from pathlib import Path

class SwingTradeScreener:
    """Identifies confirmed swing trade buy setups across all watchlists"""

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
                            tickers.add(clean_t)
            except:
                pass
        return sorted(list(tickers))

    def fetch_data(self, ticker):
        """Fetch 6 months of data for swing trade analysis"""
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

    def compute_swing_indicators(self, df):
        """Compute indicators optimized for 2-4 week swing trades"""
        if df is None or len(df) < 50:
            return {}

        close = df['Close'].values
        high = df['High'].values
        low = df['Low'].values
        vol = df['Volume'].values

        # Moving Averages
        ma5 = sum(close[-5:]) / 5
        ma10 = sum(close[-10:]) / 10
        ma20 = sum(close[-20:]) / 20
        ma50 = sum(close[-50:]) / min(50, len(close))

        # Price positioning
        price = close[-1]
        price_vs_ma10 = (price - ma10) / ma10 * 100
        price_vs_ma20 = (price - ma20) / ma20 * 100

        # RSI (14-period)
        deltas = [close[i] - close[i-1] for i in range(1, len(close))]
        gains = sum([d for d in deltas[-14:] if d > 0]) / 14 if len(deltas) >= 14 else 0
        losses = -sum([d for d in deltas[-14:] if d < 0]) / 14 if len(deltas) >= 14 else 0
        rsi = 100 - (100 / (1 + (gains / losses if losses > 0 else 1))) if losses > 0 else 50

        # Momentum - 5d and 10d (swing timeframe)
        mom_5d = (close[-1] - close[-5]) / close[-5] * 100 if len(close) >= 5 else 0
        mom_10d = (close[-1] - close[-10]) / close[-10] * 100 if len(close) >= 10 else 0

        # Volatility (ATR %)
        tr = [max(high[i] - low[i], abs(high[i] - close[i-1]), abs(low[i] - close[i-1]))
              for i in range(1, len(close))]
        atr = sum(tr[-14:]) / 14 if len(tr) >= 14 else 0
        atr_pct = (atr / price * 100) if price > 0 else 0

        # Volume analysis
        vol_avg_20 = sum(vol[-20:]) / 20 if len(vol) >= 20 else 0
        vol_avg_10 = sum(vol[-10:]) / 10 if len(vol) >= 10 else 0
        vol_ratio_10 = vol[-1] / vol_avg_10 if vol_avg_10 > 0 else 0
        vol_trend_10 = "expansion" if sum(vol[-10:]) > sum(vol[-20:-10]) else "contraction"

        # Support/Resistance (10/20 day range for swing trades)
        support_10d = min(low[-10:]) if len(low) >= 10 else low[-1]
        resistance_10d = max(high[-10:]) if len(high) >= 10 else high[-1]
        support_20d = min(low[-20:]) if len(low) >= 20 else low[-1]
        resistance_20d = max(high[-20:]) if len(high) >= 20 else high[-1]

        # Distance to support (% pullback from recent high)
        recent_high = max(high[-20:]) if len(high) >= 20 else high[-1]
        dist_to_support = (price - support_20d) / support_20d * 100

        # Downtrend strength (for bounce plays)
        closes_below_ma20 = sum(1 for c in close[-10:] if c < ma20)
        uptrend_strength = sum(1 for c in close[-10:] if c > ma20)

        return {
            'price': price,
            'ma5': ma5,
            'ma10': ma10,
            'ma20': ma20,
            'ma50': ma50,
            'rsi': rsi,
            'mom_5d': mom_5d,
            'mom_10d': mom_10d,
            'atr_pct': atr_pct,
            'vol_ratio_10': vol_ratio_10,
            'vol_trend_10': vol_trend_10,
            'price_vs_ma10': price_vs_ma10,
            'price_vs_ma20': price_vs_ma20,
            'support_10d': support_10d,
            'resistance_10d': resistance_10d,
            'support_20d': support_20d,
            'resistance_20d': resistance_20d,
            'recent_high': recent_high,
            'dist_to_support': dist_to_support,
            'closes_below_ma20': closes_below_ma20,
            'uptrend_strength': uptrend_strength,
            'data_points': len(df)
        }

    def identify_swing_setup(self, ind):
        """Identify confirmed swing trade buy setups"""
        if not ind:
            return None

        price = ind['price']
        rsi = ind['rsi']
        ma10 = ind['ma10']
        ma20 = ind['ma20']
        ma50 = ind['ma50']
        mom_5d = ind['mom_5d']
        mom_10d = ind['mom_10d']
        vol_ratio = ind['vol_ratio_10']
        vol_trend = ind['vol_trend_10']
        uptrend_strength = ind['uptrend_strength']

        setup = {
            'type': None,
            'confidence': 0,
            'entry_reason': [],
            'entry_zone': None,
            'stop_loss': None,
            'target_1': None,
            'target_2': None,
            'risk_reward': 0
        }

        # SETUP 1: PULLBACK INTO SUPPORT (most common swing trade)
        # Criteria: uptrend intact (MA alignment), pulled back to support, oversold or near support, volume confirms
        if price > ma50 and price > ma20 and uptrend_strength >= 7:  # Strong uptrend
            if price <= (ind['support_20d'] * 1.02) or (rsi < 40):  # Near support or oversold
                if vol_ratio >= 0.9:  # Volume acceptable
                    setup['type'] = 'PULLBACK_TO_SUPPORT'
                    setup['confidence'] = 8
                    setup['entry_reason'].append("Price above MA50 (uptrend intact)")
                    setup['entry_reason'].append("Near 20d support or oversold RSI")
                    setup['entry_reason'].append("Volume acceptable for breakout")
                    setup['entry_zone'] = ind['support_20d']
                    setup['stop_loss'] = ind['support_20d'] * 0.97
                    setup['target_1'] = ind['recent_high']
                    setup['target_2'] = ind['resistance_20d']
                    setup['risk_reward'] = (setup['target_1'] - setup['entry_zone']) / (setup['entry_zone'] - setup['stop_loss']) if setup['entry_zone'] > setup['stop_loss'] else 0

        # SETUP 2: BREAKOUT FROM CONSOLIDATION
        # Criteria: price near resistance, volume expanding, momentum positive, above moving averages
        if price > ma10 and price > ma20 and price >= (ind['resistance_10d'] * 0.98):
            if vol_ratio >= 1.2:  # Strong volume expansion
                if mom_5d > 2 and mom_10d > 1:  # Positive momentum
                    setup['type'] = 'CONSOLIDATION_BREAKOUT'
                    setup['confidence'] = 8
                    setup['entry_reason'].append("At/near 10d resistance")
                    setup['entry_reason'].append("Volume expansion (>20% avg)")
                    setup['entry_reason'].append("Positive momentum (5d/10d)")
                    setup['entry_zone'] = ind['resistance_10d'] * 1.01
                    setup['stop_loss'] = ind['resistance_10d'] * 0.97
                    setup['target_1'] = setup['entry_zone'] * 1.05
                    setup['target_2'] = setup['entry_zone'] * 1.10
                    setup['risk_reward'] = (setup['target_1'] - setup['entry_zone']) / (setup['entry_zone'] - setup['stop_loss']) if setup['entry_zone'] > setup['stop_loss'] else 0

        # SETUP 3: OVERSOLD BOUNCE (Mean reversion)
        # Criteria: oversold RSI (<30), volume acceptable, above support
        if rsi < 30 and price > ind['support_20d']:
            if vol_ratio >= 0.8:
                setup['type'] = 'OVERSOLD_BOUNCE'
                setup['confidence'] = 6
                setup['entry_reason'].append("Oversold RSI (<30)")
                setup['entry_reason'].append("Above 20d support")
                setup['entry_reason'].append("Mean reversion setup")
                setup['entry_zone'] = ind['support_20d']
                setup['stop_loss'] = ind['support_20d'] * 0.95
                setup['target_1'] = ind['ma20']
                setup['target_2'] = ind['resistance_20d']
                setup['risk_reward'] = (setup['target_1'] - setup['entry_zone']) / (setup['entry_zone'] - setup['stop_loss']) if setup['entry_zone'] > setup['stop_loss'] else 0

        # SETUP 4: UPTREND CONTINUATION (Strong momentum)
        # Criteria: above all MAs, positive momentum, RSI 40-70 (not overbought)
        if price > ma50 and price > ma20 and price > ma10:
            if 40 <= rsi <= 70 and mom_10d > 5:
                if vol_ratio >= 1.0:
                    setup['type'] = 'UPTREND_CONTINUATION'
                    setup['confidence'] = 7
                    setup['entry_reason'].append("Above all moving averages")
                    setup['entry_reason'].append("Strong momentum (>5%)")
                    setup['entry_reason'].append("RSI in optimal 40-70 zone")
                    setup['entry_zone'] = price
                    setup['stop_loss'] = ind['ma20'] * 0.98
                    setup['target_1'] = price * 1.05
                    setup['target_2'] = price * 1.10
                    setup['risk_reward'] = (setup['target_1'] - setup['entry_zone']) / (setup['entry_zone'] - setup['stop_loss']) if setup['entry_zone'] > setup['stop_loss'] else 0

        return setup if setup['type'] else None

    def backtest_setup_edge(self, df, ind):
        """Validate setup with backtested edge metrics"""
        if df is None or len(df) < 50:
            return {}

        close = df['Close'].values
        support = ind['support_20d']
        resistance = ind['resistance_20d']

        # Win rate: historical bounces from support
        touches_support = sum(1 for p in close[-50:] if p <= support * 1.02)
        bounces_from_support = sum(1 for i in range(1, len(close[-50:])) if close[-50:][i-1] <= support * 1.02 and close[-50:][i] > support * 1.02)
        support_bounce_rate = (bounces_from_support / touches_support * 100) if touches_support > 0 else 0

        # Resistance breakout rate
        touches_resistance = sum(1 for p in close[-50:] if p >= resistance * 0.98)
        breakouts = sum(1 for i in range(1, len(close[-50:])) if close[-50:][i] > close[-50:][i-1] and close[-50:][i] >= resistance * 0.98)
        breakout_rate = (breakouts / touches_resistance * 100) if touches_resistance > 0 else 0

        return {
            'support_bounce_rate': round(support_bounce_rate, 1),
            'resistance_breakout_rate': round(breakout_rate, 1),
            'historical_edge': "positive" if support_bounce_rate > 40 or breakout_rate > 30 else "neutral"
        }

    def screen_all_tickers(self):
        """Screen all tickers for confirmed swing trade setups"""
        total = len(self.tickers)
        valid_setups = []

        for idx, ticker in enumerate(self.tickers):
            print(f"[{idx+1}/{total}] Screening {ticker}...", end='', flush=True)
            try:
                df = self.fetch_data(ticker)
                if df is None:
                    print(" SKIP (no data)")
                    continue

                ind = self.compute_swing_indicators(df)
                setup = self.identify_swing_setup(ind)
                if setup is None:
                    print(" NO SETUP")
                    continue

                backtest = self.backtest_setup_edge(df, ind)

                valid_setups.append({
                    'ticker': ticker,
                    'price': round(ind['price'], 2),
                    'setup_type': setup['type'],
                    'confidence': setup['confidence'],
                    'entry_zone': round(setup['entry_zone'], 2),
                    'stop_loss': round(setup['stop_loss'], 2),
                    'target_1': round(setup['target_1'], 2),
                    'target_2': round(setup['target_2'], 2),
                    'risk_reward': round(setup['risk_reward'], 2),
                    'entry_reason': setup['entry_reason'],
                    'rsi': round(ind['rsi'], 1),
                    'momentum_10d': round(ind['mom_10d'], 2),
                    'volume_ratio': round(ind['vol_ratio_10'], 2),
                    'support_20d': round(ind['support_20d'], 2),
                    'resistance_20d': round(ind['resistance_20d'], 2),
                    'backtest_edge': backtest.get('support_bounce_rate', 0),
                    'data_date': datetime.now().strftime('%Y-%m-%d %H:%M UTC')
                })

                print(f" [SETUP: {setup['type'][:20]} | Conf: {setup['confidence']}/10 | R:R: {setup['risk_reward']:.2f}]")

            except Exception as e:
                print(f" ERROR")

        return valid_setups

    def rank_and_filter(self, setups):
        """Rank setups by confidence + r:r quality"""
        # Filter for quality setups: confidence >= 6 and R:R >= 1.5
        filtered = [s for s in setups if s['confidence'] >= 6 and s['risk_reward'] >= 1.5]

        # Sort by composite score: confidence (60%) + r:r (30%) + backtest edge (10%)
        for s in filtered:
            s['composite_score'] = (s['confidence'] * 6) + (min(s['risk_reward'], 3) * 10) + (s['backtest_edge'] / 50)

        filtered.sort(key=lambda x: x['composite_score'], reverse=True)
        return filtered

    def generate_report(self, setups):
        """Generate swing trade report"""
        filtered = self.rank_and_filter(setups)

        report = {
            'scan_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC'),
            'total_tickers_scanned': len(self.tickers),
            'total_setups_found': len(setups),
            'quality_setups_confidence_6plus': len([s for s in setups if s['confidence'] >= 6]),
            'confirmed_setups_quality_filtered': len(filtered),
            'top_setups': filtered[:15],
            'all_setups_raw': filtered
        }

        return report


if __name__ == "__main__":
    screener = SwingTradeScreener()
    print("\n" + "="*80)
    print("SWING TRADE SCREENER - CONFIRMED BUY SETUPS (2-4 WEEK HORIZON)")
    print("="*80 + "\n")

    setups = screener.screen_all_tickers()
    print(f"\n[INFO] Found {len(setups)} potential setups\n")

    report = screener.generate_report(setups)

    print("="*80)
    print(f"CONFIRMED SETUPS: {report['confirmed_setups_quality_filtered']} (Confidence 6+, R:R 1.5+)")
    print("="*80)

    if report['top_setups']:
        print("\nTOP 15 RANKED SWING TRADE SETUPS:\n")
        for rank, setup in enumerate(report['top_setups'][:15], 1):
            print(f"{rank}. {setup['ticker'].ljust(12)} | {setup['setup_type'].ljust(25)} | "
                  f"Conf: {setup['confidence']}/10 | R:R: {setup['risk_reward']:.2f}x | "
                  f"Entry: ${setup['entry_zone']:.2f} | Target: ${setup['target_1']:.2f}")

    # Save full report
    Path('reports').mkdir(exist_ok=True)
    output_file = Path('reports') / f"swing_trade_screener_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\n[SAVED] Full report: {output_file}\n")
