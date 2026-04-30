#!/usr/bin/env python3
"""
Weekend Catalyst Agent – VIF Trading System
Scans for macro news, earnings catalysts, and sector events over the weekend.
Outputs a structured Monday morning briefing with ranked opportunities.
Runs: Saturday 8 AM + Sunday 6 PM (CT)
"""
import sys, os, json, logging
from datetime import datetime, timedelta
from pathlib import Path

try:
    import yfinance as yf
    import pandas as pd
except ImportError as e:
    print(f"ERROR: Missing dependency – {e}")
    sys.exit(1)

try:
    import anthropic
except ImportError:
    print("ERROR: anthropic not installed")
    sys.exit(1)

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = lambda *a, **kw: None

load_dotenv(override=True)  # .env wins over any stale system env var

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [WEEKEND] %(message)s",
    handlers=[
        logging.FileHandler("logs/weekend_catalyst.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)
Path("logs").mkdir(exist_ok=True)
Path("reports").mkdir(exist_ok=True)

CLAUDE_API_KEY = os.getenv("ANTHROPIC_API_KEY") or os.getenv("CLAUDE_API_KEY")
CLAUDE_MODEL   = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6")

# ── Watchlist loader ──────────────────────────────────────────────────────────
def load_all_tickers():
    tickers = set()
    for wl in ["vantage_portfolio", "ai_verticals", "energy_ai"]:
        try:
            with open(f"watchlists/{wl}.txt") as f:
                for t in f.read().replace("\n", ",").split(","):
                    t = t.strip().split(":")[-1]
                    if t and not t.startswith("###"):
                        tickers.add(t)
        except FileNotFoundError:
            pass
    return sorted(tickers)


# ── Market data snapshot ──────────────────────────────────────────────────────
def fetch_weekly_data(tickers: list[str]) -> dict:
    """Pull 1-month of OHLCV, compute weekly indicators."""
    data = {}
    logger.info(f"Fetching weekly data for {len(tickers)} tickers…")
    for t in tickers:
        try:
            df = yf.download(t, period="1mo", progress=False)
            if df is None or len(df) < 5:
                continue
            # Flatten MultiIndex if present
            if isinstance(df.columns, pd.MultiIndex):
                df = pd.DataFrame({
                    "Close": df[("Close", t)],
                    "High":  df[("High",  t)],
                    "Low":   df[("Low",   t)],
                    "Volume":df[("Volume", t)],
                }).dropna()
            else:
                df = df[["Close", "High", "Low", "Volume"]].dropna()

            close = df["Close"].values
            vol   = df["Volume"].values

            week_chg  = (close[-1] - close[-5]) / close[-5] * 100 if len(close) >= 5 else 0
            month_chg = (close[-1] - close[0])  / close[0]  * 100
            vol_avg   = vol[-10:].mean() if len(vol) >= 10 else vol.mean()
            vol_ratio = vol[-1] / vol_avg if vol_avg > 0 else 1.0

            # Quick RSI
            deltas = [close[i] - close[i-1] for i in range(1, len(close))]
            gains  = sum(d for d in deltas[-14:] if d > 0) / 14 if len(deltas) >= 14 else 0
            losses = -sum(d for d in deltas[-14:] if d < 0) / 14 if len(deltas) >= 14 else 0
            rsi    = 100 - (100 / (1 + gains/losses)) if losses > 0 else 50.0

            data[t] = {
                "price":      round(float(close[-1]), 2),
                "week_chg":   round(week_chg, 2),
                "month_chg":  round(month_chg, 2),
                "rsi":        round(rsi, 1),
                "vol_ratio":  round(vol_ratio, 2),
                "high_1m":    round(float(df["High"].max()), 2),
                "low_1m":     round(float(df["Low"].min()),  2),
            }
        except Exception as e:
            logger.warning(f"  {t}: {type(e).__name__}")
    return data


# ── Earnings/event calendar (lightweight via yfinance) ────────────────────────
def get_upcoming_events(tickers: list[str]) -> list[dict]:
    """Flag tickers with earnings or major events in the next 5 trading days."""
    events = []
    for t in tickers:
        try:
            info = yf.Ticker(t).info
            # yfinance exposes earningsTimestamp for some tickers
            ts = info.get("earningsTimestamp")
            if ts:
                event_dt = datetime.fromtimestamp(ts)
                days_away = (event_dt - datetime.now()).days
                if -2 <= days_away <= 7:
                    events.append({
                        "ticker": t,
                        "event": "EARNINGS",
                        "date": event_dt.strftime("%Y-%m-%d"),
                        "days_away": days_away,
                    })
        except Exception:
            pass
    return events


# ── Prompt for Claude ─────────────────────────────────────────────────────────
WEEKEND_PROMPT = """You are a VIF (Volatility Imbalance Framework) v4.0 analyst preparing a concise Monday Morning Briefing.

INPUT DATA:
{data_json}

UPCOMING EVENTS (earnings/catalysts within 7 days):
{events_json}

MACRO CONTEXT:
- Analysis date: {date}
- Review the past week's price action, volume anomalies, and RSI positioning.
- Identify weekend news themes: Fed policy, CHIPS Act updates, AI capex, geopolitical risk, energy prices.

TASK – Return ONLY valid JSON, no markdown, no commentary:
{{
  "briefing_date": "{date}",
  "macro_themes": ["theme1", "theme2"],
  "top_long_setups": [
    {{"ticker": "X", "reason": "one sentence", "entry_zone": "$XX", "risk": "one word"}}
  ],
  "top_short_watch": [
    {{"ticker": "X", "reason": "one sentence"}}
  ],
  "earnings_watch": [
    {{"ticker": "X", "date": "YYYY-MM-DD", "bias": "bullish|bearish|neutral", "key_metric": "what to watch"}}
  ],
  "kill_switch_alerts": [
    {{"ticker": "X", "switch": "K1-K6", "reason": "one sentence"}}
  ],
  "sector_rotation": "one paragraph – where money is moving and why",
  "monday_game_plan": "2-3 actionable bullet points for the open"
}}

Rules:
- top_long_setups: max 5 tickers, highest conviction only (RSI < 70, vol_ratio > 1.0 preferred)
- top_short_watch: max 3 tickers
- earnings_watch: only tickers present in the input data
- Kill switch K4 = earnings within 5 days (flag if risk is high)
- Be concise. No filler. Every word earns its place."""


def run_weekend_analysis(market_data: dict, events: list) -> dict:
    if not CLAUDE_API_KEY:
        logger.error("CLAUDE_API_KEY not set – skipping AI analysis")
        return {"error": "No API key"}

    # Batch into top 40 by volume ratio (most active this week)
    top = sorted(market_data.items(), key=lambda x: abs(x[1].get("week_chg", 0)), reverse=True)[:40]
    batch = dict(top)

    prompt = WEEKEND_PROMPT.format(
        data_json=json.dumps(batch, indent=2),
        events_json=json.dumps(events, indent=2),
        date=datetime.now().strftime("%Y-%m-%d %A"),
    )

    client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
    try:
        msg = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}],
        )
        text = msg.content[0].text
        j0, j1 = text.find("{"), text.rfind("}") + 1
        return json.loads(text[j0:j1]) if j0 != -1 else {"raw": text}
    except Exception as e:
        logger.error(f"Claude API error: {e}")
        return {"error": str(e)}


def main():
    logger.info("=" * 70)
    logger.info("WEEKEND CATALYST AGENT – VIF TRADING SYSTEM")
    logger.info("=" * 70)

    tickers = load_all_tickers()
    logger.info(f"Loaded {len(tickers)} tickers")

    market_data = fetch_weekly_data(tickers)
    logger.info(f"Market data fetched for {len(market_data)} tickers")

    events = get_upcoming_events(tickers)
    logger.info(f"Upcoming events flagged: {len(events)}")

    logger.info("Running Claude VIF weekend analysis…")
    briefing = run_weekend_analysis(market_data, events)

    # Save
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = Path("reports") / f"weekend_briefing_{ts}.json"
    payload = {
        "generated_at": datetime.now().isoformat(),
        "tickers_scanned": len(market_data),
        "upcoming_events": events,
        "briefing": briefing,
    }
    with open(out, "w") as f:
        json.dump(payload, f, indent=2)

    # Print compact summary to console
    print("\n" + "=" * 70)
    print("MONDAY MORNING BRIEFING")
    print("=" * 70)
    print(json.dumps(briefing, indent=2))
    print(f"\n[SAVED] {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
