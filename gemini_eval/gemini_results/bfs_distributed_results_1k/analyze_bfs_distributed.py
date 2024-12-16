
import os
import pandas as pd
import glob
import re

def parse_bfs_output(file_path):
    exec_times = []
    with open(file_path, 'r') as file:
        for line in file:
            if "exec_time" in line:
                exec_times.append(float(line.split('=')[1].strip().replace('(s)', '')))
    return sum(exec_times) / len(exec_times) if exec_times else 0

def parse_cpu_metrics(file_path):
    cpu_usage = []
    with open(file_path, 'r') as file:
        for line in file:
            if 'all' in line:
                parts = line.split()
                if len(parts) >= 11:
                    cpu_usage.append(100 - float(parts[-1]))  # %idle -> CPU Usage
    return sum(cpu_usage) / len(cpu_usage) if cpu_usage else 0

def parse_disk_metrics(file_path):
    disk_util = []
    with open(file_path, 'r') as file:
        for line in file:
            if 'sda' in line:
                parts = line.split()
                if len(parts) >= 18:
                    disk_util.append(float(parts[-1]))  # %util
    return sum(disk_util) / len(disk_util) if disk_util else 0

def parse_memory_metrics(file_path):
    memory_usage = []
    with open(file_path, 'r') as file:
        for line in file:
            if '%memused' in line:
                next_line = next(file, None)
                if next_line:
                    parts = next_line.split()
                    if len(parts) >= 4:
                        memory_usage.append(float(parts[3]))
    return sum(memory_usage) / len(memory_usage) if memory_usage else 0

def parse_mpi_logs(file_path):
    send_times = []
    recv_times = []
    with open(file_path, 'r') as file:
        for line in file:
            if "MPI_Send" in line:
                match = re.search(r"Time: ([0-9\.]+)s", line)
                if match:
                    send_times.append(float(match.group(1)))
            elif "MPI_Recv" in line:
                match = re.search(r"Time: ([0-9\.]+)s", line)
                if match:
                    recv_times.append(float(match.group(1)))
    avg_send_time = sum(send_times) / len(send_times) if send_times else 0
    avg_recv_time = sum(recv_times) / len(recv_times) if recv_times else 0
    return avg_send_time, avg_recv_time

def analyze_bfs_metrics(output_dir):
    results = []
    process_counts = ["2", "4", "8", "16"]

    for count in process_counts:
        bfs_file = os.path.join(output_dir, f"bfs_{count}_mpi_output.log")
        cpu_file = os.path.join(output_dir, f"mpstat_{count}_procs.log")
        disk_file = os.path.join(output_dir, f"iostat_{count}_procs.log")
        memory_file = os.path.join(output_dir, f"sar_{count}_procs.log")
        mpi_file = os.path.join(output_dir, f"mpi_logs_1k_{count}process.log")
        # print(f"Checking files for process count {count}:")
        # print(f"BFS File: {bfs_file}, Exists: {os.path.exists(bfs_file)}")
        # print(f"CPU File: {cpu_file}, Exists: {os.path.exists(cpu_file)}")
        # print(f"Disk File: {disk_file}, Exists: {os.path.exists(disk_file)}")
        # print(f"Memory File: {memory_file}, Exists: {os.path.exists(memory_file)}")
        # print(f"MPI File: {mpi_file}, Exists: {os.path.exists(mpi_file)}")


        if not (os.path.exists(bfs_file) and os.path.exists(cpu_file) and os.path.exists(disk_file) and os.path.exists(memory_file) and os.path.exists(mpi_file)):
            print(f"Missing files for process count {count}. Skipping...")
            continue

        exec_time = parse_bfs_output(bfs_file)
        avg_cpu = parse_cpu_metrics(cpu_file)
        avg_disk = parse_disk_metrics(disk_file)
        avg_memory = parse_memory_metrics(memory_file)
        mpi_send, mpi_recv = parse_mpi_logs(mpi_file)

        results.append({
            "Processes": int(count),
            "Execution Time (s)": exec_time,
            "Avg CPU Usage (%)": avg_cpu,
            "Avg Disk Utilization (%)": avg_disk,
            "Avg Memory Usage (%)": avg_memory,
            "MPI Send Time (s)": mpi_send,
            "MPI Recv Time (s)": mpi_recv
        })

    df = pd.DataFrame(results)
    return df

if __name__ == "__main__":
    output_dir = "."  # Current directory
    # print('output dir is: ', output_dir)
    results = analyze_bfs_metrics(output_dir)
    if not results.empty:
        print("{:<10} {:<20} {:<20} {:<25} {:<25} {:<20} {:<20}".format(
            "Processes", "Execution Time (s)", "Avg CPU Usage (%)",
            "Avg Disk Utilization (%)", "Avg Memory Usage (%)",
            "MPI Send Time (s)", "MPI Recv Time (s)"
        ))
        print("=" * 120)
        for _, row in results.iterrows():
            print("{:<10} {:<20.3f} {:<20.2f} {:<25.2f} {:<25.2f} {:<20.3f} {:<20.3f}".format(
                row['Processes'], row['Execution Time (s)'], row['Avg CPU Usage (%)'],
                row['Avg Disk Utilization (%)'], row['Avg Memory Usage (%)'],
                row['MPI Send Time (s)'], row['MPI Recv Time (s)']
            ))
        results.to_csv(os.path.join(output_dir, "bfs_distributed_1k_results.csv"), index=False)
        print("Results saved to bfs_distributed_1k_results.csv")
    else:
        print("No metrics data processed. Please check the log files.")
