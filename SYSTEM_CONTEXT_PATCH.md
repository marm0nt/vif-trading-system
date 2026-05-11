# docs/SYSTEM_CONTEXT.md — Update Patch (May 11, 2026)

**File is currently locked (likely open in editor). Apply this patch by:**
1. Closing the file in all editors
2. Running: `git checkout docs/SYSTEM_CONTEXT.md` to reset
3. Then reapply the updates listed below

---

## Changes Required

### 1. Add New Agents to Section 3 (after `orchestrator.py`)

```markdown
| `orchestrator_swarm.py` | **Phase 3:** Swarm-based orchestration (LRAgent + LatentMAS routing) | Phase 3 integration replaces orchestrator.py | **YES** — Next-gen coordinator |
| `finviz_screener_agent.py` | **Phase 3:** FinViz Discovery Screener (19 custom screeners, independent mode) | `schedule_daily.py` 07:30 | **YES** — Institutional discovery |
| `finviz_orchestrator_coordinator.py` | **Phase 3:** FinViz swarm integration (manages screener as subagent) | orchestrator_swarm finviz_screen pipeline | YES — Swarm routing |
| `external_alpha_auditor.py` | **Phase 4.5:** GitHub + HF MCP wrapper (validates low-confidence signals) | Critic agent when confidence < 55% | Soft — Enhancement layer |
```

### 2. Insert New Section 4.5 (Before "## 5. Pipeline Flow")

```markdown
---

## 4.5. Swarm Intelligence Framework (Phase 3, In Development)

**Status:** Infrastructure deployed (May 9, 2026), Phase 3 integration pending.

| Component | Purpose | Status |
|-----------|---------|--------|
| `swarm/orchestrator.py` | Master swarm coordinator (LRAgent + LatentMAS) | Phase 2 complete |
| `swarm/vif_analyst_agent.py` | Specialist VIF analysis agent | Phase 2 complete |
| `swarm/catalyst_monitor_agent.py` | Specialist catalyst monitoring agent | Phase 2 complete |
| `swarm/swing_screener_agent.py` | Specialist swing setup screener agent | Phase 2 complete |
| `swarm/critic_agent.py` | **Validation + Munger Inversion audit** | Phase 2 complete |
| `swarm/risk_agent.py` | Risk assessment specialist | Phase 2 complete |
| `swarm/specialist_agent.py` | Base specialist agent class | Phase 1 complete |
| `swarm/kv_cache_manager.py` | State persistence (LRAgent KV cache) | Phase 1 complete |
| `swarm/latent_memory.py` | LatentMAS distributed memory | Phase 1 complete |
| `swarm/gossip_router.py` | Inter-agent gossip protocol | Phase 1 complete |
| `swarm/consensus.py` | Consensus decision logic | Phase 1 complete |
| `swarm/smolagents_bridge.py` | smolagents framework integration | Phase 1 complete |

**Key Advancement (May 10):** Critic agent now performs Munger Inversion audit on all signals (identify what could break the thesis, not just confirm). Boosts low-confidence signal analysis.
```

### 3. Update Daily Premarket Schedule

Replace:
```
07:00  catalyst_analysis.py
       └─ Fetches earnings, news, K4 kill switches
       
08:45  orchestrator.py --mode premarket
```

With:
```
07:00  catalyst_analysis.py
       └─ Fetches earnings, news, K4 kill switches

07:30  finviz_screener_agent.py (Phase 3)
       ├─ Runs 19 custom screeners
       ├─ Institutional discovery (independent of VIF watchlists)
       └─ Outputs JSON to reports/catalysts/
       
08:45  orchestrator.py --mode premarket
```

### 4. Update Skills in Section 2

Replace:
```markdown
| `agent-design-principles.md` | Anthropic agentic patterns mapped to VIF (7 pattern types, production checklist) | Annual |
```

With:
```markdown
| `agent-design-principles.md` | Anthropic agentic patterns mapped to VIF (7 pattern types, production checklist) | Annual |
| `finviz-custom-screeners.md` | **NEW (May 2026):** 19 FinViz screener configurations + factor mappings | Quarterly |
| `external-alpha-audit.md` | **NEW (May 2026):** GitHub + HF research audit workflow (Phase 4.5) | Quarterly |
| `repo-navigation.md` | **NEW (May 2026):** GitHub repo parsing patterns for factor extraction | As needed |
```

### 5. Update Timestamp

At the top of the file, add:
```markdown
**Last updated:** 2026-05-11
```

---

## Status

✅ Parts 1 & 2 (Hook + Script) — **COMPLETE**
⏳ Part 3 (SYSTEM_CONTEXT.md) — **BLOCKED BY FILE LOCK** (apply patch manually when file is unlocked)

**To proceed:** Close the file in all editors, then apply the changes above.
