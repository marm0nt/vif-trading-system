#!/usr/bin/env python3
import sys, os, argparse
from datetime import datetime

try:
    import anthropic
except ImportError:
    print("ERROR: anthropic library not installed")
    sys.exit(1)

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = lambda *a, **kw: None

from pathlib import Path
import yaml

load_dotenv(override=True)  # .env wins over any stale system env var

CLAUDE_API_KEY = os.getenv("ANTHROPIC_API_KEY") or os.getenv("CLAUDE_API_KEY")

def get_model(role="analyst"):
    config_path = Path("config/vif_config.yml")
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config.get("api", {}).get("models", {}).get(role, "claude-sonnet-4-6")
    return os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6")

if not CLAUDE_API_KEY:
    print("ERROR: ANTHROPIC_API_KEY not found in .env")
    sys.exit(1)

client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

SYSTEM_PROMPT = """You are a VIF (Volatility Imbalance Framework) v4.0 trading expert.
Knowledge:
- Layer 1: Gamma regime (positive/negative/transition)
- Layer 2: Structural levels (support/resistance)
- Layer 3: Volume confirmation (ATAS, GEX)
- Window A: 10:30-11:30 AM European close fade
- Window B: 1:30-2:30 PM gamma flip reversal
- Kill switches K1-K6 for trading override

Answer trading questions using VIF framework."""

def main():
    parser = argparse.ArgumentParser(description="VIF Trading Research Agent")
    parser.add_argument("--query", "-q", required=True, help="Your question")
    parser.add_argument("--model", "-m", choices=["router", "analyst", "synthesizer"], default="analyst", help="Model role to use")
    args = parser.parse_args()

    CLAUDE_MODEL = get_model(args.model)

    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Claude Research Agent")
    print(f"Model Role: {args.model} -> {CLAUDE_MODEL}")
    print(f"Query: {args.query}\n")

    try:
        message = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": args.query}]
        )

        print("=" * 80)
        print("RESPONSE")
        print("=" * 80)
        print(message.content[0].text)
        print("=" * 80)
        print(f"Tokens: {message.usage.input_tokens + message.usage.output_tokens}")
        return 0

    except Exception as e:
        print(f"ERROR: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())