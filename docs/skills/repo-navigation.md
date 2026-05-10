# Repository Navigation & Factor Extraction Skill

**Purpose:** Enable autonomous discovery, parsing, and factor extraction from GitHub repositories to validate and enhance VIF trading signals.

**Owner:** Critic Agent + Risk Agent (collaborative)

---

## Strict Filters (Prevent Context Overflow)

### Repository Selection Criteria
```python
REPO_FILTERS = {
    "min_stars": 500,           # Production-proven
    "max_size_mb": 500,         # Prevent massive downloads
    "languages": ["python"],    # Compatible with existing codebase
    "licenses": ["MIT", "Apache-2.0", "GPL-3.0"],
    "max_age_days": 365,        # Active maintenance
    "exclude_patterns": [
        "test/", "docs/", "__pycache__", ".git/", "node_modules/",
        "*.egg-info", "dist/", "build/", "venv/"
    ]
}
```

### File Discovery Pattern
When exploring a repo, **only process** these file types:
- `*indicators*.py`, `*factor*.py`, `*signal*.py` → Factor logic
- `*config*.yml`, `*config*.json` → Parameter documentation
- `README.md` → High-level methodology
- `requirements.txt` → Dependency validation

**Skip everything else** to avoid token waste on boilerplate.

---

## Factor Extraction Algorithm

### Stage 1: Identify Computation Methods
Scan for patterns:
```python
# Look for these patterns in codebase
PATTERNS = {
    "RSI": r"RSI|relative strength|rsi\(",
    "MACD": r"MACD|moving average convergence|macd\(",
    "Bollinger": r"bollinger|bb_|bollingerband",
    "ATR": r"ATR|average true range|atr\(",
    "EMA": r"EMA|exponential moving average|ema\(",
    "Custom": r"class.*Indicator|def.*calculate"
}
```

### Stage 2: Extract Parameters
For each indicator found, extract:
- Period/window length (default: use repo's value)
- Input source (close, high, low, volume, etc.)
- Thresholds for signals (buy_threshold, sell_threshold, etc.)
- Any custom transformations

### Stage 3: Compare to VIF Baseline
```python
BASELINE = {
    "RSI": {"window": 14, "buy_threshold": 65, "sell_threshold": 35},
    "MACD": {"fast": 12, "slow": 26, "signal": 9},
    "BB": {"window": 20, "dev": 2},
    "EMA": {"periods": [9, 21, 50, 200]},
    "ATR": {"window": 14}
}
```

Generate a **deviation score** (0-100):
- 0 = Identical to VIF baseline
- 100 = Completely different methodology

---

## Novel Factor Detection

When deviation score > 40:
1. Document the novel factor
2. Extract implementation
3. Estimate integration effort (1-5 days)
4. Flag for "Week 2-3" TradingAgents debate layer

**Example Novel Factors to Look For:**
- Volume-weighted RSI (volume * momentum)
- Multi-timeframe EMA confirmation (daily + weekly alignment)
- Gamma regime extensions (third regime type beyond positive/negative)
- Earnings-aware filters (K4 integration patterns)

---

## Repository Catalog Structure

### File: `data/external_repos_catalog.json`
```json
{
  "repos": [
    {
      "name": "TauricResearch/TradingAgents",
      "url": "https://github.com/TauricResearch/TradingAgents",
      "stars": 59400,
      "last_commit": "2026-05-08",
      "factors_found": {
        "RSI": {"window": 14, "deviation": 0},
        "MACD": {"fast": 12, "slow": 26, "signal": 9, "deviation": 0},
        "ensemble_voting": {"type": "novel", "deviation": 85}
      },
      "novel_factors": [
        {
          "name": "ensemble_voting",
          "description": "Multi-agent consensus on BUY/SELL with disagreement weighting",
          "effort_days": 4,
          "integration_point": "critic_agent.py"
        }
      ],
      "integration_status": "CANDIDATE_WEEK2",
      "last_analyzed": "2026-05-09T20:35:00Z"
    }
  ]
}
```

---

## Rate Limit Management

### GitHub API Quotas (Authenticated)
- 5,000 requests/hour (enough for 1 deep repo scan/day)
- Monitor: `X-RateLimit-Remaining` header
- **Strategy:** Batch repo discovery on Sunday evening, cache results for week

### Hugging Face API Quotas
- Paper search: 100 queries/day (sufficient)
- Cache results: 30 days

---

## Execution Flow (Critic Agent)

```
1. VIF analyst generates BUY/SELL with confidence < 55%
   ↓
2. Critic queries external_alpha_audit skill
   ├─ hf.paper_search() → ["paper_1", "paper_2", "paper_3"]
   ├─ github.search_repos() → [repo_1, repo_2, repo_3]
   │
3. For each repo:
   ├─ Clone (shallow, max 500MB)
   ├─ Extract factors (stage 1-3)
   ├─ Calculate deviation score
   ├─ Store in catalog
   │
4. Synthesize findings:
   ├─ If factor validation: confidence += 5
   ├─ If contradiction: confidence -= 10
   ├─ If novel factor found: flag for Week 2 integration
   │
5. Return to VIF signal with audit metadata
```

---

## Failure Handling

### Network Timeout (GitHub/HF down)
→ Use cached catalog (data/external_repos_catalog.json)
→ Skip external validation, proceed with VIF signal as-is

### Large Repository (>500MB)
→ Skip, fetch next candidate repo
→ Log warning: "Repo too large for analysis: {repo_name}"

### Unrecognized Factor Type
→ Treat as novel, assign deviation score 100
→ Extract implementation, store in catalog for future reference

---

## Skill Maturity Stages

| Stage | Capability | Status |
|-------|-----------|--------|
| **Phase 1** | Paper search + repo discovery | ✓ READY (May 9, 2026) |
| **Phase 2** | Factor extraction + comparison | 🔄 IN PROGRESS |
| **Phase 3** | Integration into critic logic | ⏳ SCHEDULED (Week 2) |
| **Phase 4** | Novel factor backtesting | ⏳ SCHEDULED (Week 3+) |

---

## Token Cost Summary

| Operation | Tokens | Frequency | Monthly Cost |
|-----------|--------|-----------|--------------|
| Deep repo analysis (1 repo) | 300 | 4/month | 1,200 |
| Paper search batch | 100 | 4/month | 400 |
| Catalog lookup (cached) | 10 | Daily | 300 |
| **Monthly total** | | | **~1,900 tokens (~$0.019)** |

Low overhead — external intelligence is cost-neutral enhancement to VIF pipeline.
