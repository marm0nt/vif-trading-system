---
name: file-organizer
description: Analyzes folder structures, finds duplicates, suggests better organization, and automates file cleanup. Use when organizing downloads, eliminating duplicates, restructuring projects, or establishing better file management habits.
---

# File Organizer Skill

This skill helps maintain clean, logical file structures without manual overhead.

## Purpose

Organize files and folders intelligently by understanding context, finding duplicates, suggesting better structures, and automating cleanup tasks. Works locally using bash commands with full confirmation before any destructive operations.

## When to Use

- Reorganizing Downloads or cluttered directories
- Finding and removing duplicate files
- Establishing logical folder hierarchies before archiving projects
- Identifying and flagging outdated files for removal
- Restructuring project directories after completion

## How to Use

### 1. Clarify Scope
Ask clarifying questions:
- What directory to organize? (full path)
- Any folders to exclude? (node_modules, .git, etc.)
- Organize by: type, date, project, purpose?
- Delete or archive old files?

### 2. Analyze Structure
Use bash commands to understand current state:
```bash
find <dir> -type f | head -20  # Sample files
du -sh <dir>/*                  # Size by folder
find <dir> -type f -mtime +365  # Files older than 1 year
```

### 3. Detect Duplicates
Multiple strategies:
```bash
find <dir> -type f -exec md5sum {} \; | sort | uniq -w32 -d  # By hash
find <dir> -type f -name "*.pdf" | sort  # By extension/name
ls -lA <dir> | grep -E "^\-.*\s+[0-9]+\s"  # By size+date
```

### 4. Propose Organization
Suggest logical groupings by:
- **By Type**: Documents/, Images/, Videos/, Code/, Archives/
- **By Date**: 2024/, 2023/, 2022/, Archive/
- **By Project**: project-name/, client-name/
- **By Purpose**: Active/, Reference/, ToDelete/

### 5. Execute with Checkpoints
Before any action:
```bash
# Preview moves (dry-run)
find <dir> -type f -name "*.pdf" -newer <cutoff>

# Execute with confirmation
mkdir -p <new-path> && mv <file> <new-path>/

# Log all changes for potential reversal
echo "Moved <file> from <old> to <new>" >> .organization-log.txt
```

### 6. Cleanup Strategy
- Preserve original modification dates: `touch -r <original> <moved>`
- Never auto-delete: flag for review or move to Archive/
- Create manifest of removed files
- Provide reversal instructions

## Safety Features

- ✅ Requires explicit confirmation before deletions
- ✅ Logs all file movements for reversal
- ✅ Preserves original modification dates
- ✅ Pauses on unexpected file types or patterns
- ✅ Offers dry-run preview before execution

## Example Workflows

### Clean Downloads Folder
1. Analyze file types and dates in ~/Downloads
2. Detect duplicates by hash
3. Propose: Documents/, Images/, Archives/, ToDelete/
4. Move files with confirmation, archive 1+ year old
5. Log all moves to reversal manifest

### Project Restructuring
1. Identify project completion date
2. Detect files not modified in 90 days
3. Propose: Active/, Reference/, Archive/ structure
4. Move inactive files, preserve project integrity
5. Create archive manifest

### Duplicate Removal
1. Scan for identical files (by md5)
2. Keep original, flag duplicates
3. Present removal candidates with disk savings
4. Execute with dry-run first
5. Provide deletion manifest
