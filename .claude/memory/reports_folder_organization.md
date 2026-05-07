---
name: Reports folder organization
description: Reports reorganized by pipeline type; structure complete with 93 files organized across 5 folders
type: project
originSessionId: bac8b4cd-87f1-42f0-897f-c9b6288f7171
---
**Date:** May 2, 2026  
**Status:** ✅ Complete

## Organization Summary

Reports folder reorganized from flat structure (93 files in root) to logical pipeline-based subfolders.

### Structure
```
reports/
├── premarket/      (10 files) - Daily VIF analysis outputs
├── swing-trades/   (16 files) - Swing screener + options strategies  
├── catalysts/      (14 files) - Macro + earnings analysis
├── weekend/        (9 files)  - Weekend briefing
├── raw/            (44 files) - Intermediate JSON (reference only)
└── archive/        (empty)    - For reports >30 days old (future)
```

### Benefits Realized
1. **Navigation speed** — Find premarket/catalysts/swing-trades instantly
2. **Maintenance ready** — Can auto-move reports >30d to archive/
3. **Analysis clarity** — Clear separation: tactical (premarket) vs. strategic (catalysts) vs. research (swing-trades)
4. **Scalability** — New analysis types just add new subfolder

### File Counts by Type
- Premarket HTML reports: 6 (latest pipeline runs)
- Catalyst analysis JSON: 6 (live K4 detection + macro)
- Swing setup screener: 5
- Weekend briefing: 7
- Raw intermediate: 44
- Options strategy docs: 8

### Maintenance Schedule
- **Weekly:** Review latest files in each folder
- **Monthly:** Move reports >30d to archive/
- **Quarterly:** Compress and backup archive/ folder

### Locked Files
- Excel files (`.xlsx`) remain in root (locked, not critical to move)
- Temporary Excel lock files (`~$*.xlsx`) will auto-delete when closed

### Documentation
- `reports/README.md` — Quick reference guide and folder glossary
- `docs/FOLDER_OPERATIONS_CHECKLIST.md` — Daily ops checklist (references reports/ folders)

### Committed
- Documentation added to git (FOLDER_OPERATIONS_CHECKLIST.md, MARKET_DATA_SOURCE_ANALYSIS.md)
- File reorganization noted (not tracked by git as file movement)
