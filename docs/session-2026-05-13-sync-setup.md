# Session: Cross-Device Brain Sync Setup
**Date:** 2026-05-13 | **System:** VIF Trading System | **Repo:** github.com/marm0nt/vif-trading-system

---

## Problem
- Desktop had **670 local commits** never pushed to GitHub
- Laptop pulled from stale `origin/main` → ran outdated code
- Agent Manager worked on laptop but not desktop
- `.claude/memory/`, `.claude/skills/`, `.claude/agents/` were at risk of drifting

## Root Cause
Git repo existed on both devices but desktop never pushed. Histories shared a common ancestor — clean fast-forward, no conflicts. Desktop was strictly ahead of `origin/main`.

---

## Solution Implemented

### Framework: claude-brain + atxtechbro "Spilled Coffee Principle"
> Destroy any device → `git clone` → fully operational with complete AI context in <15 min.

**Research verdict:** Community-rated #1 for cross-device AI dev sync (2026). Pure git, no cloud deps, works forever.

### Files Created/Modified

| File | Purpose |
|------|---------|
| `brain-sync.bat` | Master sync script — commit + pull + push in one shot |
| `sync.bat` | Simpler per-session sync (start/end of session) |
| `SYNC.md` | Human reference + troubleshooting guide |
| `scripts/install-brain-sync-hook.ps1` | Installs post-commit auto-push hook |
| `.claude/hooks/post-commit-sync.sh` | Hook definition — pushes on every commit |
| `.gitignore` | Updated to track `.claude/` brain, exclude machine-local files |
| `CLAUDE.md` | Updated with Cross-Device Brain Sync section |

### .gitignore Rules (Key Changes)

**Tracked in git (syncs across devices):**
- `.claude/memory/` — AI learned context
- `.claude/skills/` — custom skill definitions
- `.claude/agents/` — agent configs
- `.claude/hooks/` — automation hooks
- `.claude/settings.json` — shared settings

**Excluded (machine-local):**
- `.env` — API key, copy manually
- `.claude/settings.local.json`
- `.claude/worktrees/`
- `.claude/**/*.lock`
- `data/`, `logs/`, `reports/`, `venv/`

---

## Activation Steps (Run Once)

### Desktop (this machine):
```bash
git push origin main          # uploads all 670 commits
```

### Laptop:
```bash
git pull origin main
powershell scripts\install-brain-sync-hook.ps1
```

### Both machines (ongoing):
```
brain-sync.bat    # double-click — handles everything
```

---

## Ongoing Workflow

```
START of session:  git pull origin main
END of session:    brain-sync.bat
After hook install: every git commit auto-pushes
```

---

## Karpathy Comparison (Research Finding)

| | VIF Brain Sync | Karpathy autoresearch |
|---|---|---|
| Solves | Cross-device continuity | Autonomous ML experimentation |
| Input | Git repo | `program.md` + GPU |
| Output | Identical env on every device | Validated code improvements |
| Relevance to VIF | ✅ In use now | ⏳ Phase 2 (needs fast backtester) |

**Key insight:** Not competing tools — they stack. autoresearch requires a <5-min feedback loop with a quantifiable score. VIF signals validate over days, so autoresearch needs a backtester adapter before it applies. That's a future phase.

**Karpathy's CLAUDE.md** (109k stars) — 4 behavioral principles for AI agents: don't assume, simplicity first, surgical changes, surface tradeoffs. Already baked into your `CLAUDE.md`.

---

## What Syncs via GitHub (Complete List)

```
agents/          scripts/         config/          watchlists/
.claude/memory/  .claude/skills/  .claude/agents/  .claude/hooks/
.claude/settings.json             CLAUDE.md        ONBOARDING.md
requirements.txt brain-sync.bat   sync.bat
```

## What Does NOT Sync (Regenerated/Local)

```
.env             venv/            data/*.pkl       data/*.csv
reports/         logs/            .claude/settings.local.json
.claude/worktrees/
```

---

## Key Sources
- [karpathy/autoresearch](https://github.com/karpathy/autoresearch)
- [atxtechbro/dotfiles](https://github.com/atxtechbro/dotfiles)
- [claude-brain — toroleapinc](https://github.com/toroleapinc/claude-brain)
- [Dylan Bochman: Dotfiles for AI Dev](https://dylanbochman.com/blog/2026-01-25-dotfiles-for-ai-assisted-development/)
- [Karpathy CLAUDE.md 100k stars](https://miraflow.ai/blog/karpathy-claude-md-100k-github-stars-ai-coding-2026)
