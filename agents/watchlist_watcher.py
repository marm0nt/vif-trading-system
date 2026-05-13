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
    load_dotenv = lambda *a, **kw: None

import yaml

# override=True ensures .env wins over any stale system env var.
load_dotenv(override=True)

CLAUDE_API_KEY = os.getenv("ANTHROPIC_API_KEY")

config_path = Path("config/vif_config.yml")
if config_path.exists():
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    CLAUDE_MODEL = config.get("api", {}).get("models", {}).get("analyst", "claude-sonnet-4-6")
else:
    CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6")

if not CLAUDE_API_KEY:
    print("ERROR: ANTHROPIC_API_KEY not found in .env")
    sys.exit(1)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/watchlist_watcher.log'),
        logging.StreamHandler()
    ]
)
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

    for ticker in tickers:
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

            # Handle MultiIndex columns from newer yfinance versions
            if isinstance(df.columns, pd.MultiIndex):
                df = pd.DataFrame({
                    'Close': df[('Close', ticker_clean)],
                    'High': df[('High', ticker_clean)],
                    'Low': df[('Low', ticker_clean)],
                    'Open': df[('Open', ticker_clean)],
                    'Volume': df[('Volume', ticker_clean)],
                })

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
    """Fallback mock data when API fails. MARKED FOR REJECTION IN PRODUCTION."""
    import random
    price = random.uniform(10, 500)
    return {
        '_is_mock': True,  # CRITICAL: Flag for detection downstream
        'price': price,
        'volume': random.uniform(1000000, 50000000),
        'vol_avg_20d': random.uniform(1000000, 50000000),
        'high_5d': price * random.uniform(1.01, 1.15),
        'low_5d': price * random.uniform(0.85, 0.99),
        'ma_20': price * random.uniform(0.95, 1.05),
        'rsi': random.uniform(25, 75),
        'change_pct': random.uniform(-5, 5)
    }

def validate_market_data(data, ticker):
    """Validate data quality. Return (is_valid, reason)."""
    if data.get('_is_mock'):
        return False, f"[{ticker}] yfinance failed — skipping (no mock data in production)"
    if data.get('volume', 0) < 50_000:
        return False, f"[{ticker}] Volume too low ({data['volume']:,.0f}) — insufficient liquidity"
    if not data.get('price'):
        return False, f"[{ticker}] No price data"
    return True, ""

def categorize_ticker_complexity(ticker_data):
    """Determine if ticker is simple (Haiku) or complex (Sonnet) based on indicators."""
    rsi = ticker_data.get('rsi', 50)
    price = ticker_data.get('price', 0)
    ma_20 = ticker_data.get('ma_20', price)
    vol_avg = ticker_data.get('vol_avg_20d', 1)
    vol_current = ticker_data.get('volume', 1)
    change_pct = abs(ticker_data.get('change_pct', 0))

    is_rsi_extreme = rsi > 75 or rsi < 25
    is_gap_large = change_pct > 5
    is_vol_strong = vol_current > vol_avg * 1.5

    if (is_rsi_extreme or is_gap_large) and is_vol_strong:
        return "complex"
    if change_pct > 8:
        return "complex"
    return "simple"

def split_into_batches(market_data, batch_size=12):
    """Split tickers into batches by complexity for hybrid model routing. Skip invalid data."""
    simple_tickers = {}
    complex_tickers = {}
    skipped = []

    for ticker, data in market_data.items():
        is_valid, reason = validate_market_data(data, ticker)
        if not is_valid:
            logger.warning(reason)
            skipped.append(ticker)
            continue

        if categorize_ticker_complexity(data) == "simple":
            simple_tickers[ticker] = data
        else:
            complex_tickers[ticker] = data

    if skipped:
        logger.info(f"Skipped {len(skipped)} tickers: {', '.join(skipped)}")

    # Batch simple tickers (Haiku)
    tickers = list(simple_tickers.keys())
    for i in range(0, len(tickers), batch_size):
        batch_list = tickers[i:i+batch_size]
        batch_data = {t: simple_tickers[t] for t in batch_list}
        yield batch_data, batch_list, "claude-haiku-4-5-20251001"

    # Batch complex tickers (Sonnet)
    tickers = list(complex_tickers.keys())
    for i in range(0, len(tickers), batch_size):
        batch_list = tickers[i:i+batch_size]
        batch_data = {t: complex_tickers[t] for t in batch_list}
        yield batch_data, batch_list, CLAUDE_MODEL

def analyze_with_vif(market_data, watchlist_name):
    """Use Claude to analyze market data with VIF framework (batched)."""
    if not market_data:
        return {"error": "No market data to analyze"}

    all_signals = {}
    all_kills = {}
    all_buys = []

    system_prompt = """You are a VIF v4.0 analyst. Apply the Volatility Imbalance Framework to the data and return ONLY valid JSON.

<vif_rules>
• Gamma regime: RSI>65 & price>MA20 = positive | RSI<35 & price<MA20 = negative | else = transition
• Volume: vol > 1.5x avg = STRONG | <0.8x = WEAK | else = NORMAL
• Kill switches: K1=RSI>80 or <20 | K2=5d-range>12% | K3=vol<500k | K4=earnings<5d | K6=price<MA20 & vol_weak
• Signal: BUY (positive gamma + strong vol + no kill) | SELL (negative gamma + kill active) | HOLD (everything else)
• Confidence: 0-100 – be honest, never inflate.
</vif_rules>

EXPECTED SCHEMA:
{
  "signals": {
    "TICKER": {
      "signal": "BUY|SELL|HOLD",
      "confidence": 75,
      "gamma_regime": "positive|negative|transition",
      "volume_signal": "strong|normal|weak",
      "kill_switch": null,
      "price": 0.00,
      "rsi": 0,
      "note": "max 12 words"
    }
  },
  "top_buys": ["TICK1"],
  "kill_alerts": {"TICKER": "K1"}
}"""

    batch_num = 0
    for batch_data, batch_list, model_to_use in split_into_batches(market_data):
        batch_num += 1
        data_summary = json.dumps(batch_data, indent=2)
        model_label = "Haiku" if "haiku" in model_to_use else "Sonnet"

        user_prompt = f"""Batch {batch_num} ({model_label}): {watchlist_name} | Tickers: {len(batch_data)} | Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}
<data>
{data_summary}
</data>"""

        try:
            message = client.messages.create(
                model=model_to_use,
                max_tokens=6000,  # Increased to avoid truncation
                system=[
                    {
                        "type": "text",
                        "text": system_prompt,
                        "cache_control": {"type": "ephemeral"}
                    }
                ],
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )

            response_text = message.content[0].text

            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json\n"):
                    response_text = response_text[5:]
                response_text = response_text.rstrip("```").strip()

            try:
                batch_result = json.loads(response_text)

                if "signals" in batch_result:
                    all_signals.update(batch_result["signals"])
                if "top_buys" in batch_result:
                    all_buys.extend(batch_result["top_buys"])
                if "kill_alerts" in batch_result:
                    all_kills.update(batch_result["kill_alerts"])

            except json.JSONDecodeError as e:
                logger.error(f"JSON parse error in batch {batch_num}: {e}")
                # Attempt JSON repair: close any open strings/brackets
                try:
                    import re
                    repair_text = response_text.rstrip()

                    # Fix unterminated strings
                    repair_text = re.sub(r'": "[^"]*$', '": "TRUNCATED"}', repair_text)

                    # Close unclosed brackets/braces
                    open_braces = repair_text.count('{') - repair_text.count('}')
                    open_brackets = repair_text.count('[') - repair_text.count(']')

                    if open_braces > 0:
                        repair_text += '}' * open_braces
                    if open_brackets > 0:
                        repair_text += ']' * open_brackets

                    batch_result = json.loads(repair_text)
                    if "signals" in batch_result:
                        all_signals.update(batch_result["signals"])
                    if "top_buys" in batch_result:
                        all_buys.extend(batch_result["top_buys"])
                    if "kill_alerts" in batch_result:
                        all_kills.update(batch_result["kill_alerts"])
                    logger.info(f"Recovered batch {batch_num} via JSON repair")
                except:
                    logger.warning(f"Batch {batch_num} skipped due to unrecoverable JSON error")

        except Exception as e:
            logger.error(f"Claude API error in batch {batch_num}: {e}")

    return {
        "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "watchlist": watchlist_name,
        "tickers_analyzed": len(market_data),
        "top_3_buys": all_buys[:3] if all_buys else [],
        "kill_switch_alerts": all_kills,
        "signals": all_signals
    }

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

        logger.info(f"Analyzing {len(market_data)} tickers with Claude ({CLAUDE_MODEL})...")
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

    # Auto-export to Excel
    try:
        from scripts.json_to_excel_exporter import json_to_excel
        excel_file = json_to_excel(str(output_file))
        if excel_file:
            logger.info(f"Excel export saved to {excel_file}")
    except Exception as e:
        logger.warning(f"Excel export failed: {e}")

    return 0

if __name__ == "__main__":
    sys.exit(main())
