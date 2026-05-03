#!/bin/bash
# Guard against accidental live trade execution commands
COMMAND=$(jq -r '.tool_input.command' < /dev/stdin)
if echo "$COMMAND" | grep -qiE 'execute_trade|place_order|submit_order|live.*trade|market.*order'; then
  jq -n '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"ask","permissionDecisionReason":"This command looks like live trade execution. Confirm to proceed."}}'
  exit 0
fi
exit 0
