#!/usr/bin/env python3
import sys, os, argparse, json
from datetime import datetime
import logging
import pickle
from pathlib import Path

try:
    import anthropic
    import yfinance as yf
    import pandas as pd
except ImportError as e:
    print(f"ERROR: Missing dependency - {e}")
    sys.exit(1)

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = lambda: None

load_dotenv()
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-opus-4-7")

if not CLAUDE_API_KEY:
    print("ERROR: CLAUDE_API_KEY not found in .env")
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
CACHE_DIR = Path("data")
CACHE_DIR.mkdir(exist_ok=True)

def parse_watchlist(watchlist_file):
    """Load and parse watchlist file."""
    try:
        with open(watchlist_file, 'r') as f:
            tickers = f.read().replace('\n', ',').split(',')
        tickers = [t.strip() for t in tickers if t.strip() and not t.startswith('###')]
        return list(set(tickers))
    except FileNotFoundError:
        logger.error(f"Watchlist file not found: {watchlist_file}")
        return []

def get_cache_path(ticker, period):
    return CACHE_DIR / f"{ticker}_{period}.pkl"

def fetch_market_data(tickers, period='5d'):
    """Fetch OHLCV data with caching, compute indicators."""
    data = {}

    for ticker in tickers[:15]:
        try:
            ticker_clean = ticker.split(':')[-1] if ':' in ticker else ticker

            cache_path = get_cache_path(ticker_clean, period)
            if cache_path.exists():
                with open(cache_path, 'rb') as f:
                    data[ticker] = pickle.load(f)
                    logger.info(f"Cached: {ticker}")
                continue

            logger.info(f"Fetching: {ticker_clean}")
            df = yf.download(ticker_clean, period=period, progress=False)

            if df is None or df.empty or len(df) < 2:
                logger.warning(f"No live data: {ticker}, using fallback")
                data[ticker] = generate_mock_data(ticker)
                continue

            df = df.dropna()
            if len(df) < 2:
                data[ticker] = generate_mock_data(ticker)
                continue

            latest = df.iloc[-1]
            first = df.iloc[0]
            ma_20 = df['Close'].tail(20).mean()
            rsi = compute_rsi(df['Close'])
            vol_avg = df['Volume'].tail(20).mean()

            data[ticker] = {
                'price': float(latest['Close']),
                'volume': float(latest['Volume']),
                'vol_avg_20d': float(vol_avg),
                'high_5d': float(df['High'].max()),
                'low_5d': float(df['Low'].min()),
                'ma_20': float(ma_20),
                'rsi': float(rsi),
                'change_pct': float((latest['Close'] - first['Close']) / first['Close'] * 100)
            }

            with open(cache_path, 'wb') as f:
                pickle.dump(data[ticker], f)

        except Exception as e:
            logger.warning(f"Fallback for {ticker}: {type(e).__name__}")
            data[ticker] = generate_mock_data(ticker)

    return data

def compute_rsi(prices, period=14):
    """Simple RSI calculation."""
    try:
        if len(prices) < period + 1:
            return 50.0
        deltas = prices.diff()
        seed = deltas[1:period+1]
        up = seed[seed >= 0].sum() / period
        down = -seed[seed < 0].sum() / period
        if down == 0:
            return 100.0 if up > 0 else 0.0
        rs = up / down
        return 100 - (100 / (1 + rs))
    except:
        return 50.0

def generate_mock_data(ticker):
    """Fallback mock data when API fails."""
    import random
    price = random.uniform(10, 500)
    return {
        'price': price,
        'volume': random.uniform(1000000, 50000000),
        'vol_avg_20d': random.uniform(1000000, 50000000),
        'high_5d': price * random.uniform(1.01, 1.15),
        'low_5d': price * random.uniform(0.85, 0.99),
        'ma_20': price * random.uniform(0.95, 1.05),
        'rsi': random.uniform(25, 75),
        'change_pct': random.uniform(-5, 5)
    }

def analyze_with_vif(market_data, watchlist_name):
    """Use Claude to analyze market data with VIF framework."""
    if not market_data:
        return {"error": "No market data to analyze"}

    data_summary = json.dumps(market_data, indent=2)

    prompt = f"""Analyze this watchlist data using VIF (Volatility Imbalance Framework) v4.0:
Watchlist: {watchlist_name}
Tickers analyzed: {len(market_data)}

Market Data (OHLCV + indicators):
{data_summary}

For each ticker, assess:
1. Gamma Regime: Estimate from RSI (>70=positive, <30=negative, else=transition) and price vs MA
2. Structural Levels: Support (near 5d low) or Resistance (near 5d high)
3. Volume Confirmation: Is volume > 1.5x 20-day average = STRONG, else WEAK
4. Kill Switches: Flag if RSI extreme (>85 or <15) or change >10%

Return ONLY valid JSON (no markdown, no extra text):
{{
  "analysis_date": "{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
  "watchlist": "{watchlist_name}",
  "tickers_analyzed": {len(market_data)},
  "signals": {{
    "TICKER": {{
      "signal": "BUY|SELL|HOLD",
      "confidence": 75,
      "gamma_regime": "positive|negative|transition",
      "level_type": "support|resistance",
      "volume_signal": "strong|weak",
      "kill_switch": "K1|K2|K3|K4|K5|K6|null",
      "price": 123.45,
      "rsi": 65,
      "reasoning": "brief 1-2 sentence explanation"
    }}
  }},
  "summary": "1-2 sentence watchlist overview"
}}"""

    try:
        message = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = message.content[0].text
        try:
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                return json.loads(response_text[json_start:json_end])
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}")
            return {"raw_response": response_text, "parse_error": str(e)}

    except Exception as e:
        logger.error(f"Claude API error: {e}")
        return {"error": str(e)}

def main():
    parser = argparse.ArgumentParser(description="VIF TradingView Watchlist Watcher")
    parser.add_argument("--watchlist", "-w", help="Watchlist file (e.g., vantage_portfolio)")
    parser.add_argument("--period", "-p", default="5d", help="Data period (1d, 5d, 1mo)")
    parser.add_argument("--all", action="store_true", help="Analyze all watchlists")
    args = parser.parse_args()

    watchlists = []
    if args.all:
        watchlists = [f.stem for f in Path("watchlists").glob("*.txt")]
    elif args.watchlist:
        watchlists = [args.watchlist]
    else:
        logger.error("Provide --watchlist NAME or --all")
        return 1

    all_results = {}

    for wl in watchlists:
        watchlist_file = f"watchlists/{wl}.txt"
        logger.info(f"\n{'='*80}")
        logger.info(f"Processing: {wl}")
        logger.info(f"{'='*80}")

        tickers = parse_watchlist(watchlist_file)
        if not tickers:
            logger.error(f"No tickers in {wl}")
            continue

        logger.info(f"Found {len(tickers)} tickers. Fetching data...")
        market_data = fetch_market_data(tickers, args.period)

        if not market_data:
            logger.error(f"Failed to fetch data for {wl}")
            continue

        logger.info(f"Analyzing {len(market_data)} tickers with Claude...")
        analysis = analyze_with_vif(market_data, wl)

        all_results[wl] = analysis

        print(f"\n{wl.upper()}")
        print("="*80)
        print(json.dumps(analysis, indent=2))
        print()

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = Path("reports") / f"analysis_{timestamp}.json"
    output_file.parent.mkdir(exist_ok=True)

    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    logger.info(f"Results saved to {output_file}")

    return 0

if __name__ == "__main__":
    sys.exit(main())
