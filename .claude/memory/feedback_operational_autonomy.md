---
name: Operational Autonomy & Lead Orchestrator
description: Martin's policy for system operation when he's unavailable. Agents execute autonomously without approval. Swarm orchestrator leads all workflows. Global permission bypass enabled.
type: feedback
---

# Operational Autonomy Policy (2026-05-13)

## Core Rules

**Martin's decision:** Agents operate autonomously without approval/permission checks.

### Rule 1: Keep Scheduled Tasks Active
- Daily jobs stay running (scheduler.py on desktop)
- Workflows execute on their cron schedule
- Do NOT stop, pause, or disable scheduled execution
- If a job fails, repair-subagent fixes it automatically, no human approval needed

**Why:** Trading signals have time-sensitive value. Delay = lost opportunity.

### Rule 1b: Scheduled Tasks Use Sonnet 4.6 Only
- **Daily scans** → Sonnet 4.6 (analysis quality matters for trading signals)
- **Scheduled workflows** → Sonnet 4.6 (consistent decision-making)
- **Sentry-monitor** (diagnostic agent) → Still Haiku (pattern matching is cheap)
- **Repair-subagent** (code fixes) → Still Sonnet 4.6 (complex logic)

**Why:** Trading signal quality = revenue impact. Use the best model, always. Haiku is only for parsing/diagnostics that don't feed trading decisions.

### Rule 2: Lead Swarm Orchestrator is Entry Point
- **orchestrator_lead.py** or **orchestrator-coordinator** agent is the master controller
- ALL multi-agent work flows through it
- It sequences: catalyst-monitor → vif-analyst → swing-trade-screener → report-builder
- It decides which agents to dispatch based on market mode (premarket/market-open/afterhours/weekend)

**Why:** Single orchestration point prevents race conditions and duplicate work.

### Rule 3: Agents Are Martin's Replacement
- When Martin is away/unavailable, agents make decisions autonomously
- sentry-monitor detects errors → repair-subagent fixes them (no human approval)
- vif-analyst generates signals → report-builder publishes them (no human gate)
- Agents commit + push fixes automatically (auto-push hook handles it)

**Why:** Real-time market requires real-time decisions. Waiting for human approval breaks the trading thesis.

### Rule 4: Bypass Permissions Globally
- Claude Code permission prompts should NOT block execution
- Agent tool use (Read, Edit, Bash, Write, Grep) proceeds without asking
- Git push/commit happens silently
- No user confirmation needed for standard operations

**How:** Set `.claude/settings.json` to `bypassPermissions: true` for this project (or globally if configured).

**Exceptions (NEVER bypass):**
- Do not delete git branches or force-push
- Do not modify `.env` or write secrets to git
- Do not make external API calls outside the VIF framework (no random web requests)
- Do not modify user's other projects (stay in vif-trading-system scope)

### Rule 5: Don't Break Anything
- Maintain system integrity at all times
- If uncertain, ask in memory (not user)
- Use surgical fixes, not large refactors
- Test before committing (run test_harness.py for offline smoke test)
- Monitor logs for cascading failures

**How to stay safe:**
- Repair-subagent uses minimal 1-3 line fixes only
- Sentry-monitor escalates unknown errors (doesn't guess)
- Orchestrator validates signal quality before publishing
- All edits are committed separately (easy to revert)

---

## What This Means in Practice

### Scenario: Market Opens, Sentry Detects ImportError
```
10:00 AM: sentry-monitor finds error in orchestrator_swarm.py
10:01 AM: repair-subagent diagnoses → applies fix → commits → auto-pushes
10:02 AM: Premarket VIF signals publish automatically (no human waiting)
→ Martin gets notification of fix, but work never stopped
```

### Scenario: Scheduler Job Fails
```
16:05 PM: After-hours job fails to run
16:06 PM: sentry-monitor detects missing agents
16:07 PM: repair-subagent installs dependency → commits fix
16:08 PM: Next scheduled job (tomorrow 07:00) runs successfully
→ No manual restart needed
```

### Scenario: User Away on Vacation
```
Morning: Catalyst-monitor runs → finds macro events
Afternoon: VIF-analyst generates signals
Evening: Report-builder publishes to reports/
All without Martin's involvement
→ System self-heals if something breaks mid-day
```

---

## Configuration Checklist

- [ ] `.claude/settings.json` has `bypassPermissions: true` for this project
- [ ] `.claude/hooks/post-commit-sync.sh` is active (auto-push)
- [ ] `schedule_daily.py` (or scheduler) running on desktop
- [ ] Sentry-monitor + repair-subagent deployed in `.claude/agents/`
- [ ] Orchestrator-coordinator is the primary agent for multi-step work
- [ ] Memory files loaded automatically on each session start

---

## How to Escalate (if agent is truly stuck)

If an agent cannot decide and needs human input:
1. Write a decision point to `.claude/memory/` with tagged `[DECISION_NEEDED]`
2. Next Claude Code session (or user) reads this memory
3. Martin adds the decision to memory or updates the agent rule
4. Agent proceeds with updated guidance

Example:
```
[DECISION_NEEDED] Should we short-circuit the VIF kill switch K4 (earnings risk) 
if the move is 8%+ in our favor? Current rule: always apply K4. 
Safety vs. upside trade-off. Guidance needed.
```

---

## Monitoring & Alerts

- Sentry-monitor logs to `logs/sentry-reports.log`
- Repair-subagent logs to `logs/sentry-repair-{timestamp}.log`
- Orchestrator logs all agent delegation to `logs/orchestrator.log`
- run_history.json tracks success/failure of each scheduled job

Martin can check these at any time to see what happened while he was away.

---

## Scope: VIF Trading System Only

This autonomy policy applies **ONLY** to the vif-trading-system project and its agents.

Does NOT apply to:
- Other git repos
- System-wide changes (install software, modify OS)
- Outside API calls (don't call random third-party services)
- User's machine (don't reconfigure VSCode, terminal, etc.)

---

## Last Updated
2026-05-13 by Martin A. — operational autonomy mode enabled.
