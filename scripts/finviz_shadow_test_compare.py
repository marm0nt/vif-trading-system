#!/usr/bin/env python3
"""
FinViz Shadow Test Comparison (Phase B)

Compares FinViz discovery with VIF signals:
- Extracts unique tickers from FinViz screeners
- Extracts consensus signals from premarket VIF analysis
- Calculates overlap percentage
- Tracks metrics over 5 days
"""

import json
from pathlib import Path
from datetime import datetime, date
from typing import Dict, Set, Tuple

def load_finviz_tickers(finviz_report: Path) -> Set[str]:
    """Extract unique tickers from FinViz screener report."""
    try:
        data = json.loads(finviz_report.read_text())
        return set(data.get("unique_tickers", []))
    except Exception as e:
        print(f"Error loading FinViz report: {e}")
        return set()

def load_vif_signals(vif_report: Path) -> Tuple[Set[str], Dict]:
    """Extract consensus signals from VIF premarket report."""
    try:
        data = json.loads(vif_report.read_text())
        consensus = data.get("consensus_signals", {})
        
        # Extract tickers with BUY/SELL signals (exclude HOLD)
        signal_tickers = {t for t, s in consensus.items() if s.get("signal") in ("BUY", "SELL")}
        
        return signal_tickers, consensus
    except Exception as e:
        print(f"Error loading VIF report: {e}")
        return set(), {}

def calculate_overlap(finviz_set: Set[str], vif_set: Set[str]) -> Dict:
    """Calculate overlap metrics between FinViz and VIF."""
    intersection = finviz_set & vif_set
    union = finviz_set | vif_set
    
    overlap_pct = (len(intersection) / len(union) * 100) if union else 0
    
    return {
        "finviz_count": len(finviz_set),
        "vif_count": len(vif_set),
        "overlap_count": len(intersection),
        "overlap_percentage": round(overlap_pct, 1),
        "union_count": len(union),
        "finviz_only": sorted(list(finviz_set - vif_set)),
        "vif_only": sorted(list(vif_set - finviz_set)),
        "agreement": sorted(list(intersection)),
    }

def run_shadow_test():
    """Execute shadow test comparison."""
    print("="*70)
    print("  FINVIZ SHADOW TEST (PHASE B) - DAY 1")
    print("="*70)
    print()
    
    reports = Path("reports")
    
    # Get latest FinViz report
    finviz_reports = sorted(reports.glob("finviz_screen_*.json"))
    if not finviz_reports:
        print("ERROR: No FinViz reports found")
        return
    
    finviz_report = finviz_reports[-1]
    print(f"FinViz Report: {finviz_report.name}")
    
    # Get latest VIF premarket report
    vif_reports = sorted(reports.glob("swarm_result_premarket_*.json"))
    if not vif_reports:
        print("ERROR: No VIF premarket reports found")
        return
    
    vif_report = vif_reports[-1]
    print(f"VIF Report: {vif_report.name}")
    print()
    
    # Extract and compare
    finviz_tickers = load_finviz_tickers(finviz_report)
    vif_tickers, consensus = load_vif_signals(vif_report)
    
    metrics = calculate_overlap(finviz_tickers, vif_tickers)
    
    # Display results
    print(f"FinViz Discoveries:    {metrics['finviz_count']} tickers")
    print(f"VIF Signals (BUY/SELL): {metrics['vif_count']} tickers")
    print(f"Overlap:                {metrics['overlap_count']} tickers ({metrics['overlap_percentage']}%)")
    print()
    
    if metrics['agreement']:
        print(f"✓ Agreement (both found): {', '.join(metrics['agreement'][:5])}")
        if len(metrics['agreement']) > 5:
            print(f"  ... and {len(metrics['agreement']) - 5} more")
        print()
    
    if metrics['finviz_only']:
        print(f"FinViz-only: {', '.join(metrics['finviz_only'][:5])}")
        if len(metrics['finviz_only']) > 5:
            print(f"  ... and {len(metrics['finviz_only']) - 5} more")
        print()
    
    if metrics['vif_only']:
        print(f"VIF-only: {', '.join(metrics['vif_only'][:5])}")
        if len(metrics['vif_only']) > 5:
            print(f"  ... and {len(metrics['vif_only']) - 5} more")
        print()
    
    # Save shadow test metrics
    shadow_file = reports / f"shadow_test_{date.today().isoformat()}.json"
    shadow_file.write_text(json.dumps({
        "timestamp": datetime.now().isoformat(),
        "finviz_report": finviz_report.name,
        "vif_report": vif_report.name,
        "metrics": metrics,
        "target_overlap_pct": 50,
        "phase_b_status": "PASS" if metrics['overlap_percentage'] >= 50 else "CONTINUE_TEST",
    }, indent=2))
    
    print(f"Shadow test metrics saved → {shadow_file.name}")
    print()
    print("="*70)
    print(f"  TARGET: >50% overlap | CURRENT: {metrics['overlap_percentage']}%")
    print(f"  STATUS: {'PASS ✓' if metrics['overlap_percentage'] >= 50 else 'CONTINUE_TEST'}")
    print("="*70)

if __name__ == "__main__":
    run_shadow_test()
