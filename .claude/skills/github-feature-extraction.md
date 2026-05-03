---
name: github-feature-extraction
description: End-to-end workflow for discovering, evaluating, extracting, and integrating features from GitHub agentic projects into the VIF Trading System. Trigger when user says "extract from this repo", "find improvements on GitHub", "run the extraction workflow", or "scan and integrate from GitHub".
---

# Skill: GitHub Agentic Feature Extraction

## When to use
- User provides a GitHub repo URL to evaluate
- User asks to find improvements for a specific VIF component
- User wants to research how other projects handle a problem (catalyst scanning, signal generation, reporting)
- Diagnostic identified a weak component and needs external inspiration

## When NOT to use
- User just wants to edit an existing file directly
- The improvement is obvious from code review (no external research needed)
- The repo is already known and the feature already extracted

---

## The 5-Phase Workflow

### Phase 1 — Discover
Delegate to **repo-scanner** subagent:
```
Input: GitHub URL or "find repos for [topic]"
Output: Structured feature inventory with reuse_score
Skip repos with: reuse_score < 5, last_commit > 6 months, no agent separation
```

### Phase 2 — Evaluate  
Apply the 4-question filter before extracting anything:
1. Does this solve a problem the VIF system has RIGHT NOW?
2. Is the core logic < 200 lines when stripped of scaffolding?
3. Can I describe what it does in one sentence?
4. Does it require dependencies not already in requirements.txt?

If any answer is NO → skip or note for future.

### Phase 3 — Extract
Delegate to **feature-extractor** subagent:
```
Input: Target file from repo-scanner result
Output: prompt, input_contract, output_contract, coupling_score
Key rule: The prompt IS the logic. Discard everything else.
```

### Phase 4 — Map
Delegate to **integration-planner** subagent:
```
Input: feature-extractor result + VIF system context
Output: target_file, pipeline_slot, integration_steps, test_command
Decision tree:
  Prompt pattern only → .claude/skills/
  Autonomous worker   → .claude/agents/ or scripts/
  Replaces existing   → Edit existing file (no duplication)
  Sequences agents    → orchestrator.py PIPELINES
```

### Phase 5 — Implement
Follow integration-planner output exactly:
1. Run offline test first (no API spend)
2. Wire into ONE pipeline mode only
3. Run one full pipeline manually
4. Check HTML report for regression
5. Only then add to schedule_daily.py

---

## Output to user
After completing all 5 phases, summarize:
- What was found in the repo
- What was extracted (prompt/pattern/full agent)
- Where it was integrated in the VIF system
- Test command to verify
- Token cost impact estimate

---

## Quick reference — mapping decision
| Feature type | Maps to |
|---|---|
| Prompt reasoning pattern | Update existing skill or create .claude/skills/ |
| Standalone analysis agent | .claude/agents/ + scripts/ |
| Replaces broken/static script | Edit existing scripts/ file |
| External API capability | utils/ wrapper + MCP if needed |
| Pipeline sequencing logic | orchestrator.py PIPELINES dict |
