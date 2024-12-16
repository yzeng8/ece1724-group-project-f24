import os
import glob
import pandas as pd
import re

def parse_bfs_output(file_path):
    exec_times = []
    with open(file_path, 'r') as file:
        for line in file:
            if "exec_time" in line:
                exec_times.append(float(line.split('=')[1].strip().replace('(s)', '')))
    return {
        'average_exec_time': sum(exec_times) / len(exec_times) if exec_times else 0,
        'exec_times': exec_times
    }

def parse_cpu_metrics(file_path):
    cpu_usage = []
    with open(file_path, 'r') as file:
        for line in file:
            if 'all' in line:
                parts = line.split()
                if len(parts) >= 11:
                    cpu_usage.append(100 - float(parts[-1]))  # %idle -> CPU Usage
    return {
        'average_cpu_usage': sum(cpu_usage) / len(cpu_usage) if cpu_usage else 0,
        'cpu_usage': cpu_usage
    }

def parse_disk_metrics(file_path):
    disk_util = []
    with open(file_path, 'r') as file:
        for line in file:
            if 'sda' in line:
                parts = line.split()
                if len(parts) >= 18:
                    disk_util.append(float(parts[-1]))  # %util
    return {
        'average_disk_util': sum(disk_util) / len(disk_util) if disk_util else 0,
        'disk_util': disk_util
    }

def parse_sar_metrics(file_path):
    memory_usage = []
    with open(file_path, 'r') as file:
        for line in file:
            if '%memused' in line:
                next_line = next(file, None)
                if next_line:
                    parts = next_line.split()
                    if len(parts) >= 4:
                        memory_usage.append(float(parts[3]))
    return {
        'average_memory_usage': sum(memory_usage) / len(memory_usage) if memory_usage else 0,
        'memory_usage': memory_usage
    }

def parse_mpi_logs(file_path):
    send_times, recv_times = [], []
    try:
        with open(file_path, 'r') as file:
            for line in file:
                send_match = re.search(r"MPI_Send.*Time: ([0-9.]+)s", line)
                recv_match = re.search(r"MPI_Recv.*Time: ([0-9.]+)s", line)
                if send_match:
                    send_times.append(float(send_match.group(1)))
                if recv_match:
                    recv_times.append(float(recv_match.group(1)))
    except FileNotFoundError:
        print(f"MPI log not found: {file_path}")
    return {
        'average_send_time': sum(send_times) / len(send_times) if send_times else 0,
        'average_recv_time': sum(recv_times) / len(recv_times) if recv_times else 0
    }

def analyze_metrics(output_dir):
    datasets = []
    for bfs_file in glob.glob(os.path.join(output_dir, "*_bfs_output.log")):
        dataset_name = os.path.basename(bfs_file).replace('_bfs_output.log', '')
        print(f"Processing dataset: {dataset_name}")  # Debugging info
        cpu_file = bfs_file.replace('_bfs_output.log', '_cpu_metrics.log')
        disk_file = bfs_file.replace('_bfs_output.log', '_disk_metrics.log')
        sar_file = bfs_file.replace('_bfs_output.log', '_sar_metrics.log')
        mpi_file = bfs_file.replace('_bfs_output.log', '_mpi_logs.log')

        if not (os.path.exists(cpu_file) and os.path.exists(disk_file) and os.path.exists(sar_file) and os.path.exists(mpi_file)):
            print(f"Missing files for {dataset_name}. Skipping...")
            continue

        bfs_data = parse_bfs_output(bfs_file)
        cpu_data = parse_cpu_metrics(cpu_file)
        disk_data = parse_disk_metrics(disk_file)
        sar_data = parse_sar_metrics(sar_file)
        mpi_data = parse_mpi_logs(mpi_file)

        datasets.append({
            'Dataset': dataset_name,
            'Avg Execution Time (s)': bfs_data['average_exec_time'],
            'Avg CPU Usage (%)': cpu_data['average_cpu_usage'],
            'Avg Disk Utilization (%)': disk_data['average_disk_util'],
            'Avg Memory Usage (%)': sar_data['average_memory_usage'],
            'Avg MPI Send Time (s)': mpi_data['average_send_time'],
            'Avg MPI Recv Time (s)': mpi_data['average_recv_time']
        })

    df = pd.DataFrame(datasets)

    # Sort the results based on dataset size extracted from the name
    df['Dataset Size'] = df['Dataset'].str.extract(r'(\d+[kmb])').iloc[:, 0]
    size_order = {'k': 1, 'm': 1_000, 'b': 1_000_000}
    df['Dataset Size'] = df['Dataset Size'].str[:-1].astype(int) * df['Dataset Size'].str[-1].map(size_order)
    df = df.sort_values('Dataset Size').drop(columns=['Dataset Size'])
    return df

if __name__ == "__main__":
    output_dir = "."  # Current directory
    results = analyze_metrics(output_dir)
    if not results.empty:
        print("===== BFS Metrics Summary =====")
        print(results)
        results.to_csv(os.path.join(output_dir, "bfs_metrics_summary.csv"), index=False)
    else:
        print("No metrics data processed. Please check the log files.")
