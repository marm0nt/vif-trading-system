---
name: Orchestrator-Coordinator Framework (May 2026)
description: Core operational framework for VIF trading system pipeline execution; governs all agent orchestration and report generation
type: feedback
originSessionId: bd97578a-725c-4697-8b30-9f925717ecce
---
## Framework Authority
**Status:** ACTIVE  
**Scope:** All pipeline work where complexity justifies structured reasoning  
**Override:** User has explicit veto on implementation; I apply judgment otherwise  

## Execution Cycle (Mandatory Structure)
All orchestrator-coordinator tasks follow:

```
<thinking>
1. Decompose request (Tree of Thoughts)
2. Establish Master Plan & collapse branches
3. Map sub-agents + Least Privilege context
4. Verify bash whitelist compliance
</thinking>

<action>
[Execute A2A JSON + Sandboxed Bash]
</action>
```

## Topological Delegation
- **Hierarchy:** Centralized orchestrator with fan-out sub-agents
- **Token Conservation:** Linear execution after ToT collapse
- **Context Restriction:** Never pass full workspace; send only relevant AST/JSON/README snippets
- **Sub-Agent Pattern:** ReAct loops with structured state handoff

## Communication Standards

### Agent-to-Agent (A2A)
- Format: **Strict JSON Schema** (no conversational filler)
- Transport: JSON files in `/workspace/reports/` or structured subprocess payloads
- Handoff: Each agent outputs state JSON for next agent to consume

### Human-Facing Reports  
- Format: **Anthropic-optimized XML tags** (`<executive_summary>`, `<blockers>`, `<metrics>`, `<recommendations>`)
- Structure: Designed for parsing reliability + human readability
- Deployment: HTML rendering of XML when visual presentation needed

## Security & Sandboxing
**Boundary:** Docker sandbox, read-only root, write-only in `/workspace`  
**Whitelist:** `mkdir`, `touch`, `cp`, `mv`, `sed`, `grep`, `git`  
**Blacklist:** `curl`, `wget`, `sudo`, destructive ops (e.g., `rm -rf`)  
**Pre-flight:** Always verify file state before modification (read-only reconnaissance)

## Traceability Protocol (AgentTrace Standard)
1. **OTel Spans:** Log all tool-use + sub-agent dispatch as JSONL in `/workspace/logs/otel/`
2. **Git Commits:** Format as `[Agent-ID] <type>(<scope>): <subject>`
   - Body must include: `Trace-ID: <UUID>` and `Parent-Prompt-Hash: <SHA>`
3. **Audit Trail:** Cryptographic linkage of agentic decisions to prompts

## Template Workflows & Reusability
**Goal:** Pre-built templates for recurring patterns eliminate reinvention

**Current Templates (To Be Created):**
- `template_watchlist_analysis.json` — Config + agent dispatch pattern for any watchlist
- `template_catalyst_scan.json` — Macro event + earnings detection workflow
- `template_swing_screener.json` — 5-setup ranking + R:R calculation
- `template_vif_master_report.json` — Consolidation + XML generation

**Future Protocol:** When similar task appears, reference template + customize payload

## Agent-Council Pattern
**When to Invoke:** Controversial decisions, high-stakes signal generation, conflicting analysis  
**Pattern:**
1. Dispatch multiple agents independently (no cross-talk)
2. Collect reasoning + conclusions in JSON
3. Synthesize as orchestrator (not majority vote—weighted by methodology rigor)
4. Commit direction + reasoning to Git/OTel

**Example:** If QXO signal confidence differs between agents, council resolves via evidence hierarchy (gamma regime > RSI > volume)

## Daily VIF Report Specifics
**Current:** VIF_DAILY_MASTER_REPORT_20260508.html (generated without framework)  
**Future:** All subsequent daily reports use full framework:
- Orchestrator decomposes 6-watchlist analysis (ToT)
- Fan 6 independent VIF analysts + catalyst monitor + swing screener
- Collect A2A JSON state from each
- Consolidate into XML report + render as HTML
- Commit with Trace-ID linking all agent outputs

---

**Why:** User wants observable, reproducible, auditable pipeline. This framework provides determinism + traceability + council oversight + reusability.

**User Intent:** "Agents should work as a team and a council"—structured reasoning > individual agent > human intuition for complex trading decisions.
