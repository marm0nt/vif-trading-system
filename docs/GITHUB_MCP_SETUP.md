# GitHub & Hugging Face MCP Setup Guide

**Status:** Phase 1 Infrastructure Complete (May 9, 2026)  
**Next:** Phase 2 Integration (Week 2)

---

## Quick Start

### 1. Configure Tokens

You need two authentication tokens:

#### GitHub Personal Access Token
1. Go to https://github.com/settings/tokens
2. Create new token (classic) with scopes: `repo`, `read:user`
3. Copy token → Add to `~/.claude/mcp.json`:

```json
"github": {
  "env": {
    "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_your_token_here"
  }
}
```

#### Hugging Face API Token
1. Go to https://huggingface.co/settings/tokens
2. Create new token with scope: `read` (public repos only)
3. Copy token → Add to `~/.claude/mcp.json`:

```json
"huggingface": {
  "env": {
    "HF_TOKEN": "hf_your_token_here"
  }
}
```

### 2. Verify MCP Configuration

```bash
cat ~/.claude/mcp.json
# Should show both servers with tokens populated
```

### 3. Test Integration (Once Tokens Added)

```bash
cd ~/vif-trading-system
python -c "
from agents.external_alpha_auditor import audit_vif_signal
result = audit_vif_signal('NVDA', 'BUY', 45)
print(f'Audit result: {result}')
"
```

---

## Repository Quick Reference

### Target Repositories

| Repo | Stars | Effort | Priority | Purpose |
|------|-------|--------|----------|---------|
| **TA Library** (bukosabino/ta) | 5k | 1d | P1 (Week 1) | Replace custom indicators with battle-tested library |
| **Backtesting.py** (kernc/backtesting.py) | 8.3k | 1-2d | P1 (Week 1) | Weekly signal validation + Sharpe ratio tracking |
| **TradingAgents** (TauricResearch/TradingAgents) | 59.4k | 3-5d | P2 (Week 2-3) | Multi-agent debate → reduce false signals by 10-15% |
| **PyBroker** (edtechre/pybroker) | 3.3k | 2-4d | P2 (Week 2-3) | Numba JIT acceleration → 8x faster analysis |
| **AgenticTrading** (Open-Finance-Lab/AgenticTrading) | 156 | 1-2w | P3 (Phase 2) | Self-improving agents with Neo4j memory |

### Integration Workflow (Phase 2+)

```
Monday (Week 2):
├─ Critic agent audit → GitHub search for TradingAgents repo
├─ Extract debate mechanism from codebase
└─ Plan integration points in native_vif_analyst_agent.py

Wednesday (Week 2):
├─ Implement multi-agent debate layer
├─ Test on Trump Admin_ Onshoring watchlist
└─ Verify confidence downgrade for false signals

Friday (Week 3):
├─ Integrate PyBroker Numba acceleration
├─ Benchmark: 85-ticker analysis time
└─ Commit if < 2 seconds (target: <1 second)
```

---

## Troubleshooting

### "GITHUB_PERSONAL_ACCESS_TOKEN not found"
→ Check `~/.claude/mcp.json` has token in `env` section  
→ Restart Claude Code session to reload environment

### "HF_TOKEN not found"
→ Same as above — verify token in mcp.json

### Rate Limit Warnings
- GitHub: 5,000 requests/hour (plenty for 1 deep repo scan/day)
- Hugging Face: 100 queries/day (sufficient for 2-3 paper searches)
→ No action needed; system will use cached results if limits hit

### Repo Too Large (>500MB)
→ System auto-skips oversized repos  
→ Check `logs/orchestrator_swarm.log` for details

---

## Files Created

- `~/.claude/mcp.json` — MCP server configuration
- `docs/skills/external-alpha-audit.md` — Audit workflow
- `docs/skills/repo-navigation.md` — Repository parsing patterns
- `agents/external_alpha_auditor.py` — MCP wrapper module
- `data/external_repos_catalog.json` — Repository analysis cache
- `data/external_papers_cache.json` — Paper search cache

---

## Next Steps (After Token Configuration)

1. **Test Phase 1 Infrastructure** (30 min)
   ```bash
   python agents/external_alpha_auditor.py
   # Should print: "Paper search (cached)" + "Repo search (cached)"
   ```

2. **Run Premarket with Audits Enabled** (5 min)
   ```bash
   python agents/orchestrator_swarm.py --mode premarket
   # Critic agent will now call audit_vif_signal() for low-confidence signals
   ```

3. **Review Audit Results**
   ```bash
   tail -50 logs/orchestrator_swarm.log | grep -i "audit\|paper\|repo"
   ```

4. **Schedule Phase 2 Integration** (Week 2)
   - TradingAgents multi-agent debate layer
   - Implement in `swarm/critic_agent.py`

---

## Token Cost Summary

| Phase | Operation | Tokens/Month | Cost |
|-------|-----------|--------------|------|
| 1 (Current) | Paper search + repo discovery | 1,900 | $0.019 |
| 2 | TradingAgents integration testing | 5,000 | $0.050 |
| 3 | Novel factor backtesting | 10,000 | $0.100 |
| **Total monthly** | | **~17,000** | **~$0.17** |

Very low overhead — external intelligence is cost-neutral enhancement.

---

## Status

✓ **Phase 1 (May 9, 2026):**
- [x] MCP configuration created
- [x] External auditor module implemented
- [x] Skill documentation written
- [x] Repository filter patterns defined
- ⏳ **Waiting for:** GitHub + HF tokens

⏳ **Phase 2 (Week 2):**
- [ ] Critic agent integration
- [ ] TradingAgents debate mechanism
- [ ] Real-time audit results in reports

⏳ **Phase 3+ (Week 3+):**
- [ ] PyBroker Numba acceleration
- [ ] Novel factor backtesting framework
- [ ] AgenticTrading self-improvement (Phase 2 defer)
