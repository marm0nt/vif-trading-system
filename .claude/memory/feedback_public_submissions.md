---
name: Public submission protocol
description: User must approve all public repos/submissions; Martin is sole author, never "Agent" or "AI"
type: feedback
originSessionId: bac8b4cd-87f1-42f0-897f-c9b6288f7171
---
**Rule: All public submissions require explicit permission and Martin's authorship.**

**Why:** Martin created this system and owns the IP. Any public-facing work (GitHub repos, published skills, documentation) must have Martin listed as author/creator, never Claude, Agent, or AI. Martin wants control over how the VIF system is represented publicly.

**How to apply:**
1. When an agent needs to submit something to public (GitHub, package registry, shared skills marketplace, etc.) → **STOP and ask Martin for permission first**
2. In the request, clearly state:
   - What is being submitted
   - Where it's being submitted (GitHub public/private, PyPI, Skills marketplace, etc.)
   - Draft of the author/attribution
3. Once permission granted:
   - Always list "Author: Martin" or "Created by Martin" (not "by Claude Code Agent")
   - If multiple contributors, Martin is primary; agents are listed as "with assistance from Claude Code"
   - Do NOT push/publish until Martin explicitly confirms

**Examples:**
- ❌ "Created by: Claude Code Agent" → ✓ "Created by: Martin"
- ❌ Auto-submit to PyPI → ✓ Ask first, then submit with Martin as author
- ❌ Fork/mirror to GitHub public → ✓ Ask first, then create with Martin as owner

This applies even if agents have pre-approval for other operations — public submissions always require fresh permission.
