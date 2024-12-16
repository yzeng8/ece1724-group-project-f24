#!/bin/bash

# Dataset file
DATASET="twitter200m.binedgelist"

# Iteration count for PageRank
ITERATIONS=35

# Number of vertices
NUM_VERTICES=41652231

# Output directory for logs
OUTPUT_DIR="pr_results_threads"
mkdir -p $OUTPUT_DIR

# Thread counts
THREAD_COUNTS=(1 2 4 8)

# Function to collect metrics
collect_metrics() {
  local threads=$1
  mpstat 1 > "$OUTPUT_DIR/pr_${threads}_cpu_metrics.log" &
  MPSTAT_PID=$!
  iostat -x 1 > "$OUTPUT_DIR/pr_${threads}_disk_metrics.log" &
  IOSTAT_PID=$!
  sar -u -r 1 > "$OUTPUT_DIR/pr_${threads}_sar_metrics.log" &
  SAR_PID=$!
}

# Function to stop metrics collection
stop_metrics() {
  kill $MPSTAT_PID
  kill $IOSTAT_PID
  kill $SAR_PID
}

# Run PageRank for each thread count
for threads in "${THREAD_COUNTS[@]}"; do
  echo "Running PageRank with $threads thread(s) on $DATASET..."

  # Start metric collection
  collect_metrics "$threads"

  # Run the PageRank command
  if [ -f "datasets/$DATASET" ]; then
    mpirun --host localhost --bind-to none --use-hwthread-cpus --oversubscribe -np "$threads" ./toolkits/pagerank "datasets/$DATASET" $NUM_VERTICES $ITERATIONS | tee "$OUTPUT_DIR/pr_${threads}_output.log"
  else
    echo "Dataset file datasets/$DATASET not found! Skipping..."
  fi

  # Stop metric collection
  stop_metrics

  echo "Finished PageRank with $threads thread(s). Logs saved to $OUTPUT_DIR."
done

# Print execution times summary
echo "===== PageRank Execution Times by Thread Count ====="
for threads in "${THREAD_COUNTS[@]}"; do
  if [ -f "$OUTPUT_DIR/pr_${threads}_output.log" ]; then
    echo -n "$threads thread(s): "
    grep "exec_time" "$OUTPUT_DIR/pr_${threads}_output.log" | awk '{print $2}' | tail -n 1
  else
    echo "$threads thread(s): No log file found."
  fi
done

echo "Logs saved to: $OUTPUT_DIR"
