# Meta-Tools Usage Guide

These tools are for **project maintenance**, not trading signal generation. They run on-demand, never in the daily schedule.

---

## 1. File Organizer Skill

**Purpose:** Clean up, organize, find duplicates in any directory.

**Quick Start:**
```
In Claude Code, type:
"Organize my scripts/ directory, group by function (analysis vs utility), remove duplicates"
```

**What It Does:**
- Analyzes current structure
- Detects duplicate files by hash
- Proposes logical groupings
- Moves files with confirmation at each step
- Logs all changes for reversal

**Best For:**
- `scripts/` cleanup (lots of one-off utilities)
- `reports/` organization (old analysis files)
- `data/` archival (old watchlist snapshots, cache files)
- `docs/` consolidation (merge redundant documentation)

**When NOT to Use:**
- ❌ Don't run on `.claude/`, `agents/`, `watchlists/` (production directories)
- ❌ Don't auto-delete without reviewing (always approve before moves)
- ❌ Don't organize while schedule_daily.py is running

**Example Workflow:**
```
You: "Clean up scripts/ directory. Separate:
- Active pipelines: orchestrator.py, watchlist_watcher.py, catalyst_analysis.py, swing_trade_screener_v2.py
- Meta tools: (everything in scripts/meta_tools/)
- Utilities: everything else
Mark old/unused scripts for archive/"

File-Organizer:
1. Analyzes scripts/ (finds 15 files, 8 are duplicates or old)
2. Detects 3 old scripts unused for 6+ months
3. Proposes structure:
   - scripts/active/
   - scripts/meta_tools/
   - scripts/archive/
   - scripts/utils/
4. Asks for confirmation on each move
5. Logs all moves to .organization-log.txt
```

---

## 2. Skill Creator Skill

**Purpose:** Create new Claude skills following best practices.

**Quick Start:**
```
python scripts/meta_tools/skill-creator/init_skill.py my-new-skill --path .claude/skills/
```

**6-Step Process:**
1. **Understand** - Gather concrete examples of how the skill will be used
2. **Plan** - Identify reusable scripts, references, assets
3. **Initialize** - Run init_skill.py to generate template
4. **Edit** - Complete SKILL.md and add bundled resources
5. **Package** - Run package_skill.py to validate and zip
6. **Iterate** - Refine based on real-world usage

**Best For:**
- Creating domain-specific skills (e.g., a "earnings-analysis" skill)
- Documenting reusable workflows (e.g., a "portfolio-rebalancing" skill)
- Packaging analysis processes for team sharing
- Extending .claude/skills/ directory with specialized tools

**Example: Create an Earnings Analysis Skill**
```
Step 1: Understand
- Skill extracts earnings surprises, tracks consensus estimates vs actual
- Triggers when user asks "What surprised in today's earnings?"
- References: historical earnings database, consensus tracking

Step 2: Plan
- Script: parse earnings releases, compare vs estimates
- References: earnings-schema.md (data format), earnings-glossary.md
- Assets: earnings-report-template.html

Step 3: Initialize
python scripts/meta_tools/skill-creator/init_skill.py earnings-analysis \
  --path .claude/skills/

Step 4: Edit
- SKILL.md: describe workflow, when to use, how to interpret earnings data
- scripts/earnings_parser.py: extract key metrics
- references/earnings-schema.md: field definitions
- assets/earnings-template.html: report template

Step 5: Package
python scripts/meta_tools/skill-creator/package_skill.py earnings-analysis

Step 6: Iterate
- Test on recent earnings events
- Refine accuracy, add missing fields
- Update references/earnings-schema.md
- Re-package and distribute
```

---

## 3. GitHub Workflow: Label Ready-to-Merge

**Purpose:** Validates skill PRs before merge.

**What It Does:**
- Only README.md can change in skill PRs
- Ensures new skills link to external repos
- Blocks crypto/blockchain keywords
- Enforces alphabetical ordering
- Auto-adds "ready-to-merge" label on success

**When It Triggers:**
- Pull request opened, synchronized, reopened, or edited
- Automatically validates without user action

**What Gets Flagged:**
```
❌ FAIL: Skill links to composio.dev (internal)
❌ FAIL: "crypto" keyword detected in description
❌ FAIL: Changes outside ## Skills section
❌ FAIL: Skill not in alphabetical order
✅ OK: All validation passed → "ready-to-merge" label added
```

**Best For:**
- Maintaining README.md consistency
- Preventing accidental internal links
- Ensuring new skills are properly formatted
- Team skill contributions

---

## Implementation Recommendations

### High Priority (Week 1)
1. **Use file-organizer to clean scripts/ directory**
   - Separate active pipeline scripts from utilities
   - Archive old scripts (advanced_analysis.py, etc. that were already archived)
   - Consolidate meta_tools organization

2. **Review reports/ directory**
   - Archive old analysis files (>30 days)
   - Consolidate duplicate report names
   - Keep only last 5 daily analyses

### Medium Priority (Week 2)
1. **Create a "watchlist-manager" skill**
   - Script: watchlist validation, ticker deduplication
   - References: watchlist schema, supported exchanges
   - Use skill-creator to package it

2. **Create a "catalyst-tracker" skill**
   - Script: parse earnings calendar, macro events
   - References: catalyst types, impact thresholds
   - Useful for team sharing

### Low Priority (Optional)
- Create "performance-analyzer" skill for post-trade reviews
- Create "indicator-validator" skill for custom technical indicator testing

---

## Safety Reminders

✅ **Safe:**
- Running file-organizer on reports/, data/, docs/
- Creating new skills in .claude/skills/
- Reviewing GitHub workflow validation

❌ **Never:**
- Wire file-organizer into schedule_daily.py
- Wire skill-creator into orchestrator.py
- Run file-organizer on production directories (agents/, watchlists/, .claude/)
- Auto-delete files without explicit confirmation

---

## Quick Commands

```bash
# List current skills
ls -la .claude/skills/

# Review file-organizer capabilities
cat scripts/meta_tools/file-organizer/SKILL.md

# Initialize a new skill
python scripts/meta_tools/skill-creator/init_skill.py <name> --path .claude/skills/

# Package a skill for distribution
python scripts/meta_tools/skill-creator/package_skill.py .claude/skills/<name>

# Check GitHub workflow validation
cat .github/workflows/label-ready-skill.yml
```

---

## When to Use vs Manual Approach

| Task | Use Meta-Tool | Use Manual |
|------|---------------|-----------|
| Clean 100+ files | ✅ file-organizer | ❌ Too slow |
| Organize 5 files | ❌ Overkill | ✅ Manual is faster |
| Find duplicates | ✅ file-organizer | ❌ Misses some |
| Create new skill | ✅ skill-creator | ❌ Inconsistent |
| Organize project | ✅ file-organizer | ❌ No validation |
| One-off cleanup | ❌ Overkill | ✅ Manual is faster |
