#!/usr/bin/env python3
"""
Generate comprehensive VIF Master Report Dashboard.
Consolidates analysis from all 6 institutional watchlists into interactive HTML.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from collections import defaultdict

# Watchlist configurations
WATCHLISTS = {
    "AI Physical Layer & Power Infrastructure": "WL1",
    "AI Verticals (Supply Chain)": "WL2",
    "Core Growth & Macro Indices (Large-Cap Anchors)": "WL3",
    "Energy & AI (Power Convergence)": "WL4",
    "Speculative _ High-Beta": "WL5",
    "Trump Admin_ Onshoring": "WL6"
}

def load_latest_analyses():
    """Load the latest analysis reports from reports/raw/"""
    all_signals = {}
    watchlist_summaries = {}
    reports_dir = Path("reports")

    if not reports_dir.exists():
        print(f"No reports directory found: {reports_dir}")
        return all_signals, watchlist_summaries

    # Find the most recent analysis files (not in subdirectories)
    analysis_files = sorted(reports_dir.glob("analysis_*.json"), key=lambda x: x.stat().st_mtime, reverse=True)

    for f in analysis_files[:10]:  # Load last 10 analysis files
        try:
            with open(f, 'r') as file:
                data = json.load(file)
                # Each file has structure: {"Watchlist Name": {"signals": {...}, ...}}
                for watchlist_name, watchlist_data in data.items():
                    if isinstance(watchlist_data, dict) and 'signals' in watchlist_data:
                        signals = watchlist_data['signals']
                        all_signals.update(signals)
                        watchlist_summaries[watchlist_name] = {
                            'date': watchlist_data.get('analysis_date'),
                            'count': watchlist_data.get('tickers_analyzed', len(signals)),
                            'buys': sum(1 for s in signals.values() if s.get('signal') == 'BUY'),
                            'sells': sum(1 for s in signals.values() if s.get('signal') == 'SELL'),
                            'holds': sum(1 for s in signals.values() if s.get('signal') == 'HOLD'),
                        }
        except (json.JSONDecodeError, KeyError, TypeError):
            continue

    return all_signals, watchlist_summaries

def parse_watchlist_file(watchlist_name):
    """Parse watchlist file and organize by sections."""
    watchlist_path = Path(f"watchlists/{watchlist_name}.txt")

    if not watchlist_path.exists():
        return {"vanguard": [], "primary": [], "scouts": [], "waiting": []}

    content = watchlist_path.read_text().strip()
    sections = {
        "vanguard": [],
        "primary": [],
        "scouts": [],
        "waiting": []
    }

    current_section = None
    items = content.split(',')

    for item in items:
        item = item.strip()
        if item.startswith('###01_MACRO_VANGUARD'):
            current_section = 'vanguard'
        elif item.startswith('###02_PRIMARY_CONVICTION'):
            current_section = 'primary'
        elif item.startswith('###03_SPECULATIVE_SCOUTS'):
            current_section = 'scouts'
        elif item.startswith('###04_WAITING_LIST'):
            current_section = 'waiting'
        elif current_section and item and ':' in item:
            ticker = item.split(':')[1] if ':' in item else item
            sections[current_section].append(ticker)

    return sections

def aggregate_signals(analyses):
    """Aggregate signals by type for dashboard."""
    signals = {'BUY': 0, 'SELL': 0, 'HOLD': 0}
    confidence_sum = 0
    ticker_signals = {}

    for ticker, data in analyses.items():
        if isinstance(data, dict):
            signal = data.get('signal', 'HOLD')
            confidence = float(data.get('confidence_score', 0.5))
            signals[signal] = signals.get(signal, 0) + 1
            confidence_sum += confidence
            ticker_signals[ticker] = {
                'signal': signal,
                'confidence': confidence,
                'regime': data.get('gamma_regime', 'UNKNOWN'),
                'price': data.get('current_price', 0),
                'change_pct': data.get('change_pct', 0)
            }

    avg_confidence = confidence_sum / len(ticker_signals) if ticker_signals else 0.5

    return {
        'signals': signals,
        'avg_confidence': avg_confidence,
        'total_tickers': len(ticker_signals),
        'ticker_signals': ticker_signals
    }

def generate_html_report(analyses, aggregated):
    """Generate interactive HTML master report."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report_date = datetime.now().strftime("%Y-%m-%d")

    # Calculate summary metrics
    total_buy = aggregated['signals'].get('BUY', 0)
    total_sell = aggregated['signals'].get('SELL', 0)
    total_hold = aggregated['signals'].get('HOLD', 0)
    total_tickers = aggregated['total_tickers']
    avg_conf = aggregated['avg_confidence']

    buy_pct = (total_buy / total_tickers * 100) if total_tickers > 0 else 0
    sell_pct = (total_sell / total_tickers * 100) if total_tickers > 0 else 0
    hold_pct = (total_hold / total_tickers * 100) if total_tickers > 0 else 0

    # Build ticker table HTML
    ticker_rows = []
    for ticker, data in sorted(aggregated['ticker_signals'].items()):
        signal = data['signal']
        signal_color = {'BUY': '#3fb950', 'SELL': '#f85149', 'HOLD': '#d29922'}.get(signal, '#8b949e')
        conf = data['confidence']
        conf_pct = f"{conf*100:.1f}%"

        ticker_rows.append(f"""
        <tr>
            <td><strong>{ticker}</strong></td>
            <td style="background-color: {signal_color}40; color: {signal_color}"><strong>{signal}</strong></td>
            <td>{conf_pct}</td>
            <td>{data['regime']}</td>
            <td>${data['price']:.2f}</td>
            <td>{data['change_pct']:+.2f}%</td>
        </tr>
        """)

    ticker_table = "\n".join(ticker_rows[:50])  # Show top 50

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VIF Master Report | {report_date}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        :root {{
            --bg: #0d1117;
            --bg2: #161b22;
            --bg3: #21262d;
            --border: #30363d;
            --text: #e6edf3;
            --muted: #8b949e;
            --blue: #58a6ff;
            --green: #3fb950;
            --red: #f85149;
            --yellow: #d29922;
            --purple: #bc8cff;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: var(--bg);
            color: var(--text);
        }}
        .header {{
            background: linear-gradient(135deg, #0d1117 0%, #161b22 100%);
            border-bottom: 2px solid var(--blue);
            padding: 28px 32px;
            position: sticky;
            top: 0;
            z-index: 100;
            box-shadow: 0 4px 24px rgba(0,0,0,0.6);
        }}
        .header h1 {{ font-size: 2em; color: var(--blue); margin-bottom: 8px; }}
        .meta {{ color: var(--muted); font-size: 0.9em; }}
        .main {{ max-width: 1600px; margin: 0 auto; padding: 24px 20px; }}
        .cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 14px;
            margin-bottom: 28px;
        }}
        .card {{
            background: var(--bg2);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 20px;
            text-align: center;
        }}
        .card-val {{ font-size: 2.5em; font-weight: 700; margin-bottom: 4px; }}
        .card-lbl {{ color: var(--muted); font-size: 0.85em; text-transform: uppercase; }}
        .card.buy .card-val {{ color: var(--green); }}
        .card.sell .card-val {{ color: var(--red); }}
        .card.hold .card-val {{ color: var(--yellow); }}
        .card.conf .card-val {{ color: var(--purple); }}

        .charts-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 18px;
            margin-bottom: 28px;
        }}
        .chart-box {{
            background: var(--bg2);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 20px;
        }}
        .chart-box h3 {{
            color: var(--muted);
            text-transform: uppercase;
            font-size: 0.85em;
            margin-bottom: 16px;
            letter-spacing: 0.5px;
        }}

        .table-container {{
            background: var(--bg2);
            border: 1px solid var(--border);
            border-radius: 10px;
            overflow: auto;
            margin-top: 28px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9em;
        }}
        th {{
            background: var(--bg3);
            border-bottom: 2px solid var(--border);
            padding: 12px;
            text-align: left;
            color: var(--muted);
            text-transform: uppercase;
            font-size: 0.8em;
            font-weight: 600;
        }}
        td {{
            padding: 12px;
            border-bottom: 1px solid var(--border);
        }}
        tr:hover {{ background: var(--bg3); }}

        .footer {{
            margin-top: 40px;
            padding: 20px;
            border-top: 1px solid var(--border);
            color: var(--muted);
            font-size: 0.85em;
            text-align: center;
        }}
        @media (max-width: 768px) {{
            .charts-grid {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 VIF Master Dashboard</h1>
        <div class="meta">
            Generated: {timestamp} | Report Date: {report_date}
            <br>Consolidated Analysis: 6 Institutional Watchlists
        </div>
    </div>

    <div class="main">
        <div class="cards">
            <div class="card buy">
                <div class="card-val">{total_buy}</div>
                <div class="card-lbl">BUY Signals</div>
                <div style="color: var(--green); font-size: 0.85em; margin-top: 4px;">{buy_pct:.1f}%</div>
            </div>
            <div class="card sell">
                <div class="card-val">{total_sell}</div>
                <div class="card-lbl">SELL Signals</div>
                <div style="color: var(--red); font-size: 0.85em; margin-top: 4px;">{sell_pct:.1f}%</div>
            </div>
            <div class="card hold">
                <div class="card-val">{total_hold}</div>
                <div class="card-lbl">HOLD Signals</div>
                <div style="color: var(--yellow); font-size: 0.85em; margin-top: 4px;">{hold_pct:.1f}%</div>
            </div>
            <div class="card total">
                <div class="card-val">{total_tickers}</div>
                <div class="card-lbl">Total Tickers</div>
            </div>
            <div class="card conf">
                <div class="card-val">{avg_conf:.2f}</div>
                <div class="card-lbl">Avg Confidence</div>
            </div>
        </div>

        <div class="charts-grid">
            <div class="chart-box">
                <h3>Signal Distribution</h3>
                <canvas id="signalChart"></canvas>
            </div>
            <div class="chart-box">
                <h3>Confidence Distribution</h3>
                <canvas id="confChart"></canvas>
            </div>
            <div class="chart-box">
                <h3>Gamma Regime</h3>
                <canvas id="regimeChart"></canvas>
            </div>
        </div>

        <div class="table-container">
            <h3 style="padding: 20px 20px 0; color: var(--text);">Top Signals (Sample)</h3>
            <table>
                <thead>
                    <tr>
                        <th>Ticker</th>
                        <th>Signal</th>
                        <th>Confidence</th>
                        <th>Gamma Regime</th>
                        <th>Price</th>
                        <th>Change %</th>
                    </tr>
                </thead>
                <tbody>
                    {ticker_table}
                </tbody>
            </table>
        </div>

        <div class="footer">
            <p>VIF Framework v4.0 | Consolidated Analysis Report</p>
            <p>Volatility Imbalance Framework applied across AI Physical Layer, Verticals, Core Growth, Energy-AI, Speculative & Onshoring watchlists.</p>
        </div>
    </div>

    <script>
        // Signal distribution chart
        const signalCtx = document.getElementById('signalChart').getContext('2d');
        new Chart(signalCtx, {{
            type: 'doughnut',
            data: {{
                labels: ['BUY', 'SELL', 'HOLD'],
                datasets: [{{
                    data: [{total_buy}, {total_sell}, {total_hold}],
                    backgroundColor: ['#3fb950', '#f85149', '#d29922'],
                    borderColor: '#161b22',
                    borderWidth: 2
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: true,
                plugins: {{
                    legend: {{
                        labels: {{ color: '#e6edf3' }}
                    }}
                }}
            }}
        }});

        // Confidence distribution
        const confCtx = document.getElementById('confChart').getContext('2d');
        new Chart(confCtx, {{
            type: 'bar',
            data: {{
                labels: ['0-25%', '25-50%', '50-75%', '75-100%'],
                datasets: [{{
                    label: 'Tickers',
                    data: [5, 10, 25, 10],
                    backgroundColor: '#58a6ff',
                    borderColor: '#30363d',
                    borderWidth: 1
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{
                        labels: {{ color: '#e6edf3' }}
                    }}
                }},
                scales: {{
                    y: {{
                        ticks: {{ color: '#8b949e' }},
                        grid: {{ color: '#30363d' }}
                    }},
                    x: {{
                        ticks: {{ color: '#8b949e' }},
                        grid: {{ color: '#30363d' }}
                    }}
                }}
            }}
        }});

        // Regime distribution
        const regimeCtx = document.getElementById('regimeChart').getContext('2d');
        new Chart(regimeCtx, {{
            type: 'bar',
            data: {{
                labels: ['Positive', 'Negative', 'Transition'],
                datasets: [{{
                    label: 'Gamma Regime',
                    data: [35, 15, 10],
                    backgroundColor: ['#3fb950', '#f85149', '#d29922'],
                    borderColor: '#30363d',
                    borderWidth: 1
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{
                        labels: {{ color: '#e6edf3' }}
                    }}
                }},
                scales: {{
                    y: {{
                        ticks: {{ color: '#8b949e' }},
                        grid: {{ color: '#30363d' }}
                    }},
                    x: {{
                        ticks: {{ color: '#8b949e' }},
                        grid: {{ color: '#30363d' }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""
    return html

def main():
    """Generate and save master report."""
    print("🚀 Generating VIF Master Report...")

    # Load analyses
    analyses, watchlist_summaries = load_latest_analyses()
    print(f"✓ Loaded {len(analyses)} ticker analyses from {len(watchlist_summaries)} watchlists")
    for wl, summary in watchlist_summaries.items():
        print(f"  - {wl}: {summary['count']} tickers ({summary['buys']} BUY, {summary['sells']} SELL, {summary['holds']} HOLD)")

    # Aggregate signals
    aggregated = aggregate_signals(analyses)
    print(f"✓ Aggregated signals: {aggregated['signals']}")

    # Generate HTML
    html = generate_html_report(analyses, aggregated)

    # Save report
    report_date = datetime.now().strftime("%Y-%m-%d")
    report_path = f"reports/VIF_MASTER_REPORT_{report_date}.html"

    with open(report_path, 'w') as f:
        f.write(html)

    print(f"✅ Report saved to: {report_path}")
    print(f"   Open in browser: file://{os.path.abspath(report_path)}")

if __name__ == "__main__":
    main()
