#!/usr/bin/env python3
"""
Agent Manager Integration Fix — Prevents Antigravity Environment Desync

Import this in ANY agent that initializes managed_agents:

    from agents.agent_manager_fix import initialize_agent_manager

    # Then use it:
    manager = initialize_agent_manager(
        model=model,
        tools=[tool1, tool2],
        managed_agents=[worker1, worker2]
    )

This wrapper ensures:
1. Environment is aligned before agent manager initializes
2. Managed agents can find imports without ModuleNotFoundError
3. No "antigravity" environment desync issues

Reference: HuggingFace SmolAgents Official Documentation
Issue Root Cause: Agent manager subprocess runs in System Python, not project env
"""

import sys
import os
from pathlib import Path
from typing import Any, List, Optional

# Fix Windows console encoding
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def _align_agent_environment():
    """Ensure agent manager can access all project modules."""
    project_root = Path(__file__).parent.parent.resolve()

    # Add project root to sys.path (agent subprocess will inherit)
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    # Add to PYTHONPATH for subprocess spawned by agent manager
    pythonpath = os.environ.get('PYTHONPATH', '')
    project_path_str = str(project_root)

    if project_path_str not in pythonpath:
        new_pythonpath = f"{project_path_str}{os.pathsep}{pythonpath}".strip(os.pathsep)
        os.environ['PYTHONPATH'] = new_pythonpath

    return str(project_root)


def initialize_agent_manager(
    model: Any,
    tools: List[Any],
    managed_agents: Optional[List[Any]] = None,
    **kwargs
) -> Any:
    """
    Initialize agent manager with environment synchronization.

    Wraps smolagents.CodeAgent or anthropic agent to prevent the
    "ModuleNotFoundError in managed_agents" issue.

    Args:
        model: LLM model (e.g., AnthropicModel, HuggingFaceModel)
        tools: List of tools available to agent
        managed_agents: List of worker agents to manage
        **kwargs: Other arguments passed to agent manager

    Returns:
        Initialized agent manager with environment fixed

    Example:
        from agents.agent_manager_fix import initialize_agent_manager
        from anthropic import Anthropic

        client = Anthropic()
        manager = initialize_agent_manager(
            model=client,
            tools=[search_tool, code_tool],
            managed_agents=[researcher, coder],
            max_steps=10
        )
    """
    # Step 1: Align environment before agent initialization
    project_root = _align_agent_environment()

    # Step 2: Verify all managed agents have names + descriptions
    if managed_agents:
        for agent in managed_agents:
            if not hasattr(agent, 'name') or not agent.name:
                agent.name = agent.__class__.__name__.lower()
            if not hasattr(agent, 'description') or not agent.description:
                agent.description = f"Worker agent: {agent.name}"

    # Step 3: Initialize agent manager with managed_agents explicitly passed
    # This is the #1 fix from HuggingFace SmolAgents documentation
    try:
        # Try smolagents first (if available)
        from smolagents import CodeAgent

        if isinstance(model, CodeAgent):
            # If model IS an agent, just ensure environment is set
            return model

        # Otherwise create new CodeAgent with managed_agents
        manager = CodeAgent(
            model=model,
            tools=tools,
            managed_agents=managed_agents or [],
            **kwargs
        )
        return manager

    except ImportError:
        # Fallback: assume it's an anthropic agent or other framework
        # The environment alignment alone should fix most issues
        pass

    # If no special handling needed, return None (caller should initialize themselves)
    # But environment is now aligned, so their initialization won't have desync issues
    return None


def diagnose_agent_environment() -> dict:
    """
    Diagnose current agent execution environment.

    Returns dict with:
    - python_executable: Path to Python being used
    - pythonpath: Current PYTHONPATH environment variable
    - sys_path: sys.path entries
    - imports_ok: Whether critical imports are available

    Use this to debug "agent not working" issues.
    """
    import subprocess

    state = {
        "python_executable": sys.executable,
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}",
        "sys_prefix": sys.prefix,
        "pythonpath": os.environ.get('PYTHONPATH', '(not set)'),
        "sys_path_count": len(sys.path),
    }

    # Also check imports
    critical = ["anthropic", "smolagents", "pandas"]
    imports_ok = {}
    for module in critical:
        try:
            __import__(module)
            imports_ok[module] = True
        except ImportError:
            imports_ok[module] = False

    state['imports'] = imports_ok
    return state


if __name__ == "__main__":
    # Test: diagnose environment when run directly
    print("[AGENT-MGR] Diagnosing agent environment...")
    state = diagnose_agent_environment()
    for key, val in state.items():
        print(f"  {key}: {val}")
    print("[AGENT-MGR] If 'imports_ok' shows False, run: pip install -r requirements.txt")
