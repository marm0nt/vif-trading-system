#!/bin/bash
# Log all tool uses to claude-audit.jsonl for session audit trail
mkdir -p logs
AUDIT_LOG="logs/claude-audit.jsonl"
jq --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --arg tool "$TOOL_NAME" '
  {
    timestamp: $ts,
    tool: $tool,
    duration_ms: (.duration_ms // null),
    success: (.status == "success"),
    exit_code: (.exit_code // null)
  }
' < /dev/stdin >> "$AUDIT_LOG" 2>/dev/null
exit 0
