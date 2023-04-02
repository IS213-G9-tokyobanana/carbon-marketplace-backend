#!/bin/bash

# List of Python scripts to run
SCRIPTS=(
    "run_payment_failed_worker.py"
    "run_payment_success_worker.py"
    "run_start_payment_worker.py"
)

# Start each script in the background
for SCRIPT in "${SCRIPTS[@]}"; do
    python "$SCRIPT" &
done

wait

echo "exited"
