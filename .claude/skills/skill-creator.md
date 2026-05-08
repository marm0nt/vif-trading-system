---
name: skill-creator
description: Guides the creation and packaging of Claude skills. Use when creating new skills that extend Claude's capabilities, or updating/distributing existing skills.
trigger: "create a skill, build a new skill, package a skill, distribute a skill"
location: scripts/meta_tools/skill-creator/
---

This is a meta-tool skill for creating and managing Claude skills. See `scripts/meta_tools/skill-creator/SKILL.md` for full documentation and the 6-step creation process.

**Quick workflow:**
1. Gather concrete examples of skill usage
2. Plan reusable contents (scripts, references, assets)
3. Initialize skill template: `python scripts/meta_tools/skill-creator/init_skill.py <name>`
4. Edit SKILL.md and bundled resources
5. Package: `python scripts/meta_tools/skill-creator/package_skill.py <skill-folder>`
6. Iterate based on real-world usage

**Bundled Resources:**
- `scripts/init_skill.py` — Generate skill template
- `scripts/package_skill.py` — Validate & package skills
