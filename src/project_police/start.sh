#!/bin/bash

# List of Python scripts to run
SCRIPTS=(
    "run_penalise_reward_worker.py"
    "run_rollback_worker.py"
)

# Start each script in the background
for SCRIPT in "${SCRIPTS[@]}"; do
    python "$SCRIPT" &
done

wait

echo "exited"
