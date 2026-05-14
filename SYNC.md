# GitHub Sync Guide — VIF Trading System

## The Problem (What Was Happening)

Your **desktop** had **670 local commits** that were never pushed to GitHub.  
Your **laptop** was pulling from GitHub (which was stale), so it never saw those changes.  
Result: two devices drifting further apart every day.

## The Fix (One-Time — Desktop Only)

Open a terminal in `C:\Users\marti\vif-trading-system` and run:

```bash
git push origin main
```

This pushes all 670 commits up to GitHub. After this, GitHub has the full, up-to-date codebase.

Then on your **laptop**, run:

```bash
git pull origin main
```

Both devices are now in sync.

---

## Ongoing Workflow (Do This Every Session)

### Option A — Use the sync script (easiest)

Double-click `sync.bat` (Windows) at the **start** and **end** of every work session.

It automatically:
1. Commits any uncommitted local changes
2. Fetches from GitHub
3. Pulls new commits from the other device
4. Pushes your local commits up

### Option B — Manual git commands

**At the START of a session** (get the other device's changes):
```bash
git pull origin main
```

**At the END of a session** (send your changes to the other device):
```bash
git add -A
git commit -m "your message here"
git push origin main
```

---

## Golden Rule

> **Pull before you start. Push when you're done.**

If you always do this, the two devices will never diverge again.

---

## What's Excluded from Sync (by .gitignore)

These files are intentionally local-only and NOT synced via GitHub:

| What | Why |
|------|-----|
| `.env` | Contains your API key — never put this on GitHub |
| `data/*.pkl`, `data/*.csv` | Cached market data — regenerates automatically |
| `reports/` | Generated output — regenerates on each run |
| `logs/` | Runtime logs — local only |
| `.claude/settings.local.json` | Machine-specific Claude settings |
| `venv/`, `env/` | Python virtual environments — install fresh on each machine |

**Important:** After pulling on the laptop for the first time, you'll need to:
1. Copy your `.env` file manually (or recreate it with your API key)
2. Run `pip install -r requirements.txt` to install dependencies
3. Your `reports/` and `logs/` will be empty — that's normal, they'll fill up as the system runs

---

## Troubleshooting

### "Push rejected" or "non-fast-forward"
Both devices made commits at the same time. Fix:
```bash
git pull --rebase origin main   # bring in remote changes first
git push origin main             # now push
```

### Merge conflict
Two devices edited the same file differently. Git will mark the conflicts inside the file. Open the file, look for `<<<<<<`, resolve it, then:
```bash
git add <file>
git rebase --continue   # if you used --rebase
# or
git commit              # if you used regular merge
git push origin main
```

### "fatal: not a git repository"
You're in the wrong folder. Make sure you're inside `C:\Users\marti\vif-trading-system`.

---

## Quick Reference Card

```
START of session:   git pull origin main
END of session:     git add -A && git commit -m "msg" && git push origin main
Or just:            double-click sync.bat
```
# Test auto-push
