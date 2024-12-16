#!/bin/bash

# Path to datasets and output log directory
DATASET_DIR="/home/zengyuyang1999/ece1724-group-project-f24/ece1724-project/data"
OUTPUT_LOG_DIR="/home/zengyuyang1999/ece1724-group-project-f24/ece1724-project/logs"
SPARK_APP_JAR="/home/zengyuyang1999/ece1724-group-project-f24/ece1724-project/graphxBrockPR.jar"
CLASS_NAME="graphxBrockPR"
SPARK_MASTER="local[*]"
SPARK_DRIVER_MEMORY="2g"
PACKAGES="org.apache.spark:spark-graphx_2.12:3.4.4,graphframes:graphframes:0.8.3-spark3.4-s_2.12"

# Ensure log directory exists
mkdir -p $OUTPUT_LOG_DIR

# Manually maintained list of files to process
FILES_LIST=(
    "brock400_4.clq"
    "brock800_4.clq"
    # "twitter-2010-100k.txt"
    # "twitter-2010-1m.txt"
    # "twitter-2010-5m.txt"
    # "twitter-2010-50m.txt"
    # "twitter-2010-100m.txt"
    # "twitter-2010-200m.txt"
    # Add more file names here as needed
)

# Function to monitor resources
monitor_resources() {
    local dataset_name=$1
    local log_prefix=$OUTPUT_LOG_DIR/metrics-${dataset_name}

    echo "Starting resource monitoring for dataset $dataset_name..."

    # Monitor CPU, memory, and I/O
    sar -u 1 > ${log_prefix}-cpu.log &
    SAR_PID=$!
    iostat -dx 1 > ${log_prefix}-disk.log &
    IOSTAT_PID=$!
    free -m -s 1 > ${log_prefix}-memory.log &
    FREE_PID=$!

    # Return PIDs for monitoring processes
    echo "$SAR_PID $IOSTAT_PID $FREE_PID"
}

# Function to stop monitoring resources
stop_resources() {
    local sar_pid=$1
    local iostat_pid=$2
    local free_pid=$3
    echo "Stopping resource monitoring..."
    kill $sar_pid $iostat_pid $free_pid
}

# Function to calculate throughput performance
calculate_throughput() {
    local dataset_path=$1
    local log_file=$2

    local file_size=$(du -b "$dataset_path" | cut -f1) # Get file size in bytes
    local execution_time=$(grep -oP 'took \K[\d.]+' "$log_file" | tail -1) # Extract execution time in seconds

    if [[ -z "$execution_time" || -z "$file_size" ]]; then
        echo "Throughput: Data or execution time not found" >> "$log_file"
    else
        local throughput=$(echo "$file_size / $execution_time" | bc -l)
        echo "Throughput: $(printf "%.2f" $throughput) bytes/second" >> "$log_file"
    fi
}

# Process each file in the manual list
for file_name in "${FILES_LIST[@]}"; do
    DATASET_PATH="$DATASET_DIR/$file_name"
    dataset_name=$(basename "$file_name" .txt)
    LOG_FILE="$OUTPUT_LOG_DIR/spark-job-$dataset_name.log"

    echo "Processing dataset: $DATASET_PATH"

    # Check if dataset exists
    if [[ ! -f $DATASET_PATH ]]; then
        echo "Dataset $DATASET_PATH not found. Skipping..."
        continue
    fi

    # Start resource monitoring
    read SAR_PID IOSTAT_PID FREE_PID <<< $(monitor_resources "$dataset_name")

    # Record start time
    START_TIME=$(date +%s)

    # Run the Spark job
    spark-submit \
        --class $CLASS_NAME \
        --master $SPARK_MASTER \
        --driver-memory $SPARK_DRIVER_MEMORY \
        --packages $PACKAGES \
        $SPARK_APP_JAR \
        file://$DATASET_PATH 1 > $LOG_FILE 2>&1

    # Record end time
    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))
    echo "Execution Time: $DURATION seconds" >> $LOG_FILE

    # Stop resource monitoring
    stop_resources $SAR_PID $IOSTAT_PID $FREE_PID

    # Calculate throughput performance
    calculate_throughput "$DATASET_PATH" "$LOG_FILE"

    echo "Finished processing dataset: $DATASET_PATH"
    echo "Logs saved to $LOG_FILE and metrics to $OUTPUT_LOG_DIR/metrics-${dataset_name}-*"
done

echo "All datasets processed."
