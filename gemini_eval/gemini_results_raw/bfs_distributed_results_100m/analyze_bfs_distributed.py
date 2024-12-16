import os
import re
import csv

# Define the directory containing the results
base_dir = "./"
process_counts = ["2", "4", "8", "16"]

# Function to parse execution logs
def parse_exec_logs(file_path):
    try:
        with open(file_path, "r") as f:
            for line in f:
                if "exec_time=" in line:
                    return float(line.split("=")[-1].replace("(s)", "").strip())
    except FileNotFoundError:
        print(f"Execution log not found: {file_path}")
    return 0.0

# Function to parse MPI logs
def parse_mpi_logs(file_path):
    total_send_time, total_recv_time = 0.0, 0.0
    send_count, recv_count = 0, 0
    try:
        with open(file_path, "r") as f:
            for line in f:
                send_match = re.search(r"MPI_Send.*Time: ([0-9.]+)s", line)
                recv_match = re.search(r"MPI_Recv.*Time: ([0-9.]+)s", line)
                if send_match:
                    total_send_time += float(send_match.group(1))
                    send_count += 1
                elif recv_match:
                    total_recv_time += float(recv_match.group(1))
                    recv_count += 1
    except FileNotFoundError:
        print(f"MPI log not found: {file_path}")
    return (total_send_time / send_count if send_count else 0.0,
            total_recv_time / recv_count if recv_count else 0.0)

# Function to parse system metrics
def parse_system_metrics(file_path, metric_type):
    total, count = 0.0, 0
    try:
        with open(file_path, "r") as f:
            for line in f:
                tokens = line.split()
                if len(tokens) < 2:
                    continue  # Skip lines without enough tokens
                try:
                    if metric_type == "cpu" and tokens and tokens[0] == "all":
                        total += 100.0 - float(tokens[-1])  # Idle % -> CPU Usage
                        count += 1
                    elif metric_type == "disk" and tokens[0] == "sda":
                        total += float(tokens[-1])  # %util
                        count += 1
                    elif metric_type == "memory" and tokens[0] == "all":
                        total += float(tokens[3])  # %memused
                        count += 1
                except ValueError:
                    continue  # Skip lines with non-numeric data
    except FileNotFoundError:
        print(f"System metric log not found: {file_path}")
    return total / count if count else 0.0

# Analyze and collect results
results = []
for count in process_counts:
    metrics = {
        "Processes": int(count),
        "Execution Time (s)": parse_exec_logs(os.path.join(base_dir, f"bfs_{count}_mpi_output.log")),
        "Avg CPU Usage (%)": parse_system_metrics(os.path.join(base_dir, f"mpstat_{count}_procs.log"), "cpu"),
        "Avg Disk Utilization (%)": parse_system_metrics(os.path.join(base_dir, f"iostat_{count}_procs.log"), "disk"),
        "Avg Memory Usage (%)": parse_system_metrics(os.path.join(base_dir, f"sar_{count}_procs.log"), "memory"),
        "MPI Send Time (s)": parse_mpi_logs(os.path.join(base_dir, f"mpi_logs_100m_{count}process.log"))[0],
        "MPI Recv Time (s)": parse_mpi_logs(os.path.join(base_dir, f"mpi_logs_100m_{count}process.log"))[1],
    }
    results.append(metrics)

# Print results to terminal
header = "Processes\tExecution Time (s)\tAvg CPU Usage (%)\tAvg Disk Utilization (%)\tAvg Memory Usage (%)\tMPI Send Time (s)\tMPI Recv Time (s)"
print(header)
for result in results:
    print(f"{result['Processes']}\t{result['Execution Time (s)']:.3f}\t{result['Avg CPU Usage (%)']:.2f}\t{result['Avg Disk Utilization (%)']:.2f}\t{result['Avg Memory Usage (%)']:.2f}\t{result['MPI Send Time (s)']:.3f}\t{result['MPI Recv Time (s)']:.3f}")

# Write results to CSV
output_file = "bfs_distributed_100m_results.csv"
with open(output_file, "w", newline="") as csvfile:
    fieldnames = ["Processes", "Execution Time (s)", "Avg CPU Usage (%)", "Avg Disk Utilization (%)", "Avg Memory Usage (%)", "MPI Send Time (s)", "MPI Recv Time (s)"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(results)

print(f"Results saved to {output_file}")
