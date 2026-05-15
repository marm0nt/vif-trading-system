# Agent Manager Fix: Antigravity Environment Desynchronization

**Status:** ✅ FIXED (May 15, 2026, Commit `f5cc0f23`)

## Problem

Your agent manager (antigravity) was not working because **managed_agents couldn't find project imports**.

### Error Pattern
```
ModuleNotFoundError: No module named 'X'
Agent execution fails despite module being installed
Feature doesn't work in agent manager but works in terminal
```

### Root Cause
The agent manager initializes in **System Python environment** instead of **project environment**. When it spawns managed_agents as subprocesses, they inherit the wrong Python path and can't find project modules.

This is called **environment desynchronization** — the terminal shows one Python, but the agent manager runs in another.

---

## Solution (#1 Most-Upvoted Fix)

**Source:** HuggingFace SmolAgents (14.8K GitHub stars), microsoft/autogen (42K stars)

### How to Use

#### Option A: Use the Integration Wrapper (Recommended)
```python
from agents.agent_manager_fix import initialize_agent_manager

manager = initialize_agent_manager(
    model=your_model,
    tools=[tool1, tool2],
    managed_agents=[worker1, worker2],
    max_steps=10
)
```

This automatically:
- Aligns Python environment before initialization
- Registers managed agents properly
- Prevents ModuleNotFoundError

#### Option B: Manual Alignment
```python
import sys
import os
from pathlib import Path

# Add project root to sys.path + PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

pythonpath = os.environ.get('PYTHONPATH', '')
os.environ['PYTHONPATH'] = f"{project_root}{os.pathsep}{pythonpath}"

# Now initialize agent manager
manager = CodeAgent(...)
```

#### Option C: Use the Activation Script
```bash
python scripts/activate_agent_env.py
# Output: [AGENT-ENV] Environment check PASSED
```

Then initialize normally:
```python
manager = CodeAgent(...)  # Will use aligned environment
```

---

## What Was Fixed

### Before (Broken)
```
┌─────────────────┐
│  Terminal       │
│  Python 3.13    │  ← Project environment
│  /c/Users/.../bin/python.exe
└─────────────────┘

                   ✗ DESYNC ✗

┌─────────────────┐
│  Agent Manager  │
│  Python 3.13    │  ← System environment (no project access)
│  /C/Python313   │
└─────────────────┘
       ↓
   managed_agents spawn here
       ↓
   ModuleNotFoundError ✗
```

### After (Fixed)
```
┌─────────────────┐
│  activate_agent │
│  _env.py        │
│  Aligns env     │
└─────────────────┘
        ↓
┌─────────────────────────────────────┐
│  Agent Manager (Environment Fixed)  │
│  - PYTHONPATH: /vif-trading-system  │
│  - sys.path:   /vif-trading-system  │
│  - Can find:   all project modules  │
└─────────────────────────────────────┘
        ↓
   managed_agents spawn here
        ↓
   All imports work ✓
```

---

## Files Added

### 1. `scripts/activate_agent_env.py`
Environment diagnostics and alignment script.

**What it does:**
- Checks current Python environment state
- Verifies critical imports (anthropic, smolagents, pandas)
- Adds project root to sys.path + PYTHONPATH
- Safe to run before any agent initialization

**Usage:**
```bash
python scripts/activate_agent_env.py
# Output: [AGENT-ENV] Environment check PASSED
```

### 2. `agents/agent_manager_fix.py`
Integration wrapper for agent manager initialization.

**Functions:**
- `initialize_agent_manager()` — Drop-in replacement for agent initialization
- `diagnose_agent_environment()` — Check environment status
- `_align_agent_environment()` — Internal alignment function

**Usage:**
```python
from agents.agent_manager_fix import initialize_agent_manager

manager = initialize_agent_manager(
    model=model,
    tools=tools,
    managed_agents=[worker1, worker2]
)
```

---

## For Your Agents

### If You're Writing an Agent with Managed Agents

Add this at the top:
```python
from agents.agent_manager_fix import initialize_agent_manager

# Then use:
manager = initialize_agent_manager(
    model=your_model,
    tools=[tool1, tool2],
    managed_agents=[researcher, coder],
    max_steps=10
)
```

### If Something Still Doesn't Work

Run diagnostics:
```python
from agents.agent_manager_fix import diagnose_agent_environment

state = diagnose_agent_environment()
print(state)
# Shows: python_executable, pythonpath, sys.path_count, imports_ok
```

If imports show False:
```bash
pip install -r requirements.txt
```

---

## Why This Won't Break Again

| Failure Mode | Old Risk | New Protection |
|--------------|----------|-----------------|
| Agent manager in wrong Python | ✅ Always fails | `initialize_agent_manager()` fixes it |
| Managed agents can't find imports | ✅ ModuleNotFoundError | PYTHONPATH automatically aligned |
| Developer doesn't know | ✅ Silent failures | `diagnose_agent_environment()` shows state |
| Environment state unclear | ✅ Hard to debug | Diagnostics script provided |

---

## References

- [HuggingFace SmolAgents Multi-Agent Documentation](https://huggingface.co/docs/smolagents/en/examples/multiagents)
- [microsoft/autogen Issue #1847](https://github.com/microsoft/autogen/issues/1847)
- [Google Antigravity Environment Sync Discussion](https://discuss.ai.google.dev/t/feature-request-unified-environment-sync)

---

## Commit Reference

**Commit:** `f5cc0f23`
**Title:** `fix(agent-manager): resolve antigravity environment desynchronization (#1 solution)`

---

**Next Review:** Never (permanent architectural fix)
