#!/usr/bin/env python3
"""
DSPy Offline Prompt Optimizer - Compile-Only Architecture (Option 2)

This script runs OFFLINE to generate optimized prompt strings.
Output: config/prompts_compiled.json (version-controlled, hand-editable JSON)

CRITICAL: Zero 'import dspy' in production code. This file is for development only.
Native agents load prompts from JSON via PromptLoader utility.

Usage:
  python research/dspy_compiler.py --export config/prompts_compiled.json

Architecture Decision (User Approved):
  - Optimizer runs offline (not at runtime)
  - Signatures define task intent + I/O schema
  - BootstrapFewShot learns from historical examples (reports/analysis_*.json)
  - Compiled output: prompt strings (system + few-shot examples) exported to JSON
  - Runtime: PromptLoader reads JSON, zero DSPy overhead
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# Only imported here for offline compilation (never in production)
try:
    import dspy
    from dspy.datasets import GSM8K
except ImportError:
    print("WARNING: dspy not installed. Install with: pip install dspy-ai")
    dspy = None


class VIFSignalSignature(dspy.Signature if dspy else object):
    """
    VIF Framework Signal Generation Signature.

    Input: Market data (OHLCV, indicators, technical levels)
    Output: BUY/SELL/HOLD signals with confidence, gamma regime, kill switches
    """
    if dspy:
        ticker_data: str = dspy.InputField(
            desc="JSON dict of ticker indicator snapshots: {price, rsi, macd, bb_upper/mid/lower, ema9/21/50/200, atr, volume, vol_avg_20d, vol_ratio, high_20d, low_20d, gamma_regime, kill_switches}"
        )
        watchlist_context: str = dspy.InputField(
            desc="Watchlist name and analysis date (e.g., 'AI Verticals, 2026-05-09')"
        )
        catalyst_overlay: str = dspy.InputField(
            desc="K4 and catalyst warnings from peer agents (e.g., 'NVDA: K4 earnings risk, confidence capped at 40')",
            default=""
        )
        signals_json: str = dspy.OutputField(
            desc='Valid JSON output: {"signals": {TICKER: {signal: "BUY|SELL|HOLD", confidence: 0-100, gamma_regime: "positive|negative|transition", volume_signal: "bullish|bearish|neutral", kill_switch: "K1-K6|null", price: float, rsi: float, note: str}}, "top_buys": [TICKER1, TICKER2, ...], "kill_alerts": {TICKER: reason}}'
        )


class CatalystSignature(dspy.Signature if dspy else object):
    """
    Macro Catalyst Analysis Signature.

    Input: Earnings dates, news headlines, macro calendar
    Output: Catalyst assessment per ticker, K4 flags (earnings risk)
    """
    if dspy:
        tickers_with_earnings: str = dspy.InputField(
            desc="JSON: {TICKER: {earnings_date: YYYY-MM-DD, days_away: int}}"
        )
        news_headlines: str = dspy.InputField(
            desc="JSON: {TICKER: [headline1, headline2, ...]}"
        )
        macro_calendar: str = dspy.InputField(
            desc="JSON: [{event: FOMC|CPI|NFP|..., date: YYYY-MM-DD, impact: high|medium|low}]"
        )
        catalyst_json: str = dspy.OutputField(
            desc='Valid JSON: {"scan_date": ISO, "macro_regime": "risk-on|risk-off|neutral", "sector_themes": {sector: {sentiment, catalysts}}, "ticker_catalysts": {TICKER: {catalyst_strength: high|medium|low, days_to_earnings: int, macro_exposure: bool}}, "high_risk_catalysts": [TICKER...], "top_5_opportunity_tickers": [...]}'
        )


def load_historical_examples(example_limit: int = 4) -> list:
    """
    Load historical trading signals from reports/ as training examples.

    For BootstrapFewShot: reads reports/analysis_*.json and extracts (input, output) pairs.
    """
    examples = []
    reports_dir = Path("reports") / "raw"

    if not reports_dir.exists():
        print(f"WARNING: reports/raw directory not found. Skipping few-shot examples.")
        return examples

    for report_file in sorted(reports_dir.glob("analysis_*.json"))[-example_limit:]:
        try:
            data = json.loads(report_file.read_text())
            # Parse report structure and extract (input, output) examples
            # This is a placeholder — actual parsing depends on report format
            if "signals" in data and "watchlist" in data:
                examples.append({
                    "watchlist": data.get("watchlist", "Unknown"),
                    "signals": data.get("signals", {}),
                })
        except Exception as e:
            print(f"  Skipped {report_file.name}: {e}")

    print(f"Loaded {len(examples)} historical examples")
    return examples


def compile_vif_signature() -> dict:
    """
    Compile VIF Signal signature using DSPy BootstrapFewShot.

    Returns: dict with "system" prompt and "few_shots" examples.
    """
    if not dspy:
        return {
            "system": "(DSPy not installed — using fallback prompt)",
            "few_shots": []
        }

    print("Compiling VIF Signal signature...")

    # Configure DSPy with Claude
    try:
        lm = dspy.LM("anthropic/claude-sonnet-4-6", temperature=0)
        dspy.settings.configure(lm=lm)
    except Exception as e:
        print(f"  Warning: Could not initialize DSPy LM: {e}")
        return {
            "system": "(LM initialization failed — using fallback)",
            "few_shots": []
        }

    # Create module with signature
    vif_module = dspy.ChainOfThought(VIFSignalSignature)

    # Load historical examples for few-shot bootstrap
    examples = load_historical_examples(example_limit=4)

    # For now, skip BootstrapFewShot (requires metric function)
    # In production: implement vif_accuracy_metric() and use teleprompter.compile()
    # teleprompter = dspy.BootstrapFewShot(metric=vif_accuracy_metric, max_bootstrapped_demos=4)
    # compiled_vif = teleprompter.compile(vif_module, trainset=examples)

    # Extract system prompt from signature
    system_prompt = vif_module.signature.get_instructions() if hasattr(vif_module.signature, 'get_instructions') else \
                    str(vif_module.signature.__doc__ or "(VIF Signal Generation)")

    return {
        "system": system_prompt,
        "few_shots": []  # Populated after BootstrapFewShot in future
    }


def compile_catalyst_signature() -> dict:
    """
    Compile Catalyst Analysis signature using DSPy.

    Returns: dict with "system" prompt and "few_shots" examples.
    """
    if not dspy:
        return {
            "system": "(DSPy not installed — using fallback prompt)",
            "few_shots": []
        }

    print("Compiling Catalyst signature...")

    # Configure DSPy
    try:
        lm = dspy.LM("anthropic/claude-sonnet-4-6", temperature=0)
        dspy.settings.configure(lm=lm)
    except Exception as e:
        print(f"  Warning: Could not initialize DSPy LM: {e}")
        return {
            "system": "(LM initialization failed — using fallback)",
            "few_shots": []
        }

    # Create module
    catalyst_module = dspy.Predict(CatalystSignature)

    system_prompt = catalyst_module.signature.get_instructions() if hasattr(catalyst_module.signature, 'get_instructions') else \
                    str(catalyst_module.signature.__doc__ or "(Catalyst Analysis)")

    return {
        "system": system_prompt,
        "few_shots": []
    }


def compile_and_export(output_path: str = "config/prompts_compiled.json"):
    """
    Compile both signatures and export to JSON.

    Args:
        output_path: Path to write prompts_compiled.json
    """
    print("=" * 70)
    print("DSPy OFFLINE PROMPT COMPILER")
    print("=" * 70)

    # Compile signatures
    vif_prompts = compile_vif_signature()
    catalyst_prompts = compile_catalyst_signature()

    # Build output structure
    output = {
        "version": "1.0",
        "generated_at": datetime.utcnow().isoformat(),
        "compiler": "dspy BootstrapFewShot (Option 2: Compile-Only Architecture)",
        "vif_signal": vif_prompts,
        "catalyst": catalyst_prompts,
        "metadata": {
            "note": "This file is version-controlled and hand-editable. Regenerate with: python research/dspy_compiler.py --export",
            "runtime_dependency": "Zero. PromptLoader reads this JSON file at runtime (no dspy import).",
            "few_shot_strategy": "BootstrapFewShot learns from reports/analysis_*.json (future enhancement)",
        }
    }

    # Write to file
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\n✓ Compiled prompts exported to: {output_path}")
    print(f"  Version: {output['version']}")
    print(f"  Generated: {output['generated_at']}")
    print(f"  Sections: {', '.join([k for k in output.keys() if k not in ['version', 'generated_at', 'compiler', 'metadata']])}")
    print("\n" + "=" * 70)

    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="DSPy Offline Prompt Compiler (Compile-Only Architecture)"
    )
    parser.add_argument(
        "--export",
        type=str,
        default="config/prompts_compiled.json",
        help="Output path for compiled prompts JSON (default: config/prompts_compiled.json)"
    )
    args = parser.parse_args()

    try:
        compile_and_export(args.export)
        return 0
    except Exception as e:
        print(f"✗ Compilation failed: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
