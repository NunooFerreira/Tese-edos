#!/bin/bash

# File to store the pod count logs
OUTPUT_FILE="pod_counts.log"

# Infinite loop to monitor pod count every 30 seconds
while true; do
    # Get the current timestamp
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

    # Count the number of pods in 'Running' state
    POD_COUNT=$(kubectl get pods --no-headers | grep -c 'Running')

    # Append the timestamp and pod count to the output file
    echo "$TIMESTAMP - Running Pods: $POD_COUNT" >> "$OUTPUT_FILE"

    # Wait for 30 seconds before the next check
    sleep 2
done
