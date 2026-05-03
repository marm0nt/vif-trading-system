#!/usr/bin/env python3
import json
from pathlib import Path
from datetime import datetime

analysis_file = Path("reports/analysis_20260501_140330.json")
with open(analysis_file, 'r') as f:
    analysis = json.load(f)

watchlist_data = analysis.get("vantage_portfolio", {})
signals = watchlist_data.get('signals', {})
kills = watchlist_data.get('kill_switch_alerts', {})

# Generate sell signals table rows
sell_rows = ""
sell_signals = [(ticker, data) for ticker, data in signals.items() if data.get('signal') == 'SELL']
for ticker, data in sorted(sell_signals, key=lambda x: x[1].get('confidence', 0), reverse=True)[:6]:
    kill_badge_class = 'badge-k2' if data.get('kill_switch') == 'K2' else 'badge-k3' if data.get('kill_switch') == 'K3' else 'badge-k6'
    sell_rows += f"""
                    <tr>
                        <td><strong>{ticker}</strong></td>
                        <td class="sell">{data.get('signal')}</td>
                        <td>{data.get('confidence')}%</td>
                        <td>${data.get('price', 0):.2f}</td>
                        <td><span class="badge {kill_badge_class}">{data.get('kill_switch', 'None')}</span></td>
                        <td>{data.get('note', '')}</td>
                    </tr>
"""

# Generate all signals table rows
all_signal_rows = ""
for ticker, data in sorted(signals.items()):
    signal_class = 'sell' if data.get('signal') == 'SELL' else 'hold'
    all_signal_rows += f"""
                    <tr>
                        <td><strong>{ticker}</strong></td>
                        <td class="{signal_class}">{data.get('signal')}</td>
                        <td>{data.get('confidence')}%</td>
                        <td>{data.get('gamma_regime')}</td>
                        <td>{data.get('volume_signal')}</td>
                        <td>${data.get('price', 0):.2f}</td>
                        <td>{data.get('kill_switch', '-')}</td>
                    </tr>
"""

# Categorize kills
kill_types = {}
for ticker, kill_code in kills.items():
    base_kill = kill_code.split()[0] if ' ' in kill_code else kill_code
    if base_kill not in kill_types:
        kill_types[base_kill] = []
    kill_types[base_kill].append(ticker)

kill_boxes = ""
kill_labels = {'K2': 'High Volatility (5d-range>12%)', 'K3': 'Low Liquidity (vol<500k)', 'K6': 'Technical Breakdown (price<MA20 & vol_weak)'}
for kill_code in ['K2', 'K3', 'K6']:
    if kill_code in kill_types:
        kill_boxes += f"""
                <div class="summary-box">
                    <h3>{kill_code} - {kill_labels.get(kill_code, '')}</h3>
                    <p><strong>Count:</strong> {len(kill_types[kill_code])} tickers</p>
                    <p><strong>Affected:</strong> {', '.join(sorted(kill_types[kill_code]))}</p>
                </div>
"""

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VIF Daily Watchlist Analysis</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', sans-serif; line-height: 1.6; color: #333; background: #f5f7fa; padding: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; border-radius: 12px; box-shadow: 0 10px 40px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px; text-align: center; }}
        .header h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
        .metadata {{ background: #f8f9fa; padding: 20px 40px; display: flex; gap: 40px; flex-wrap: wrap; border-bottom: 1px solid #e0e0e0; }}
        .metadata-item {{ display: flex; flex-direction: column; }}
        .metadata-label {{ font-weight: 600; color: #667eea; font-size: 0.85em; text-transform: uppercase; }}
        .metadata-value {{ color: #333; font-size: 1em; margin-top: 4px; }}
        .tabs {{ display: flex; gap: 0; background: #f8f9fa; border-bottom: 2px solid #e0e0e0; }}
        .tab-btn {{ padding: 15px 30px; cursor: pointer; border: none; background: transparent; font-size: 1em; border-bottom: 3px solid transparent; transition: all 0.3s; }}
        .tab-btn:hover {{ background: #e8eaf0; }}
        .tab-btn.active {{ color: #667eea; border-bottom-color: #667eea; font-weight: 600; }}
        .content {{ padding: 40px; }}
        .tab-content {{ display: none; }}
        .tab-content.active {{ display: block; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 12px; text-align: left; }}
        td {{ padding: 12px; border-bottom: 1px solid #e0e0e0; }}
        tr:hover {{ background: #f8f9fa; }}
        .sell {{ color: #d32f2f; font-weight: 600; }}
        .hold {{ color: #f57c00; }}
        .badge {{ display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 0.85em; font-weight: 600; }}
        .badge-k2 {{ background: #ffcdd2; color: #c62828; }}
        .badge-k3 {{ background: #ffe0b2; color: #e65100; }}
        .badge-k6 {{ background: #f8bbd0; color: #ad1457; }}
        .summary-box {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
        .summary-box h3 {{ color: #667eea; margin-bottom: 10px; }}
        .footer {{ background: #f8f9fa; padding: 20px 40px; text-align: center; border-top: 1px solid #e0e0e0; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 VIF Daily Watchlist Analysis</h1>
            <p>Volatility Imbalance Framework v4.0 Signal Generation</p>
        </div>

        <div class="metadata">
            <div class="metadata-item">
                <span class="metadata-label">Watchlist</span>
                <span class="metadata-value">{watchlist_data.get('watchlist', 'N/A')}</span>
            </div>
            <div class="metadata-item">
                <span class="metadata-label">Tickers Analyzed</span>
                <span class="metadata-value">{watchlist_data.get('tickers_analyzed', 0)}</span>
            </div>
            <div class="metadata-item">
                <span class="metadata-label">Analysis Date</span>
                <span class="metadata-value">{watchlist_data.get('analysis_date', 'N/A')}</span>
            </div>
            <div class="metadata-item">
                <span class="metadata-label">Generated</span>
                <span class="metadata-value">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</span>
            </div>
        </div>

        <div class="tabs">
            <button class="tab-btn active" onclick="switchTab('summary')">Summary</button>
            <button class="tab-btn" onclick="switchTab('signals')">All Signals</button>
            <button class="tab-btn" onclick="switchTab('kills')">Kill Switch Alerts</button>
            <button class="tab-btn" onclick="switchTab('methodology')">Methodology</button>
        </div>

        <div class="content">
            <div id="summary" class="tab-content active">
                <h2>Portfolio Summary</h2>
                <div class="summary-box">
                    <h3>📈 Market Regime</h3>
                    <p><strong>Dominant Gamma:</strong> Transition (RSI=50 neutral across portfolio)</p>
                    <p><strong>Implication:</strong> No directional bias. Market in consolidation. Avoid new positions without additional catalyst confirmation.</p>
                </div>

                <div class="summary-box">
                    <h3>🔴 Alert Status</h3>
                    <p><strong>Kill Switch Alerts:</strong> {len(kills)} tickers affected</p>
                    <p><strong>K2 (High Volatility):</strong> Elevated 5-day ranges exceed safety threshold</p>
                    <p><strong>K6 (Technical Breakdown):</strong> Price below MA20 with weak volume confirmation</p>
                </div>

                <div class="summary-box">
                    <h3>📊 Signal Distribution</h3>
                    <p><strong>BUY Signals:</strong> 0 (requires positive gamma + strong volume + no kills)</p>
                    <p><strong>SELL Signals:</strong> {len([s for s in signals.values() if s.get('signal') == 'SELL'])} high-conviction opportunities</p>
                    <p><strong>HOLD Signals:</strong> {len([s for s in signals.values() if s.get('signal') == 'HOLD'])} (transition regime, waiting for catalyst)</p>
                </div>

                <h3>Top SELL Opportunities</h3>
                <table>
                    <tr>
                        <th>Ticker</th>
                        <th>Signal</th>
                        <th>Confidence</th>
                        <th>Price</th>
                        <th>Kill Switch</th>
                        <th>Note</th>
                    </tr>
{sell_rows}
                </table>
            </div>

            <div id="signals" class="tab-content">
                <h2>All Ticker Signals</h2>
                <table>
                    <tr>
                        <th>Ticker</th>
                        <th>Signal</th>
                        <th>Confidence</th>
                        <th>Gamma Regime</th>
                        <th>Volume</th>
                        <th>Price</th>
                        <th>Kill Switch</th>
                    </tr>
{all_signal_rows}
                </table>
            </div>

            <div id="kills" class="tab-content">
                <h2>Kill Switch Alert Summary</h2>
{kill_boxes}
            </div>

            <div id="methodology" class="tab-content">
                <h2>VIF v4.0 Framework</h2>
                <div class="summary-box">
                    <h3>Gamma Regime Detection</h3>
                    <p><strong>Positive:</strong> RSI > 65 AND price > MA20 → Bullish momentum, buy pressure dominant</p>
                    <p><strong>Negative:</strong> RSI < 35 AND price < MA20 → Bearish momentum, sell pressure dominant</p>
                    <p><strong>Transition:</strong> All other combinations → Market consolidation, elevated uncertainty</p>
                </div>

                <div class="summary-box">
                    <h3>Volume Confirmation</h3>
                    <p><strong>STRONG:</strong> Current volume > 1.5x 20-day average → Conviction behind price move</p>
                    <p><strong>NORMAL:</strong> 0.8x to 1.5x 20-day average → Average liquidity, inconclusive</p>
                    <p><strong>WEAK:</strong> &lt; 0.8x 20-day average → Lack of participation, suspect move</p>
                </div>

                <div class="summary-box">
                    <h3>Kill Switches (Override Conditions)</h3>
                    <p><strong>K1:</strong> RSI > 80 or RSI < 20 (extreme overbought/oversold, reversal risk)</p>
                    <p><strong>K2:</strong> 5-day price range > 12% (excessive intraday volatility, whipsaw risk)</p>
                    <p><strong>K3:</strong> Current volume < 500k (illiquid, poor execution odds)</p>
                    <p><strong>K6:</strong> Price < MA20 AND volume_signal=weak (technical breakdown, no confirmation)</p>
                </div>

                <div class="summary-box">
                    <h3>Signal Logic</h3>
                    <p><strong>BUY:</strong> Positive gamma + strong volume + no active kill switches (high conviction)</p>
                    <p><strong>SELL:</strong> Negative gamma + kill switch triggered (confirmed bearish bias + override)</p>
                    <p><strong>HOLD:</strong> Everything else (transition regime or mixed signals, wait for clarity)</p>
                </div>
            </div>
        </div>

        <div class="footer">
            <p>📊 VIF Trading System v4.0 | Claude Sonnet 4.6 Analysis | Generated {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>⚠️ Analysis for educational purposes. Not investment advice. Backtest all strategies before live trading.</p>
        </div>
    </div>

    <script>
        function switchTab(tabName) {{
            const contents = document.querySelectorAll('.tab-content');
            const buttons = document.querySelectorAll('.tab-btn');
            contents.forEach(el => el.classList.remove('active'));
            buttons.forEach(el => el.classList.remove('active'));
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
        }}
    </script>
</body>
</html>
"""

output_file = Path("reports") / f"VANTAGE_PORTFOLIO_ANALYSIS_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
with open(output_file, 'w') as f:
    f.write(html)

print(f"✅ HTML Report Generated: {output_file}")
