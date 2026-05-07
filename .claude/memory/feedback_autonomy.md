---
name: Autonomy & Decision-Making Preference
description: User wants autonomous execution with minimal checkpoints — only escalate genuine forks or unknowns
type: feedback
originSessionId: 275d482b-9bda-41df-ac22-0d73fa9237a0
---
Execute fully and autonomously on all minor decisions (categorization, deduplication, ordering, formatting, metadata generation). Do not stop at intermediate checkpoints or ask for approval on low-stakes choices.

**Why:** User explicitly said "I only want to be inquired about big decisions or scenarios you are unsure of." Excessive checkpoints waste time and interrupt flow.

**How to apply:**
- Build, write, and deliver final outputs in one pass
- Only pause when a decision is irreversible AND genuinely ambiguous (e.g., deleting data that can't be recovered, conflicting instructions with no clear winner)
- For duplicate/categorization/tier decisions: use best judgment and document the rationale in output
- For agent delegation: if a task is purely mechanical and fits an existing agent pattern, delegate without asking
