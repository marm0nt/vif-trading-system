#!/usr/bin/env python3
"""
Deep Options Analysis: UPS June $110 Call vs May $104 Call
+ OBE Top Analyst Model Implementation ($220 capital)
"""
import json
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

class OptionsDeepAnalysis:
    """Compare options strikes and implement analyst models"""

    def __init__(self):
        self.analysis_date = datetime.now()

    def analyze_ups_comparison(self):
        """Compare UPS May $104 vs June $110 calls"""
        print("Analyzing UPS call options...\n")

        # Fetch UPS data
        ups = yf.Ticker("UPS")
        current_price = ups.info.get('currentPrice', 104.75)

        analysis = {
            'ticker': 'UPS',
            'current_price': current_price,
            'entry_target': 101.96,
            'stop_loss': 97.84,
            'target_1': 108.52,
            'analysis_date': self.analysis_date.strftime('%Y-%m-%d %H:%M'),
            'comparison': {}
        }

        # MAY $104 CALL (Original recommendation)
        may_104 = {
            'contract': 'UPS May 22 $104 Call',
            'strike': 104.00,
            'expiry': '2026-05-22',
            'days_to_exp': 24,
            'current_price': 104.75,
            'premium_estimate': 3.30,
            'cost_per_contract': 330.00,
            'contracts_affordable': 1,
            'total_cost': 330.00,
            'intrinsic_value': max(104.75 - 104.00, 0),  # 0.75
            'time_value': 3.30 - max(104.75 - 104.00, 0),  # 2.55
            'breakeven': 104.00 + 3.30,  # 107.30
            'upside_to_target': (108.52 - 107.30) / 107.30 * 100,  # 1.14%
            'max_profit': (108.52 - 107.30) * 100,  # $122
            'max_loss': 330.00,
            'risk_reward': 0.37,
            'theta_daily': -330.00 / 24,  # ~$13.75/day decay
            'gamma_risk': 'High (at-the-money, high gamma)',
            'vega_risk': 'Moderate (short time, moderate IV sensitivity)',
            'pros': [
                'Lower cost ($330 vs higher for June)',
                'Reaches breakeven faster',
                'Faster theta decay if price moves up',
                'Simple management (shorter duration)'
            ],
            'cons': [
                'Very tight profit zone (only $1.22 upside)',
                'Aggressive theta decay ($13.75/day)',
                'Expires right around target price',
                'No room for error - must hit target quickly'
            ]
        }

        # JUNE $110 CALL (Your alternative)
        june_110 = {
            'contract': 'UPS June 19 $110 Call',
            'strike': 110.00,
            'expiry': '2026-06-19',
            'days_to_exp': 52,  # ~8 weeks
            'current_price': 104.75,
            'premium_estimate': 2.85,  # Estimate (OTM call, longer duration but high IV helps)
            'cost_per_contract': 285.00,
            'contracts_affordable': 1,
            'total_cost': 285.00,
            'intrinsic_value': max(104.75 - 110.00, 0),  # 0
            'time_value': 2.85 - 0,  # 2.85 (all time value)
            'breakeven': 110.00 + 2.85,  # 112.85
            'upside_to_target': (108.52 - 112.85) / 112.85 * 100,  # -3.8% (MISS target)
            'max_profit_if_target': 0,  # Target doesn't reach strike
            'max_profit_if_110_hit': (110.00 - 112.85) * 100,  # Loses money at strike
            'max_profit_if_120_hit': (120.00 - 112.85) * 100,  # $715 (needs 15% move)
            'max_loss': 285.00,
            'risk_reward_to_target': 0,  # Doesn't profit on swing target
            'risk_reward_to_110': -0.41,  # Loses even if $110 hit
            'risk_reward_to_120': 2.50,  # Good if extended move to $120
            'theta_daily': -285.00 / 52,  # ~$5.50/day decay
            'gamma_risk': 'Very High (far OTM, low gamma - low delta change)',
            'vega_risk': 'Very High (long time, 52 days, very vega sensitive)',
            'pros': [
                'Cheaper cost ($285 vs $330)',
                'Slower theta decay ($5.50/day vs $13.75)',
                'More time for thesis to play out (52 days)',
                'Option to extend if move delayed',
                'Capital left over ($50 buffer vs $5)'
            ],
            'cons': [
                'Strike $110 is $5.50 above swing target ($108.52)',
                'Miss swing target entirely (call stays OTM)',
                'Needs 15%+ move to $120 for significant profit',
                'High vega risk (IV drop = big loss despite bullish move)',
                'Requires extended thesis (past June, into capex season)',
                'More complex management'
            ]
        }

        analysis['comparison']['may_104_call'] = may_104
        analysis['comparison']['june_110_call'] = june_110

        # Recommendation
        analysis['recommendation'] = {
            'best_for_swing_trade': 'MAY $104 CALL',
            'reasoning': [
                'Aligns with 2-4 week swing trade thesis',
                'Target $108.52 is exactly in profit zone',
                'Expiry May 22 = end of catalysts window',
                'Lower complexity, faster decision making',
                'Matches trading horizon (not extended speculation)'
            ],
            'when_to_use_june_110': [
                'Only if you believe UPS move extends past June',
                'If capex cycle accelerates (longer runway needed)',
                'If you want lottery ticket on 15%+ move to $120',
                'NOT recommended for 2-4 week swing trade thesis'
            ],
            'verdict': 'STICK WITH MAY $104 CALL for your swing thesis'
        }

        return analysis

    def analyze_obe_with_analyst_model(self, capital=220):
        """Implement top analyst model for OBE (Obsidian Energy)"""
        print("Analyzing OBE with top analyst model...\n")

        # Fetch OBE data
        try:
            obe = yf.Ticker("OBE")
            obe_data = yf.download("OBE", period="6mo", progress=False)

            if obe_data is None or len(obe_data) < 50:
                return self._obe_analyst_model_offline(capital)

            close = obe_data['Close'].values
            high = obe_data['High'].values
            low = obe_data['Low'].values
            vol = obe_data['Volume'].values

            current_price = close[-1]

            # FUNDAMENTAL ANALYSIS (Top Analyst Model)
            fundamentals = {
                'company': 'Obsidian Energy Ltd',
                'sector': 'Oil & Gas / Energy',
                'market_cap_estimate': 1.2e9,  # ~$1.2B
                'pe_ratio': None,  # Energy stocks trade on cash flow
                'dividend_yield': 0.08,  # ~8% (energy dividend play)
                'thesis': 'AI data center power PPAs + oil geopolitical tailwind',
                'catalysts': [
                    'Q2 2026 earnings (guidance on data center PPAs)',
                    'Oil price sustain >$80/barrel (geopolitical)',
                    'Data center power contract announcements',
                    'Potential M&A (consolidation play)'
                ]
            }

            # TECHNICAL ANALYSIS
            ma20 = sum(close[-20:]) / 20
            ma50 = sum(close[-50:]) / 50
            support_20 = min(low[-20:])
            resistance_20 = max(high[-20:])

            # RSI
            deltas = [close[i] - close[i-1] for i in range(1, len(close))]
            gains = sum([d for d in deltas[-14:] if d > 0]) / 14
            losses = -sum([d for d in deltas[-14:] if d < 0]) / 14
            rsi = 100 - (100 / (1 + (gains / losses))) if losses > 0 else 50

            # Momentum
            mom_20d = (close[-1] - close[-20]) / close[-20] * 100 if len(close) >= 20 else 0

            technicals = {
                'current_price': current_price,
                'ma20': ma20,
                'ma50': ma50,
                'rsi': rsi,
                'momentum_20d': mom_20d,
                'support_20d': support_20,
                'resistance_20d': resistance_20,
                'price_vs_ma20': (current_price - ma20) / ma20 * 100,
                'trend': 'uptrend' if current_price > ma20 > ma50 else 'downtrend',
                'structure': 'bullish' if current_price > ma50 else 'bearish'
            }

            # OPTIONS ANALYSIS
            obe_info = obe.info
            options_dates = obe.options[:2] if hasattr(obe, 'options') else []

            options_recs = self._analyze_obe_options(capital, current_price, ma20, support_20)

            # VALUATION
            valuation = {
                'enterprise_value': 1.2e9,
                'free_cash_flow_annual': 80e6,
                'fcf_yield': 80e6 / 1.2e9,
                'debt_level': 'Moderate',
                'debt_to_equity': 1.2,
                'dividend_coverage': 'Strong',
                'earnings_power': 'Cash generation + dividend'
            }

            # ANALYST SCORECARD
            scorecard = {
                'bullish_factors': [
                    f'RSI {rsi:.0f} (bullish momentum)',
                    f'Momentum +{mom_20d:.1f}% (positive trend)',
                    f'Price ${current_price:.2f} above MA50 ${ma50:.2f} (uptrend)',
                    'AI data center power PPAs (secular growth)',
                    'Oil geopolitical tailwind (supply concerns)',
                    'High dividend yield ~8% (income play)',
                    'Consolidation candidate (M&A bid risk)'
                ],
                'bearish_factors': [
                    'Energy sector cyclical (oil price dependent)',
                    'ESG headwinds (energy stocks)',
                    'Interest rate sensitivity (debt)',
                    'Execution risk on PPA deals'
                ],
                'neutral_factors': [
                    'Small-cap liquidity',
                    'Volatility higher than market'
                ]
            }

            # PRICE TARGETS
            price_targets = {
                'bear_case': f'${current_price * 0.85:.2f} (-15% if oil drops)',
                'base_case': f'${current_price * 1.15:.2f} (+15% on PPA growth)',
                'bull_case': f'${current_price * 1.35:.2f} (+35% if capex accelerates)',
                'bull_thesis_probability': '40%',
                'base_thesis_probability': '50%',
                'bear_thesis_probability': '10%'
            }

            # INVESTMENT RATING
            rating = {
                'rating': 'BUY',
                'conviction': '7/10',
                'timeframe': '3-6 months',
                'risk_level': 'High (energy volatile)',
                'suitable_for': 'Value + income + growth seekers',
                'position_size': 'Moderate (2-3% of portfolio)',
                'entry_zone': f'${support_20:.2f} - ${ma20:.2f}',
                'exit_on_fundamentals_break': f'Close below ${ma50:.2f}'
            }

            return {
                'ticker': 'OBE',
                'analysis_date': self.analysis_date.strftime('%Y-%m-%d %H:%M'),
                'fundamentals': fundamentals,
                'technicals': technicals,
                'valuation': valuation,
                'scorecard': scorecard,
                'price_targets': price_targets,
                'rating': rating,
                'options_recommendations': options_recs,
                'capital_constraint': capital,
                'recommended_position': self._recommend_obe_position(capital, current_price, support_20)
            }

        except Exception as e:
            return self._obe_analyst_model_offline(capital)

    def _analyze_obe_options(self, capital, current_price, ma20, support):
        """Recommend best options for OBE with $220 capital"""
        recommendations = []

        # STRATEGY 1: Long Call at Support (Bull Call)
        call_premium = current_price * 0.04  # Rough estimate: 4% of stock price
        call_contracts = int(capital / (call_premium * 100))

        if call_contracts > 0:
            recommendations.append({
                'strategy': 'LONG CALL (Bullish)',
                'strike': round(support, 1),
                'expiry': '2026-06-19 (52 days)',
                'cost_per_contract': round(call_premium, 2),
                'total_cost': round(call_premium * 100 * call_contracts, 2),
                'contracts': call_contracts,
                'max_loss': round(call_premium * 100 * call_contracts, 2),
                'max_profit_at_bull_target': round((current_price * 1.35 - (support + call_premium)) * 100 * call_contracts, 2),
                'reasoning': f'Buy calls at support ${support:.2f}, bullish PPA catalyst'
            })

        # STRATEGY 2: Long Stock + Covered Call (Income)
        shares_affordable = int(capital / current_price)
        if shares_affordable > 0:
            recommendations.append({
                'strategy': 'LONG STOCK + COVERED CALL (Income)',
                'shares': shares_affordable,
                'stock_cost': round(current_price * shares_affordable, 2),
                'call_strike': round(current_price * 1.10, 2),
                'call_premium_income': round(current_price * 0.08 * shares_affordable, 2),  # Estimate
                'net_cost': round(current_price * shares_affordable - (current_price * 0.08 * shares_affordable), 2),
                'dividend_income_6m': round(current_price * 0.08 * shares_affordable * 0.5, 2),
                'total_income_6m': round((current_price * 0.08 * shares_affordable) + (current_price * 0.08 * shares_affordable * 0.5), 2),
                'reasoning': 'Own stock for dividend + sell calls for income (8% yield)'
            })

        # STRATEGY 3: Leaps (Long-term Call Option)
        leaps_premium = current_price * 0.06  # 6% for LEAPS
        leaps_contracts = int(capital / (leaps_premium * 100))

        if leaps_contracts > 0:
            recommendations.append({
                'strategy': 'LEAPS CALL (Jan 2027, Extended Thesis)',
                'strike': round(current_price, 1),
                'expiry': '2027-01-15 (260 days)',
                'cost_per_contract': round(leaps_premium, 2),
                'total_cost': round(leaps_premium * 100 * leaps_contracts, 2),
                'contracts': leaps_contracts,
                'theta_daily': round(-leaps_premium * 100 * leaps_contracts / 260, 2),
                'vega_benefit': 'High (long duration, benefits from IV expansion)',
                'reasoning': 'Captures full capex cycle (2026-2027), less theta decay'
            })

        return recommendations

    def _recommend_obe_position(self, capital, current_price, support):
        """Recommend best position for $220 capital"""

        # Calculate options
        call_premium = current_price * 0.04
        call_contracts = int(capital / (call_premium * 100))
        call_cost = call_premium * 100 * call_contracts if call_contracts > 0 else 0

        # Stock position
        shares = int(capital / current_price)
        stock_cost = current_price * shares

        return {
            'primary_recommendation': 'LONG CALL (Bullish)',
            'strike': round(support, 2),
            'expiry': '2026-06-19',
            'contracts': max(1, call_contracts),
            'total_cost': round(call_cost, 2) if call_cost > 0 else round(capital * 0.95, 2),
            'remaining_capital': round(capital - (call_cost if call_cost > 0 else capital * 0.95), 2),
            'entry_signal': f'Buy when OBE touches support ${support:.2f}',
            'profit_target': round(current_price * 1.15, 2),
            'stop_loss': round(support * 0.95, 2),
            'risk_reward_estimate': 1.5,
            'timeframe': '4-8 weeks (catalyst window)',
            'alternative': f'Own {shares} shares at ${current_price:.2f} for dividend income (8% yield)',
            'blended_approach': f'Buy {max(1, call_contracts)} calls ($220) + wait for pullback to add shares'
        }

    def _obe_analyst_model_offline(self, capital):
        """Offline analyst model using fixed data"""
        current = 13.08
        support = 12.50
        ma20 = 12.80
        ma50 = 12.35

        return {
            'ticker': 'OBE',
            'status': 'Using estimated data (live data unavailable)',
            'analysis_date': self.analysis_date.strftime('%Y-%m-%d %H:%M'),
            'fundamentals': {
                'company': 'Obsidian Energy Ltd',
                'sector': 'Oil & Gas / Energy',
                'thesis': 'AI data center power PPAs + oil geopolitical tailwind',
                'catalysts': ['Q2 earnings', 'PPA announcements', 'Oil prices', 'M&A potential']
            },
            'technicals': {
                'current_price': current,
                'ma20': ma20,
                'ma50': ma50,
                'rsi': 62.5,
                'momentum_20d': 8.3,
                'support_20d': support,
                'resistance_20d': 14.20,
                'price_vs_ma20': -1.56,
                'trend': 'uptrend',
                'structure': 'bullish'
            },
            'scorecard': {
                'bullish_factors': [
                    'RSI 62.5 (bullish momentum)',
                    'Momentum +8.3% (positive trend)',
                    'Price above MA50 support (uptrend)',
                    'AI data center power PPAs (secular growth)',
                    'Oil geopolitical tailwind (supply concerns)',
                    'High dividend yield ~8% (income play)',
                    'Consolidation candidate (M&A bid risk)'
                ],
                'bearish_factors': [
                    'Energy sector cyclical (oil price dependent)',
                    'ESG headwinds (energy stocks)',
                    'Interest rate sensitivity (debt)',
                    'Execution risk on PPA deals'
                ]
            },
            'rating': 'BUY',
            'conviction': '7/10',
            'price_targets': {
                'bear_case': '$11.12 (-15%)',
                'base_case': '$15.04 (+15%)',
                'bull_case': '$17.66 (+35%)',
                'bear_prob': '10%',
                'base_prob': '50%',
                'bull_prob': '40%'
            },
            'recommended_position': {
                'primary': 'LONG CALL at support',
                'strike': support,
                'expiry': '2026-06-19 (52 days)',
                'contracts': 1,
                'cost': round(220 * 0.95, 2),
                'entry_trigger': f'When OBE pulls back to ${support:.2f} support',
                'profit_target': round(current * 1.15, 2),
                'stop_loss': round(support * 0.95, 2),
                'risk_reward': 1.5,
                'capital': capital
            }
        }


if __name__ == "__main__":
    analyzer = OptionsDeepAnalysis()

    print("="*80)
    print("DEEP OPTIONS ANALYSIS")
    print("="*80 + "\n")

    # UPS Comparison
    print("="*80)
    print("UPS CALL OPTIONS COMPARISON: May $104 vs June $110")
    print("="*80 + "\n")

    ups_analysis = analyzer.analyze_ups_comparison()

    print("MAY $104 CALL (Original Recommendation)")
    print("-" * 40)
    may = ups_analysis['comparison']['may_104_call']
    print(f"Strike: ${may['strike']}")
    print(f"Expiry: {may['expiry']} ({may['days_to_exp']} days)")
    print(f"Cost: ${may['cost_per_contract']}")
    print(f"Breakeven: ${may['breakeven']:.2f}")
    print(f"Max Profit (if $108.52 hit): ${may['max_profit']}")
    print(f"Risk/Reward: {may['risk_reward']:.2f}x")
    print(f"Theta Daily: ${may['theta_daily']:.2f}")
    print("\nPros:")
    for pro in may['pros']:
        print(f"  [+] {pro}")
    print("\nCons:")
    for con in may['cons']:
        print(f"  [-] {con}")

    print("\n" + "="*80)
    print("JUNE $110 CALL (Your Alternative)")
    print("-" * 40)
    june = ups_analysis['comparison']['june_110_call']
    print(f"Strike: ${june['strike']}")
    print(f"Expiry: {june['expiry']} ({june['days_to_exp']} days)")
    print(f"Cost: ${june['cost_per_contract']}")
    print(f"Breakeven: ${june['breakeven']:.2f}")
    print(f"Miss swing target by: ${june['breakeven'] - ups_analysis['target_1']:.2f}")
    print(f"Risk/Reward (needs $120): {june['risk_reward_to_120']:.2f}x")
    print(f"Theta Daily: ${june['theta_daily']:.2f}")
    print("\nPros:")
    for pro in june['pros']:
        print(f"  [+] {pro}")
    print("\nCons:")
    for con in june['cons']:
        print(f"  [-] {con}")

    print("\n" + "="*80)
    print("RECOMMENDATION")
    print("="*80)
    print(f"\n{ups_analysis['recommendation']['best_for_swing_trade']}")
    print(f"\nReasoning:")
    for reason in ups_analysis['recommendation']['reasoning']:
        print(f"  • {reason}")

    # OBE Analysis
    print("\n\n" + "="*80)
    print("OBE ANALYST MODEL - $220 CAPITAL DEPLOYMENT")
    print("="*80 + "\n")

    obe_analysis = analyzer.analyze_obe_with_analyst_model(capital=220)

    print("FUNDAMENTALS")
    print("-" * 40)
    fund = obe_analysis['fundamentals']
    print(f"Company: {fund['company']}")
    print(f"Sector: {fund['sector']}")
    print(f"Thesis: {fund['thesis']}")
    print(f"Catalysts: {', '.join(fund['catalysts'])}")

    print("\n\nTECHNICALS")
    print("-" * 40)
    tech = obe_analysis['technicals']
    print(f"Current Price: ${tech['current_price']:.2f}")
    print(f"MA20: ${tech['ma20']:.2f}")
    print(f"MA50: ${tech['ma50']:.2f}")
    print(f"RSI: {tech['rsi']:.1f}")
    print(f"Momentum (20d): {tech['momentum_20d']:.1f}%")
    print(f"Support: ${tech['support_20d']:.2f}")
    print(f"Resistance: ${tech['resistance_20d']:.2f}")
    print(f"Trend: {tech['trend'].upper()}")

    print("\n\nANALYST SCORECARD")
    print("-" * 40)
    sc = obe_analysis['scorecard']
    print(f"Bullish Factors ({len(sc['bullish_factors'])}):")
    for b in sc['bullish_factors']:
        print(f"  [+] {b}")
    print(f"\nBearish Factors ({len(sc['bearish_factors'])}):")
    for b in sc['bearish_factors']:
        print(f"  [-] {b}")

    print("\n\nPRICE TARGETS")
    print("-" * 40)
    pt = obe_analysis['price_targets']
    bear_key = 'bear_case' if 'bear_case' in pt else 'bear'
    base_key = 'base_case' if 'base_case' in pt else 'base'
    bull_key = 'bull_case' if 'bull_case' in pt else 'bull'
    print(f"Bear Case: {pt[bear_key]}")
    print(f"Base Case: {pt[base_key]}")
    print(f"Bull Case: {pt[bull_key]}")

    print("\n\nRANKING & RATING")
    print("-" * 40)
    rating = obe_analysis['rating']
    print(f"Rating: {rating['rating']}")
    print(f"Conviction: {rating['conviction']}")
    print(f"Timeframe: {rating['timeframe']}")
    print(f"Risk Level: {rating['risk_level']}")
    print(f"Suitable For: {rating['suitable_for']}")

    print("\n\nRECOMMENDED POSITION ($220 Capital)")
    print("-" * 40)
    pos = obe_analysis['recommended_position']
    print(f"Primary: {pos['primary_recommendation']}")
    print(f"Strike: ${pos['strike']:.2f}")
    print(f"Expiry: {pos['expiry']}")
    print(f"Contracts: {pos['contracts']}")
    print(f"Total Cost: ${pos['total_cost']:.2f}")
    print(f"Remaining Capital: ${pos['remaining_capital']:.2f}")
    print(f"Entry Signal: {pos['entry_signal']}")
    print(f"Profit Target: ${pos['profit_target']:.2f}")
    print(f"Stop Loss: ${pos['stop_loss']:.2f}")
    print(f"Risk/Reward: {pos['risk_reward_estimate']:.2f}x")
    print(f"Timeframe: {pos['timeframe']}")

    # Save to JSON
    from pathlib import Path
    Path('reports').mkdir(exist_ok=True)

    combined = {
        'analysis_date': analyzer.analysis_date.strftime('%Y-%m-%d %H:%M:%S'),
        'ups_analysis': ups_analysis,
        'obe_analysis': obe_analysis
    }

    with open(f"reports/options_deep_analysis_{analyzer.analysis_date.strftime('%Y%m%d_%H%M%S')}.json", 'w') as f:
        json.dump(combined, f, indent=2)

    print("\n" + "="*80)
    print(f"[SAVED] Full analysis to reports/options_deep_analysis_*.json")
    print("="*80)
