#!/usr/bin/env python3
"""Daily Watchlist Analysis - Standardized Model for Swing/Position Trading"""
import json
import pandas as pd
import yfinance as yf
from datetime import datetime
from pathlib import Path
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/daily_watchlist_analysis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DailyWatchlistAnalyzer:
    """Standardized analysis model: trend + momentum + technicals + narrative + setup"""

    def __init__(self):
        self.tickers = ["UMAC", "WULF", "ASTS", "RKLB", "GFS", "NBIS", "NET", "SMCI"]
        self.results = {}

    def fetch_data(self, ticker):
        """Fetch 3-6 months of data for comprehensive analysis"""
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
        """Compute all technical indicators"""
        if df is None or len(df) < 50:
            return {}

        close = df['Close'].values
        high = df['High'].values
        low = df['Low'].values
        vol = df['Volume'].values

        # Moving Averages (trend structure)
        ma5 = sum(close[-5:]) / 5
        ma20 = sum(close[-20:]) / 20
        ma50 = sum(close[-50:]) / min(50, len(close))
        ma200 = sum(close[-200:]) / min(200, len(close)) if len(close) >= 200 else ma50

        # Price positioning
        price = close[-1]
        price_vs_ma20 = (price - ma20) / ma20 * 100
        price_vs_ma50 = (price - ma50) / ma50 * 100
        price_vs_ma200 = (price - ma200) / ma200 * 100

        # RSI (momentum)
        deltas = [close[i] - close[i-1] for i in range(1, len(close))]
        gains = sum([d for d in deltas[-14:] if d > 0]) / 14 if len(deltas) >= 14 else 0
        losses = -sum([d for d in deltas[-14:] if d < 0]) / 14 if len(deltas) >= 14 else 0
        rsi = 100 - (100 / (1 + (gains / losses if losses > 0 else 1))) if losses > 0 else 50

        # Momentum (velocity)
        mom_5d = (close[-1] - close[-5]) / close[-5] * 100 if len(close) >= 5 else 0
        mom_20d = (close[-1] - close[-20]) / close[-20] * 100 if len(close) >= 20 else 0
        mom_50d = (close[-1] - close[-50]) / close[-50] * 100 if len(close) >= 50 else 0

        # Volatility (ATR, standard deviation)
        tr = [max(high[i] - low[i], abs(high[i] - close[i-1]), abs(low[i] - close[i-1]))
              for i in range(1, len(close))]
        atr = sum(tr[-14:]) / 14 if len(tr) >= 14 else 0
        atr_pct = (atr / price * 100) if price > 0 else 0

        returns = [(close[i] - close[i-1]) / close[i-1] for i in range(1, len(close))]
        volatility = (sum([r**2 for r in returns[-20:]]) / 20) ** 0.5 if len(returns) >= 20 else 0

        # Volume (momentum confirmation)
        vol_avg = sum(vol[-20:]) / 20 if len(vol) >= 20 else 0
        vol_ratio = vol[-1] / vol_avg if vol_avg > 0 else 0
        vol_trend = "expansion" if vol[-1] > vol_avg else "contraction"

        # Range analysis
        high_20d = max(high[-20:])
        low_20d = min(low[-20:])
        range_20d = high_20d - low_20d
        pct_range = (price - low_20d) / range_20d * 100 if range_20d > 0 else 50
        range_location = "discount" if pct_range < 33 else ("premium" if pct_range > 67 else "mid-range")

        # Support/Resistance
        support = low_20d
        resistance = high_20d
        midpoint = (high_20d + low_20d) / 2

        return {
            'price': price,
            'ma5': ma5,
            'ma20': ma20,
            'ma50': ma50,
            'ma200': ma200,
            'rsi': rsi,
            'mom_5d': mom_5d,
            'mom_20d': mom_20d,
            'mom_50d': mom_50d,
            'volatility': volatility,
            'atr_pct': atr_pct,
            'volume_ratio': vol_ratio,
            'volume_trend': vol_trend,
            'price_vs_ma20': price_vs_ma20,
            'price_vs_ma50': price_vs_ma50,
            'price_vs_ma200': price_vs_ma200,
            'support': support,
            'resistance': resistance,
            'midpoint': midpoint,
            'pct_range': pct_range,
            'high_20d': high_20d,
            'low_20d': low_20d,
            'range_location': range_location,
            'pct_range': pct_range,
            'data_points': len(df)
        }

    def analyze_trend_structure(self, ind):
        """1. TREND STRUCTURE - Market structure and key levels"""
        if not ind:
            return {}

        price = ind['price']
        ma5 = ind['ma5']
        ma20 = ind['ma20']
        ma50 = ind['ma50']
        ma200 = ind['ma200']

        # Determine trend direction
        if ma5 > ma20 > ma50 > ma200:
            trend = "strong_uptrend"
        elif ma5 < ma20 < ma50 < ma200:
            trend = "strong_downtrend"
        elif ma20 > ma50 > ma200:
            trend = "uptrend"
        elif ma20 < ma50 < ma200:
            trend = "downtrend"
        else:
            trend = "consolidation"

        # Key levels
        structure = {
            'trend': trend,
            'price_vs_ma20': "above" if price > ma20 else "below",
            'price_vs_ma50': "above" if price > ma50 else "below",
            'price_vs_ma200': "above" if price > ma200 else "below",
            'ma_alignment': "bullish" if ma5 > ma20 > ma50 > ma200 else ("bearish" if ma5 < ma20 < ma50 < ma200 else "mixed"),
            'support': round(ind['support'], 2),
            'resistance': round(ind['resistance'], 2),
            'midpoint': round(ind['midpoint'], 2),
            'range_location': "discount" if ind['pct_range'] < 33 else ("premium" if ind['pct_range'] > 67 else "mid-range")
        }

        return structure

    def analyze_momentum(self, ind):
        """2. MOMENTUM - Relative strength, volume, acceleration"""
        if not ind:
            return {}

        rsi = ind['rsi']
        mom_5d = ind['mom_5d']
        mom_20d = ind['mom_20d']
        vol_ratio = ind['volume_ratio']
        vol_trend = ind['volume_trend']

        # RSI regime
        if rsi > 70:
            rsi_regime = "overbought"
        elif rsi < 30:
            rsi_regime = "oversold"
        elif rsi > 60:
            rsi_regime = "bullish"
        elif rsi < 40:
            rsi_regime = "bearish"
        else:
            rsi_regime = "neutral"

        # Momentum direction
        if mom_20d > 10:
            momentum_direction = "strong_acceleration"
        elif mom_20d > 0 and mom_5d > mom_20d:
            momentum_direction = "acceleration"
        elif mom_20d > 0:
            momentum_direction = "positive_drift"
        elif mom_20d < -10:
            momentum_direction = "strong_deceleration"
        elif mom_20d < 0 and mom_5d < mom_20d:
            momentum_direction = "deceleration"
        else:
            momentum_direction = "negative_drift"

        # Volume confirmation
        volume_signal = "strong" if vol_ratio > 1.5 else ("weak" if vol_ratio < 0.8 else "normal")

        momentum = {
            'rsi': round(rsi, 1),
            'rsi_regime': rsi_regime,
            'momentum_5d_pct': round(mom_5d, 2),
            'momentum_20d_pct': round(mom_20d, 2),
            'momentum_direction': momentum_direction,
            'volume_ratio': round(vol_ratio, 2),
            'volume_trend': vol_trend,
            'volume_signal': volume_signal,
            'acceleration_vs_prior': "accelerating" if mom_5d > mom_20d else "decelerating"
        }

        return momentum

    def analyze_technicals(self, ind):
        """3. TECHNICAL POSITIONING - MAs, volatility, range location"""
        if not ind:
            return {}

        volatility = ind['volatility']
        atr_pct = ind['atr_pct']
        price_vs_ma20 = ind['price_vs_ma20']
        ma5 = ind['ma5']
        ma20 = ind['ma20']
        ma50 = ind['ma50']
        ma200 = ind['ma200']

        # MA alignment
        ma_alignment = "bullish" if ma5 > ma20 > ma50 > ma200 else ("bearish" if ma5 < ma20 < ma50 < ma200 else "mixed")

        # Volatility regime
        if volatility > 0.03:
            vol_regime = "high_expansion"
        elif volatility > 0.02:
            vol_regime = "normal_high"
        elif volatility < 0.01:
            vol_regime = "compression"
        else:
            vol_regime = "normal"

        technicals = {
            'ma_structure': ma_alignment,
            'price_distance_to_ma20': round(price_vs_ma20, 2),
            'volatility_regime': vol_regime,
            'atr_pct': round(atr_pct, 2),
            'range_position': ind['range_location'],
            'compression_expansion': "compression" if volatility < 0.015 else "expansion"
        }

        return technicals

    def get_narrative(self, ticker):
        """4. NARRATIVE / CATALYSTS - Industry theme and speculative catalysts"""
        narratives = {
            'UMAC': {
                'theme': 'EV Charging / Clean Energy',
                'catalysts': 'EV infrastructure buildout, charging network expansion, IRA subsidies',
                'sector': 'CleanTech',
                'relative_to_market': 'Small-cap EV play, cyclical'
            },
            'WULF': {
                'theme': 'Crypto Mining / Energy',
                'catalysts': 'Bitcoin halving cycles, energy grid modernization, potential gov support',
                'sector': 'Crypto/Energy',
                'relative_to_market': 'Volatile, correlated to BTC price'
            },
            'ASTS': {
                'theme': 'Satellite Communications',
                'catalysts': 'Direct-to-device satellite, 3GPP standardization, telecom partnerships',
                'sector': 'Space Tech',
                'relative_to_market': 'High-risk growth, long runway'
            },
            'RKLB': {
                'theme': 'Commercial Spaceflight',
                'catalysts': 'Rocket launches, payload contracts, space infrastructure demand',
                'sector': 'Space/Defense',
                'relative_to_market': 'Growth-oriented, government contracts'
            },
            'GFS': {
                'theme': 'Semiconductor Equipment / AI Infrastructure',
                'catalysts': 'AI chip testing, advanced packaging, foundry capacity expansion',
                'sector': 'Semiconductors',
                'relative_to_market': 'Beneficiary of AI capex cycle'
            },
            'NBIS': {
                'theme': 'Specialty Pharma / Biotech',
                'catalysts': 'FDA approvals, clinical trial readouts, partnership announcements',
                'sector': 'Biotech',
                'relative_to_market': 'Binary event risk, clinical trial dependent'
            },
            'NET': {
                'theme': 'Cloud Infrastructure / Cybersecurity',
                'catalysts': 'Cloud adoption, DDoS mitigation demand, enterprise IT spending',
                'sector': 'Cloud/Security',
                'relative_to_market': 'SaaS growth beneficiary'
            },
            'SMCI': {
                'theme': 'AI Infrastructure / Data Center',
                'catalysts': 'AI server demand, data center capex, GPU/TPU integration',
                'sector': 'Semiconductors/AI',
                'relative_to_market': 'Direct AI infrastructure play, strong secular tailwind'
            }
        }
        return narratives.get(ticker, {})

    def generate_trade_setup(self, ind, momentum, trend):
        """5. TRADE SETUP - Entry, target, invalidation if valid"""
        if not all([ind, momentum, trend]):
            return {}

        price = ind['price']
        support = ind['support']
        resistance = ind['resistance']
        rsi = momentum['rsi']
        trend_dir = trend['trend']
        mom_20d = momentum['momentum_20d_pct']

        setup = {}

        # Long setup criteria
        if (trend_dir in ["strong_uptrend", "uptrend"] and
            rsi < 70 and
            mom_20d > 0):
            setup['direction'] = "LONG"
            setup['conviction'] = 8 if rsi < 50 else 6
            setup['entry_zone'] = round(price - (price * 0.02), 2)  # 2% pullback
            setup['invalidation'] = round(support, 2)
            setup['target_1'] = round(resistance, 2)
            setup['target_2'] = round(resistance + (resistance - support) * 0.5, 2)
            setup['risk_reward'] = round((setup['target_1'] - setup['entry_zone']) / (setup['entry_zone'] - setup['invalidation']), 2) if setup['entry_zone'] > setup['invalidation'] else 0

        # Short setup criteria
        elif (trend_dir in ["strong_downtrend", "downtrend"] and
              rsi > 30 and
              mom_20d < 0):
            setup['direction'] = "SHORT"
            setup['conviction'] = 8 if rsi > 50 else 6
            setup['entry_zone'] = round(price + (price * 0.02), 2)
            setup['invalidation'] = round(resistance, 2)
            setup['target_1'] = round(support, 2)
            setup['target_2'] = round(support - (resistance - support) * 0.5, 2)
            setup['risk_reward'] = round((setup['entry_zone'] - setup['target_1']) / (setup['invalidation'] - setup['entry_zone']), 2) if setup['invalidation'] > setup['entry_zone'] else 0

        # Neutral/consolidation
        else:
            setup['direction'] = "NEUTRAL"
            setup['conviction'] = 3
            setup['entry_zone'] = "Await breakout"
            setup['invalidation'] = "N/A (consolidation)"
            setup['target_1'] = "Range breakout target"
            setup['target_2'] = "Extended move target"
            setup['risk_reward'] = 0

        return setup

    def conviction_score(self, trend, momentum, technicals, setup):
        """6. CONVICTION SCORE - Rate 1-10 based on confluence"""
        score = 0

        # Trend alignment (max 3 points)
        if trend.get('ma_alignment') == 'bullish' or trend.get('ma_alignment') == 'bearish':
            score += 3
        elif trend.get('ma_alignment') == 'mixed':
            score += 1

        # Momentum confirmation (max 3 points)
        rsi = momentum.get('rsi', 50)
        if (30 < rsi < 70) and momentum.get('volume_signal') == 'strong':
            score += 3
        elif (rsi > 70 or rsi < 30) and momentum.get('volume_signal') == 'normal':
            score += 1

        # Directional alignment (max 2 points)
        if momentum.get('momentum_direction') in ['acceleration', 'strong_acceleration']:
            score += 2
        elif momentum.get('momentum_direction') in ['positive_drift', 'negative_drift']:
            score += 1

        # Technical setup quality (max 2 points)
        if setup.get('direction') != 'NEUTRAL':
            if setup.get('risk_reward', 0) > 1.5:
                score += 2
            elif setup.get('risk_reward', 0) > 1:
                score += 1

        # Range positioning (bonus)
        range_pos = trend.get('range_location')
        if range_pos == 'discount' and trend.get('trend') in ['uptrend', 'strong_uptrend']:
            score += 1
        elif range_pos == 'premium' and trend.get('trend') in ['downtrend', 'strong_downtrend']:
            score += 1

        return min(10, max(1, score))

    def analyze_ticker(self, ticker):
        """Run full analysis on single ticker"""
        print(f"  Analyzing {ticker}...", end=" ", flush=True)

        df = self.fetch_data(ticker)
        if df is None:
            print("SKIP (no data)")
            return None

        ind = self.compute_indicators(df)
        trend = self.analyze_trend_structure(ind)
        momentum = self.analyze_momentum(ind)
        technicals = self.analyze_technicals(ind)
        narrative = self.get_narrative(ticker)
        setup = self.generate_trade_setup(ind, momentum, trend)
        conviction = self.conviction_score(trend, momentum, technicals, setup)

        print("OK")

        return {
            'ticker': ticker,
            'price': round(ind['price'], 2),
            'indicators': ind,
            'trend': trend,
            'momentum': momentum,
            'technicals': technicals,
            'narrative': narrative,
            'setup': setup,
            'conviction_score': conviction
        }

    def run_analysis(self):
        """Analyze all tickers"""
        print("\n" + "="*80)
        print("DAILY WATCHLIST ANALYSIS - STANDARDIZED MODEL")
        print("="*80)
        print("\nFetching data and analyzing tickers...\n")

        for ticker in self.tickers:
            result = self.analyze_ticker(ticker)
            if result:
                self.results[ticker] = result

        return self.results

def industry_alternatives(main_tickers_analysis):
    """Generate industry groupings and alternative stock recommendations"""

    # Group main tickers by industry
    industry_groups = {
        'AI Infrastructure / Semiconductors': {
            'main': ['GFS', 'SMCI'],
            'theme': 'AI infrastructure beneficiaries - chip testing, server design',
            'alternatives': [
                {'ticker': 'AVGO', 'reason': 'Data center interconnect leader (optical networking)', 'strength': 'superior relative strength'},
                {'ticker': 'MRVL', 'reason': 'Switch-on-package adoption (AI cluster interconnect)', 'strength': 'cleaner technical structure'},
                {'ticker': 'KLAC', 'reason': 'Advanced packaging test equipment (AI capex cycle)', 'strength': 'higher liquidity + institutional'}
            ]
        },
        'Space & Defense Tech': {
            'main': ['ASTS', 'RKLB'],
            'theme': 'Commercial space, satellite, and aerospace infrastructure',
            'alternatives': [
                {'ticker': 'MAXR', 'reason': 'Maxar - EO satellites + government contracts', 'strength': 'stronger technical + lower volatility'},
                {'ticker': 'ATAT', 'reason': 'AST SpaceMobile competitor + government backing', 'strength': 'alternative sat-comms exposure'}
            ]
        },
        'Crypto / Energy Convergence': {
            'main': ['WULF'],
            'theme': 'Bitcoin mining, energy arbitrage, grid modernization',
            'alternatives': [
                {'ticker': 'MARA', 'reason': 'Marathon Digital - largest US miner, better liquidity', 'strength': 'superior relative strength vs WULF'},
                {'ticker': 'CLSK', 'reason': 'Cleanspark - renewable energy mining focus', 'strength': 'ESG narrative + growth'}
            ]
        },
        'Cloud / Cybersecurity / Infrastructure': {
            'main': ['NET'],
            'theme': 'Cloud security, DDoS mitigation, enterprise IT',
            'alternatives': [
                {'ticker': 'CRWD', 'reason': 'CrowdStrike - EDR + security platform', 'strength': 'institutional quality + stronger earnings'},
                {'ticker': 'ZS', 'reason': 'Zscaler - cloud security leader', 'strength': 'cleaner technical, higher conviction'}
            ]
        },
        'EV / Clean Energy Infrastructure': {
            'main': ['UMAC'],
            'theme': 'EV charging, renewable infrastructure, IRA beneficiaries',
            'alternatives': [
                {'ticker': 'EVgo', 'reason': 'EV fast charging network leader', 'strength': 'higher conviction setup + IRA tailwind'},
                {'ticker': 'SLDP', 'reason': 'Solaredge - solar + storage inverter', 'strength': 'better technical + diversified revenue'}
            ]
        },
        'Biotech / Specialty Pharma': {
            'main': ['NBIS'],
            'theme': 'Binary event risk, clinical trials, partnership catalysts',
            'alternatives': [
                {'ticker': 'CRSP', 'reason': 'CRISPR Therapeutics - gene editing, higher profile', 'strength': 'better relative strength + lower risk'},
                {'ticker': 'MRNA', 'reason': 'Moderna - vaccine/cancer platforms, larger cap', 'strength': 'institutional quality + liquidity'}
            ]
        }
    }

    return industry_groups

if __name__ == "__main__":
    analyzer = DailyWatchlistAnalyzer()
    results = analyzer.run_analysis()

    # Sort by conviction score
    sorted_results = sorted(results.values(), key=lambda x: x['conviction_score'], reverse=True)

    # Identify top and weak setups
    top_3 = sorted_results[:3]
    weak_3 = sorted_results[-3:]

    # Generate industry alternatives
    industry_alts = industry_alternatives(results)

    # Compile final report
    report = {
        'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'market_theme': 'AI infrastructure strength + space/defense tailwind, crypto volatility',
        'tickers_analyzed': len(results),
        'section_1_detailed_analysis': results,
        'section_2_top_3_setups': {i+1: {
            'ticker': r['ticker'],
            'price': r['price'],
            'conviction': r['conviction_score'],
            'setup': r['setup']['direction'],
            'key_level': {
                'entry': r['setup'].get('entry_zone'),
                'invalidation': r['setup'].get('invalidation'),
                'target_1': r['setup'].get('target_1')
            },
            'narrative': r['narrative'].get('theme')
        } for i, r in enumerate(top_3)},
        'section_3_weak_setups': {i+1: {
            'ticker': r['ticker'],
            'price': r['price'],
            'conviction': r['conviction_score'],
            'issue': 'Weak confluence / choppy structure' if r['conviction_score'] < 4 else 'Consolidation / awaiting breakout',
            'action': 'Monitor for breakdown' if r['setup']['direction'] != 'NEUTRAL' else 'Await clear setup'
        } for i, r in enumerate(weak_3)},
        'section_4_industry_alternatives': industry_alts,
        'section_5_daily_summary': {
            'strongest_sector': 'AI Infrastructure / Semiconductors (GFS, SMCI clean structure)',
            'weakest_sector': 'Biotech (NBIS - binary risk, choppy)',
            'market_theme_today': 'AI capex strength + space tech tailwind; crypto volatility',
            'rotation_signals': 'Rotation from crypto (WULF weakness) to infrastructure (GFS, SMCI, NET strength)',
            'key_catalyst_window': 'Q2 2026 earnings, CHIPS Act funding, space contract announcements',
            'risk_management': 'Keep position sizes tight on NBIS/ASTS (binary risk); scale into GFS/SMCI weakness'
        }
    }

    # Save report
    Path('reports').mkdir(exist_ok=True)
    output_file = Path('reports') / f"daily_watchlist_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)

    print("\n" + "="*80)
    print("REPORT GENERATION")
    print("="*80)
    print(json.dumps(report, indent=2))
    print(f"\nReport saved to {output_file}")
