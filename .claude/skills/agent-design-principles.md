---
name: agent-design-principles
description: >
  Reference when designing, debugging, or evaluating any VIF agent or subagent.
  Use when the user asks: "which pattern should I use?", "why is this agent failing?",
  "how should orchestrator delegate?", "is this the right tool design?", or
  "how do we test agents?" Implements Anthropic's December 2024 canonical guidance,
  mapped to VIF system components. Invoke with /agent-design-principles.
---
# Skill: Agent Design Principles
<!-- Source: Anthropic Engineering Blog — "Building Effective Agents", Dec 19 2024 -->
<!-- Authors: Erik S. and Barry Zhang -->
<!-- Mapped to VIF Trading System by Claude Code, May 2026 -->

## Core Rule: Simple > Complex

> "The most successful agent implementations use simple, composable patterns rather than complex frameworks."

Start with the simplest pattern that works. Add complexity **only** when it demonstrably improves outcomes. This is why VIF uses direct subprocess delegation before adding Claude-to-Claude agent chaining.

---

## When to Use Agents vs Workflows

| | Workflow | Agent |
|---|---|---|
| **Control** | Predefined code paths | LLM directs its own process |
| **Best for** | Fixed-sequence, deterministic tasks | Open-ended, unpredictable tasks |
| **VIF examples** | `schedule_daily.py` cron jobs | `orchestrator-coordinator` delegating to subagents |

**Use an agent when:**
- Steps can't be hardcoded in advance
- Multi-turn adaptive decision-making is needed
- Clear success criteria exist (e.g., signals generated, report produced)

**Don't use an agent when:**
- Latency is critical (agents cost more time)
- A single LLM call with retrieval suffices
- Task is fully deterministic

---

## The 7 Agentic Patterns (VIF Mappings)

### 1. Augmented LLM
**What:** LLM + retrieval + tools + memory  
**VIF:** Every agent call in `watchlist_watcher.py` — Claude + yfinance + indicators + cache  
**Principle:** Tailor augmentations to the specific use case; use MCP for third-party tools

### 2. Prompt Chaining
**What:** Decompose task → each LLM call processes previous output  
**VIF:** catalyst-monitor → vif-analyst → swing-screener (K4 flags feed into signals, signals feed into screener)  
**Use when:** Fixed subtasks that can be cleanly decomposed

### 3. Routing
**What:** Classify input → direct to specialized follow-up  
**VIF:** `categorize_ticker_complexity()` in `watchlist_watcher.py` — routes simple tickers to Haiku, complex to Sonnet  
**Use when:** Distinct categories need different handling, classification is reliable

### 4. Parallelization
**Subtypes:** Sectioning (independent parallel tasks) / Voting (same task multiple times)  
**VIF opportunity:** Multiple watchlists (`vantage_portfolio`, `ai_verticals`, `energy_ai`) can run in parallel instead of sequential — current gap  
**Use when:** Speed optimization needed, tasks are independent

### 5. Orchestrator-Workers ← **VIF Primary Pattern**
**What:** Central LLM breaks down tasks → delegates to worker LLMs → synthesizes results  
**VIF:** `orchestrator-coordinator` → [catalyst-monitor, vif-analyst, swing-screener, report-builder]  
**Use when:** Cannot predict subtasks upfront, flexibility > predictability

### 6. Evaluator-Optimizer
**What:** LLM generates → another LLM evaluates and provides feedback (loop)  
**VIF:** Not yet implemented. Opportunity: one Claude call generates signals, second validates kill switch logic  
**Use when:** Clear evaluation criteria exist, iterative refinement measurably improves output

### 7. Autonomous Agents
**What:** Plan and operate independently, return to human for judgment  
**VIF:** `weekend-catalyst-analyst` running Saturday/Sunday with WebSearch supplements  
**Use when:** Open-ended problems, cannot hardcode paths, trust model decision-making

---

## ⚠️ CRITICAL: Ground Truth from Environment

> "During execution, it is crucial for agents to gain 'ground truth' from the environment at each step (such as tool call results or code execution) to assess its progress."

**Never chain assumptions. Always verify with actual tool results.**

| Anti-pattern | Ground-truth pattern |
|---|---|
| Assume previous agent succeeded | Check `result["success"]` before proceeding |
| Infer indicator values from memory | Call `fetch_and_compute()`, verify output |
| Assume JSON parsed correctly | Validate schema before passing downstream |
| Continue pipeline on silent failure | Log failure, surface in post-run summary |

**VIF implementation:**
```python
# Every agent call MUST check ground truth:
result = run_agent(label, cmd, timeout=600)
if not result["success"]:
    logger.error(f"{label} failed – continuing pipeline")
    # Log, don't abort. Collect real failure state.
```

**Why this matters for VIF:**
1. **Prevents hallucination loops** — K4 flags must come from actual catalyst-monitor output, not inference
2. **Stops assumption drift** — vif-analyst must read real OHLCV data, not cached assumptions
3. **Enables recovery** — humans can intercept when orchestrator reports actual failures, not assumed success

---

## Tool Design (ACI Principles)

> "Tool documentation and testing must be prioritized equally with overall prompts."

**Format rules:**
1. Give the model tokens to "think" before committing to an action
2. Keep format close to natural text — minimize JSON overhead where possible
3. Avoid forcing model to count thousands of lines or excessive escaping

**Documentation rules:**
- Include example usage, edge cases, input requirements, boundaries
- Test with many inputs in workbench before deploying
- **Poka-yoke:** Make arguments harder to misuse

**VIF example:**
```bash
# BAD: relative paths let model get confused
python agents/watchlist_watcher.py --watchlist ./vantage_portfolio

# GOOD: absolute paths eliminate ambiguity (Anthropic: "switching to absolute paths improved performance to flawless execution")
python agents/watchlist_watcher.py --watchlist vantage_portfolio  # resolved internally to absolute
```

**When designing a new VIF tool/agent:**
- [ ] Does the tool description include what it DOESN'T do?
- [ ] Are all paths absolute or reliably resolved?
- [ ] Is the output schema documented with a concrete example?
- [ ] Does it return failure info, not just success info?

---

## Production Deployment Checklist

Per Anthropic guidance, every VIF agent in production must have:

- [ ] **Sandboxed testing** — `python tests/test_harness.py` before live runs
- [ ] **Appropriate guardrails** — `.claude/hooks/guard-live-trades.sh` (already implemented)
- [ ] **Correct failure assumptions** — no agent silently succeeds when it actually failed
- [ ] **Continuous measurement** — `scripts/check_usage.py`, `logs/run_history.json`

---

## Evaluation Framework (Appendix 2 Pattern)

When testing a new VIF agent:

1. **Generate tasks grounded in real use** — use actual watchlist tickers, not toy examples
2. **Use realistic data** — yfinance OHLCV, not hardcoded mock prices
3. **Pair each task with verifiable outcome** — known signal for known market condition
4. **Avoid overly strict verifiers** — accept "BUY" and "STRONG_BUY" as equivalent pass
5. **Run programmatically** — `while-loop + LLM/tool alternation`, check pass rate

**Avoid:**
- Oversimplified sandbox environments (mock data hides real failures)
- Overfitting to one strategy (multiple valid paths exist for VIF signals)

---

## Pattern Selection Guide (Quick Reference)

```
User asks for: "run premarket analysis"
→ Prompt Chaining (fixed sequence: catalyst → vif → screener → report)

User asks for: "why did NVDA get a BUY signal?"
→ Augmented LLM (market-researcher + tools + cached reports)

User asks for: "screen all 3 watchlists simultaneously"
→ Parallelization / Sectioning (independent watchlists, merge results)

User asks for: "improve my signal quality"
→ Evaluator-Optimizer (generate signals → evaluate vs kill switches → refine)

User asks for: "run weekend briefing autonomously"
→ Autonomous Agent (weekend-catalyst-analyst + WebSearch, self-directed)

User asks for: "route this ticker to the right model"
→ Routing (categorize_ticker_complexity → Haiku or Sonnet)
```

---

## Anti-Patterns to Avoid

**Anthropic explicitly warns against:**

| Anti-pattern | VIF Risk | Mitigation |
|---|---|---|
| Jump to frameworks first | Adding LangChain/CrewAI before understanding what's needed | Use direct API calls (already doing this) |
| Abstract away underlying logic | Hidden prompts break debugging | All agent prompts visible in `.claude/agents/` |
| Complex agent design upfront | Over-engineering week 1 | Add subagents only when subprocess delegation hits limits |
| Skip evaluation | Deploying agents without test harness | Run `test_harness.py` before new agent goes to schedule |

---

## References

- **Anthropic source:** https://www.anthropic.com/engineering/building-effective-agents
- **Claude Agent SDK:** https://platform.claude.com/docs/en/agent-sdk/overview
- **Cookbook:** https://platform.claude.com/cookbook/patterns-agents-basic-workflows
- **Related VIF skill:** `/orchestrating-pipelines` — pipeline execution patterns
- **Related VIF skill:** `/analyzing-vif-signals` — signal generation patterns
