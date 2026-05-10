# External Alpha Audit Skill — GitHub & Hugging Face MCP Integration

**Purpose:** Enable the VIF swarm to discover, analyze, and validate trading research from public repositories and academic papers.

**Activation:** When a BUY signal confidence is below 55% or a SELL signal conflicts with market regime.

---

## Phase 2: Paper + Repository Discovery Loop

### Step 1: Hugging Face Paper Search
Trigger when: VIF analyst generates ambiguous signals (e.g., HOLD with mixed gamma regimes)

```python
# Example query (executed by critic agent)
hf.paper_search(
    query="Multi-agent consensus for volatility prediction 2026",
    top_k=3
)
```

**Expected Output:**
- Paper title, authors, arxiv link
- Key findings on gamma regime detection
- Factor generation methodology

### Step 2: GitHub Repository Discovery
For each paper, search for reference implementation:

```python
github.search_repos(
    query="volatility imbalance framework agent swarm",
    language="python",
    stars=">1000",
    sort="stars"
)
```

**Filter Criteria:**
- Stars > 1,000 (production-proven code)
- Active maintenance (commits within 3 months)
- MIT/Apache license (compatible with VIF)

### Step 3: Factor Generation Analysis
For top 3 repos:
- Extract `_NON_EQUITY_EXCLUDE` equivalents (repo-specific ticker filters)
- Document indicator computation methods
- Compare to VIF's current RSI/MACD/BB approach
- Identify 2-3 novel factors for integration

---

## Phase 3: Validation & Integration Decision

### Confidence Boost Criteria
If external research confirms VIF's gamma regime logic:
- Increase confidence by +5 points (max cap: 95)
- Add note: "[Validated by {paper_title}, {year}]"
- Store paper link in signal metadata for audit trail

### Conflict Resolution
If external repo contradicts VIF signal:
- Flag for critic agent review
- Downgrade confidence by -10 points (min floor: 30)
- Add note: "[Conflicts with {repo_name}/{issue_number}]"

---

## Integration Points

### 1. Critic Agent (`swarm/critic_agent.py`)
- Call `external_alpha_audit()` when VIF signal confidence < 55%
- Fetch relevant papers + repo implementations
- Return override recommendation: "UPGRADE", "DOWNGRADE", "VETO", "HOLD"

### 2. VIF Analyst (`swarm/native_vif_analyst_agent.py`)
- Store paper link + repo URL in signal metadata
- Enable future backtesting against historical research claims

### 3. Risk Agent (`swarm/risk_agent.py`)
- If conflict detected, add to LATS risk mitigation scenario
- Example: "Research contradicts trend signal → increase stop loss by 1 ATR"

---

## Cost & Token Efficiency

| Operation | Cost | Frequency |
|-----------|------|-----------|
| Paper search (HF MCP) | ~100 tokens | Per ambiguous signal (~2-3/week) |
| Repo discovery (GitHub MCP) | ~50 tokens | Per paper found (~1-2/month) |
| Factor comparison (local) | ~200 tokens | On-demand, cached 30 days |
| **Monthly total** | **~500 tokens** | **Low overhead** |

---

## Skill Activation Flowchart

```
VIF Analyst generates signal
    ↓
Confidence < 55% OR Gamma regime transition?
    ├─ YES → Critic calls external_alpha_audit()
    │         ├─ Search papers (HF MCP)
    │         ├─ Find repos (GitHub MCP)
    │         ├─ Extract factors
    │         └─ Return confidence adjustment
    │
    └─ NO → Pass signal downstream (normal flow)
```

---

## File Locations

- **Papers database:** `data/external_papers_cache.json` (auto-refreshed monthly)
- **Repository catalog:** `data/external_repos_catalog.json` (cached, indexed by factor type)
- **Validation audit trail:** `reports/alpha_audit_trail_{date}.json`

---

## Disclaimer

External repositories and papers are **informational only**. VIF's final signal remains independent and is governed by the framework's kill switches (K1-K6) and circuit breaker (-5% drawdown rule). No external source overrides the structural risk management layer.
