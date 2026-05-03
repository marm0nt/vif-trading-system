#!/usr/bin/env python3
"""
VIF Orchestrator - Master Delegation Agent
==========================================
Master pipeline controller. Sequences sub-agents by mode:
  premarket  -> Catalyst Scan, VIF Watchlist (1mo), Swing Screener
  afterhours -> Daily Conviction, VIF Wrap (5d)
  weekend    -> Weekend Catalyst Brief
  full       -> All of the above

Usage:
  python agents/orchestrator.py --mode premarket
  python agents/orchestrator.py --mode afterhours
  python agents/orchestrator.py --ticker NVDA
"""
import sys, os, json, logging, argparse, subprocess
from datetime import datetime
from pathlib import Path

# Fix Windows console encoding so Unicode in log messages doesn't crash
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = lambda *a, **kw: None

load_dotenv(override=True)  # .env wins over any stale system env var
Path("logs").mkdir(exist_ok=True)
Path("reports").mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [ORCHESTRATOR] %(message)s",
    handlers=[
        logging.FileHandler("logs/orchestrator.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# ── Python interpreter (use venv if available) ────────────────────────────────
VENV_PY = str(Path("venv/Scripts/python.exe"))
PYTHON   = VENV_PY if Path(VENV_PY).exists() else sys.executable

# ── Mode → agent pipeline map ─────────────────────────────────────────────────
PIPELINES = {
    "premarket": [
        # 07:00 – 09:30 CT
        # Goal: identify best setups BEFORE the open
        ("Catalyst Scan",         ["scripts/catalyst_analysis.py"]),
        ("VIF Watchlist (1mo)",   ["agents/watchlist_watcher.py", "--all", "--period", "1mo"]),
        ("Swing Screener",        ["scripts/swing_trade_screener_v2.py"]),
    ],
    "market_open": [
        # 09:35 CT – catch opening volume
        ("Opening Swing Screen",  ["scripts/swing_trade_screener_v2.py"]),
    ],
    "afterhours": [
        # 16:05 CT – review how the day closed
        ("Daily Conviction Model",["scripts/daily_watchlist_analysis.py"]),
        ("VIF Wrap (5d)",         ["agents/watchlist_watcher.py", "--all", "--period", "5d"]),
    ],
    "weekend": [
        # Saturday/Sunday – macro + earnings prep
        ("Weekend Catalyst Brief",["agents/weekend_catalyst_agent.py"]),
    ],
    "full": [
        # On-demand: complete end-to-end run
        ("Catalyst Scan",         ["scripts/catalyst_analysis.py"]),
        ("VIF Full Scan (1mo)",   ["agents/watchlist_watcher.py", "--all", "--period", "1mo"]),
        ("Swing Screener V2",     ["scripts/swing_trade_screener_v2.py"]),
        ("Daily Analysis",        ["scripts/daily_watchlist_analysis.py"]),
        ("Weekend Brief",         ["agents/weekend_catalyst_agent.py"]),
    ],
}


def run_agent(label: str, cmd_args: list[str], timeout: int = 600) -> dict:
    """
    Run a sub-agent script, capture output.
    Returns a result dict with success flag, key outputs.

    📚 LEARNING: This pattern is called "Orchestrator-Worker."
       The orchestrator delegates to workers (sub-agents) and collects
       their outputs to build a unified picture. Each worker only
       knows about its own job – the orchestrator synthesises them.
    """
    full_cmd = [PYTHON] + cmd_args
    logger.info(f"  → Delegating to [{label}]  cmd={' '.join(cmd_args)}")
    try:
        result = subprocess.run(
            full_cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(Path.cwd()),
        )
        ok = result.returncode == 0
        if ok:
            logger.info(f"    ✓ {label} completed")
        else:
            logger.error(f"    ✗ {label} FAILED (exit {result.returncode})")
            for line in result.stderr.splitlines()[-5:]:
                logger.error(f"      {line}")
        return {"label": label, "success": ok, "cmd": cmd_args, "stdout_tail": result.stdout[-500:]}
    except subprocess.TimeoutExpired:
        logger.error(f"    ✗ {label} TIMEOUT ({timeout}s)")
        return {"label": label, "success": False, "cmd": cmd_args, "stdout_tail": "TIMEOUT"}
    except Exception as e:
        logger.error(f"    ✗ {label} ERROR: {e}")
        return {"label": label, "success": False, "cmd": cmd_args, "stdout_tail": str(e)}


def run_pipeline(mode: str) -> list[dict]:
    """Execute a full named pipeline, return job results."""
    # Guard against concurrent pipeline execution for same mode
    lock_path = Path(".claude") / f"pipeline_{mode}.lock"
    if lock_path.exists():
        try:
            ts_lock = lock_path.read_text().strip()
            ts_start = datetime.fromisoformat(ts_lock)
            elapsed = (datetime.now() - ts_start).total_seconds()
            if elapsed < 600:  # 10 min timeout
                logger.warning(f"Pipeline [{mode.upper()}] already running (started {elapsed:.0f}s ago). Skipping.")
                return [{"label": f"Pipeline {mode}", "success": False, "cmd": [], "stdout_tail": "SKIPPED: already running"}]
        except:
            pass
        lock_path.unlink(missing_ok=True)

    try:
        # Write lock file
        lock_path.parent.mkdir(exist_ok=True)
        lock_path.write_text(datetime.now().isoformat())

        pipeline = PIPELINES.get(mode, PIPELINES["full"])
        logger.info(f"Pipeline: [{mode.upper()}] – {len(pipeline)} agents")
        results = []
        for label, cmd in pipeline:
            results.append(run_agent(label, cmd))
        return results
    finally:
        lock_path.unlink(missing_ok=True)


def run_single_ticker(ticker: str) -> dict:
    """
    Deep dive on a single ticker across all agents.

    📚 LEARNING: This is a "fan-out then fan-in" pattern.
       We send one ticker to multiple specialist agents in parallel,
       then collect their specialist outputs and merge them.
    """
    logger.info(f"Single-ticker deep dive: {ticker}")
    from agents.indicators import fetch_and_compute

    # Step 1: Technical Agent – compute all indicators locally
    logger.info("  [Technical Agent] Computing indicators...")
    ind = fetch_and_compute(ticker, period="6mo")
    if not ind:
        return {"error": f"No data for {ticker}"}

    # Step 2: VIF Analyst – Claude reads the indicators
    logger.info("  [VIF Analyst] Running Claude VIF analysis...")
    result = run_agent(
        f"VIF Analysis ({ticker})",
        ["agents/watchlist_watcher.py", "--watchlist", "energy_ai", "--period", "1mo"],
    )

    return {
        "ticker": ticker,
        "indicators": ind,
        "vif_agent_result": result,
        "timestamp": datetime.now().isoformat(),
    }


def save_run_log(results: list[dict], mode: str) -> Path:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = Path("reports") / f"orchestrator_{mode}_{ts}.json"
    out.write_text(json.dumps({
        "mode": mode,
        "started_at": datetime.now().isoformat(),
        "jobs": results,
        "summary": {
            "total": len(results),
            "passed": sum(1 for r in results if r.get("success")),
            "failed": sum(1 for r in results if not r.get("success")),
        }
    }, indent=2))
    logger.info(f"Run log saved -> {out}")
    return out


def _latest_json(prefix: str) -> dict | None:
    candidates = sorted(Path("reports").glob(f"{prefix}*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    for path in candidates:
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
    return None


# ── Signal color helpers ──────────────────────────────────────────────────────
_SIG_BG   = {"BUY": "#d4edda", "SELL": "#f8d7da", "HOLD": "#fff3cd"}
_SIG_FG   = {"BUY": "#155724", "SELL": "#721c24", "HOLD": "#856404"}
_SIG_ICON = {"BUY": "▲", "SELL": "▼", "HOLD": "●"}
_KS_BG    = {"K1": "#ffe0b2", "K2": "#ffcdd2", "K3": "#ffe0b2",
             "K4": "#f8bbd0", "K5": "#e1bee7", "K6": "#f8bbd0"}
_KS_FG    = {"K1": "#e65100", "K2": "#c62828", "K3": "#bf360c",
             "K4": "#ad1457", "K5": "#6a1b9a", "K6": "#ad1457"}

def _ks_badge(ks: str | None) -> str:
    if not ks:
        return '<span style="color:#aaa">—</span>'
    parts = str(ks).split(",")
    out = ""
    for k in parts:
        k = k.strip()
        bg = _KS_BG.get(k, "#eee")
        fg = _KS_FG.get(k, "#333")
        out += f'<span style="display:inline-block;padding:2px 8px;border-radius:12px;font-size:0.8em;font-weight:700;background:{bg};color:{fg};margin:1px">{k}</span>'
    return out

def _sig_badge(sig: str) -> str:
    s = str(sig).upper()
    bg = _SIG_BG.get(s, "#f8f9fa")
    fg = _SIG_FG.get(s, "#333")
    icon = _SIG_ICON.get(s, "●")
    return f'<span style="display:inline-block;padding:3px 12px;border-radius:14px;font-weight:700;font-size:0.9em;background:{bg};color:{fg}">{icon} {s}</span>'

def _conf_bar(conf) -> str:
    try:
        pct = int(conf)
    except (TypeError, ValueError):
        return str(conf)
    color = "#27ae60" if pct >= 65 else ("#f39c12" if pct >= 45 else "#e74c3c")
    return (
        f'<div style="display:flex;align-items:center;gap:8px">'
        f'<div style="width:80px;height:8px;background:#e0e0e0;border-radius:4px;overflow:hidden">'
        f'<div style="width:{min(pct,100)}%;height:100%;background:{color};border-radius:4px"></div></div>'
        f'<span style="font-size:0.85em;color:#555">{pct}%</span></div>'
    )

def _gamma_badge(regime: str) -> str:
    cfg = {
        "positive":   ("▲ Positive",   "#e8f5e9", "#2e7d32"),
        "negative":   ("▼ Negative",   "#ffebee", "#c62828"),
        "transition": ("↔ Transition", "#fff8e1", "#f57f17"),
    }
    label, bg, fg = cfg.get(str(regime).lower(), (regime, "#f5f5f5", "#555"))
    return f'<span style="padding:2px 10px;border-radius:10px;font-size:0.8em;font-weight:600;background:{bg};color:{fg}">{label}</span>'


# ── Section builders ──────────────────────────────────────────────────────────

def _build_summary_section(results: list[dict], ts_label: str,
                            wl_data: dict | None, swing_data: dict | None) -> str:
    passed = sum(1 for r in results if r.get("success"))
    total  = len(results)
    status_cls = "alert-success" if passed == total else "alert-warning"

    # aggregate signals across all watchlists
    all_sigs: dict[str, dict] = {}
    if wl_data:
        for wl_name, wl in wl_data.items():
            if isinstance(wl, dict) and "signals" in wl:
                for ticker, sig in wl["signals"].items():
                    clean = ticker.split(":")[-1]
                    all_sigs[clean] = sig

    buys  = [(t, s) for t, s in all_sigs.items() if s.get("signal","").upper() == "BUY"]
    sells = [(t, s) for t, s in all_sigs.items() if s.get("signal","").upper() == "SELL"]
    holds = [(t, s) for t, s in all_sigs.items() if s.get("signal","").upper() == "HOLD"]
    kills = [(t, s) for t, s in all_sigs.items() if s.get("kill_switch")]
    total_analyzed = sum(
        wl.get("tickers_analyzed", 0)
        for wl in (wl_data or {}).values()
        if isinstance(wl, dict)
    )
    swing_count = (swing_data or {}).get("total_confirmed", 0) if swing_data else 0

    # metric cards
    cards = [
        ("Tickers Analyzed", total_analyzed, "#667eea"),
        ("BUY Signals",      len(buys),      "#27ae60"),
        ("SELL Signals",     len(sells),     "#e74c3c"),
        ("Kill Switches",    len(kills),     "#f39c12"),
        ("Swing Setups",     swing_count,    "#764ba2"),
    ]
    card_html = '<div style="display:flex;flex-wrap:wrap;gap:16px;margin:24px 0">'
    for label, val, color in cards:
        card_html += (
            f'<div style="flex:1;min-width:140px;background:#fff;border:1px solid #e0e0e0;'
            f'border-top:4px solid {color};border-radius:8px;padding:16px 20px;'
            f'box-shadow:0 2px 6px rgba(0,0,0,0.06)">'
            f'<div style="font-size:0.78em;font-weight:700;color:{color};text-transform:uppercase;letter-spacing:0.5px">{label}</div>'
            f'<div style="font-size:2em;font-weight:800;color:#222;margin-top:4px">{val}</div>'
            f'</div>'
        )
    card_html += "</div>"

    # pipeline status table
    pipe_rows = ""
    for r in results:
        ok = r["success"]
        icon = "✓" if ok else "✗"
        clr  = "#155724" if ok else "#721c24"
        bg   = "#d4edda" if ok else "#f8d7da"
        pipe_rows += (
            f'<tr><td><strong>{r["label"]}</strong></td>'
            f'<td style="color:{clr};background:{bg};font-weight:700;text-align:center">{icon}</td>'
            f'<td style="font-size:0.85em;color:#666"><code>{" ".join(r.get("cmd",[]))}</code></td></tr>'
        )

    # top buys highlight
    buy_html = ""
    if buys:
        buy_html = '<h3 style="color:#27ae60;margin:24px 0 12px">Top BUY Signals</h3>'
        buy_html += (
            '<table><thead><tr><th>Ticker</th><th>Confidence</th>'
            '<th>Gamma</th><th>Volume</th><th>Kill Switch</th><th>Note</th></tr></thead><tbody>'
        )
        for ticker, s in sorted(buys, key=lambda x: x[1].get("confidence",0), reverse=True):
            buy_html += (
                f'<tr><td><strong>{ticker}</strong></td>'
                f'<td>{_conf_bar(s.get("confidence","—"))}</td>'
                f'<td>{_gamma_badge(s.get("gamma_regime","—"))}</td>'
                f'<td>{s.get("volume_signal","—")}</td>'
                f'<td>{_ks_badge(s.get("kill_switch"))}</td>'
                f'<td style="font-size:0.85em;color:#555">{s.get("note","—")[:100]}</td></tr>'
            )
        buy_html += "</tbody></table>"

    # top sells highlight
    sell_html = ""
    if sells:
        sell_html = '<h3 style="color:#e74c3c;margin:24px 0 12px">Top SELL Signals</h3>'
        sell_html += (
            '<table><thead><tr><th>Ticker</th><th>Price</th><th>Confidence</th>'
            '<th>Kill Switch</th><th>Note</th></tr></thead><tbody>'
        )
        for ticker, s in sorted(sells, key=lambda x: x[1].get("confidence",0), reverse=True):
            sell_html += (
                f'<tr><td><strong>{ticker}</strong></td>'
                f'<td>${s.get("price","—")}</td>'
                f'<td>{_conf_bar(s.get("confidence","—"))}</td>'
                f'<td>{_ks_badge(s.get("kill_switch"))}</td>'
                f'<td style="font-size:0.85em;color:#555">{s.get("note","—")[:100]}</td></tr>'
            )
        sell_html += "</tbody></table>"

    return f"""
        <div class="alert {status_cls}">
            <strong>{passed}/{total} pipeline agents succeeded</strong> &nbsp;|&nbsp; {ts_label}
        </div>
        {card_html}
        <table>
            <thead><tr><th>Agent</th><th style="width:60px;text-align:center">Status</th><th>Command</th></tr></thead>
            <tbody>{pipe_rows}</tbody>
        </table>
        {buy_html}
        {sell_html}
    """


def _build_signals_section(wl_data: dict | None) -> str:
    if not wl_data:
        return "<p>No watchlist analysis data available.</p>"

    out = ""
    for wl_name, wl in wl_data.items():
        if not isinstance(wl, dict) or "signals" not in wl:
            continue
        signals = wl["signals"]
        analyzed = wl.get("tickers_analyzed", len(signals))
        date_str = wl.get("analysis_date", "—")

        # summary boxes
        buys  = sum(1 for s in signals.values() if s.get("signal","").upper() == "BUY")
        sells = sum(1 for s in signals.values() if s.get("signal","").upper() == "SELL")
        holds = sum(1 for s in signals.values() if s.get("signal","").upper() == "HOLD")
        kills = sum(1 for s in signals.values() if s.get("kill_switch"))
        top_buys = wl.get("top_3_buys", [])

        out += f"""
        <div style="margin:32px 0 8px">
            <h3 style="font-size:1.3em;color:#667eea;border-bottom:2px solid #667eea;padding-bottom:6px;margin-bottom:16px">
                {wl_name.replace("_"," ").title()}
                <span style="font-size:0.7em;font-weight:400;color:#888;margin-left:12px">{analyzed} tickers · {date_str}</span>
            </h3>
            <div style="display:flex;gap:12px;flex-wrap:wrap;margin-bottom:20px">
                <div style="padding:10px 20px;background:#d4edda;border-radius:8px;font-weight:700;color:#155724">▲ BUY {buys}</div>
                <div style="padding:10px 20px;background:#f8d7da;border-radius:8px;font-weight:700;color:#721c24">▼ SELL {sells}</div>
                <div style="padding:10px 20px;background:#fff3cd;border-radius:8px;font-weight:700;color:#856404">● HOLD {holds}</div>
                <div style="padding:10px 20px;background:#ffe0b2;border-radius:8px;font-weight:700;color:#e65100">⚠ Kill Switches {kills}</div>
            </div>
        """
        if top_buys:
            out += f'<p style="margin-bottom:12px"><strong>Top Buys:</strong> {", ".join(str(t).split(":")[-1] for t in top_buys)}</p>'

        # full signals table — sort by signal priority then confidence
        order = {"BUY": 0, "SELL": 1, "HOLD": 2}
        sorted_sigs = sorted(
            signals.items(),
            key=lambda x: (order.get(x[1].get("signal","").upper(), 9), -x[1].get("confidence", 0))
        )
        out += """
        <table>
            <thead><tr>
                <th>Ticker</th><th>Signal</th><th>Confidence</th><th>Price</th>
                <th>RSI</th><th>Gamma</th><th>Volume</th><th>Kill</th><th>Note</th>
            </tr></thead><tbody>
        """
        for ticker, s in sorted_sigs:
            clean = ticker.split(":")[-1]
            out += (
                f'<tr>'
                f'<td><strong>{clean}</strong></td>'
                f'<td>{_sig_badge(s.get("signal","—"))}</td>'
                f'<td>{_conf_bar(s.get("confidence","—"))}</td>'
                f'<td style="font-weight:600">${s.get("price","—")}</td>'
                f'<td>{s.get("rsi","—")}</td>'
                f'<td>{_gamma_badge(s.get("gamma_regime","—"))}</td>'
                f'<td>{s.get("volume_signal","—")}</td>'
                f'<td>{_ks_badge(s.get("kill_switch"))}</td>'
                f'<td style="font-size:0.82em;color:#555;max-width:220px">{s.get("note","—")[:110]}</td>'
                f'</tr>'
            )
        out += "</tbody></table></div>"
    return out


def _build_catalyst_section(data: dict | None) -> str:
    if not data:
        return "<p>No catalyst data available.</p>"

    # Theme tags cloud
    themes = data.get("catalyst_themes", {})
    theme_html = ""
    if themes:
        theme_html = '<div style="margin:0 0 28px"><h3 style="color:#764ba2;margin-bottom:12px">Active Catalyst Themes</h3><div style="display:flex;flex-wrap:wrap;gap:10px">'
        theme_colors = ["#667eea","#764ba2","#27ae60","#e74c3c","#f39c12","#2196f3","#00bcd4","#ff5722"]
        for i, (theme, tickers) in enumerate(themes.items()):
            color = theme_colors[i % len(theme_colors)]
            clean_tickers = ", ".join(t.split(":")[-1] for t in tickers)
            theme_html += (
                f'<div style="background:#f8f9fa;border-left:4px solid {color};'
                f'padding:10px 16px;border-radius:6px;min-width:200px;flex:1">'
                f'<div style="font-weight:700;color:{color};font-size:0.85em">{theme}</div>'
                f'<div style="font-size:0.82em;color:#555;margin-top:4px">{clean_tickers}</div>'
                f'</div>'
            )
        theme_html += "</div></div>"

    # Per-watchlist ranked catalysts
    wa_html = ""
    for wl_name, wl in data.get("watchlist_analyses", {}).items():
        cats = wl.get("top_5_catalysts", {})
        if not cats:
            continue
        wa_html += f'<h3 style="color:#667eea;margin:28px 0 16px;border-bottom:1px solid #e0e0e0;padding-bottom:8px">{wl_name.replace("_"," ").title()} — Top Catalysts</h3>'
        for rank_key in sorted(cats.keys()):
            c = cats[rank_key]
            ticker = c.get("ticker","—").split(":")[-1]
            rank   = c.get("rank","—")
            company = c.get("company","")
            sector  = c.get("sector","")
            near    = c.get("near_term_catalyst","—")
            risks   = c.get("key_risks","—")

            policy_li  = "".join(f"<li>{x}</li>" for x in c.get("policy_catalysts",[]))
            gov_li     = "".join(f"<li>{x}</li>" for x in c.get("government_catalysts",[]))
            fund_li    = "".join(f"<li>{x}</li>" for x in c.get("fundamental_catalysts",[]))

            wa_html += f"""
            <div style="border:1px solid #e0e0e0;border-radius:10px;padding:20px;margin-bottom:16px;background:#fafafa">
                <div style="display:flex;align-items:center;gap:14px;margin-bottom:14px">
                    <div style="width:36px;height:36px;border-radius:50%;background:linear-gradient(135deg,#667eea,#764ba2);
                                color:white;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:1.1em">#{rank}</div>
                    <div>
                        <span style="font-size:1.2em;font-weight:800;color:#222">{ticker}</span>
                        <span style="margin-left:10px;color:#666;font-size:0.9em">{company}</span>
                        <span style="margin-left:8px;padding:2px 8px;background:#e3f2fd;color:#1565c0;
                                     border-radius:10px;font-size:0.75em;font-weight:600">{sector}</span>
                    </div>
                </div>
                <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;margin-bottom:14px">
                    <div><div style="font-size:0.75em;font-weight:700;color:#667eea;text-transform:uppercase;margin-bottom:4px">Policy</div>
                         <ul style="font-size:0.83em;color:#444;padding-left:16px;line-height:1.8">{policy_li}</ul></div>
                    <div><div style="font-size:0.75em;font-weight:700;color:#764ba2;text-transform:uppercase;margin-bottom:4px">Government</div>
                         <ul style="font-size:0.83em;color:#444;padding-left:16px;line-height:1.8">{gov_li}</ul></div>
                    <div><div style="font-size:0.75em;font-weight:700;color:#27ae60;text-transform:uppercase;margin-bottom:4px">Fundamental</div>
                         <ul style="font-size:0.83em;color:#444;padding-left:16px;line-height:1.8">{fund_li}</ul></div>
                </div>
                <div style="display:flex;gap:12px;flex-wrap:wrap">
                    <div style="padding:6px 12px;background:#e8f5e9;border-radius:6px;font-size:0.82em">
                        <strong style="color:#2e7d32">Near-term:</strong> {near}</div>
                    <div style="padding:6px 12px;background:#fff3e0;border-radius:6px;font-size:0.82em">
                        <strong style="color:#e65100">Risks:</strong> {risks}</div>
                </div>
            </div>
            """
    return theme_html + wa_html


def _build_swing_section(data: dict | None) -> str:
    if not data:
        return "<p>No swing setup data available.</p>"

    setups = data.get("top_setups", data.get("all_setups", []))
    if not setups:
        return "<p>No setups found in swing screener output.</p>"

    total = data.get("total_confirmed", len(setups))
    scan_date = data.get("scan_date", "—")

    setup_type_colors = {
        "PULLBACK_TO_MA20":       ("#e8f5e9", "#2e7d32"),
        "BULLISH_MA_MOMENTUM":    ("#e3f2fd", "#1565c0"),
        "SUPPORT_BOUNCE":         ("#f3e5f5", "#6a1b9a"),
        "CONSOLIDATION_BREAKOUT": ("#fff8e1", "#f57f17"),
        "OVERSOLD_BOUNCE":        ("#fce4ec", "#ad1457"),
    }

    header = f"""
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:20px;flex-wrap:wrap;gap:12px">
        <div>
            <span style="font-size:1.6em;font-weight:800;color:#222">{total}</span>
            <span style="color:#666;margin-left:8px">confirmed setups</span>
        </div>
        <div style="font-size:0.85em;color:#888">Scanned: {scan_date}</div>
    </div>
    """

    cards = ""
    for s in setups[:25]:
        setup_type = s.get("setup_type", "—")
        bg, fg = setup_type_colors.get(setup_type, ("#f5f5f5", "#333"))
        ticker = s.get("ticker","—")
        price  = s.get("price","—")
        entry  = s.get("entry","—")
        stop   = s.get("stop_loss","—")
        t1     = s.get("target_1","—")
        t2     = s.get("target_2","—")
        rr     = s.get("risk_reward","—")
        rsi    = s.get("rsi","—")
        conf   = s.get("confidence", s.get("quality_score","—"))
        momentum = s.get("momentum_20d","—")
        vol_ratio = s.get("volume_ratio","—")
        reasons = s.get("reasons", [])
        reason_tags = "".join(
            f'<span style="display:inline-block;padding:2px 8px;margin:2px;background:#f0f0f0;'
            f'border-radius:10px;font-size:0.75em;color:#555">{r}</span>'
            for r in reasons
        )

        rr_color = "#27ae60" if float(rr) >= 2.0 else ("#f39c12" if float(rr) >= 1.0 else "#e74c3c") if rr != "—" else "#999"

        cards += f"""
        <div style="border:1px solid #e0e0e0;border-radius:10px;overflow:hidden;margin-bottom:16px;background:#fff;box-shadow:0 2px 8px rgba(0,0,0,0.05)">
            <div style="display:flex;align-items:center;justify-content:space-between;padding:14px 20px;background:{bg};border-bottom:1px solid #e0e0e0">
                <div style="display:flex;align-items:center;gap:14px">
                    <span style="font-size:1.4em;font-weight:800;color:#222">{ticker}</span>
                    <span style="padding:3px 10px;border-radius:10px;font-size:0.78em;font-weight:700;background:{fg}22;color:{fg}">{setup_type.replace("_"," ")}</span>
                </div>
                <div style="text-align:right">
                    <div style="font-size:0.75em;color:#888">Current Price</div>
                    <div style="font-size:1.2em;font-weight:700;color:#222">${price}</div>
                </div>
            </div>
            <div style="padding:16px 20px">
                <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(110px,1fr));gap:12px;margin-bottom:14px">
                    <div style="background:#f8f9fa;border-radius:6px;padding:10px;text-align:center">
                        <div style="font-size:0.7em;font-weight:700;color:#667eea;text-transform:uppercase">Entry</div>
                        <div style="font-size:1.1em;font-weight:700;color:#333">${entry}</div>
                    </div>
                    <div style="background:#f8f9fa;border-radius:6px;padding:10px;text-align:center">
                        <div style="font-size:0.7em;font-weight:700;color:#e74c3c;text-transform:uppercase">Stop</div>
                        <div style="font-size:1.1em;font-weight:700;color:#e74c3c">${stop}</div>
                    </div>
                    <div style="background:#f8f9fa;border-radius:6px;padding:10px;text-align:center">
                        <div style="font-size:0.7em;font-weight:700;color:#27ae60;text-transform:uppercase">Target 1</div>
                        <div style="font-size:1.1em;font-weight:700;color:#27ae60">${t1}</div>
                    </div>
                    <div style="background:#f8f9fa;border-radius:6px;padding:10px;text-align:center">
                        <div style="font-size:0.7em;font-weight:700;color:#27ae60;text-transform:uppercase">Target 2</div>
                        <div style="font-size:1.1em;font-weight:700;color:#27ae60">${t2}</div>
                    </div>
                    <div style="background:#f8f9fa;border-radius:6px;padding:10px;text-align:center">
                        <div style="font-size:0.7em;font-weight:700;color:{rr_color};text-transform:uppercase">R:R</div>
                        <div style="font-size:1.1em;font-weight:700;color:{rr_color}">{rr}</div>
                    </div>
                    <div style="background:#f8f9fa;border-radius:6px;padding:10px;text-align:center">
                        <div style="font-size:0.7em;font-weight:700;color:#764ba2;text-transform:uppercase">RSI</div>
                        <div style="font-size:1.1em;font-weight:700;color:#764ba2">{rsi}</div>
                    </div>
                </div>
                <div style="display:flex;gap:12px;flex-wrap:wrap;margin-bottom:10px;font-size:0.82em;color:#666">
                    <span>20d Momentum: <strong>{momentum}%</strong></span>
                    <span>Vol Ratio: <strong>{vol_ratio}x</strong></span>
                    <span>Confidence: <strong>{conf}</strong></span>
                </div>
                <div>{reason_tags}</div>
            </div>
        </div>
        """
    return header + cards


def _build_kill_switch_section(wl_data: dict | None) -> str:
    if not wl_data:
        return "<p>No data available.</p>"

    ks_descriptions = {
        "K1": ("RSI Extreme / Overbought",     "RSI ≥ 80 — severely overbought, avoid new longs",     "#e65100"),
        "K2": ("High Volatility / Gap Risk",   "5-day range ≥ 12% — elevated chop risk",              "#c62828"),
        "K3": ("Low Liquidity",                "Volume below 500k threshold — avoid due to slippage",  "#bf360c"),
        "K4": ("Earnings Within 2 Days",       "Binary event risk — do not initiate new positions",    "#ad1457"),
        "K5": ("High Correlation Override",    "Position correlated with existing holding",            "#6a1b9a"),
        "K6": ("Technical Breakdown",          "Price below MA20 with weak volume confirmation",       "#ad1457"),
    }

    all_kills: dict[str, list] = {}
    for wl_name, wl in wl_data.items():
        if not isinstance(wl, dict):
            continue
        for ticker, ks in wl.get("kill_switch_alerts", {}).items():
            clean = ticker.split(":")[-1]
            for k in str(ks).split(","):
                k = k.strip()
                all_kills.setdefault(k, []).append((clean, wl_name))

    if not all_kills:
        return '<div class="alert alert-success"><strong>No kill switch alerts active.</strong></div>'

    out = f'<div class="alert alert-warning"><strong>{sum(len(v) for v in all_kills.values())} kill switch alerts across {len(all_kills)} types</strong></div>'

    for ks_key in sorted(all_kills.keys()):
        tickers = all_kills[ks_key]
        desc, detail, color = ks_descriptions.get(ks_key, (ks_key, "", "#333"))
        ticker_tags = "".join(
            f'<span style="display:inline-block;padding:3px 10px;margin:3px;background:{color}22;'
            f'border-radius:12px;font-size:0.85em;font-weight:700;color:{color}">{t}</span>'
            for t, _ in sorted(set(tickers), key=lambda x: x[0])
        )
        out += f"""
        <div style="border:1px solid {color}44;border-left:5px solid {color};border-radius:8px;
                    padding:16px 20px;margin-bottom:14px;background:{color}08">
            <div style="display:flex;align-items:center;gap:12px;margin-bottom:8px">
                <span style="padding:3px 12px;border-radius:12px;font-weight:800;font-size:0.9em;
                             background:{color};color:white">{ks_key}</span>
                <strong style="color:#222">{desc}</strong>
                <span style="font-size:0.82em;color:#666">({len(tickers)} tickers)</span>
            </div>
            <p style="font-size:0.83em;color:#555;margin-bottom:10px">{detail}</p>
            <div>{ticker_tags}</div>
        </div>
        """
    return out


def generate_html_report(results: list[dict], mode: str):
    """Build a fully-parsed, browsable HTML report from pipeline results."""
    try:
        sys.path.insert(0, str(Path.cwd()))
        from scripts.html_report_generator import create_html_template, save_html_report
    except ImportError as e:
        logger.warning(f"HTML report skipped (import error): {e}")
        return

    ts_label  = datetime.now().strftime("%Y-%m-%d %H:%M")
    wl_data   = _latest_json("analysis_")
    cat_data  = _latest_json("catalyst_analysis_")
    swing_data = _latest_json("swing_setups_")

    sections = [
        {"heading": "Summary",       "html": _build_summary_section(results, ts_label, wl_data, swing_data)},
        {"heading": "VIF Signals",   "html": _build_signals_section(wl_data)},
        {"heading": "Kill Switches", "html": _build_kill_switch_section(wl_data)},
        {"heading": "Catalysts",     "html": _build_catalyst_section(cat_data)},
        {"heading": "Swing Setups",  "html": _build_swing_section(swing_data)},
    ]

    ts_file  = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"pipeline_{mode}_{ts_file}"
    path = save_html_report(filename, create_html_template(
        f"VIF {mode.upper()} Report — {ts_label}",
        sections,
        {"author": "VIF Orchestrator"},
    ))
    logger.info(f"HTML report -> {path}")


def main():
    parser = argparse.ArgumentParser(
        description="VIF Orchestrator – delegates to all specialist agents"
    )
    parser.add_argument("--watchlist", "-w", help="Single watchlist name")
    parser.add_argument("--ticker",    "-t", help="Single ticker deep dive")
    parser.add_argument("--all",       action="store_true", help="All watchlists")
    parser.add_argument(
        "--mode", "-m",
        choices=list(PIPELINES.keys()),
        default="full",
        help="Pipeline mode (default: full)"
    )
    args = parser.parse_args()

    logger.info("=" * 65)
    logger.info("  VIF ORCHESTRATOR – AGENT DELEGATION SYSTEM")
    logger.info(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  |  mode={args.mode}")
    logger.info("=" * 65)

    if args.ticker:
        result = run_single_ticker(args.ticker.upper())
        print(json.dumps(result, indent=2))
        return 0

    results = run_pipeline(args.mode)
    save_run_log(results, args.mode)
    generate_html_report(results, args.mode)

    # Print summary (ASCII-only for Windows console compatibility)
    passed = sum(1 for r in results if r.get("success"))
    print(f"\n{'='*65}")
    print(f"ORCHESTRATOR COMPLETE | {passed}/{len(results)} agents succeeded")
    print(f"{'='*65}")
    for r in results:
        icon = "OK" if r["success"] else "FAIL"
        print(f"  [{icon}]  {r['label']}")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
