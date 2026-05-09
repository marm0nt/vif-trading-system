#!/usr/bin/env python3
"""
Auto-update system context and changelog on git commits.
Runs as git post-commit hook to maintain living documentation.
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

class SystemContextUpdater:
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.docs_system = repo_root / "docs" / "system"
        self.agents_dir = repo_root / "agents"
        self.scripts_dir = repo_root / "scripts"
        self.skills_dir = repo_root / ".claude" / "skills"
        self.system_context_path = self.docs_system / "system_context.md"
        self.changelog_path = self.docs_system / "CHANGELOG.md"

    def get_latest_commit_files(self) -> List[str]:
        """Get files changed in the latest commit."""
        try:
            result = subprocess.run(
                ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"],
                capture_output=True, text=True, cwd=self.repo_root
            )
            return result.stdout.strip().split('\n') if result.stdout.strip() else []
        except Exception as e:
            print(f"⚠️  Error getting commit files: {e}")
            return []

    def scan_agents(self) -> Dict[str, dict]:
        """Scan agents/ directory for all agent definitions."""
        agents = {}
        if self.agents_dir.exists():
            for file in self.agents_dir.glob("*.py"):
                if file.name.startswith("_"):
                    continue
                agents[file.stem] = {
                    "file": str(file.relative_to(self.repo_root)),
                    "modified": datetime.fromtimestamp(file.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
                }
        return agents

    def scan_skills(self) -> Dict[str, dict]:
        """Scan .claude/skills for all skill definitions."""
        skills = {}
        if self.skills_dir.exists():
            for file in self.skills_dir.glob("*.md"):
                skills[file.stem] = {
                    "file": str(file.relative_to(self.repo_root)),
                    "modified": datetime.fromtimestamp(file.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
                }
        return skills

    def scan_frameworks(self) -> Dict[str, dict]:
        """Identify frameworks from agents and configuration."""
        frameworks = {}

        # Check for orchestrator (multi-agent framework)
        if (self.agents_dir / "orchestrator.py").exists():
            frameworks["multi-agent-orchestrator"] = {
                "agents": ["catalyst-monitor", "vif-analyst", "swing-trade-screener"],
                "status": "active"
            }

        # Check for swarm intelligence
        if (self.agents_dir / "swarm_orchestrator.py").exists() or \
           any(f.name.startswith("swarm") for f in self.agents_dir.glob("*.py")):
            frameworks["swarm-intelligence"] = {
                "components": ["LRAgent", "LatentMAS", "consensus-routing"],
                "status": "active"
            }

        return frameworks

    def get_recent_changes(self) -> Tuple[List[str], List[str], List[str]]:
        """Identify new, modified, and deleted files in agents/scripts/skills."""
        try:
            result = subprocess.run(
                ["git", "diff-tree", "--no-commit-id", "--diff-filter=A", "--name-only", "-r", "HEAD"],
                capture_output=True, text=True, cwd=self.repo_root
            )
            added = [f for f in result.stdout.strip().split('\n')
                    if f and any(d in f for d in ["agents/", "scripts/", "skills/"])]
        except:
            added = []

        try:
            result = subprocess.run(
                ["git", "diff-tree", "--no-commit-id", "--diff-filter=M", "--name-only", "-r", "HEAD"],
                capture_output=True, text=True, cwd=self.repo_root
            )
            modified = [f for f in result.stdout.strip().split('\n')
                       if f and any(d in f for d in ["agents/", "scripts/", "skills/"])]
        except:
            modified = []

        return added, modified, []

    def generate_system_context(self) -> str:
        """Generate updated system_context.md."""
        agents = self.scan_agents()
        skills = self.scan_skills()
        frameworks = self.scan_frameworks()
        added, modified, _ = self.get_recent_changes()

        context = f"""# VIF Trading System — Complete Architecture Map

**Last updated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Status:** All systems operational

---

## 1. Active Agents

| Agent | File | Status |
|-------|------|--------|
"""

        for agent_name, info in sorted(agents.items()):
            context += f"| {agent_name} | {info['file']} | ✅ Active |\n"

        context += f"""
---

## 2. Skills & Knowledge Modules

| Skill | Purpose | Last Updated |
|-------|---------|--------------|
"""

        for skill_name, info in sorted(skills.items()):
            context += f"| {skill_name} | Core framework reference | {info['modified']} |\n"

        context += f"""
---

## 3. Active Frameworks

"""
        for fw_name, fw_info in sorted(frameworks.items()):
            context += f"### {fw_name}\n"
            context += f"- Status: {fw_info.get('status', 'unknown')}\n"
            if 'agents' in fw_info:
                context += f"- Agents: {', '.join(fw_info['agents'])}\n"
            if 'components' in fw_info:
                context += f"- Components: {', '.join(fw_info['components'])}\n"
            context += "\n"

        context += f"""---

## 4. Recent Changes

**Added:**
"""
        if added:
            for f in added:
                context += f"- ✨ {f}\n"
        else:
            context += "- (none)\n"

        context += f"""
**Modified:**
"""
        if modified:
            for f in modified:
                context += f"- 🔧 {f}\n"
        else:
            context += "- (none)\n"

        context += f"""
---

## 5. How to Use This Documentation

1. **For system overview:** Read Section 3 (Active Frameworks)
2. **To understand agents:** Check Section 1 (Active Agents)
3. **For skill reference:** See Section 2 (Skills & Knowledge Modules)
4. **To track changes:** Review Section 4 (Recent Changes) and CHANGELOG.md

---

See **LEVERAGE_GUIDE.md** for backtested patterns and consensus best practices.
See **CHANGELOG.md** for detailed change history.
"""

        return context

    def generate_changelog(self) -> str:
        """Generate or append to CHANGELOG.md."""
        added, modified, deleted = self.get_recent_changes()

        changelog = f"""# System Context Changelog

## {datetime.now().strftime("%Y-%m-%d %H:%M")}

"""

        if added:
            changelog += "### New\n"
            for f in added:
                changelog += f"- ✨ {f}\n"
            changelog += "\n"

        if modified:
            changelog += "### Modified\n"
            for f in modified:
                changelog += f"- 🔧 {f}\n"
            changelog += "\n"

        # Append to existing changelog if it exists
        if self.changelog_path.exists():
            existing = self.changelog_path.read_text()
            changelog += existing

        return changelog

    def update(self) -> bool:
        """Update system context and changelog."""
        try:
            # Ensure docs/system directory exists
            self.docs_system.mkdir(parents=True, exist_ok=True)

            # Generate and save system context
            context = self.generate_system_context()
            self.system_context_path.write_text(context)
            print(f"✅ Updated {self.system_context_path.relative_to(self.repo_root)}")

            # Generate and save changelog
            changelog = self.generate_changelog()
            self.changelog_path.write_text(changelog)
            print(f"✅ Updated {self.changelog_path.relative_to(self.repo_root)}")

            return True
        except Exception as e:
            print(f"❌ Error updating system context: {e}", file=sys.stderr)
            return False

def main():
    """Main entry point for post-commit hook."""
    repo_root = Path(__file__).parent.parent  # vif-trading-system/

    updater = SystemContextUpdater(repo_root)
    success = updater.update()

    # Try to add and commit changes (non-blocking if it fails)
    if success:
        try:
            subprocess.run(
                ["git", "add", "docs/system/system_context.md", "docs/system/CHANGELOG.md"],
                cwd=repo_root, capture_output=True, timeout=5
            )
            print("✅ System context files staged")
        except Exception as e:
            print(f"⚠️  Could not stage files: {e}")

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
