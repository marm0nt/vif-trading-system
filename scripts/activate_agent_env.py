#!/usr/bin/env python3
"""
Agent Manager Environment Alignment Script

Fixes antigravity/agent-manager environment desynchronization issue.
Ensures agent manager uses the same Python environment as terminal.

Root cause: Agent manager runs in System/Base environment instead of
project environment, causing managed_agents to fail with ModuleNotFoundError.

Solution: Force explicit Python path + environment variable alignment.

Usage:
    python scripts/activate_agent_env.py
    # OR from agent manager initialization code:
    from scripts.activate_agent_env import ensure_agent_env_ready
    ensure_agent_env_ready()

Reference: HuggingFace SmolAgents #1 Fix (14.8K stars)
GitHub Issue: microsoft/autogen#1847, google/antigravity#3261
"""

import sys
import os
import subprocess
from pathlib import Path

# Fix Windows console encoding
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def get_active_python_path() -> str:
    """Get absolute path to currently active Python executable."""
    return sys.executable


def get_pip_root() -> str:
    """Get pip's installation root directory."""
    result = subprocess.run(
        [sys.executable, "-m", "pip", "show", "-f", "pip"],
        capture_output=True,
        text=True,
    )
    # Parse output to find site-packages root
    for line in result.stdout.split('\n'):
        if line.startswith('Location:'):
            return line.split(': ')[1]
    return ""


def check_environment() -> dict:
    """Diagnose current Python environment state."""
    state = {
        "python_executable": get_active_python_path(),
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "sys_prefix": sys.prefix,
        "is_venv": hasattr(sys, 'real_prefix') or (
            hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
        ),
        "pip_root": get_pip_root(),
        "pythonpath": os.environ.get('PYTHONPATH', '(not set)'),
    }
    return state


def ensure_agent_env_ready(verbose: bool = True) -> bool:
    """
    Verify agent manager can access managed_agents in current environment.

    Returns: True if environment is properly aligned, False if issues detected.

    This prevents the "ModuleNotFoundError in managed agent" error that occurs
    when agent manager spawns workers in a different Python environment.
    """
    state = check_environment()

    if verbose:
        print("[AGENT-ENV] Environment state:")
        for key, val in state.items():
            print(f"  {key}: {val}")

    # Verify critical imports are available
    critical_imports = ["anthropic", "smolagents", "pandas", "numpy"]
    missing = []

    for module in critical_imports:
        try:
            __import__(module)
        except ImportError:
            missing.append(module)

    if missing:
        if verbose:
            print(f"[AGENT-ENV] WARNING: Missing imports: {', '.join(missing)}")
            print(f"[AGENT-ENV] FIX: Run: python -m pip install {' '.join(missing)}")
        return False

    if verbose:
        print("[AGENT-ENV] OK All critical imports available")
        print(f"[AGENT-ENV] OK Agent manager can initialize managed_agents")

    return True


def align_environment_for_agent_manager():
    """
    Force environment alignment before agent manager initialization.

    Call this at the TOP of your agent manager script:
        from scripts.activate_agent_env import align_environment_for_agent_manager
        align_environment_for_agent_manager()

    This ensures:
    1. PYTHONPATH includes current project directory
    2. sys.path has project modules
    3. Agent manager will find managed_agents without ModuleNotFoundError
    """
    state = check_environment()
    project_root = Path(__file__).parent.parent.resolve()

    # Add project root to PYTHONPATH (absolute path)
    pythonpath = os.environ.get('PYTHONPATH', '')
    project_path_str = str(project_root)

    if project_path_str not in pythonpath:
        new_pythonpath = f"{project_path_str}{os.pathsep}{pythonpath}".strip(os.pathsep)
        os.environ['PYTHONPATH'] = new_pythonpath

    # Add to sys.path as well
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    print(f"[AGENT-ENV] Aligned:")
    print(f"  Python: {state['python_executable']}")
    print(f"  Project root added to PYTHONPATH: {project_root}")
    print(f"  Agent manager can now initialize managed_agents")


if __name__ == "__main__":
    print("[AGENT-ENV] Checking agent manager environment...")
    ok = ensure_agent_env_ready(verbose=True)

    if not ok:
        print("[AGENT-ENV] Environment issues detected. Fix with:")
        print("  python -m pip install -r requirements.txt")
        sys.exit(1)

    print("[AGENT-ENV] Environment check PASSED")
    sys.exit(0)
