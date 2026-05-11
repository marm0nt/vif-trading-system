#!/usr/bin/env python3
"""
Generate SYSTEM_MANIFEST.md - A complete registry of all files, agents, skills, and components.
Run this script to auto-generate and update the manifest.

Usage:
    python scripts/generate_manifest.py
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import subprocess


def get_git_info(file_path: Path) -> Dict[str, Any]:
    """Get git metadata for a file (last commit, age)."""
    try:
        # Last commit hash (short)
        commit = subprocess.check_output(
            ["git", "log", "-1", "--format=%h", "--", str(file_path)],
            text=True, stderr=subprocess.DEVNULL
        ).strip()

        # Last commit date
        date = subprocess.check_output(
            ["git", "log", "-1", "--format=%ai", "--", str(file_path)],
            text=True, stderr=subprocess.DEVNULL
        ).strip()

        return {"last_commit": commit, "last_modified": date}
    except (subprocess.CalledProcessError, FileNotFoundError):
        return {}


def scan_agents(root_dir: Path) -> List[Dict[str, Any]]:
    """Scan agents/ directory and catalog all agents."""
    agents = []
    agents_dir = root_dir / "agents"

    if not agents_dir.exists():
        return agents

    for py_file in sorted(agents_dir.glob("*.py")):
        if py_file.name.startswith("_"):
            continue

        # Read docstring
        docstring = ""
        try:
            with open(py_file, 'r') as f:
                lines = f.readlines()
                in_doc = False
                for line in lines[:50]:  # Check first 50 lines
                    if '"""' in line:
                        in_doc = not in_doc
                    elif in_doc:
                        docstring += line.strip() + " "
        except:
            pass

        agent = {
            "name": py_file.stem,
            "file": str(py_file.relative_to(root_dir)),
            "type": "agent",
            "description": docstring[:100] if docstring else "",
            **get_git_info(py_file)
        }
        agents.append(agent)

    return agents


def scan_skills(root_dir: Path) -> List[Dict[str, Any]]:
    """Scan .claude/skills directory and catalog all skills."""
    skills = []
    skills_dir = root_dir / ".claude" / "skills"

    if not skills_dir.exists():
        return skills

    for md_file in sorted(skills_dir.glob("*.md")):
        if md_file.name == "TEMPLATE_SKILL.md":
            continue

        # Extract description from file
        description = ""
        try:
            with open(md_file, 'r') as f:
                lines = f.readlines()
                for i, line in enumerate(lines[:10]):
                    if "description" in line.lower() or "#" in line:
                        description = line.strip().lstrip("# ").lstrip("- description: ")
                        break
        except:
            pass

        skill = {
            "name": md_file.stem,
            "file": str(md_file.relative_to(root_dir)),
            "type": "skill",
            "description": description[:80],
            **get_git_info(md_file)
        }
        skills.append(skill)

    return skills


def scan_scripts(root_dir: Path) -> List[Dict[str, Any]]:
    """Scan scripts/ directory for analysis scripts."""
    scripts = []
    scripts_dir = root_dir / "scripts"

    if not scripts_dir.exists():
        return scripts

    for category_dir in ["active", "archive"]:
        cat_path = scripts_dir / category_dir
        if not cat_path.exists():
            continue

        for py_file in sorted(cat_path.rglob("*.py")):
            if py_file.name.startswith("_"):
                continue

            docstring = ""
            try:
                with open(py_file, 'r') as f:
                    lines = f.readlines()
                    in_doc = False
                    for line in lines[:50]:
                        if '"""' in line:
                            in_doc = not in_doc
                        elif in_doc:
                            docstring += line.strip() + " "
            except:
                pass

            script = {
                "name": py_file.stem,
                "file": str(py_file.relative_to(root_dir)),
                "type": "script",
                "category": category_dir,
                "description": docstring[:100] if docstring else "",
                **get_git_info(py_file)
            }
            scripts.append(script)

    return scripts


def scan_configs(root_dir: Path) -> List[Dict[str, Any]]:
    """Scan config/ directory."""
    configs = []
    config_dir = root_dir / "config"

    if not config_dir.exists():
        return configs

    for cfg_file in sorted(config_dir.glob("*")):
        if cfg_file.is_file():
            config = {
                "name": cfg_file.stem,
                "file": str(cfg_file.relative_to(root_dir)),
                "type": "config",
                "description": f"Configuration file ({cfg_file.suffix})",
                **get_git_info(cfg_file)
            }
            configs.append(config)

    return configs


def scan_watchlists(root_dir: Path) -> List[Dict[str, Any]]:
    """Scan watchlists/ directory."""
    watchlists = []
    watchlists_dir = root_dir / "watchlists"

    if not watchlists_dir.exists():
        return watchlists

    for wl_file in sorted(watchlists_dir.rglob("*.txt")):
        # Count tickers
        ticker_count = 0
        try:
            with open(wl_file, 'r') as f:
                ticker_count = len([line.strip() for line in f if line.strip()])
        except:
            pass

        wl = {
            "name": wl_file.stem,
            "file": str(wl_file.relative_to(root_dir)),
            "type": "watchlist",
            "tickers": ticker_count,
            **get_git_info(wl_file)
        }
        watchlists.append(wl)

    return watchlists


def scan_docs(root_dir: Path) -> List[Dict[str, Any]]:
    """Scan docs/ directory."""
    docs = []
    docs_dir = root_dir / "docs"

    if not docs_dir.exists():
        return docs

    for doc_file in sorted(docs_dir.rglob("*.md")):
        doc = {
            "name": doc_file.stem,
            "file": str(doc_file.relative_to(root_dir)),
            "type": "documentation",
            **get_git_info(doc_file)
        }
        docs.append(doc)

    return docs


def scan_utilities(root_dir: Path) -> List[Dict[str, Any]]:
    """Scan utils/ directory."""
    utils = []
    utils_dir = root_dir / "utils"

    if not utils_dir.exists():
        return utils

    for util_file in sorted(utils_dir.glob("*.py")):
        if util_file.name.startswith("_"):
            continue

        docstring = ""
        try:
            with open(util_file, 'r') as f:
                lines = f.readlines()
                in_doc = False
                for line in lines[:20]:
                    if '"""' in line:
                        in_doc = not in_doc
                    elif in_doc:
                        docstring += line.strip() + " "
        except:
            pass

        util = {
            "name": util_file.stem,
            "file": str(util_file.relative_to(root_dir)),
            "type": "utility",
            "description": docstring[:80] if docstring else "",
            **get_git_info(util_file)
        }
        utils.append(util)

    return utils


def generate_manifest_md(root_dir: Path, catalog: Dict[str, List[Any]]) -> str:
    """Generate markdown for the manifest."""
    timestamp = datetime.now().isoformat()

    md = f"""# System Manifest

**Auto-generated:** {timestamp}

This document is the complete registry of all files, agents, skills, scripts, and configurations in the VIF Trading System. It serves as a single source of truth for what exists, where it is, and what it does.

**How to use this manifest:**
- Find a component by name or type
- See when it was last modified (git commit)
- Understand dependencies between components
- Track what's active vs archived

---

## Quick Stats

- **Total Agents:** {len(catalog.get('agents', []))}
- **Total Skills:** {len(catalog.get('skills', []))}
- **Total Scripts:** {len(catalog.get('scripts', []))}
- **Total Configs:** {len(catalog.get('configs', []))}
- **Total Watchlists:** {len(catalog.get('watchlists', []))}
- **Total Docs:** {len(catalog.get('docs', []))}
- **Total Utilities:** {len(catalog.get('utilities', []))}

---

"""

    # Agents Section
    md += "## Agents\n\n"
    md += "Core analysis agents that drive the VIF trading system.\n\n"
    for agent in catalog.get('agents', []):
        md += f"### `{agent['name']}`\n"
        md += f"**File:** `{agent['file']}`\n"
        if agent.get('last_commit'):
            md += f"**Last Modified:** {agent['last_modified']} ({agent['last_commit']})\n"
        if agent.get('description'):
            md += f"**Description:** {agent['description']}\n"
        md += "\n"

    # Skills Section
    md += "## Skills\n\n"
    md += "Trading analysis and utility skills used by agents.\n\n"
    for skill in catalog.get('skills', []):
        md += f"### `{skill['name']}`\n"
        md += f"**File:** `{skill['file']}`\n"
        if skill.get('description'):
            md += f"**Description:** {skill['description']}\n"
        md += "\n"

    # Scripts Section
    if catalog.get('scripts'):
        md += "## Scripts\n\n"
        md += "Standalone analysis and utility scripts.\n\n"

        # Organize by category
        active = [s for s in catalog['scripts'] if s.get('category') == 'active']
        archive = [s for s in catalog['scripts'] if s.get('category') == 'archive']

        if active:
            md += "### Active Scripts\n\n"
            for script in active:
                md += f"- **{script['name']}** (`{script['file']}`)\n"
                if script.get('description'):
                    md += f"  - {script['description']}\n"
            md += "\n"

        if archive:
            md += "### Archived Scripts\n\n"
            for script in archive:
                md += f"- **{script['name']}** (`{script['file']}`)\n"
            md += "\n"

    # Configs Section
    if catalog.get('configs'):
        md += "## Configuration Files\n\n"
        for config in catalog.get('configs', []):
            md += f"- **{config['name']}** (`{config['file']}`)\n"
            md += f"  - {config['description']}\n"
        md += "\n"

    # Watchlists Section
    if catalog.get('watchlists'):
        md += "## Watchlists\n\n"
        for wl in catalog.get('watchlists', []):
            md += f"- **{wl['name']}** ({wl.get('tickers', 0)} tickers) - `{wl['file']}`\n"
        md += "\n"

    # Utilities Section
    if catalog.get('utilities'):
        md += "## Utilities\n\n"
        md += "Shared utilities and helpers.\n\n"
        for util in catalog.get('utilities', []):
            md += f"### `{util['name']}`\n"
            md += f"**File:** `{util['file']}`\n"
            if util.get('description'):
                md += f"**Description:** {util['description']}\n"
            md += "\n"

    # Docs Section
    if catalog.get('docs'):
        md += "## Documentation\n\n"
        for doc in catalog.get('docs', []):
            md += f"- [{doc['name']}]({doc['file']})\n"
        md += "\n"

    # Footer
    md += """---

## Telemetry & Observability

This manifest is **static** (updated by running `generate_manifest.py`). For **dynamic** system observability, see:

- `logs/telemetry.jsonl` — Runtime event log (agents starting/ending, APIs called, errors, etc.)
- `docs/SYSTEM_HEALTH.md` — System health dashboard (updated periodically)
- `logs/*.log` — Agent-specific logs (structured)

## Integration with CI/CD

To keep this manifest up-to-date:

```bash
# Add to pre-commit hook or CI pipeline
python scripts/generate_manifest.py
git add SYSTEM_MANIFEST.md
git commit -m "Update system manifest"
```

"""

    return md


def main():
    """Generate and save the system manifest."""
    root_dir = Path.cwd()

    # If not in project root, try to find it
    if not (root_dir / "agents").exists():
        root_dir = Path(__file__).parent.parent
        if not (root_dir / "agents").exists():
            print("ERROR: Could not find project root (no agents/ directory)")
            return

    print(f"Scanning system from: {root_dir}")

    # Catalog all components
    catalog = {
        'agents': scan_agents(root_dir),
        'skills': scan_skills(root_dir),
        'scripts': scan_scripts(root_dir),
        'configs': scan_configs(root_dir),
        'watchlists': scan_watchlists(root_dir),
        'docs': scan_docs(root_dir),
        'utilities': scan_utilities(root_dir),
    }

    # Generate markdown
    manifest_md = generate_manifest_md(root_dir, catalog)

    # Save to file
    manifest_file = root_dir / "SYSTEM_MANIFEST.md"
    with open(manifest_file, 'w') as f:
        f.write(manifest_md)

    print(f"✓ Manifest generated: {manifest_file}")

    # Also save as JSON for programmatic access
    manifest_json = root_dir / "SYSTEM_MANIFEST.json"
    with open(manifest_json, 'w') as f:
        json.dump(catalog, f, indent=2, default=str)

    print(f"✓ JSON catalog saved: {manifest_json}")

    # Print summary
    total = sum(len(v) for v in catalog.values())
    print(f"\nManifest Summary:")
    for key, items in catalog.items():
        if items:
            print(f"  {key}: {len(items)}")
    print(f"  TOTAL: {total}")


if __name__ == '__main__':
    main()
