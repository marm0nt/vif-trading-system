---
name: file-organizer
description: Organizes files and folders locally using bash analysis and categorization. Use when cleaning downloads, removing duplicates, restructuring projects, or identifying files for archival.
trigger: "organize files, clean downloads, find duplicates, restructure folders, archive files"
location: scripts/meta_tools/file-organizer/
---

This is a meta-tool skill for organizing your local filesystem. See `scripts/meta_tools/file-organizer/SKILL.md` for full documentation.

**Quick use:**
1. Provide the directory to organize
2. Skill analyzes structure and detects duplicates
3. Proposes logical hierarchy
4. Executes moves with confirmation at each step

No external dependencies—uses bash commands only.
