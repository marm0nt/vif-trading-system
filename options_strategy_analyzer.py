#!/usr/bin/env python3
"""
Options Strategy Analyzer for Top 5 Swing Trade Setups
Designs optimal single-leg options strategies within capital constraints
"""
import json
from datetime import datetime, timedelta
import yfinance as yf

class OptionsStrategyAnalyzer:
    """Analyze options strategies for $335 capital constraint"""

    def __init__(self, capital=335):
        self.capital = capital
        self.top_5 = [
            {'ticker': 'TSEM', 'price': 194.0, 'entry': 201.93, 'stop': 193.77, 't1': 228.73},
            {'ticker': 'DLR', 'price': 193.84, 'entry': 190.66, 'stop': 182.95, 't1': 208.14},
            {'ticker': 'UPS', 'price': 104.75, 'entry': 101.96, 'stop': 97.84, 't1': 108.52},
            {'ticker': 'LITE', 'price': 798.89, 'entry': 836.34, 'stop': 802.55, 't1': 960.00},
            {'ticker': 'NBIS', 'price': 136.14, 'entry': 139.28, 'stop': 133.65, 't1': 168.71},
        ]

    def fetch_option_chain(self, ticker):
        """Fetch option chain data"""
        try:
            stock = yf.Ticker(ticker)
            options_dates = stock.options
            if not options_dates:
                return None

            # Get nearest expiration (2-4 weeks out)
            target_expiry = datetime.now() + timedelta(days=21)
            closest_date = min(options_dates, key=lambda x: abs(datetime.strptime(x, '%Y-%m-%d') - target_expiry))

            option_chain = stock.option_chain(closest_date)
            return {
                'expiry': closest_date,
                'calls': option_chain.calls,
                'puts': option_chain.puts
            }
        except:
            return None

    def analyze_call_strategy(self, ticker, current_price, entry_price, target_price):
        """
        LONG CALL STRATEGY (Bullish)
        - Buy call at/near entry price
        - Profit if price rises above strike + premium paid
        - Max loss = premium paid (defined risk)
        - Ideal for upside with capital efficiency
        """
        options = self.fetch_option_chain(ticker)
        if not options:
            return None

        calls = options['calls'].sort_values('strike')
        expiry = options['expiry']
        days_to_exp = (datetime.strptime(expiry, '%Y-%m-%d') - datetime.now()).days

        recommendations = []

        for idx, call in calls.iterrows():
            strike = call['strike']
            mid_price = (call['bid'] + call['ask']) / 2

            # Filter: Only affordable calls (within capital budget)
            contract_cost = mid_price * 100  # 1 contract = 100 shares
            if contract_cost > self.capital:
                continue

            # Filter: Strike should be near entry price (at-the-money or slightly OTM)
            if strike < entry_price * 0.98 or strike > entry_price * 1.05:
                continue

            # Calculate metrics
            contracts_affordable = int(self.capital / contract_cost)
            total_cost = contracts_affordable * contract_cost
            breakeven = strike + mid_price
            upside_to_target = (target_price - strike) / strike * 100
            max_loss_pct = (mid_price / strike) * 100

            recommendations.append({
                'strategy': 'LONG CALL',
                'ticker': ticker,
                'strike': strike,
                'expiry': expiry,
                'days_to_exp': days_to_exp,
                'call_price': mid_price,
                'contracts': contracts_affordable,
                'total_capital': total_cost,
                'remaining_capital': self.capital - total_cost,
                'breakeven': breakeven,
                'upside_to_target_pct': upside_to_target,
                'max_loss_pct': max_loss_pct,
                'max_loss_dollars': total_cost,
                'max_profit_pct': (target_price - breakeven) / breakeven * 100 if breakeven > 0 else 0,
                'max_profit_dollars': (target_price - breakeven) * contracts_affordable * 100 if breakeven > 0 else 0,
                'intrinsic_value': max(strike - current_price, 0),
                'time_value': mid_price - max(strike - current_price, 0),
                'bid_ask_spread': call['ask'] - call['bid'],
                'open_interest': call['openInterest'],
                'volume': call['volume'] if 'volume' in call else 0
            })

        return sorted(recommendations, key=lambda x: x['upside_to_target_pct'], reverse=True)[:3]

    def analyze_put_strategy(self, ticker, current_price, entry_price, stop_price):
        """
        LONG PUT STRATEGY (Bearish/Defensive)
        - Buy put below entry price
        - Profit if price falls below strike - premium paid
        - Max loss = premium paid (defined risk)
        - Ideal for downside protection or bearish bets

        NOTE: For your bullish swing trades, this is mainly for HEDGE
        """
        options = self.fetch_option_chain(ticker)
        if not options:
            return None

        puts = options['puts'].sort_values('strike')
        expiry = options['expiry']
        days_to_exp = (datetime.strptime(expiry, '%Y-%m-%d') - datetime.now()).days

        recommendations = []

        for idx, put in puts.iterrows():
            strike = put['strike']
            mid_price = (put['bid'] + put['ask']) / 2

            # Filter: Only affordable puts
            contract_cost = mid_price * 100
            if contract_cost > self.capital:
                continue

            # Filter: Strike should be near stop price (protective or speculative)
            if strike > current_price * 1.02 or strike < stop_price * 0.95:
                continue

            contracts_affordable = int(self.capital / contract_cost)
            total_cost = contracts_affordable * contract_cost
            breakeven = strike - mid_price
            max_profit_pct = (strike - breakeven) / breakeven * 100 if breakeven > 0 else 0

            recommendations.append({
                'strategy': 'LONG PUT',
                'ticker': ticker,
                'strike': strike,
                'expiry': expiry,
                'days_to_exp': days_to_exp,
                'put_price': mid_price,
                'contracts': contracts_affordable,
                'total_capital': total_cost,
                'remaining_capital': self.capital - total_cost,
                'breakeven': breakeven,
                'downside_to_stop_pct': (stop_price - strike) / strike * 100,
                'max_loss_pct': (mid_price / strike) * 100,
                'max_loss_dollars': total_cost,
                'max_profit_pct': max_profit_pct,
                'max_profit_dollars': (strike - breakeven) * contracts_affordable * 100 if breakeven > 0 else 0,
                'intrinsic_value': max(strike - current_price, 0),
                'time_value': mid_price - max(strike - current_price, 0),
                'bid_ask_spread': put['ask'] - put['bid'],
                'open_interest': put['openInterest'],
                'volume': put['volume'] if 'volume' in put else 0
            })

        return sorted(recommendations, key=lambda x: x['max_profit_pct'], reverse=True)[:3]

    def recommend_best_strategy(self):
        """Recommend best options strategy per ticker"""
        results = {
            'capital': self.capital,
            'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'strategies_by_ticker': {}
        }

        for stock in self.top_5:
            ticker = stock['ticker']
            price = stock['price']
            entry = stock['entry']
            stop = stock['stop']
            target = stock['t1']

            print(f"Analyzing {ticker}...", end='', flush=True)

            calls = self.analyze_call_strategy(ticker, price, entry, target)
            puts = self.analyze_put_strategy(ticker, price, entry, stop)

            results['strategies_by_ticker'][ticker] = {
                'current_price': price,
                'entry_target': entry,
                'stop_loss': stop,
                'target_1': target,
                'call_strategies': calls if calls else [],
                'put_strategies': puts if puts else [],
                'recommended': None
            }

            # Recommend best strategy
            if calls:
                best_call = calls[0]
                results['strategies_by_ticker'][ticker]['recommended'] = {
                    'type': 'LONG CALL (Bullish)',
                    'strike': best_call['strike'],
                    'expiry': best_call['expiry'],
                    'contracts': best_call['contracts'],
                    'cost_per_contract': best_call['call_price'],
                    'total_cost': best_call['total_capital'],
                    'max_loss': best_call['max_loss_dollars'],
                    'target_profit': best_call['max_profit_dollars'],
                    'risk_reward': best_call['max_profit_dollars'] / best_call['max_loss_dollars'] if best_call['max_loss_dollars'] > 0 else 0,
                    'upside_to_target': best_call['upside_to_target_pct'],
                    'reasoning': f"Bullish setup; {best_call['contracts']} contract(s) afford {best_call['upside_to_target_pct']:.1f}% upside to target"
                }

            print(" OK")

        return results


if __name__ == "__main__":
    analyzer = OptionsStrategyAnalyzer(capital=335)

    print("\n" + "="*80)
    print("OPTIONS STRATEGY ANALYZER - $335 CAPITAL DEPLOYMENT")
    print("="*80 + "\n")

    results = analyzer.recommend_best_strategy()

    print("\n" + "="*80)
    print("RECOMMENDED STRATEGIES BY TICKER")
    print("="*80 + "\n")

    for ticker, data in results['strategies_by_ticker'].items():
        if data['recommended']:
            rec = data['recommended']
            print(f"\n{ticker.upper()}")
            print(f"  Current Price: ${data['current_price']:.2f}")
            print(f"  Entry Target: ${data['entry_target']:.2f}")
            print(f"  Stop Loss: ${data['stop_loss']:.2f}")
            print(f"\n  RECOMMENDED: {rec['type']}")
            print(f"  Strike: ${rec['strike']:.2f}")
            print(f"  Expiry: {rec['expiry']}")
            print(f"  Contracts: {rec['contracts']}")
            print(f"  Cost Per Contract: ${rec['cost_per_contract']:.2f}")
            print(f"  Total Cost: ${rec['total_cost']:.2f}")
            print(f"  Max Loss: ${rec['max_loss']:.2f}")
            print(f"  Target Profit: ${rec['target_profit']:.2f}")
            print(f"  Risk/Reward: {rec['risk_reward']:.2f}x")
            print(f"  Upside to Target: {rec['upside_to_target']:.1f}%")
            print(f"  Reasoning: {rec['reasoning']}")

    # Save results
    import pathlib
    pathlib.Path('reports').mkdir(exist_ok=True)
    with open(f"reports/options_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", 'w') as f:
        json.dump(results, f, indent=2)

    print("\n" + "="*80)
    print("[SAVED] Full analysis to reports/options_analysis_*.json")
