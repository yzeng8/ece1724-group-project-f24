#!/bin/bash

# Dataset files and iteration counts
DATASETS=(
  "twitter1k.binedgelist"
  "twitter10k.binedgelist"
  "twitter100k.binedgelist"
  "twitter1m.binedgelist"
  "twitter5m.binedgelist"
  "twitter50m.binedgelist"
  "twitter100m.binedgelist"
  "twitter200m.binedgelist"
)
ITERATIONS=(5 5 10 10 20 30 35 35)

# Number of vertices
NUM_VERTICES=41652231

# Output directory for logs
OUTPUT_DIR="pr_results_sin_thread"
mkdir -p $OUTPUT_DIR

# Function to collect metrics
collect_metrics() {
  local dataset=$1
  # Check if mpstat exists
  if command -v mpstat > /dev/null 2>&1; then
    mpstat 1 > "$OUTPUT_DIR/${dataset}_cpu_metrics.log" &
    MPSTAT_PID=$!
  else
    echo "mpstat not found. Skipping CPU metrics collection."
    MPSTAT_PID=""
  fi

  # Check if iostat exists
  if command -v iostat > /dev/null 2>&1; then
    iostat -x 1 > "$OUTPUT_DIR/${dataset}_disk_metrics.log" &
    IOSTAT_PID=$!
  else
    echo "iostat not found. Skipping disk metrics collection."
    IOSTAT_PID=""
  fi

  # Check if sar exists
  if command -v sar > /dev/null 2>&1; then
    sar -u -r 1 > "$OUTPUT_DIR/${dataset}_sar_metrics.log" &
    SAR_PID=$!
  else
    echo "sar not found. Skipping system metrics collection."
    SAR_PID=""
  fi
}

# Function to stop metric collection
stop_metrics() {
  [ -n "$MPSTAT_PID" ] && kill $MPSTAT_PID
  [ -n "$IOSTAT_PID" ] && kill $IOSTAT_PID
  [ -n "$SAR_PID" ] && kill $SAR_PID
}

# Run PageRank for each dataset
for i in "${!DATASETS[@]}"; do
  dataset="${DATASETS[i]}"
  iterations="${ITERATIONS[i]}"
  echo "Running PageRank on $dataset with $iterations iterations..."

  # Start metric collection
  collect_metrics "$dataset"

  # Run the PageRank command and save the output
  if [ -f "datasets/$dataset" ]; then
    mpirun --bind-to none -np 1 ./toolkits/pagerank "datasets/$dataset" $NUM_VERTICES $iterations | tee "$OUTPUT_DIR/${dataset}_pr_output.log"
  else
    echo "Dataset file datasets/$dataset not found! Skipping..."
  fi

  # Stop metric collection
  stop_metrics

  echo "Finished PageRank on $dataset. Logs saved to $OUTPUT_DIR."
done

# Print summary of execution times
echo "===== PageRank Execution Times ====="
for dataset in "${DATASETS[@]}"; do
  if [ -f "$OUTPUT_DIR/${dataset}_pr_output.log" ]; then
    echo -n "$dataset: "
    grep "exec_time" "$OUTPUT_DIR/${dataset}_pr_output.log" | awk '{print $2}' | tail -n 1
  else
    echo "$dataset: No log file found."
  fi
done

echo "Logs saved to: $OUTPUT_DIR"
