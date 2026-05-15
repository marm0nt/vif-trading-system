#!/usr/bin/env python3
"""
VIF Trading System Bootstrap Guard — Prevents Venv Path Failures

CRITICAL: Every agent/script MUST import this at module startup:
    from bootstrap import ensure_environment_ready

This guard:
1. Detects broken/missing venv references
2. Validates system Python is usable
3. Prevents subprocess failures from venv path issues
4. Logs environment state for debugging

Philosophy: Use system Python, never hardcode venv paths.
All dependencies installed globally via pyproject.toml + pip.
"""

import sys
import os
import subprocess
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Environment constants
SCRIPT_ROOT = Path(__file__).parent.resolve()
PYTHON_EXECUTABLE = sys.executable
VENV_DANGER_PATTERNS = [
    "venv/Scripts/python.exe",
    ".venv/Scripts/python.exe",
    "venv/bin/python",
    ".venv/bin/python",
    r"\.venv\\Scripts",
    r"venv\\Scripts",
]

def _check_venv_references():
    """Scan main agent/script files for hardcoded venv path patterns (early warning)."""
    dangerous_files = []

    for pattern in [
        SCRIPT_ROOT / "agents" / "*.py",
        SCRIPT_ROOT / "scripts" / "*.py",
        SCRIPT_ROOT / "schedule_daily.py",
    ]:
        for py_file in SCRIPT_ROOT.glob(pattern.name) if "*" in pattern.name else [pattern]:
            if not py_file.exists():
                continue

            try:
                content = py_file.read_text(errors="ignore")
                # Check for hardcoded venv subprocess calls (dangerous patterns)
                if any(pattern in content for pattern in [
                    'subprocess.run([',
                    'Popen([',
                    '"venv',
                    "'venv",
                ]):
                    # Do deeper inspection for actual venv/Scripts patterns
                    for danger in VENV_DANGER_PATTERNS:
                        if danger in content:
                            dangerous_files.append(str(py_file.relative_to(SCRIPT_ROOT)))
                            logger.warning(f"⚠ {py_file.name} contains hardcoded venv path: {danger}")
                            break
            except Exception as e:
                logger.debug(f"Could not scan {py_file}: {e}")

    return dangerous_files

def _verify_python_executable():
    """Verify current Python is usable and accessible."""
    try:
        result = subprocess.run(
            [PYTHON_EXECUTABLE, "--version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode != 0:
            raise RuntimeError(f"Python check failed: {result.stderr}")
        version = result.stdout.strip()
        logger.debug(f"✓ Python executable valid: {PYTHON_EXECUTABLE} ({version})")
        return True
    except Exception as e:
        logger.error(f"✗ Python executable check failed: {e}")
        logger.error(f"  Using: {PYTHON_EXECUTABLE}")
        return False

def _verify_imports():
    """Verify critical imports are available."""
    required = ["anthropic", "schedule", "pandas", "numpy"]
    missing = []

    for module in required:
        try:
            __import__(module)
            logger.debug(f"✓ {module} available")
        except ImportError:
            missing.append(module)
            logger.warning(f"⚠ {module} not found")

    return len(missing) == 0

def ensure_environment_ready(component_name: str = "Unknown") -> bool:
    """
    Validate environment before running any agent/script.

    Call this at the TOP of your module:
        from bootstrap import ensure_environment_ready
        ensure_environment_ready(__name__)

    Returns: True if safe to continue, False if critical issues found.
    """
    logger.info(f"[BOOTSTRAP] Initializing {component_name}")

    # Check 1: Python is usable
    python_ok = _verify_python_executable()
    if not python_ok:
        logger.critical("Python executable check failed. Cannot proceed.")
        return False

    # Check 2: Imports are available
    imports_ok = _verify_imports()
    if not imports_ok:
        logger.warning("Some imports missing, but continuing (may fail later)")

    # Check 3: Scan for venv hardcoding (early warning)
    dangerous = _check_venv_references()
    if dangerous:
        logger.warning(f"⚠ Found {len(dangerous)} files with potential venv hardcoding:")
        for f in dangerous:
            logger.warning(f"  - {f}")
        logger.warning("These must be fixed to use system Python directly.")

    # Log environment for debugging
    logger.debug(f"  Python: {PYTHON_EXECUTABLE}")
    logger.debug(f"  CWD: {os.getcwd()}")
    logger.debug(f"  PYTHONPATH: {os.environ.get('PYTHONPATH', 'not set')}")

    return python_ok

# Auto-init: log on import
def _setup_logging():
    """Configure basic logging if not already configured."""
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s [BOOTSTRAP] %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)

_setup_logging()

# On first import, run a quick check
_verify_python_executable()
