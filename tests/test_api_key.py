#!/usr/bin/env python3
"""Diagnose API key shadowing and verify billing."""
import os, sys
import anthropic
from dotenv import load_dotenv, dotenv_values

pre = os.environ.get("ANTHROPIC_API_KEY")
load_dotenv(override=True)
fil = dotenv_values(".env").get("ANTHROPIC_API_KEY")

def fp(k):
    return (k[:20] + "..." + k[-6:]) if k and len(k) > 30 else "<not set>"

print("System env key:", fp(pre))
print(".env file key :", fp(fil))

if pre and fil and pre != fil:
    print("\n** SHADOWING DETECTED **")
    print("System env was overriding .env. Forcing .env this run.")
    print("Remove the system var, then reopen all terminals:")
    print("  PowerShell: setx ANTHROPIC_API_KEY \"\"")
elif not pre:
    print("No system env key. .env is the only source. Good.")
else:
    print("Both sources match.")

key = os.getenv("ANTHROPIC_API_KEY")
if not key:
    print("ERROR: no key available")
    sys.exit(1)

print("\nKey in use:", fp(key))
client = anthropic.Anthropic(api_key=key)

print("\n[1] Listing models (no charge)...")
try:
    m = client.models.list()
    print("    OK -", len(m.data), "models")
except Exception as e:
    print("    FAIL:", type(e).__name__, str(e)[:200])
    sys.exit(1)

print("\n[2] Billed call to claude-haiku-4-5...")
try:
    r = client.messages.create(
        model="claude-haiku-4-5", max_tokens=5,
        messages=[{"role":"user","content":"hi"}])
    print("    OK - id=" + r.id)
    print("\nSUCCESS: key valid, billing active.")
except Exception as e:
    print("    FAIL:", str(e)[:300])
    sys.exit(1)
