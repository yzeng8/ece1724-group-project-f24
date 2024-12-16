#!/bin/bash

# Dataset file
DATASET="twitter100m.binedgelist"

# Number of vertices and root
NUM_VERTICES=41652231
ROOT=0

# Output directory for logs
OUTPUT_DIR="bfs_distributed_results"
mkdir -p $OUTPUT_DIR

# Hostfile path
HOSTFILE="$HOME/hostfile"

# Array of process counts
# PROCESS_COUNTS=(2 4 8)
PROCESS_COUNTS=(16)
# PROCESS_COUNTS=(4 8)

# Function to collect metrics
collect_metrics() {
  local process_count=$1
  mpstat 1 > "$OUTPUT_DIR/mpstat_${process_count}_procs.log" &
  MPSTAT_PID=$!
  iostat -x 1 > "$OUTPUT_DIR/iostat_${process_count}_procs.log" &
  IOSTAT_PID=$!
  sar -u -r 1 > "$OUTPUT_DIR/sar_${process_count}_procs.log" &
  SAR_PID=$!
}

# Function to stop metrics collection
stop_metrics() {
  kill $MPSTAT_PID
  kill $IOSTAT_PID
  kill $SAR_PID
}

# Run BFS for each process count
for num_procs in "${PROCESS_COUNTS[@]}"; do
  echo "Running distributed BFS with $num_procs processes..."

  # Start metric collection
  collect_metrics "$num_procs"

  # Run distributed BFS with verbose MPI logging
  mpirun --hostfile $HOSTFILE -np $num_procs --map-by ppr:$((num_procs/2)):node \
    --display-map --report-bindings \
    --output-filename "$OUTPUT_DIR/bfs_${num_procs}_mpi_output" \
    ./toolkits/bfs "datasets/$DATASET" $NUM_VERTICES $ROOT

  # Stop metric collection
  stop_metrics

  echo "Finished BFS with $num_procs processes. Logs saved to $OUTPUT_DIR."
done

# Print summary
echo "===== BFS Distributed Execution Complete ====="
echo "Logs and outputs have been saved to $OUTPUT_DIR."
