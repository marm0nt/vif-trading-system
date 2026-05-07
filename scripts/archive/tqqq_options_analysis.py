#!/usr/bin/env python3
"""
TQQQ Options Analysis - $500 Capital Optimization
Analyzes option chains for TQQQ (Nasdaq 3x Leveraged ETF) with capital constraint
Uses VIF framework + options Greeks for optimal contract selection
"""

import yfinance as yf
import pandas as pd
import json
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from anthropic import Anthropic
from dotenv import load_dotenv

# Load .env
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

logging.basicConfig(
    format='%(asctime)s [TQQQ] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO
)
logger = logging.getLogger()

api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError("ANTHROPIC_API_KEY not found in environment or .env file")

client = Anthropic(api_key=api_key)

def fetch_tqqq_data():
    """Fetch TQQQ price data and options chain info"""
    logger.info("Fetching TQQQ data...")
    ticker = yf.Ticker("TQQQ")

    # Current price
    hist = ticker.history(period="5d")
    current_price = hist['Close'].iloc[-1]
    logger.info(f"TQQQ current price: ${current_price:.2f}")

    # Options expirations
    expirations = ticker.options[:10]  # Next 10 expirations

    return {
        'ticker': 'TQQQ',
        'current_price': current_price,
        'hist_close': hist['Close'].tolist(),
        'hist_volume': hist['Volume'].tolist(),
        'expirations': expirations
    }

def analyze_options_chains(data):
    """Fetch and analyze options chains for TQQQ"""
    logger.info("Analyzing options chains...")
    ticker = yf.Ticker("TQQQ")

    chains_data = []

    # Analyze nearest expirations (weekly + monthly)
    for expiry in data['expirations'][:6]:  # First 6 expirations
        try:
            chain = ticker.option_chain(expiry)

            calls = chain.calls
            puts = chain.puts

            # Filter for capital constraint ($500 max per contract)
            capital_constraint = 500
            current_price = data['current_price']

            # Find contracts within budget
            affordable_calls = calls[calls['ask'] * 100 <= capital_constraint].copy()
            affordable_puts = puts[puts['ask'] * 100 <= capital_constraint].copy()

            # Select columns that are available (greeks may not be in all quotes)
            available_cols = ['strike', 'bid', 'ask', 'openInterest', 'impliedVolatility']
            available_cols = [c for c in available_cols if c in affordable_calls.columns]

            chains_data.append({
                'expiration': expiry,
                'calls_count': len(affordable_calls),
                'puts_count': len(affordable_puts),
                'top_calls': affordable_calls.nlargest(5, 'openInterest')[available_cols].to_dict('records') if len(affordable_calls) > 0 else [],
                'top_puts': affordable_puts.nlargest(5, 'openInterest')[available_cols].to_dict('records') if len(affordable_puts) > 0 else []
            })
            logger.info(f"  {expiry}: {len(affordable_calls)} calls, {len(affordable_puts)} puts in budget")
        except Exception as e:
            logger.warning(f"  {expiry}: {str(e)}")

    return chains_data

def run_vif_options_analysis(data, chains):
    """Use Claude to run VIF-based options analysis"""
    logger.info("Running Claude VIF options analysis...")

    # Build context
    chains_summary = json.dumps(chains[:3], indent=2, default=str)  # First 3 expirations

    prompt = f"""
You are an expert options trader using the VIF (Volatility Imbalance Framework) for TQQQ analysis.

## Current Market State
- Ticker: TQQQ (Nasdaq 3x Leveraged)
- Current Price: ${data['current_price']:.2f}
- Capital Available: $500 per contract
- Recent Close: {data['hist_close'][-1]:.2f}

## Options Chains (Within Budget)
{chains_summary}

## Task: Optimal Contract Selection

Given the $500 capital constraint, recommend the single BEST contract for each strategy:

1. **Bullish Setup** - Best call contract
   - Criteria: Delta >0.3, Theta decay acceptable, IV reasonable
   - Target: Directional upside with defined risk

2. **Income Strategy** - Best put sell (OTM)
   - Criteria: Delta <0.30 (low probability ITM), High theta decay
   - Target: Premium collection

3. **Volatility Play** - Best straddle/strangle components
   - Criteria: High gamma, balanced theta
   - Target: Gamma scalp on breakout

For each recommendation, provide:
- Exact strike and expiration
- Premium cost and max profit/loss
- Risk/reward ratio
- Probability of profit (if achievable)
- Best time to enter (pre-market, regular hours, after-hours)

Explain using VIF gamma regime concepts where applicable.
"""

    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}]
    )

    analysis = response.content[0].text
    logger.info(f"Analysis complete ({response.usage.input_tokens} input, {response.usage.output_tokens} output tokens)")

    return analysis

def main():
    logger.info("=" * 80)
    logger.info("TQQQ OPTIONS ANALYSIS – $500 CAPITAL OPTIMIZATION")
    logger.info("=" * 80)

    # Fetch data
    data = fetch_tqqq_data()

    # Analyze chains
    chains = analyze_options_chains(data)

    # Run VIF analysis
    analysis = run_vif_options_analysis(data, chains)

    # Save results
    report = {
        'timestamp': datetime.now().isoformat(),
        'ticker': 'TQQQ',
        'current_price': data['current_price'],
        'capital_available': 500,
        'chains_analyzed': len(chains),
        'vif_analysis': analysis
    }

    report_path = f"reports/options/tqqq_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2, default=str)

    logger.info(f"[SAVED] {report_path}")

    # Print summary
    print("\n" + "=" * 80)
    print("TQQQ OPTIONS RECOMMENDATIONS")
    print("=" * 80)
    print(analysis)
    print("=" * 80)

if __name__ == "__main__":
    main()
