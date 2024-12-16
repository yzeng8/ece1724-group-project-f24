#!/bin/bash

# Dataset and configuration
DATASET="twitter200m.binedgelist"
NUM_VERTICES=41652231
ROOT=0
OUTPUT_DIR="bfs_results_threads"
THREAD_COUNTS=(1 2 4 6 8)  # Number of threads to test

# Create output directory
mkdir -p $OUTPUT_DIR

# Function to collect metrics
collect_metrics() {
  local threads=$1
  # CPU, memory, and disk metrics
  mpstat 1 > "$OUTPUT_DIR/${DATASET}_threads${threads}_cpu_metrics.log" &
  MPSTAT_PID=$!
  iostat -x 1 > "$OUTPUT_DIR/${DATASET}_threads${threads}_disk_metrics.log" &
  IOSTAT_PID=$!
  sar -u -r 1 > "$OUTPUT_DIR/${DATASET}_threads${threads}_sar_metrics.log" &
  SAR_PID=$!
}

# Function to stop metrics collection
stop_metrics() {
  kill $MPSTAT_PID
  kill $IOSTAT_PID
  kill $SAR_PID
}

# Run BFS with different thread counts
for threads in "${THREAD_COUNTS[@]}"; do
  echo "Running BFS with $threads thread(s) on $DATASET..."

  # Start metrics collection
  collect_metrics "$threads"

  # Run BFS and capture the output
  mpirun --bind-to none -np $threads ./toolkits/bfs "datasets/$DATASET" $NUM_VERTICES $ROOT | \
  tee "$OUTPUT_DIR/${DATASET}_threads${threads}_bfs_output.log"

  # Stop metrics collection
  stop_metrics

  echo "Finished BFS with $threads thread(s). Logs saved to $OUTPUT_DIR."
done

# Print summary of execution times
echo "===== BFS Execution Times by Thread Count ====="
for threads in "${THREAD_COUNTS[@]}"; do
  log_file="$OUTPUT_DIR/${DATASET}_threads${threads}_bfs_output.log"
  if [ -f "$log_file" ]; then
    echo -n "$threads thread(s): "
    grep "exec_time" "$log_file" | awk '{print $2}' | tail -n 1
  else
    echo "$threads thread(s): No log file found."
  fi
done

echo "Logs saved to: $OUTPUT_DIR"
