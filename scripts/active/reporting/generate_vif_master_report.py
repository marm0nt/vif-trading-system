#!/usr/bin/env python3
"""
VIF Master Interactive Report Generator
========================================
Reads the latest analysis JSON outputs and produces a single,
fully-interactive HTML dashboard covering all 6 watchlists.

Features:
- Dark professional trading theme
- Filterable/sortable signal table (BUY/SELL/HOLD, watchlist, tier, search)
- Chart.js visualizations (signal distribution, confidence, kill switches)
- Kill switch alert panel
- Per-watchlist summary tabs
- VIF tier labels (Macro Vanguard / Primary Conviction / Speculative / Waiting)
- Cross-watchlist duplicate detection
- CSV export

Usage:
  python scripts/generate_vif_master_report.py
  python scripts/generate_vif_master_report.py --json reports/analysis_20260507_120000.json
"""

import json
import argparse
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# ── Watchlist tier parsing ────────────────────────────────────────────────────

TIER_MAP = {
    "###01_MACRO_VANGUARD":    "Macro Vanguard",
    "###02_PRIMARY_CONVICTION":"Primary Conviction",
    "###03_SPECULATIVE_SCOUTS":"Speculative",
    "###04_WAITING_LIST":      "Waiting List",
}
TIER_COLORS = {
    "Macro Vanguard":    {"bg": "#1e3a5f", "fg": "#60a5fa", "badge": "#2563eb"},
    "Primary Conviction":{"bg": "#1a3d2b", "fg": "#4ade80", "badge": "#16a34a"},
    "Speculative":       {"bg": "#3d2a1a", "fg": "#fb923c", "badge": "#ea580c"},
    "Waiting List":      {"bg": "#2d2d2d", "fg": "#9ca3af", "badge": "#6b7280"},
}
SIGNAL_COLORS = {
    "BUY":  {"bg": "#166534", "fg": "#bbf7d0", "border": "#16a34a"},
    "SELL": {"bg": "#7f1d1d", "fg": "#fecaca", "border": "#dc2626"},
    "HOLD": {"bg": "#78350f", "fg": "#fef3c7", "border": "#d97706"},
}
KS_COLORS = {
    "K1": "#f97316", "K2": "#ef4444", "K3": "#f97316",
    "K4": "#ec4899", "K5": "#a855f7", "K6": "#ec4899",
}

WATCHLIST_DISPLAY = {
    "AI Physical Layer & Power Infrastructure": "AI Physical Layer",
    "AI Verticals (Supply Chain)": "AI Verticals",
    "Core Growth & Macro Indices (Large-Cap Anchors)": "Core Growth",
    "Energy & AI (Power Convergence)": "Energy & AI",
    "Speculative _ High-Beta": "Speculative/HB",
    "Trump Admin_ Onshoring": "Onshoring",
}


def load_watchlist_tiers() -> dict:
    """Returns {ticker: (tier_name, watchlist_name)} from all watchlist files."""
    tier_data = {}
    wl_dir = Path("watchlists")
    for txt in wl_dir.glob("*.txt"):
        wl_name = txt.stem
        current_tier = "Speculative"
        with open(txt, encoding="utf-8") as f:
            raw = f.read()
        tokens = re.split(r"[\n,]+", raw)
        for tok in tokens:
            tok = tok.strip()
            if not tok:
                continue
            if tok in TIER_MAP:
                current_tier = TIER_MAP[tok]
                continue
            ticker = tok.split(":")[-1] if ":" in tok else tok
            if ticker and not ticker.startswith("#"):
                if ticker not in tier_data:
                    tier_data[ticker] = []
                tier_data[ticker].append({"tier": current_tier, "watchlist": wl_name})
    return tier_data


def load_latest_analysis(override_path: str = None) -> dict:
    """Load the most recent analysis JSON, merge all watchlists."""
    if override_path:
        candidates = [Path(override_path)]
    else:
        candidates = sorted(
            Path("reports").glob("analysis_*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )

    merged = {}
    for path in candidates[:1]:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            merged.update(data)
            print(f"  Loaded: {path.name}")
            break
        except Exception as e:
            print(f"  Warning: failed to load {path}: {e}")

    # Also pick up any individual watchlist JSONs from pipeline runs
    for path in sorted(Path("reports").glob("pipeline_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)[:3]:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict) and "signals" in data:
                wl = data.get("watchlist", path.stem)
                if wl not in merged:
                    merged[wl] = data
        except Exception:
            pass

    return merged


def flatten_signals(analysis: dict, tier_data: dict) -> list:
    """Convert raw analysis dict → flat list of signal rows."""
    rows = []
    for wl_name, wl_data in analysis.items():
        if not isinstance(wl_data, dict):
            continue
        signals = wl_data.get("signals", {})
        kill_alerts = wl_data.get("kill_switch_alerts", {})
        analysis_date = wl_data.get("analysis_date", "")

        for ticker, sig_data in signals.items():
            if not isinstance(sig_data, dict):
                continue

            signal = sig_data.get("signal", "HOLD").upper()

            # Confidence: handle both 0-100 integer and 0.0-1.0 float formats
            raw_conf = sig_data.get("confidence", 0)
            if isinstance(raw_conf, str):
                try:
                    raw_conf = float(raw_conf.strip("%"))
                    if raw_conf > 1:
                        raw_conf = raw_conf / 100
                except Exception:
                    raw_conf = 0.5
            else:
                raw_conf = float(raw_conf)
                if raw_conf > 1:        # it's 0-100 integer — normalise to 0-1
                    raw_conf = raw_conf / 100
            confidence = round(raw_conf, 3)

            gamma = sig_data.get("gamma_regime", "unknown")

            # Reasoning: try multiple field names used by different agents
            reasoning = (sig_data.get("note") or sig_data.get("reasoning")
                         or sig_data.get("analysis") or "")

            # Kill switch: merge signal-level field + watchlist-level alert dict
            ks_from_sig  = sig_data.get("kill_switch", "")
            ks_from_dict = kill_alerts.get(ticker, "")
            kill_switches = ks_from_sig or ks_from_dict

            # Tier lookup: strip exchange prefix (NASDAQ:KLRA → KLRA)
            plain = ticker.split(":")[-1] if ":" in ticker else ticker
            ticker_tiers = (tier_data.get(ticker)
                            or tier_data.get(plain)
                            or [{"tier": "Speculative", "watchlist": wl_name}])
            primary = ticker_tiers[0]
            tier = primary["tier"]
            wl_display = WATCHLIST_DISPLAY.get(wl_name, wl_name[:20])
            in_multiple = len(set(t["watchlist"] for t in ticker_tiers)) > 1

            rows.append({
                "ticker": ticker,
                "ticker_plain": plain,
                "signal": signal,
                "confidence": confidence,
                "confidence_pct": f"{int(confidence*100)}%",
                "gamma": gamma,
                "tier": tier,
                "watchlist": wl_name,
                "watchlist_short": wl_display,
                "kill_switches": kill_switches,
                "reasoning": str(reasoning)[:300].replace('"', "'"),
                "in_multiple": in_multiple,
                "analysis_date": analysis_date,
                "price": sig_data.get("price", 0),
                "rsi": sig_data.get("rsi", 0),
            })

    rows.sort(key=lambda r: (-r["confidence"], r["signal"]))
    return rows


def build_stats(rows: list, analysis: dict) -> dict:
    buy  = sum(1 for r in rows if r["signal"] == "BUY")
    sell = sum(1 for r in rows if r["signal"] == "SELL")
    hold = sum(1 for r in rows if r["signal"] == "HOLD")
    ks_total = sum(1 for r in rows if r["kill_switches"])
    avg_conf = sum(r["confidence"] for r in rows) / len(rows) if rows else 0
    top_buy  = [r for r in rows if r["signal"] == "BUY"][:10]
    watchlists_count = len(analysis)
    return {
        "total": len(rows), "buy": buy, "sell": sell, "hold": hold,
        "kill_switches": ks_total, "avg_confidence": f"{avg_conf*100:.1f}%",
        "watchlists": watchlists_count, "top_buy": top_buy,
    }


def rows_to_js_array(rows: list) -> str:
    """Serialise signal rows as JS object array embedded in HTML."""
    return json.dumps(rows, ensure_ascii=False)


def signal_badge(signal: str) -> str:
    c = SIGNAL_COLORS.get(signal, SIGNAL_COLORS["HOLD"])
    icon = {"BUY": "▲", "SELL": "▼", "HOLD": "●"}.get(signal, "●")
    return (f'<span class="sig-badge sig-{signal.lower()}">'
            f'{icon} {signal}</span>')


def tier_badge(tier: str) -> str:
    c = TIER_COLORS.get(tier, TIER_COLORS["Speculative"])
    short = {"Macro Vanguard": "MACRO", "Primary Conviction": "PRIMARY",
             "Speculative": "SPEC", "Waiting List": "WAIT"}.get(tier, tier[:5].upper())
    return f'<span class="tier-badge tier-{short.lower()}">{short}</span>'


def ks_badges(ks: str) -> str:
    if not ks:
        return '<span class="ks-none">—</span>'
    out = ""
    for k in str(ks).split(","):
        k = k.strip()
        if k:
            color = KS_COLORS.get(k, "#6b7280")
            out += f'<span class="ks-badge" style="background:{color}22;color:{color};border-color:{color}">{k}</span>'
    return out


def conf_bar(conf: float) -> str:
    pct = min(100, max(0, int(conf * 100)))
    color = "#16a34a" if conf >= 0.7 else "#d97706" if conf >= 0.5 else "#dc2626"
    return (f'<div class="conf-bar-wrap">'
            f'<div class="conf-bar" style="width:{pct}%;background:{color}"></div>'
            f'<span class="conf-label">{pct}%</span></div>')


def generate_html(rows: list, stats: dict, analysis: dict) -> str:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Chart data
    wl_names = list({r["watchlist_short"] for r in rows})
    wl_buy   = [sum(1 for r in rows if r["watchlist_short"] == w and r["signal"] == "BUY") for w in wl_names]
    wl_sell  = [sum(1 for r in rows if r["watchlist_short"] == w and r["signal"] == "SELL") for w in wl_names]
    wl_hold  = [sum(1 for r in rows if r["watchlist_short"] == w and r["signal"] == "HOLD") for w in wl_names]

    top10 = [r for r in rows if r["signal"] == "BUY"][:10]
    top10_tickers = [r["ticker"] for r in top10]
    top10_conf    = [int(r["confidence"] * 100) for r in top10]

    signal_dist = [stats["buy"], stats["hold"], stats["sell"]]

    rows_js = rows_to_js_array(rows)

    # Unique filters
    all_watchlists = sorted({r["watchlist_short"] for r in rows})
    all_tiers = ["Macro Vanguard", "Primary Conviction", "Speculative", "Waiting List"]

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>VIF Master Dashboard | {ts[:10]}</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
:root {{
  --bg:      #0d1117;
  --bg2:     #161b22;
  --bg3:     #21262d;
  --border:  #30363d;
  --text:    #e6edf3;
  --muted:   #8b949e;
  --blue:    #58a6ff;
  --green:   #3fb950;
  --red:     #f85149;
  --yellow:  #d29922;
  --purple:  #bc8cff;
  --orange:  #f0883e;
}}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family:'Segoe UI',system-ui,sans-serif; background:var(--bg); color:var(--text); font-size:14px; }}
a {{ color:var(--blue); text-decoration:none; }}

/* ── Layout ─────────────────────────────────────────────── */
.header {{
  background:linear-gradient(135deg,#0d1117 0%,#161b22 100%);
  border-bottom:2px solid var(--blue);
  padding:28px 32px 20px;
  position:sticky; top:0; z-index:100;
  box-shadow:0 4px 24px rgba(0,0,0,0.6);
}}
.header-row {{ display:flex; align-items:center; gap:20px; flex-wrap:wrap; }}
.header h1 {{ font-size:1.7em; color:var(--blue); font-weight:700; }}
.meta-chips {{ display:flex; gap:10px; flex-wrap:wrap; margin-top:8px; }}
.chip {{ background:var(--bg3); border:1px solid var(--border); border-radius:20px;
         padding:4px 14px; font-size:0.82em; color:var(--muted); }}
.chip span {{ color:var(--text); font-weight:600; }}

.main {{ max-width:1700px; margin:0 auto; padding:24px 20px; }}

/* ── Summary Cards ──────────────────────────────────────── */
.cards {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:14px; margin-bottom:28px; }}
.card {{
  background:var(--bg2); border:1px solid var(--border); border-radius:10px;
  padding:18px 20px; text-align:center;
  transition:border-color .2s, transform .15s;
}}
.card:hover {{ border-color:var(--blue); transform:translateY(-2px); }}
.card-val {{ font-size:2.2em; font-weight:700; margin-bottom:4px; }}
.card-lbl {{ font-size:0.78em; color:var(--muted); text-transform:uppercase; letter-spacing:.6px; }}
.card.buy   .card-val {{ color:var(--green); }}
.card.sell  .card-val {{ color:var(--red); }}
.card.hold  .card-val {{ color:var(--yellow); }}
.card.total .card-val {{ color:var(--blue); }}
.card.ks    .card-val {{ color:var(--orange); }}
.card.conf  .card-val {{ color:var(--purple); }}

/* ── Charts ─────────────────────────────────────────────── */
.charts-grid {{ display:grid; grid-template-columns:340px 1fr 1fr; gap:18px; margin-bottom:28px; }}
.chart-box {{
  background:var(--bg2); border:1px solid var(--border); border-radius:10px;
  padding:20px; position:relative;
}}
.chart-box h3 {{ font-size:0.9em; color:var(--muted); text-transform:uppercase;
                 letter-spacing:.6px; margin-bottom:16px; }}
.chart-box canvas {{ max-height:240px; }}

/* ── Filter bar ─────────────────────────────────────────── */
.toolbar {{
  background:var(--bg2); border:1px solid var(--border); border-radius:10px;
  padding:16px 20px; margin-bottom:18px;
  display:flex; flex-wrap:wrap; gap:12px; align-items:center;
}}
.toolbar label {{ font-size:0.82em; color:var(--muted); text-transform:uppercase; letter-spacing:.5px; }}
.filter-group {{ display:flex; align-items:center; gap:8px; }}
.btn-filter {{
  background:var(--bg3); border:1px solid var(--border); color:var(--muted);
  border-radius:6px; padding:6px 14px; cursor:pointer; font-size:0.84em;
  transition:all .2s;
}}
.btn-filter:hover {{ border-color:var(--blue); color:var(--text); }}
.btn-filter.active {{ background:var(--blue); border-color:var(--blue); color:#fff; font-weight:600; }}
.btn-filter.buy-btn.active  {{ background:var(--green); border-color:var(--green); }}
.btn-filter.sell-btn.active {{ background:var(--red); border-color:var(--red); }}
.btn-filter.hold-btn.active {{ background:var(--yellow); border-color:var(--yellow); color:#000; }}
select.f-select {{
  background:var(--bg3); border:1px solid var(--border); color:var(--text);
  border-radius:6px; padding:6px 12px; font-size:0.84em; cursor:pointer;
}}
input.f-search {{
  background:var(--bg3); border:1px solid var(--border); color:var(--text);
  border-radius:6px; padding:6px 14px; font-size:0.84em; width:200px;
  outline:none;
}}
input.f-search:focus {{ border-color:var(--blue); }}
.result-count {{ color:var(--muted); font-size:0.82em; margin-left:auto; }}

/* ── Table ──────────────────────────────────────────────── */
.table-wrap {{ overflow-x:auto; border-radius:10px; border:1px solid var(--border); }}
table {{
  width:100%; border-collapse:collapse; background:var(--bg2);
  font-size:0.88em;
}}
thead th {{
  background:var(--bg3); color:var(--muted); text-transform:uppercase;
  font-size:0.78em; letter-spacing:.5px; padding:12px 16px;
  border-bottom:2px solid var(--border); cursor:pointer;
  user-select:none; white-space:nowrap;
}}
thead th:hover {{ color:var(--blue); }}
thead th .sort-arrow {{ opacity:.4; margin-left:4px; }}
thead th.sort-asc .sort-arrow::after  {{ content:"▲"; }}
thead th.sort-desc .sort-arrow::after {{ content:"▼"; }}
thead th:not(.sort-asc):not(.sort-desc) .sort-arrow::after {{ content:"⇅"; }}
tbody tr {{ border-bottom:1px solid var(--border); transition:background .12s; }}
tbody tr:hover {{ background:var(--bg3); }}
tbody td {{ padding:11px 16px; vertical-align:middle; }}
tbody tr.hidden {{ display:none; }}

/* ── Badges ─────────────────────────────────────────────── */
.sig-badge {{
  display:inline-block; padding:4px 12px; border-radius:20px;
  font-weight:700; font-size:0.82em; letter-spacing:.3px; white-space:nowrap;
}}
.sig-buy  {{ background:#166534; color:#bbf7d0; }}
.sig-sell {{ background:#7f1d1d; color:#fecaca; }}
.sig-hold {{ background:#78350f; color:#fef3c7; }}

.tier-badge {{
  display:inline-block; padding:3px 9px; border-radius:4px;
  font-size:0.75em; font-weight:700; letter-spacing:.4px;
}}
.tier-macro   {{ background:#1e3a5f; color:#60a5fa; }}
.tier-primary {{ background:#1a3d2b; color:#4ade80; }}
.tier-spec    {{ background:#3d2a1a; color:#fb923c; }}
.tier-wait    {{ background:#2d2d2d; color:#9ca3af; }}

.ks-badge {{
  display:inline-block; padding:2px 8px; border-radius:12px;
  font-size:0.75em; font-weight:700; border:1px solid; margin:1px;
}}
.ks-none {{ color:var(--border); }}

.multi-badge {{
  display:inline-block; background:#1e1b4b; color:#a78bfa;
  border:1px solid #4c1d95; border-radius:4px;
  font-size:0.72em; padding:2px 6px; margin-left:4px;
}}

/* ── Confidence bar ─────────────────────────────────────── */
.conf-bar-wrap {{
  display:flex; align-items:center; gap:8px; min-width:120px;
}}
.conf-bar {{
  height:8px; border-radius:4px; min-width:2px; max-width:80px; flex-shrink:0;
  transition:width .3s;
}}
.conf-label {{ font-size:0.82em; color:var(--muted); white-space:nowrap; }}

/* ── Kill Switch Alert Panel ────────────────────────────── */
.ks-panel {{
  background:var(--bg2); border:1px solid #7f1d1d; border-radius:10px;
  padding:18px 22px; margin-bottom:24px;
}}
.ks-panel h3 {{
  color:var(--red); font-size:0.9em; text-transform:uppercase;
  letter-spacing:.6px; margin-bottom:12px;
}}
.ks-list {{ display:flex; flex-wrap:wrap; gap:8px; }}
.ks-item {{
  background:#7f1d1d22; border:1px solid #7f1d1d55; border-radius:8px;
  padding:6px 14px; font-size:0.85em;
}}
.ks-item strong {{ color:var(--red); }}

/* ── Top Buys Panel ─────────────────────────────────────── */
.top-buys-grid {{
  display:grid; grid-template-columns:repeat(auto-fill,minmax(200px,1fr));
  gap:12px; margin-bottom:28px;
}}
.buy-card {{
  background:var(--bg2); border:1px solid #166534; border-radius:10px;
  padding:14px 16px; transition:transform .15s, border-color .2s;
}}
.buy-card:hover {{ transform:translateY(-2px); border-color:#16a34a; }}
.buy-card .ticker {{ font-size:1.3em; font-weight:700; color:var(--green); }}
.buy-card .wl-label {{ font-size:0.75em; color:var(--muted); margin:2px 0 6px; }}
.buy-card .details {{ font-size:0.8em; color:var(--muted); margin-top:8px; line-height:1.5; }}

/* ── Watchlist tabs ─────────────────────────────────────── */
.wl-tabs {{ display:flex; gap:4px; margin-bottom:0; flex-wrap:wrap; }}
.wl-tab {{
  padding:8px 16px; cursor:pointer; border-radius:8px 8px 0 0;
  background:var(--bg3); border:1px solid var(--border); border-bottom:none;
  font-size:0.84em; color:var(--muted); transition:all .2s;
}}
.wl-tab:hover {{ color:var(--text); }}
.wl-tab.active {{ background:var(--bg2); color:var(--blue); border-bottom-color:var(--bg2); }}
.wl-section {{
  background:var(--bg2); border:1px solid var(--border);
  border-radius:0 10px 10px 10px; padding:20px; margin-bottom:28px;
  display:none;
}}
.wl-section.active {{ display:block; }}

/* ── Export ─────────────────────────────────────────────── */
.export-btn {{
  background:var(--bg3); border:1px solid var(--border); color:var(--muted);
  border-radius:6px; padding:7px 16px; cursor:pointer; font-size:0.84em;
  transition:all .2s;
}}
.export-btn:hover {{ border-color:var(--green); color:var(--green); }}

/* ── Section labels ─────────────────────────────────────── */
.section-hdr {{
  font-size:0.78em; text-transform:uppercase; letter-spacing:.7px;
  color:var(--muted); border-bottom:1px solid var(--border);
  padding-bottom:8px; margin-bottom:16px;
}}

/* ── Tooltip ─────────────────────────────────────────────── */
.reasoning-cell {{ max-width:340px; }}
.reasoning-text {{
  white-space:nowrap; overflow:hidden; text-overflow:ellipsis;
  max-width:320px; color:var(--muted); font-size:0.82em; cursor:help;
}}

@media(max-width:900px) {{
  .charts-grid {{ grid-template-columns:1fr; }}
  .header h1 {{ font-size:1.3em; }}
  input.f-search {{ width:140px; }}
}}
</style>
</head>
<body>

<!-- ── HEADER ────────────────────────────────────────────────────────────── -->
<div class="header">
  <div class="header-row">
    <div>
      <h1>VIF Master Dashboard</h1>
      <div class="meta-chips">
        <div class="chip">Date <span>{ts[:10]}</span></div>
        <div class="chip">Watchlists <span>{stats['watchlists']}</span></div>
        <div class="chip">Tickers <span>{stats['total']}</span></div>
        <div class="chip">Avg Confidence <span>{stats['avg_confidence']}</span></div>
        <div class="chip">Generated <span>{ts}</span></div>
      </div>
    </div>
    <button class="export-btn" onclick="exportCSV()" style="margin-left:auto">⬇ Export CSV</button>
  </div>
</div>

<div class="main">

<!-- ── SUMMARY CARDS ─────────────────────────────────────────────────────── -->
<div class="cards">
  <div class="card total"><div class="card-val">{stats['total']}</div><div class="card-lbl">Total Analyzed</div></div>
  <div class="card buy"><div class="card-val">{stats['buy']}</div><div class="card-lbl">BUY Signals</div></div>
  <div class="card sell"><div class="card-val">{stats['sell']}</div><div class="card-lbl">SELL Signals</div></div>
  <div class="card hold"><div class="card-val">{stats['hold']}</div><div class="card-lbl">HOLD Signals</div></div>
  <div class="card ks"><div class="card-val">{stats['kill_switches']}</div><div class="card-lbl">Kill Switch Alerts</div></div>
  <div class="card conf"><div class="card-val">{stats['avg_confidence']}</div><div class="card-lbl">Avg Confidence</div></div>
</div>

<!-- ── CHARTS ────────────────────────────────────────────────────────────── -->
<div class="charts-grid">
  <div class="chart-box">
    <h3>Signal Distribution</h3>
    <canvas id="chartPie"></canvas>
  </div>
  <div class="chart-box">
    <h3>BUY/SELL/HOLD by Watchlist</h3>
    <canvas id="chartBar"></canvas>
  </div>
  <div class="chart-box">
    <h3>Top 10 BUY Confidence</h3>
    <canvas id="chartConf"></canvas>
  </div>
</div>

<!-- ── KILL SWITCH ALERTS ─────────────────────────────────────────────────── -->
{_build_ks_panel(rows)}

<!-- ── TOP BUY SETUPS ─────────────────────────────────────────────────────── -->
<div class="section-hdr">Top BUY Setups (Highest Conviction)</div>
<div class="top-buys-grid">
{_build_top_buy_cards(stats['top_buy'])}
</div>

<!-- ── WATCHLIST BREAKDOWN ───────────────────────────────────────────────── -->
<div class="section-hdr">Per-Watchlist Breakdown</div>
{_build_wl_tabs(rows, all_watchlists)}

<!-- ── MASTER SIGNAL TABLE ───────────────────────────────────────────────── -->
<div class="section-hdr">All Signals — Filter, Sort & Search</div>
<div class="toolbar">
  <div class="filter-group">
    <label>Signal</label>
    <button class="btn-filter active" onclick="filterSignal('ALL',this)">ALL</button>
    <button class="btn-filter buy-btn" onclick="filterSignal('BUY',this)">▲ BUY</button>
    <button class="btn-filter sell-btn" onclick="filterSignal('SELL',this)">▼ SELL</button>
    <button class="btn-filter hold-btn" onclick="filterSignal('HOLD',this)">● HOLD</button>
  </div>
  <div class="filter-group">
    <label>Watchlist</label>
    <select class="f-select" onchange="filterWatchlist(this.value)">
      <option value="ALL">All Watchlists</option>
      {"".join(f'<option value="{w}">{w}</option>' for w in all_watchlists)}
    </select>
  </div>
  <div class="filter-group">
    <label>Tier</label>
    <select class="f-select" onchange="filterTier(this.value)">
      <option value="ALL">All Tiers</option>
      {"".join(f'<option value="{t}">{t}</option>' for t in all_tiers)}
    </select>
  </div>
  <div class="filter-group">
    <label>Kill Switch</label>
    <select class="f-select" onchange="filterKS(this.value)">
      <option value="ALL">Any</option>
      <option value="HAS_KS">Has Alert</option>
      <option value="CLEAN">No Alerts</option>
    </select>
  </div>
  <input class="f-search" type="text" placeholder="Search ticker…" oninput="filterSearch(this.value)">
  <span class="result-count" id="rowCount"></span>
</div>

<div class="table-wrap">
<table id="sigTable">
  <thead>
    <tr>
      <th onclick="sortTable(0)" data-col="0">Ticker <span class="sort-arrow"></span></th>
      <th onclick="sortTable(1)" data-col="1">Signal <span class="sort-arrow"></span></th>
      <th onclick="sortTable(2)" data-col="2">Confidence <span class="sort-arrow"></span></th>
      <th onclick="sortTable(7)" data-col="7">Price <span class="sort-arrow"></span></th>
      <th onclick="sortTable(8)" data-col="8">RSI <span class="sort-arrow"></span></th>
      <th onclick="sortTable(3)" data-col="3">Tier <span class="sort-arrow"></span></th>
      <th onclick="sortTable(4)" data-col="4">Watchlist <span class="sort-arrow"></span></th>
      <th onclick="sortTable(5)" data-col="5">Gamma <span class="sort-arrow"></span></th>
      <th onclick="sortTable(6)" data-col="6">Kill Switches <span class="sort-arrow"></span></th>
      <th>Notes</th>
    </tr>
  </thead>
  <tbody id="sigBody">
  </tbody>
</table>
</div>

</div><!-- /main -->

<!-- ── DATA + SCRIPTS ────────────────────────────────────────────────────── -->
<script>
const RAW_ROWS = {rows_js};

const WL_NAMES  = {json.dumps(list(WATCHLIST_DISPLAY.keys()))};
const WL_NAMES_SHORT = {json.dumps(list(WATCHLIST_DISPLAY.values()))};
const WL_BUY  = {json.dumps(wl_buy)};
const WL_SELL = {json.dumps(wl_sell)};
const WL_HOLD = {json.dumps(wl_hold)};
const TOP10_TICKERS = {json.dumps(top10_tickers)};
const TOP10_CONF    = {json.dumps(top10_conf)};
const SIGNAL_DIST   = {json.dumps(signal_dist)};

// ── State ──
let activeSignal = 'ALL', activeWL = 'ALL', activeTier = 'ALL';
let activeKS = 'ALL', searchTerm = '';
let sortCol = 2, sortDir = -1;  // default: confidence desc

// ── Charts ────────────────────────────────────────────────────────────────
const pieCtx = document.getElementById('chartPie').getContext('2d');
new Chart(pieCtx, {{
  type: 'doughnut',
  data: {{
    labels: ['BUY', 'HOLD', 'SELL'],
    datasets: [{{ data: SIGNAL_DIST, backgroundColor: ['#3fb950','#d29922','#f85149'],
                 borderColor:'#161b22', borderWidth:3 }}]
  }},
  options: {{
    plugins: {{
      legend: {{ labels: {{ color:'#e6edf3', font:{{size:13}} }} }},
      tooltip: {{ bodyColor:'#e6edf3', titleColor:'#58a6ff' }}
    }},
    cutout: '62%'
  }}
}});

const barCtx = document.getElementById('chartBar').getContext('2d');
new Chart(barCtx, {{
  type: 'bar',
  data: {{
    labels: WL_NAMES_SHORT,
    datasets: [
      {{ label:'BUY',  data:WL_BUY,  backgroundColor:'#3fb950' }},
      {{ label:'SELL', data:WL_SELL, backgroundColor:'#f85149' }},
      {{ label:'HOLD', data:WL_HOLD, backgroundColor:'#d29922' }},
    ]
  }},
  options: {{
    responsive:true,
    plugins: {{
      legend: {{ labels:{{ color:'#e6edf3' }} }},
      tooltip:{{ bodyColor:'#e6edf3', titleColor:'#58a6ff' }}
    }},
    scales: {{
      x:{{ stacked:true, ticks:{{ color:'#8b949e', maxRotation:35 }}, grid:{{ color:'#21262d' }} }},
      y:{{ stacked:true, ticks:{{ color:'#8b949e' }}, grid:{{ color:'#21262d' }} }},
    }}
  }}
}});

const confCtx = document.getElementById('chartConf').getContext('2d');
new Chart(confCtx, {{
  type: 'bar',
  data: {{
    labels: TOP10_TICKERS,
    datasets:[{{ label:'Confidence %', data:TOP10_CONF,
      backgroundColor: TOP10_CONF.map(v => v>=70?'#3fb950':v>=50?'#d29922':'#f85149'),
      borderRadius:4 }}]
  }},
  options: {{
    indexAxis:'y',
    plugins:{{ legend:{{display:false}}, tooltip:{{bodyColor:'#e6edf3', titleColor:'#58a6ff'}} }},
    scales:{{
      x:{{ min:0, max:100, ticks:{{color:'#8b949e',callback:v=>v+'%'}}, grid:{{color:'#21262d'}} }},
      y:{{ ticks:{{color:'#e6edf3'}} }}
    }}
  }}
}});

// ── Table rendering ───────────────────────────────────────────────────────
function sigBadge(sig) {{
  const icon = {{BUY:'▲',SELL:'▼',HOLD:'●'}}[sig]||'●';
  return `<span class="sig-badge sig-${{sig.toLowerCase()}}">${{icon}} ${{sig}}</span>`;
}}
function tierBadge(tier) {{
  const m={{'Macro Vanguard':'macro','Primary Conviction':'primary',
            'Speculative':'spec','Waiting List':'wait'}};
  const short={{'Macro Vanguard':'MACRO','Primary Conviction':'PRIMARY',
                'Speculative':'SPEC','Waiting List':'WAIT'}};
  return `<span class="tier-badge tier-${{m[tier]||'spec'}}">${{short[tier]||tier}}</span>`;
}}
function ksBadges(ks) {{
  if(!ks) return '<span class="ks-none">—</span>';
  const colors={{'K1':'#f97316','K2':'#ef4444','K3':'#f97316',
                 'K4':'#ec4899','K5':'#a855f7','K6':'#ec4899'}};
  return ks.split(',').map(k=>{{
    k=k.trim(); const c=colors[k]||'#6b7280';
    return `<span class="ks-badge" style="background:${{c}}22;color:${{c}};border-color:${{c}}">${{k}}</span>`;
  }}).join('');
}}
function confBar(v) {{
  const pct=Math.min(100,Math.max(0,Math.round(v*100)));
  const c=pct>=70?'#3fb950':pct>=50?'#d29922':'#f85149';
  return `<div class="conf-bar-wrap"><div class="conf-bar" style="width:${{pct}}%;background:${{c}}"></div>
          <span class="conf-label">${{pct}}%</span></div>`;
}}
function gammaBadge(g) {{
  const m={{'positive':'#3fb950','negative':'#f85149','neutral':'#d29922',
            'transition':'#a78bfa'}};
  const c=m[(g||'').toLowerCase()]||'#8b949e';
  return `<span style="color:${{c}};font-size:.82em;font-weight:600;">${{g||'—'}}</span>`;
}}

function renderTable() {{
  const tbody = document.getElementById('sigBody');
  let rows = [...RAW_ROWS];

  // filters
  if(activeSignal!='ALL') rows=rows.filter(r=>r.signal==activeSignal);
  if(activeWL!='ALL')     rows=rows.filter(r=>r.watchlist_short==activeWL);
  if(activeTier!='ALL')   rows=rows.filter(r=>r.tier==activeTier);
  if(activeKS=='HAS_KS')  rows=rows.filter(r=>r.kill_switches);
  if(activeKS=='CLEAN')   rows=rows.filter(r=>!r.kill_switches);
  if(searchTerm)          rows=rows.filter(r=>r.ticker.toUpperCase().includes(searchTerm.toUpperCase()));

  // sort
  rows.sort((a,b)=>{{
    let av,bv;
    switch(sortCol){{
      case 0: av=a.ticker; bv=b.ticker; break;
      case 1: av=a.signal; bv=b.signal; break;
      case 2: av=a.confidence; bv=b.confidence; break;
      case 3: av=a.tier; bv=b.tier; break;
      case 4: av=a.watchlist_short; bv=b.watchlist_short; break;
      case 5: av=a.gamma; bv=b.gamma; break;
      case 6: av=a.kill_switches||''; bv=b.kill_switches||''; break;
      case 7: av=a.price||0; bv=b.price||0; break;
      case 8: av=a.rsi||0; bv=b.rsi||0; break;
      default: av=a.confidence; bv=b.confidence;
    }}
    if(av<bv) return sortDir;
    if(av>bv) return -sortDir;
    return 0;
  }});

  document.getElementById('rowCount').textContent = rows.length + ' result' + (rows.length!=1?'s':'');

  tbody.innerHTML = rows.map(r=>{{
    const multi = r.in_multiple ? '<span class="multi-badge">×WL</span>' : '';
    const rsiColor = r.rsi>75?'#f85149':r.rsi<30?'#3fb950':'#8b949e';
    return `<tr>
      <td><strong>${{r.ticker_plain||r.ticker}}</strong>${{multi}}</td>
      <td>${{sigBadge(r.signal)}}</td>
      <td>${{confBar(r.confidence)}}</td>
      <td style="font-size:.82em;color:var(--muted);white-space:nowrap">${{r.price?'$'+Number(r.price).toFixed(2):'—'}}</td>
      <td style="font-size:.82em;color:${{rsiColor}};font-weight:600">${{r.rsi?Number(r.rsi).toFixed(1):'—'}}</td>
      <td>${{tierBadge(r.tier)}}</td>
      <td style="font-size:.82em;color:var(--muted)">${{r.watchlist_short}}</td>
      <td>${{gammaBadge(r.gamma)}}</td>
      <td>${{ksBadges(r.kill_switches)}}</td>
      <td class="reasoning-cell"><div class="reasoning-text" title="${{r.reasoning}}">${{r.reasoning||'—'}}</div></td>
    </tr>`;
  }}).join('');

  // sort arrows
  document.querySelectorAll('thead th').forEach((th,i)=>{{
    th.classList.remove('sort-asc','sort-desc');
    if(i==sortCol) th.classList.add(sortDir==1?'sort-asc':'sort-desc');
  }});
}}

// ── Filter / sort handlers ─────────────────────────────────────────────────
function filterSignal(sig, btn) {{
  activeSignal = sig;
  document.querySelectorAll('.btn-filter').forEach(b=>b.classList.remove('active'));
  btn.classList.add('active');
  renderTable();
}}
function filterWatchlist(v) {{ activeWL = v; renderTable(); }}
function filterTier(v)      {{ activeTier = v; renderTable(); }}
function filterKS(v)        {{ activeKS = v; renderTable(); }}
function filterSearch(v)    {{ searchTerm = v; renderTable(); }}
function sortTable(col) {{
  if(sortCol==col) sortDir*=-1; else {{ sortCol=col; sortDir=-1; }}
  renderTable();
}}

// ── Watchlist tabs ─────────────────────────────────────────────────────────
function switchWLTab(name, btn) {{
  document.querySelectorAll('.wl-tab').forEach(t=>t.classList.remove('active'));
  document.querySelectorAll('.wl-section').forEach(s=>s.classList.remove('active'));
  btn.classList.add('active');
  document.getElementById('wl-'+name).classList.add('active');
}}

// ── CSV export ─────────────────────────────────────────────────────────────
function exportCSV() {{
  const headers = ['Ticker','Signal','Confidence','Tier','Watchlist','Gamma','KillSwitches','Reasoning'];
  const rows = RAW_ROWS.map(r=>[
    r.ticker, r.signal, r.confidence_pct, r.tier, r.watchlist,
    r.gamma, r.kill_switches||'', '"'+r.reasoning.replace(/"/g,"'")+'"'
  ].join(','));
  const csv = [headers.join(','), ...rows].join('\\n');
  const blob = new Blob([csv], {{type:'text/csv'}});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href=url; a.download='vif_signals_{ts[:10].replace('-','')}.csv'; a.click();
}}

// ── Init ───────────────────────────────────────────────────────────────────
renderTable();
</script>
</body>
</html>
"""
    return html


def _build_ks_panel(rows: list) -> str:
    ks_rows = [r for r in rows if r["kill_switches"]]
    if not ks_rows:
        return ""
    items = "".join(
        f'<div class="ks-item"><strong>{r["ticker"]}</strong> '
        f'({r["watchlist_short"]}) — {r["kill_switches"]}</div>'
        for r in ks_rows[:24]
    )
    return f'''<div class="ks-panel">
  <h3>⚠️ Kill Switch Alerts ({len(ks_rows)} tickers flagged)</h3>
  <div class="ks-list">{items}</div>
</div>'''


def _build_top_buy_cards(top_buy: list) -> str:
    if not top_buy:
        return '<p style="color:var(--muted)">No BUY signals found.</p>'
    cards = ""
    for r in top_buy:
        gamma_color = {"positive": "#3fb950", "negative": "#f85149",
                       "neutral": "#d29922"}.get(r.get("gamma", "").lower(), "#8b949e")
        ks = f'<br>⚠️ {r["kill_switches"]}' if r["kill_switches"] else ""
        multi = '<br>🔁 Multi-watchlist' if r["in_multiple"] else ""
        price_txt = f'${r["price"]:.2f}' if r.get("price") else "—"
        rsi_val = r.get("rsi", 0)
        rsi_color = "#f85149" if rsi_val > 75 else "#3fb950" if rsi_val < 30 else "#8b949e"
        rsi_txt = f'RSI: <span style="color:{rsi_color};font-weight:700">{rsi_val:.1f}</span>' if rsi_val else ""
        cards += f'''<div class="buy-card">
  <div class="ticker">{r["ticker_plain"]}</div>
  <div class="wl-label">{r["watchlist_short"]}</div>
  <div style="display:flex;align-items:baseline;gap:10px;margin:4px 0">
    <span style="font-size:1.3em;font-weight:700;color:#3fb950">{int(r["confidence"]*100)}%</span>
    <span style="font-size:.85em;color:var(--muted)">{price_txt}</span>
  </div>
  <div class="details">
    {rsi_txt}<br>
    Tier: {r["tier"]}<br>
    Gamma: <span style="color:{gamma_color}">{r.get("gamma","—")}</span>{ks}{multi}
  </div>
</div>'''
    return cards


def _build_wl_tabs(rows: list, all_watchlists: list) -> str:
    if not all_watchlists:
        return ""
    tabs = ""
    for i, wl in enumerate(all_watchlists):
        active = "active" if i == 0 else ""
        tabs += f'<button class="wl-tab {active}" onclick="switchWLTab(\'{i}\',this)">{wl}</button>'

    sections = ""
    for i, wl in enumerate(all_watchlists):
        active = "active" if i == 0 else ""
        wl_rows = [r for r in rows if r["watchlist_short"] == wl]
        buy  = sum(1 for r in wl_rows if r["signal"] == "BUY")
        sell = sum(1 for r in wl_rows if r["signal"] == "SELL")
        hold = sum(1 for r in wl_rows if r["signal"] == "HOLD")
        ks   = sum(1 for r in wl_rows if r["kill_switches"])

        table_rows = ""
        for r in sorted(wl_rows, key=lambda x: -x["confidence"]):
            icon = {"BUY": "▲", "SELL": "▼", "HOLD": "●"}.get(r["signal"], "●")
            sig_class = f'sig-{r["signal"].lower()}'
            conf_pct = int(r["confidence"] * 100)
            ks_txt = r["kill_switches"] or "—"
            table_rows += f'''<tr>
  <td><strong>{r["ticker"]}</strong></td>
  <td><span class="sig-badge {sig_class}">{icon} {r["signal"]}</span></td>
  <td>{conf_pct}%</td>
  <td>{r["tier"]}</td>
  <td style="color:var(--muted);font-size:.82em">{r.get("gamma","—")}</td>
  <td style="font-size:.8em;color:#f97316">{ks_txt}</td>
</tr>'''

        sections += f'''<div id="wl-{i}" class="wl-section {active}">
  <div style="display:flex;gap:20px;margin-bottom:16px;flex-wrap:wrap">
    <div class="card buy"  style="padding:10px 18px;min-width:100px"><div class="card-val">{buy}</div><div class="card-lbl">BUY</div></div>
    <div class="card sell" style="padding:10px 18px;min-width:100px"><div class="card-val">{sell}</div><div class="card-lbl">SELL</div></div>
    <div class="card hold" style="padding:10px 18px;min-width:100px"><div class="card-val">{hold}</div><div class="card-lbl">HOLD</div></div>
    <div class="card ks"   style="padding:10px 18px;min-width:100px"><div class="card-val">{ks}</div><div class="card-lbl">Kill Switch</div></div>
  </div>
  <div class="table-wrap">
  <table>
    <thead><tr><th>Ticker</th><th>Signal</th><th>Confidence</th><th>Tier</th><th>Gamma</th><th>Kill Switches</th></tr></thead>
    <tbody>{table_rows if table_rows else '<tr><td colspan="6" style="color:var(--muted);text-align:center">No data yet — analysis pending</td></tr>'}</tbody>
  </table>
  </div>
</div>'''

    return f'<div class="wl-tabs">{tabs}</div>\n{sections}'


def main():
    parser = argparse.ArgumentParser(description="Generate VIF Master Interactive Report")
    parser.add_argument("--json", help="Path to specific analysis JSON file")
    parser.add_argument("--output", default="VIF_MASTER_DASHBOARD", help="Output filename (no extension)")
    args = parser.parse_args()

    print("VIF Master Report Generator")
    print("=" * 50)

    print("Loading watchlist tiers...")
    tier_data = load_watchlist_tiers()
    print(f"  Loaded tier data for {len(tier_data)} tickers")

    print("Loading analysis data...")
    analysis = load_latest_analysis(args.json)

    if not analysis:
        print("  WARNING: No analysis JSON found. Generating empty dashboard.")
        print("  Run: python agents/watchlist_watcher.py --all --period 1mo")
        analysis = {}

    print(f"  Loaded {len(analysis)} watchlist results")

    print("Building signal rows...")
    rows = flatten_signals(analysis, tier_data)
    print(f"  {len(rows)} signal rows")

    stats = build_stats(rows, analysis)
    print(f"  BUY:{stats['buy']} SELL:{stats['sell']} HOLD:{stats['hold']} KS:{stats['kill_switches']}")

    print("Generating HTML...")
    html = generate_html(rows, stats, analysis)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_name = f"{args.output}_{ts}"
    out_path = Path("reports") / f"{out_name}.html"
    out_path.parent.mkdir(exist_ok=True)
    out_path.write_text(html, encoding="utf-8")

    print(f"\n✅ Report saved: {out_path}")
    print(f"   Open in browser: file:///{out_path.resolve()}")
    return str(out_path)


if __name__ == "__main__":
    main()
