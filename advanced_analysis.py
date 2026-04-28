#!/usr/bin/env python3
"""Advanced watchlist analysis: VIF + Situational Awareness + Alpha Generation"""
import json
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from pathlib import Path

class AdvancedAnalyzer:
    """Multi-framework trading analysis."""

    def __init__(self):
        self.watchlists = {
            'vantage_portfolio': self.load_watchlist('vantage_portfolio'),
            'ai_verticals': self.load_watchlist('ai_verticals'),
            'energy_ai': self.load_watchlist('energy_ai'),
        }

    def load_watchlist(self, name):
        """Load watchlist from file."""
        try:
            with open(f'watchlists/{name}.txt', 'r') as f:
                tickers = f.read().replace('\n', ',').split(',')
            return [t.strip() for t in tickers if t.strip() and not t.startswith('###')]
        except:
            return []

    def fetch_data(self, ticker):
        """Fetch market data."""
        try:
            df = yf.download(ticker.split(':')[-1], period="3mo", progress=False)
            if df is None or len(df) < 10:
                return None
            if isinstance(df.columns, pd.MultiIndex):
                ticker_clean = ticker.split(':')[-1]
                close_col = ('Close', ticker_clean)
                vol_col = ('Volume', ticker_clean)
                if close_col not in df.columns:
                    return None
                df_clean = pd.DataFrame({
                    'Close': df[close_col],
                    'High': df[('High', ticker_clean)],
                    'Low': df[('Low', ticker_clean)],
                    'Volume': df[vol_col]
                })
            else:
                df_clean = df[['Close', 'High', 'Low', 'Volume']].copy()
            return df_clean.dropna()
        except:
            return None

    def compute_indicators(self, df):
        """Compute technical indicators."""
        if df is None or len(df) < 14:
            return {}

        close = df['Close'].values
        high = df['High'].values
        low = df['Low'].values
        vol = df['Volume'].values

        # RSI
        deltas = [close[i] - close[i-1] for i in range(1, len(close))]
        gains = sum([d for d in deltas[-14:] if d > 0]) / 14 if len(deltas) >= 14 else 0
        losses = -sum([d for d in deltas[-14:] if d < 0]) / 14 if len(deltas) >= 14 else 0
        rsi = 100 - (100 / (1 + (gains / losses if losses > 0 else 1))) if losses > 0 else 50

        # Moving Averages
        ma20 = sum(close[-20:]) / min(20, len(close))
        ma50 = sum(close[-50:]) / min(50, len(close))
        ma200 = sum(close[-200:]) / min(200, len(close))

        # Volatility
        returns = [(close[i] - close[i-1]) / close[i-1] for i in range(1, len(close))]
        volatility = (sum([r**2 for r in returns[-20:]]) / 20) ** 0.5 if len(returns) >= 20 else 0

        # Volume analysis
        vol_avg = sum(vol[-20:]) / min(20, len(vol))
        vol_ratio = vol[-1] / vol_avg if vol_avg > 0 else 0

        # Price momentum
        mom_5 = (close[-1] - close[-5]) / close[-5] if len(close) >= 5 else 0
        mom_20 = (close[-1] - close[-20]) / close[-20] if len(close) >= 20 else 0

        # Support/Resistance
        support = min(low[-20:]) if len(low) >= 20 else low[-1]
        resistance = max(high[-20:]) if len(high) >= 20 else high[-1]
        price = close[-1]

        return {
            'price': price,
            'rsi': rsi,
            'ma20': ma20,
            'ma50': ma50,
            'ma200': ma200,
            'volatility': volatility,
            'volume_ratio': vol_ratio,
            'momentum_5d': mom_5,
            'momentum_20d': mom_20,
            'support': support,
            'resistance': resistance,
            'data_points': len(df)
        }

    def vif_analysis(self, indicators):
        """VIF Framework analysis."""
        if not indicators:
            return {}

        price = indicators['price']
        rsi = indicators['rsi']
        ma20 = indicators['ma20']
        vol_ratio = indicators['volume_ratio']
        mom = indicators['momentum_5d']

        # Gamma regime
        if rsi > 60 and price > ma20:
            gamma = "positive"
        elif rsi < 40 and price < ma20:
            gamma = "negative"
        else:
            gamma = "transition"

        # Structural levels
        support = indicators['support']
        resistance = indicators['resistance']
        distance_to_support = (price - support) / support * 100
        distance_to_resistance = (resistance - price) / resistance * 100

        if distance_to_support < 5:
            level_type = "support"
        elif distance_to_resistance < 5:
            level_type = "resistance"
        else:
            level_type = "neutral"

        # Volume
        vol_signal = "strong" if vol_ratio > 1.5 else "weak"

        return {
            'gamma_regime': gamma,
            'level_type': level_type,
            'volume_signal': vol_signal
        }

    def situational_awareness(self, ticker, indicators):
        """Situational Awareness LP model analysis."""
        if not indicators:
            return {}

        rsi = indicators['rsi']
        price = indicators['price']
        support = indicators['support']
        resistance = indicators['resistance']
        vol_ratio = indicators['volume_ratio']
        volatility = indicators['volatility']
        mom_5d = indicators['momentum_5d']
        mom_20d = indicators['momentum_20d']

        # Market microstructure
        trend_strength = "strong" if abs(mom_20d) > 0.05 else "weak"
        pullback = "yes" if mom_5d < 0 and mom_20d > 0 else "no"
        volatility_regime = "high" if volatility > 0.02 else "normal"

        # Price positioning
        price_pct_support = (price - support) / support * 100 if support > 0 else 0
        price_pct_resistance = (resistance - price) / resistance * 100 if resistance > 0 else 0

        # Signal strength
        signal_strength = 0
        if rsi > 70 or rsi < 30:
            signal_strength += 2
        if vol_ratio > 1.5:
            signal_strength += 1
        if abs(mom_20d) > 0.05:
            signal_strength += 1

        return {
            'trend_strength': trend_strength,
            'pullback_opportunity': pullback,
            'volatility_regime': volatility_regime,
            'price_pct_support': round(price_pct_support, 2),
            'price_pct_resistance': round(price_pct_resistance, 2),
            'signal_strength': signal_strength
        }

    def backtest_signals(self, df, indicators):
        """Backtest historical signal performance."""
        if df is None or len(df) < 50:
            return {}

        close = df['Close'].values
        recent_high = max(close[-20:])
        recent_low = min(close[-20:])
        support = indicators.get('support', recent_low)
        resistance = indicators.get('resistance', recent_high)

        # Win rate simulation (based on mean reversion)
        touches_support = sum(1 for p in close[-50:] if p <= support * 1.01)
        touches_resistance = sum(1 for p in close[-50:] if p >= resistance * 0.99)

        support_bounce_rate = (touches_support / 50 * 100) if touches_support > 0 else 10
        resistance_rejection_rate = (touches_resistance / 50 * 100) if touches_resistance > 0 else 15

        return {
            'support_bounce_rate': round(support_bounce_rate, 1),
            'resistance_rejection_rate': round(resistance_rejection_rate, 1),
            'backtest_edge': "positive" if support_bounce_rate > 20 else "neutral"
        }

    def generate_alpha(self, ticker, indicators, vif, situational, backtest):
        """Generate alpha sources."""
        alpha_sources = []

        # Mean reversion alpha
        if indicators.get('rsi', 50) < 30:
            alpha_sources.append({
                'type': 'mean_reversion',
                'edge': 'oversold_bounce',
                'confidence': 'high',
                'target_move': '+3-5%'
            })

        # Momentum alpha
        if indicators.get('momentum_20d', 0) > 0.05:
            alpha_sources.append({
                'type': 'momentum',
                'edge': 'trend_continuation',
                'confidence': 'medium',
                'target_move': '+2-4%'
            })

        # Volatility alpha
        if indicators.get('volatility', 0) > 0.02:
            alpha_sources.append({
                'type': 'volatility',
                'edge': 'vol_expansion_trade',
                'confidence': 'medium',
                'target_move': '+1-3% (on reversal)'
            })

        return alpha_sources

    def rank_score(self, ticker, indicators, vif, situational, backtest):
        """Calculate composite ranking score."""
        score = 0
        details = []

        # RSI component (0-20 pts)
        rsi = indicators.get('rsi', 50)
        if rsi < 30:
            score += 15
            details.append(f"Oversold RSI {rsi:.1f} (+15)")
        elif rsi > 70:
            score += 5
            details.append(f"Overbought RSI {rsi:.1f} (+5)")
        else:
            score += 10
            details.append(f"Neutral RSI {rsi:.1f} (+10)")

        # Momentum component (0-20 pts)
        mom_20d = indicators.get('momentum_20d', 0)
        if mom_20d > 0.05:
            score += 15
            details.append(f"Strong uptrend +{mom_20d*100:.1f}% (+15)")
        elif mom_20d < -0.05:
            score += 5
            details.append(f"Downtrend {mom_20d*100:.1f}% (+5)")
        else:
            score += 8
            details.append(f"Consolidation (+8)")

        # Volume component (0-15 pts)
        vol_ratio = indicators.get('volume_ratio', 1)
        if vol_ratio > 1.5:
            score += 12
            details.append(f"High volume {vol_ratio:.1f}x (+12)")
        else:
            score += 6
            details.append(f"Normal volume (+6)")

        # Volatility component (0-15 pts)
        volatility = indicators.get('volatility', 0)
        if volatility > 0.025:
            score += 10
            details.append(f"High volatility (+10)")
        else:
            score += 5
            details.append(f"Normal volatility (+5)")

        # Signal strength (0-15 pts)
        signal = situational.get('signal_strength', 0)
        score += signal * 3
        details.append(f"Signal strength {signal}/4 (+{signal*3})")

        # Backtest edge (0-20 pts)
        edge = backtest.get('backtest_edge', 'neutral')
        if edge == 'positive':
            score += 15
            details.append(f"Positive backtest edge (+15)")
        else:
            score += 5
            details.append(f"Neutral backtest edge (+5)")

        return score, details

    def analyze_watchlist(self, watchlist_name):
        """Analyze entire watchlist."""
        tickers = self.watchlists.get(watchlist_name, [])
        results = []

        print(f"\nAnalyzing {watchlist_name}: {len(tickers)} tickers")

        for i, ticker in enumerate(tickers[:15]):  # Limit to 15 for speed
            print(f"  [{i+1}/{min(15, len(tickers))}] {ticker}...", end='', flush=True)

            try:
                df = self.fetch_data(ticker)
                if df is None or len(df) < 14:
                    print(" SKIP (insufficient data)")
                    continue

                indicators = self.compute_indicators(df)
                vif = self.vif_analysis(indicators)
                situational = self.situational_awareness(ticker, indicators)
                backtest = self.backtest_signals(df, indicators)
                alpha = self.generate_alpha(ticker, indicators, vif, situational, backtest)
                score, score_details = self.rank_score(ticker, indicators, vif, situational, backtest)

                results.append({
                    'ticker': ticker,
                    'score': score,
                    'indicators': indicators,
                    'vif': vif,
                    'situational': situational,
                    'backtest': backtest,
                    'alpha_sources': alpha,
                    'score_breakdown': score_details
                })
                print(" OK")

            except Exception as e:
                print(f" ERROR")

        # Sort by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def format_report(self, watchlist_name, results):
        """Format analysis report."""
        top5 = results[:5]
        report = {
            'watchlist': watchlist_name,
            'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'tickers_analyzed': len(results),
            'top_5_ranked': []
        }

        for rank, result in enumerate(top5, 1):
            ticker = result['ticker']
            indicators = result['indicators']

            top_report = {
                'rank': rank,
                'ticker': ticker,
                'composite_score': result['score'],
                'price': round(indicators.get('price', 0), 2),
                'current_metrics': {
                    'rsi': round(indicators.get('rsi', 50), 1),
                    'momentum_5d': f"{indicators.get('momentum_5d', 0)*100:.1f}%",
                    'momentum_20d': f"{indicators.get('momentum_20d', 0)*100:.1f}%",
                    'volatility': f"{indicators.get('volatility', 0)*100:.2f}%",
                    'volume_ratio': round(indicators.get('volume_ratio', 1), 2),
                    'support': round(indicators.get('support', 0), 2),
                    'resistance': round(indicators.get('resistance', 0), 2)
                },
                'vif_framework': result['vif'],
                'situational_awareness': {
                    'trend_strength': result['situational'].get('trend_strength'),
                    'pullback_opportunity': result['situational'].get('pullback_opportunity'),
                    'volatility_regime': result['situational'].get('volatility_regime'),
                    'signal_strength': result['situational'].get('signal_strength')
                },
                'backtest_edge': result['backtest'],
                'alpha_sources': result['alpha_sources'],
                'score_breakdown': result['score_breakdown']
            }
            report['top_5_ranked'].append(top_report)

        return report

if __name__ == "__main__":
    analyzer = AdvancedAnalyzer()

    all_results = {}

    for watchlist in ['vantage_portfolio', 'ai_verticals', 'energy_ai']:
        print(f"\n{'='*80}")
        print(f"ANALYZING: {watchlist.upper()}")
        print(f"{'='*80}")

        results = analyzer.analyze_watchlist(watchlist)
        report = analyzer.format_report(watchlist, results)
        all_results[watchlist] = report

        print(f"\n{watchlist.upper()} - TOP 5 RANKED")
        print("="*80)
        print(json.dumps(report, indent=2))

    # Save consolidated report
    Path('reports').mkdir(exist_ok=True)
    output_file = Path('reports') / f"advanced_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2)

    print(f"\n\nComplete analysis saved to {output_file}")
