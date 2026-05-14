#!/usr/bin/env python3
"""
Catalyst Analysis Agent — VIF Trading System
=============================================
Live Claude-powered catalyst scanner. Replaces the previous static hardcoded dict.

What it does:
  - Loads all tickers from all watchlists
  - Fetches real earnings dates from yfinance .calendar
  - Detects K4 kill switch (earnings within 5 days)
  - Calls Claude to reason about policy/macro/fundamental catalysts
  - Outputs structured JSON consumed by the HTML report and pipeline

Run:
  python scripts/catalyst_analysis.py
  python scripts/catalyst_analysis.py --watchlist vantage_portfolio
  python scripts/catalyst_analysis.py --top 10
"""

import sys, os, json, logging, argparse
from datetime import datetime, timedelta
from pathlib import Path

try:
    import yfinance as yf
    import anthropic
except ImportError as e:
    print(f"ERROR: Missing dependency — {e}")
    sys.exit(1)

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = lambda *a, **kw: None

try:
    import yaml
except ImportError:
    yaml = None

load_dotenv(override=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [CATALYST] %(message)s",
    handlers=[
        logging.FileHandler("logs/catalyst_analysis.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)
Path("logs").mkdir(exist_ok=True)
Path("reports").mkdir(exist_ok=True)

# ── Config ────────────────────────────────────────────────────────────────────
_cfg_path = Path("config/vif_config.yml")
if yaml and _cfg_path.exists():
    _cfg = yaml.safe_load(_cfg_path.read_text())
    ANALYST_MODEL    = _cfg.get("api", {}).get("models", {}).get("analyst", "claude-sonnet-4-6")
    SYNTHESIZER_MODEL = _cfg.get("api", {}).get("models", {}).get("synthesizer", "claude-opus-4-7")
else:
    ANALYST_MODEL    = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6")
    SYNTHESIZER_MODEL = "claude-opus-4-7"

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY:
    logger.error("ANTHROPIC_API_KEY not set")
    sys.exit(1)

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

K4_THRESHOLD_DAYS = 5   # earnings within this many days triggers K4
BATCH_SIZE        = 15  # tickers per Claude call

# Hardcoded FOMC meeting dates for 2026 (published by Fed annually)
FOMC_2026 = [
    "2026-01-28", "2026-03-18", "2026-04-29", "2026-06-17",
    "2026-07-29", "2026-09-16", "2026-10-28", "2026-12-09",
]


# ── Watchlist loader ──────────────────────────────────────────────────────────
def load_watchlist(name: str) -> list[str]:
    path = Path(f"watchlists/{name}.txt")
    if not path.exists():
        logger.warning(f"Watchlist not found: {path}")
        return []
    tickers = []
    for t in path.read_text().replace("\n", ",").split(","):
        t = t.strip()
        if t and not t.startswith("###"):
            clean = t.split(":")[-1]  # strip exchange prefix
            if clean:
                tickers.append(clean)
    return list(dict.fromkeys(tickers))  # deduplicate, preserve order


def load_all_watchlists() -> dict[str, list[str]]:
    watchlists = {}
    for wl_file in Path("watchlists").glob("*.txt"):
        tickers = load_watchlist(wl_file.stem)
        if tickers:
            watchlists[wl_file.stem] = tickers
    return watchlists


# ── Earnings calendar ─────────────────────────────────────────────────────────
def get_earnings_dates(tickers: list[str]) -> dict[str, dict]:
    """
    Fetch earnings dates for a list of tickers via yfinance.calendar.
    Returns {ticker: {date, days_away, k4_active}}
    """
    results = {}
    now = datetime.now()
    logger.info(f"Fetching earnings calendar for {len(tickers)} tickers...")

    for t in tickers:
        try:
            cal = yf.Ticker(t).calendar
            if not isinstance(cal, dict):
                continue
            dates = cal.get("Earnings Date", [])
            if not dates:
                continue
            # Use the nearest future date
            future = [d for d in dates if datetime.strptime(str(d), "%Y-%m-%d") >= now]
            if not future:
                continue
            nearest = min(future, key=lambda d: abs((datetime.strptime(str(d), "%Y-%m-%d") - now).days))
            days_away = (datetime.strptime(str(nearest), "%Y-%m-%d") - now).days
            results[t] = {
                "date": str(nearest),
                "days_away": days_away,
                "k4_active": abs(days_away) <= K4_THRESHOLD_DAYS,
            }
        except Exception:
            pass

    k4_count = sum(1 for v in results.values() if v["k4_active"])
    logger.info(f"Earnings found: {len(results)} tickers | K4 alerts: {k4_count}")
    return results


# ── Macro calendar (lightweight, no external API needed) ─────────────────────
def get_macro_events() -> list[dict]:
    """
    Returns forward-looking macro calendar with actual FOMC dates.
    FOMC dates are hardcoded from the official Fed schedule (published annually).
    """
    today = datetime.now().date()
    events = []

    # Next 2 FOMC meetings
    fomc_count = 0
    for date_str in sorted(FOMC_2026):
        d = datetime.strptime(date_str, "%Y-%m-%d").date()
        days_away = (d - today).days
        if days_away >= 0:
            events.append({
                "event": "FOMC Meeting",
                "date": date_str,
                "days_away": days_away,
                "impact": "HIGH",
                "affected_sectors": ["Financials", "Tech", "REITs"],
            })
            fomc_count += 1
            if fomc_count >= 2:
                break

    # Approximate monthly releases (BLS publishes schedule annually)
    events += [
        {"event": "CPI Release",  "approximate": "monthly ~13th", "impact": "HIGH",  "affected_sectors": ["Bonds", "Tech", "Consumer"]},
        {"event": "PPI Release",  "approximate": "monthly ~14th", "impact": "MED",   "affected_sectors": ["Industrials", "Materials"]},
        {"event": "Jobs Report",  "approximate": "first Friday",  "impact": "HIGH",  "affected_sectors": ["Consumer", "Financials"]},
        {"event": "PCE Deflator", "approximate": "monthly ~28th", "impact": "HIGH",  "affected_sectors": ["Tech", "Consumer"]},
    ]
    return events


def fetch_news_headlines(tickers: list[str], max_per_ticker: int = 5) -> dict[str, list[str]]:
    """
    Fetch recent news headlines via yfinance for a batch of tickers.
    Returns {ticker: [headline1, headline2, ...]}
    """
    results = {}
    for t in tickers:
        try:
            news = yf.Ticker(t).get_news(count=max_per_ticker)
            if not news:
                continue
            headlines = []
            for item in news[:max_per_ticker]:
                # yfinance news items have nested content structure
                content = item.get("content", item)
                title = content.get("title", item.get("title", ""))
                if title:
                    headlines.append(title)
            if headlines:
                results[t] = headlines
        except Exception:
            pass
    if results:
        logger.info(f"News fetched for {len(results)}/{len(tickers)} tickers")
    return results


# ── Claude prompt ─────────────────────────────────────────────────────────────
CATALYST_SYSTEM_PROMPT = """You are a senior macro and fundamental analyst for an AI-powered trading system using the VIF (Volatility Imbalance Framework) v4.0.

Your job: identify real, current catalysts that could cause price moves > 5% in the next 5-30 trading days for the tickers provided. You think in terms of:
- Policy catalysts: Fed decisions, CHIPS Act funding rounds, export controls, tariffs, executive orders
- Government catalysts: DoD contracts, FDA approvals, ARPA grants, regulatory decisions
- Fundamental catalysts: earnings beats/misses, guidance changes, revenue preannouncements, analyst upgrades
- Sector rotation: capital flows between sectors driven by macro regime changes
- Macro regime: rate environment, inflation trajectory, risk-on/risk-off positioning

RULES:
- Only cite catalysts that are plausible given the current macro environment (May 2026)
- Be specific: "CHIPS Act round 3 disbursement Q3 2026" not "government support"
- Assign a catalyst_strength: HIGH (>10% expected move) | MED (5-10%) | LOW (<5%)
- Flag kill_switch K4 ONLY if earnings are within 5 days of today
- sector_rotation must name the DESTINATION sector, not just the source
- macro_regime must include current Fed stance, rate trajectory, and risk appetite

Return ONLY valid JSON — no markdown, no commentary."""

CATALYST_USER_TEMPLATE = """Today: {today}

TICKERS TO ANALYZE: {tickers}

EARNINGS CALENDAR (from yfinance — authoritative):
{earnings_json}

RECENT NEWS HEADLINES (from yfinance, last 48-72 hours):
{news_json}

MACRO CALENDAR:
{macro_json}

TASK — Return this exact JSON structure:
{{
  "scan_date": "{today}",
  "macro_regime": {{
    "fed_stance": "one phrase",
    "rate_trajectory": "rising|falling|neutral",
    "risk_appetite": "risk-on|risk-off|neutral",
    "key_theme": "one sentence describing dominant macro driver"
  }},
  "sector_themes": [
    {{"theme": "theme name", "tickers": ["T1","T2"], "catalyst_strength": "HIGH|MED|LOW", "time_horizon": "1-5d|5-30d|30d+"}}
  ],
  "macro_calendar": [
    {{"event": "event name", "date": "YYYY-MM-DD or 'TBD'", "impact": "HIGH|MED|LOW", "affected_sectors": ["sector1"]}}
  ],
  "ticker_catalysts": [
    {{
      "ticker": "TICK",
      "catalyst_type": "policy|government|fundamental|sector|macro",
      "catalyst": "specific catalyst description",
      "catalyst_strength": "HIGH|MED|LOW",
      "time_horizon": "1-5d|5-30d|30d+",
      "key_risk": "one sentence",
      "kill_switch": null
    }}
  ],
  "high_risk_catalysts": [
    {{
      "ticker": "TICK",
      "catalyst": "description",
      "date": "YYYY-MM-DD or approximate",
      "days_away": 0,
      "risk": "HIGH|MED|LOW",
      "action": "K4 kill switch — do not take new positions"
    }}
  ],
  "top_5_opportunity_tickers": ["T1","T2","T3","T4","T5"],
  "top_3_risk_tickers": ["T1","T2","T3"]
}}"""


# ── Claude analysis ───────────────────────────────────────────────────────────
def analyze_catalysts_with_claude(
    tickers: list[str],
    earnings: dict,
    macro_events: list,
    news: dict,
    batch_label: str = "all",
) -> dict:
    """Single Claude call for a batch of tickers."""
    today = datetime.now().strftime("%Y-%m-%d %A")

    # Only include earnings and news for tickers in this batch
    batch_earnings = {t: v for t, v in earnings.items() if t in tickers}
    batch_news     = {t: v for t, v in news.items()     if t in tickers}

    user_prompt = CATALYST_USER_TEMPLATE.format(
        today=today,
        tickers=", ".join(tickers),
        earnings_json=json.dumps(batch_earnings, indent=2),
        news_json=json.dumps(batch_news, indent=2) if batch_news else "No recent headlines available.",
        macro_json=json.dumps(macro_events, indent=2),
    )

    try:
        msg = client.messages.create(
            model=ANALYST_MODEL,
            max_tokens=8192,  # Increased from 4096 to avoid truncation
            system=[
                {
                    "type": "text",
                    "text": CATALYST_SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=[{"role": "user", "content": user_prompt}],
            temperature=0,
        )
        text = msg.content[0].text.strip()

        # Check if response was truncated (no closing braces/brackets)
        if not text.endswith('}') and not text.endswith(']'):
            logger.warning(f"Batch '{batch_label}': Possible truncation detected, response may be incomplete")

        # Strip markdown fences if present
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:-1]) if lines[-1].strip() == "```" else "\n".join(lines[1:])

        result = json.loads(text)
        logger.info(
            f"Batch '{batch_label}': {len(tickers)} tickers | "
            f"themes={len(result.get('sector_themes',[]))} | "
            f"catalysts={len(result.get('ticker_catalysts',[]))} | "
            f"high_risk={len(result.get('high_risk_catalysts',[]))}"
        )
        return result

    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error (batch '{batch_label}'): {e}")
        # Attempt to repair common JSON issues
        try:
            import re
            repair_text = text.rstrip()

            # Fix unterminated strings (look for incomplete strings before closing braces/brackets)
            repair_text = re.sub(r'": "[^"]*$', '": "TRUNCATED"}', repair_text)

            # Close any unclosed brackets/braces
            open_braces = repair_text.count('{') - repair_text.count('}')
            open_brackets = repair_text.count('[') - repair_text.count(']')

            if open_braces > 0:
                repair_text += '}' * open_braces
            if open_brackets > 0:
                repair_text += ']' * open_brackets

            result = json.loads(repair_text)
            logger.info(f"Batch '{batch_label}': Recovered from JSON error via repair")
            return result
        except Exception as repair_e:
            logger.error(f"JSON repair failed ({repair_e}). Returning empty structure for batch '{batch_label}'")
            return {
                "sector_themes": [],
                "ticker_catalysts": [],
                "high_risk_catalysts": [],
                "macro_regime": {"status": "unknown"},
            }
    except Exception as e:
        logger.error(f"Claude API error (batch '{batch_label}'): {e}")
        return {
            "sector_themes": [],
            "ticker_catalysts": [],
            "high_risk_catalysts": [],
            "macro_regime": {"status": "unknown"},
        }


def merge_batch_results(batches: list[dict]) -> dict:
    """Merge multiple batch results into a single unified report."""
    merged = {
        "macro_regime": {},
        "sector_themes": [],
        "macro_calendar": [],
        "ticker_catalysts": [],
        "high_risk_catalysts": [],
        "top_5_opportunity_tickers": [],
        "top_3_risk_tickers": [],
    }

    seen_themes = set()
    seen_catalysts = set()
    seen_k4 = set()

    for batch in batches:
        if "error" in batch:
            continue

        # Use the first valid macro_regime (they should all agree)
        if not merged["macro_regime"] and batch.get("macro_regime"):
            merged["macro_regime"] = batch["macro_regime"]

        # Deduplicate sector themes by name
        for theme in batch.get("sector_themes", []):
            key = theme.get("theme", "")
            if key not in seen_themes:
                merged["sector_themes"].append(theme)
                seen_themes.add(key)

        # Deduplicate macro calendar by event name
        for evt in batch.get("macro_calendar", []):
            key = evt.get("event", "")
            if key not in seen_themes:
                merged["macro_calendar"].append(evt)
                seen_themes.add(key)

        # Deduplicate ticker catalysts by (ticker, catalyst_type)
        for cat in batch.get("ticker_catalysts", []):
            key = (cat.get("ticker"), cat.get("catalyst_type"))
            if key not in seen_catalysts:
                merged["ticker_catalysts"].append(cat)
                seen_catalysts.add(key)

        # Deduplicate K4 alerts by ticker
        for alert in batch.get("high_risk_catalysts", []):
            t = alert.get("ticker")
            if t and t not in seen_k4:
                merged["high_risk_catalysts"].append(alert)
                seen_k4.add(t)

        # Accumulate opportunity and risk tickers
        merged["top_5_opportunity_tickers"].extend(batch.get("top_5_opportunity_tickers", []))
        merged["top_3_risk_tickers"].extend(batch.get("top_3_risk_tickers", []))

    # Deduplicate opportunity/risk lists, keep order
    merged["top_5_opportunity_tickers"] = list(dict.fromkeys(merged["top_5_opportunity_tickers"]))[:5]
    merged["top_3_risk_tickers"]        = list(dict.fromkeys(merged["top_3_risk_tickers"]))[:3]

    return merged


# ── Per-watchlist analysis ────────────────────────────────────────────────────
def analyze_watchlist(
    watchlist_name: str,
    tickers: list[str],
    earnings: dict,
    macro_events: list,
    news: dict,
    top_n: int = 15,
) -> dict:
    """Run Claude catalyst analysis for a single watchlist."""
    # Prioritize tickers with known earnings dates first, then alphabetical
    with_earnings = [t for t in tickers if t in earnings]
    without = [t for t in tickers if t not in with_earnings]
    prioritized = (with_earnings + without)[:top_n]

    logger.info(f"Analyzing '{watchlist_name}': {len(prioritized)} tickers (of {len(tickers)} total)")

    # Batch into groups
    batches = []
    for i in range(0, len(prioritized), BATCH_SIZE):
        batch = prioritized[i : i + BATCH_SIZE]
        label = f"{watchlist_name}_batch{i // BATCH_SIZE + 1}"
        result = analyze_catalysts_with_claude(batch, earnings, macro_events, news, label)
        batches.append(result)

    merged = merge_batch_results(batches)
    merged["watchlist"] = watchlist_name
    merged["tickers_analyzed"] = len(prioritized)
    merged["total_tickers_in_watchlist"] = len(tickers)
    return merged


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="VIF Live Catalyst Scanner")
    parser.add_argument("--watchlist", "-w", help="Single watchlist (e.g., vantage_portfolio)")
    parser.add_argument("--top",       "-t", type=int, default=15, help="Max tickers per watchlist (default 15)")
    args = parser.parse_args()

    logger.info("=" * 70)
    logger.info("CATALYST ANALYSIS AGENT — VIF TRADING SYSTEM (LIVE)")
    logger.info(f"  {datetime.now().strftime('%Y-%m-%d %H:%M')}  |  model={ANALYST_MODEL}")
    logger.info("=" * 70)

    # Load watchlists
    if args.watchlist:
        watchlists = {args.watchlist: load_watchlist(args.watchlist)}
    else:
        watchlists = load_all_watchlists()

    if not watchlists:
        logger.error("No watchlists found in watchlists/")
        return 1

    # Collect all unique tickers for a single earnings calendar + news fetch
    all_tickers  = list(dict.fromkeys(t for tickers in watchlists.values() for t in tickers))
    earnings     = get_earnings_dates(all_tickers)
    macro_events = get_macro_events()
    news         = fetch_news_headlines(all_tickers)

    # Run per-watchlist analysis
    report = {
        "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "model": ANALYST_MODEL,
        "catalyst_themes": {},  # populated below from merged sector_themes
        "watchlist_analyses": {},
        "k4_kill_switches": {},  # all K4 alerts across all watchlists
    }

    all_themes: dict[str, list[str]] = {}

    for wl_name, tickers in watchlists.items():
        result = analyze_watchlist(wl_name, tickers, earnings, macro_events, news, top_n=args.top)
        report["watchlist_analyses"][wl_name.upper()] = result

        # Aggregate K4 alerts
        for alert in result.get("high_risk_catalysts", []):
            t = alert.get("ticker")
            if t:
                report["k4_kill_switches"][t] = {
                    "switch": "K4",
                    "earnings_date": alert.get("date"),
                    "days_away": alert.get("days_away"),
                    "action": "Do not initiate new positions",
                }

        # Aggregate sector themes
        for theme in result.get("sector_themes", []):
            name = theme.get("theme", "")
            tks  = theme.get("tickers", [])
            if name not in all_themes:
                all_themes[name] = []
            all_themes[name].extend(tks)

    # Deduplicate theme tickers
    report["catalyst_themes"] = {k: list(dict.fromkeys(v)) for k, v in all_themes.items()}

    # Add earnings calendar for all tickers with dates
    report["earnings_calendar"] = {
        t: v for t, v in sorted(earnings.items(), key=lambda x: x[1]["days_away"])
    }

    # Save
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = Path("reports") / f"catalyst_analysis_{ts}.json"
    out.write_text(json.dumps(report, indent=2))
    logger.info(f"Catalyst analysis saved -> {out}")

    # Console summary
    print(f"\n{'='*70}")
    print(f"CATALYST SCAN COMPLETE | {len(watchlists)} watchlists | {len(all_tickers)} tickers")
    print(f"{'='*70}")
    print(f"  K4 Kill Switches: {len(report['k4_kill_switches'])} tickers")
    print(f"  Sector Themes:    {len(report['catalyst_themes'])} active")
    print(f"  Earnings tracked: {len(report['earnings_calendar'])} tickers")
    if report["k4_kill_switches"]:
        print(f"\n  K4 ALERTS (do not trade):")
        for t, v in report["k4_kill_switches"].items():
            print(f"    {t}: earnings {v['earnings_date']} ({v['days_away']}d away)")
    print(f"\n  Saved: {out}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
