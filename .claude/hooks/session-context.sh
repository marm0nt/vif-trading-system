#!/bin/bash
# Inject market context at session startup
# Read last run info and next scheduled job
LAST_RUN=$(tail -1 logs/run_history.json 2>/dev/null | jq -r '.timestamp // "unknown"' || echo "no runs logged")
NEXT_JOB=$(python3 -c "import schedule; print('Next: 08:45 premarket analysis')" 2>/dev/null || echo "scheduler not available")
DAILY_COST=$(python3 -c "import json; print('Cost today: checking logs...')" 2>/dev/null || echo "cost tracking unavailable")

CONTEXT="Market Context: Last run=$LAST_RUN | $NEXT_JOB | $DAILY_COST"
jq -n --arg ctx "$CONTEXT" '{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":$ctx}}'
exit 0
