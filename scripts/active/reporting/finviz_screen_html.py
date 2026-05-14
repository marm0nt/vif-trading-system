#!/usr/bin/env python3
"""
Human-readable HTML for FinViz screener JSON envelopes (reports/finviz_screen_*.json).

Uses the same template/CSS as other VIF HTML reports. Safe for batch conversion of
existing JSON files with zero API tokens.
"""

from __future__ import annotations

import argparse
import html as html_lib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))


def _esc(s: Any) -> str:
    if s is None:
        return "—"
    return html_lib.escape(str(s), quote=True)


def _fmt_float(x: Any, digits: int = 2) -> str:
    try:
        return f"{float(x):.{digits}f}"
    except (TypeError, ValueError):
        return _esc(x)


def _screener_section_html(screener_key: str, block: Dict[str, Any]) -> str:
    name = block.get("screener_name") or screener_key
    filters = block.get("filters_applied") or []
    tickers = block.get("tickers") or []
    qscores = block.get("quality_scores") or {}
    meta = block.get("metadata") or {}

    fli = "".join(f"<li>{_esc(f)}</li>" for f in filters)
    filters_html = f"<h4>Filters</h4><ul>{fli}</ul>" if fli else ""

    mock_note = ""
    ds = meta.get("data_source")
    if ds == "mock":
        mock_note = (
            '<p class="alert alert-warning" style="margin:12px 0;padding:10px 14px;border-radius:8px;">'
            "<strong>Mock data</strong> — connect live FinViz for production screening.</p>"
        )

    rows: List[str] = []
    for t in tickers:
        q = qscores.get(t)
        qcell = _fmt_float(q) if q is not None else "—"
        rows.append(f"<tr><td><strong>{_esc(t)}</strong></td><td>{qcell}</td></tr>")
    tbody = "".join(rows) if rows else '<tr><td colspan="2">No tickers</td></tr>'

    meta_rows = "".join(
        f"<tr><td>{_esc(k)}</td><td>{_esc(v)}</td></tr>"
        for k, v in sorted(meta.items(), key=lambda kv: str(kv[0]))
    )

    return f"""
    <h3>{_esc(name)}</h3>
    {mock_note}
    {filters_html}
    <h4>Top results</h4>
    <div style="overflow-x:auto">
    <table>
        <thead><tr><th>Ticker</th><th>Quality</th></tr></thead>
        <tbody>{tbody}</tbody>
    </table>
    </div>
    <h4>Screener metadata</h4>
    <table><thead><tr><th>Field</th><th>Value</th></tr></thead>
    <tbody>{meta_rows}</tbody></table>
    """


def _summary_html(envelope: Dict[str, Any]) -> str:
    fr = envelope.get("finviz_results") or {}
    ut = envelope.get("unique_tickers") or []
    chips = " ".join(
        f'<span class="badge badge-info" style="margin:2px;">{_esc(t)}</span>' for t in ut[:80]
    )
    more = ""
    if len(ut) > 80:
        more = f'<p style="color:#666;font-size:0.9em;">… and {len(ut) - 80} more tickers (see JSON for full list).</p>'

    return f"""
    <div class="metric" style="display:inline-block;margin:8px 16px 8px 0;">
        <div class="metric-label">Unique tickers</div>
        <div class="metric-value">{_esc(envelope.get("discovery_count", len(ut)))}</div>
    </div>
    <div class="metric" style="display:inline-block;margin:8px 16px 8px 0;">
        <div class="metric-label">Screeners (with results)</div>
        <div class="metric-value">{_esc(fr.get("screeners_with_results", "—"))}
            / {_esc(fr.get("screeners_executed", "—"))}</div>
    </div>
    <div class="metric" style="display:inline-block;margin:8px 16px 8px 0;">
        <div class="metric-label">Duration (run)</div>
        <div class="metric-value">{_esc(envelope.get("duration_ms", "—"))} ms</div>
    </div>
    <div class="metric" style="display:inline-block;margin:8px 16px 8px 0;">
        <div class="metric-label">Cache hit</div>
        <div class="metric-value">{_esc(fr.get("cache_hit", "—"))}</div>
    </div>
    <p><strong>Trace ID:</strong> <code>{_esc(envelope.get("trace_id"))}</code></p>
    <p><strong>Timestamp:</strong> {_esc(envelope.get("timestamp"))}</p>
    <h4>Discovered universe</h4>
    <div style="line-height:1.8;">{chips}</div>
    {more}
    """


def finviz_screen_envelope_to_html(envelope: Dict[str, Any]) -> str:
    from scripts.active.reporting.html_report_generator import create_html_template

    fr = envelope.get("finviz_results") or {}
    results = fr.get("results") or {}

    sections: List[Dict[str, str]] = [
        {"heading": "Summary", "html": _summary_html(envelope)},
    ]

    for key in sorted(results.keys()):
        sections.append(
            {
                "heading": key.replace("_", " ").title()[:48],
                "html": _screener_section_html(key, results[key]),
            }
        )

    extras: List[str] = []
    if fr.get("comparison") is not None:
        extras.append(
            "<h4>VIF comparison</h4><pre style=\"overflow:auto;background:#f8f9fa;padding:12px;\">"
            + _esc(json.dumps(fr["comparison"], indent=2, default=str)[:120000])
            + "</pre>"
        )
    if fr.get("novel_discoveries") is not None:
        extras.append(
            "<h4>Novel discoveries</h4><pre style=\"overflow:auto;background:#f8f9fa;padding:12px;\">"
            + _esc(json.dumps(fr["novel_discoveries"], indent=2, default=str)[:120000])
            + "</pre>"
        )
    if extras:
        sections.append({"heading": "Raw enrichments", "html": "\n".join(extras)})

    title_ts = str(envelope.get("timestamp") or "")[:19].replace("T", " ")
    return create_html_template(
        title=f"FinViz Screeners — {title_ts}",
        content_sections=sections,
        metadata={
            "author": "VIF FinViz Screener (deterministic HTML)",
            "timestamp": str(envelope.get("timestamp") or ""),
        },
    )


def write_finviz_screen_html(
    json_path: Path,
    envelope: Optional[Dict[str, Any]] = None,
) -> Path:
    """Write reports/<stem>.html next to the JSON path's basename."""
    from scripts.active.reporting.html_report_generator import save_html_report

    json_path = Path(json_path)
    if envelope is None:
        envelope = json.loads(json_path.read_text(encoding="utf-8"))
    html = finviz_screen_envelope_to_html(envelope)
    out = save_html_report(json_path.stem, html)
    return Path(out)


def _expand_paths(argv: List[str]) -> List[Path]:
    paths: List[Path] = []
    for raw in argv:
        p = Path(raw)
        if any(c in raw for c in "*?["):
            paths.extend(sorted(Path().glob(raw)))
        elif p.is_file():
            paths.append(p)
        else:
            print(f"Skip missing: {raw}", file=sys.stderr)
    return paths


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert finviz_screen_*.json to HTML.")
    parser.add_argument(
        "paths",
        nargs="*",
        help="JSON files or globs (default: reports/finviz_screen_*.json)",
    )
    args = parser.parse_args()
    os_cwd = Path.cwd()
    if (os_cwd / "reports").is_dir():
        pass
    elif (_REPO_ROOT / "reports").is_dir():
        os.chdir(_REPO_ROOT)

    paths = _expand_paths(args.paths) if args.paths else sorted(Path("reports").glob("finviz_screen_*.json"))
    if not paths:
        print("No matching finviz_screen_*.json files.", file=sys.stderr)
        return 1
    for jp in paths:
        try:
            out = write_finviz_screen_html(jp)
            print(out)
        except Exception as e:
            print(f"ERROR {jp}: {e}", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
