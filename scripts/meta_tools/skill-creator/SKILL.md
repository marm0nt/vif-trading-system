---
name: skill-creator
description: Guide for creating effective skills that extend Claude's capabilities. Use when creating new skills, updating existing skills, or packaging skills for distribution.
---

# Skill Creator

This skill provides structured guidance for creating effective skills that extend Claude's capabilities with specialized knowledge, workflows, and tool integrations.

## Purpose

Create modular, self-contained skills that transform Claude from general-purpose to specialized. Skills are "onboarding guides" for specific domains—they bundle procedural knowledge, tool integrations, domain expertise, and reusable assets that no model can fully possess.

## Skill Anatomy

Every skill consists of:

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter: name, description
│   └── Markdown instructions
└── Bundled Resources (optional)
    ├── scripts/      - Executable code (Python/Bash)
    ├── references/   - Documentation & schemas
    └── assets/       - Templates, icons, boilerplate
```

### Frontmatter (Required)
```yaml
---
name: skill-name
description: When and how to use this skill. Use third-person imperative form.
---
```

### SKILL.md Content Structure
1. **Purpose** - What the skill does (2-3 sentences)
2. **When to Use** - Specific use cases (bullet list)
3. **How to Use** - Step-by-step workflow or examples
4. **Safety/Validation** - Confirm before destructive ops
5. **Example Workflows** - Real-world application scenarios

## Skill Creation Process (6 Steps)

### Step 1: Understanding with Concrete Examples
Gather specific examples of how the skill will be used:
- "What functionality should this skill support?"
- "Can you give concrete examples of how it would be used?"
- "What would a user say that should trigger this skill?"

**Conclude when:** Clear sense of functionality exists.

### Step 2: Planning Reusable Contents
For each concrete example, identify:
- Scripts that are rewritten repeatedly
- References (schemas, APIs, domain knowledge)
- Assets (templates, boilerplate, configs)

**Example:** A pdf-editor skill needs `scripts/rotate_pdf.py` and `references/pdf-spec.md`.

### Step 3: Initialize the Skill
Use the init_skill.py script to generate template:
```bash
python scripts/init_skill.py <skill-name> --path <output-directory>
```

This creates:
- skill-name/ directory with SKILL.md template
- Example subdirectories: scripts/, references/, assets/
- TODO placeholders for customization

**Skip if:** Updating an existing skill (go to Step 4).

### Step 4: Edit the Skill

#### Write for Another Claude Instance
Include information that would be beneficial and non-obvious to another Claude:
- Procedural knowledge
- Domain-specific details
- Reusable assets and scripts
- Workflow examples

#### Delete Unneeded Examples
The init script generates examples—delete any you don't need.

#### Write SKILL.md in Imperative Form
Use verb-first, instructional language:
- ✅ "To accomplish X, do Y"
- ✅ "Analyze the input, then propose changes"
- ❌ "You should do X" (avoid second-person)

#### Answer These Questions
1. What is the purpose of the skill? (2-3 sentences)
2. When should the skill be used? (bullet list)
3. How should Claude use it? (reference bundled resources)

### Step 5: Package the Skill
Validate and create distributable zip:
```bash
python scripts/package_skill.py <path/to/skill-folder>
```

The script:
- ✅ Validates YAML frontmatter format
- ✅ Checks naming conventions
- ✅ Verifies directory structure
- ✅ Creates skill-name.zip with all files
- ❌ Reports errors and exits on validation failure

**Output:** `skill-name.zip` ready for distribution.

### Step 6: Iterate
After testing the skill in real workflows:
1. Notice struggles or inefficiencies
2. Identify SKILL.md or bundled resource improvements
3. Update and test again
4. Repeat packaging if distributing updates

## Progressive Disclosure Design

Skills use three-level loading to manage context efficiently:

| Level | Content | Size | When Loaded |
|-------|---------|------|-------------|
| 1 | name + description | ~100 words | Always |
| 2 | SKILL.md body | <5k words | When skill triggers |
| 3 | Bundled resources | Unlimited | On-demand, as needed |

Scripts can be executed without reading into context window.

## Best Practices

### References vs SKILL.md
- **References file:** Large documentation, schemas, APIs, policies
  - Load only when Claude determines it's needed
  - Use grep search patterns in SKILL.md for discoverability
  - Example: `references/api-docs.md` for API specifications

- **SKILL.md:** Essential procedural instructions, workflow guidance
  - Keep lean, focus on HOW to use the skill
  - Reference bundled resources, don't duplicate

### Scripts
- Include when the same code is rewritten repeatedly
- Store deterministic, reliable code
- Example: `scripts/rotate_pdf.py` for PDF manipulation
- Scripts are executable without being read into context

### Assets
- Templates, boilerplate, icons, fonts
- Files used in final output, not loaded into context
- Example: `assets/react-template/` for web app boilerplate
- Example: `assets/logo.png` for brand assets

## Example Skill Structure

**PDF Editor Skill:**
```
pdf-editor/
├── SKILL.md
│   ├── name: pdf-editor
│   ├── description: Edit, rotate, merge, split PDFs
│   └── Instructions referencing scripts/
├── scripts/
│   ├── rotate_pdf.py
│   ├── merge_pdfs.py
│   └── extract_pages.py
├── references/
│   └── pdf-operations-guide.md
└── assets/
    └── sample.pdf
```

**Skill-Creator Skill** (this skill itself):
```
skill-creator/
├── SKILL.md (procedural guide you're reading)
├── scripts/
│   ├── init_skill.py (generates new skill templates)
│   └── package_skill.py (validates & packages skills)
└── references/
    └── skill-template-checklist.md
```

## Packaging Checklist

Before running `package_skill.py`, verify:
- [ ] SKILL.md exists with proper YAML frontmatter
- [ ] name and description are present and specific
- [ ] Unnecessary example directories deleted
- [ ] All referenced files (scripts, references, assets) exist
- [ ] SKILL.md uses imperative/instructional tone
- [ ] No sensitive credentials in skill content
