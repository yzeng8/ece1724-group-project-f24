import os
import glob
import pandas as pd

def parse_pr_output(file_path):
    exec_times = []
    final_deltas = []
    with open(file_path, 'r') as file:
        for line in file:
            if "exec_time" in line:
                exec_times.append(float(line.split('=')[1].strip().replace('(s)', '')))
            elif "delta(" in line and line.strip().endswith(")"):
                delta = float(line.split('=')[1].strip())
                final_deltas.append(delta)
    return {
        'average_exec_time': sum(exec_times) / len(exec_times) if exec_times else 0,
        'final_delta': final_deltas[-1] if final_deltas else None
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

def analyze_metrics(output_dir):
    threads = []
    for pr_file in glob.glob(os.path.join(output_dir, "pr_*_output.log")):
        thread_count = os.path.basename(pr_file).split('_')[1]  # Extract thread count
        print(f"Processing thread count: {thread_count}")  # Debugging output

        cpu_file = pr_file.replace('_output.log', '_cpu_metrics.log')
        disk_file = pr_file.replace('_output.log', '_disk_metrics.log')
        sar_file = pr_file.replace('_output.log', '_sar_metrics.log')

        if not (os.path.exists(cpu_file) and os.path.exists(disk_file) and os.path.exists(sar_file)):
            print(f"Missing files for {thread_count} threads. Skipping...")
            continue

        pr_data = parse_pr_output(pr_file)
        cpu_data = parse_cpu_metrics(cpu_file)
        disk_data = parse_disk_metrics(disk_file)
        sar_data = parse_sar_metrics(sar_file)

        threads.append({
            'Threads': int(thread_count),
            'Avg Execution Time (s)': pr_data['average_exec_time'],
            'Final Delta': pr_data['final_delta'],
            'Avg CPU Usage (%)': cpu_data['average_cpu_usage'],
            'Avg Disk Utilization (%)': disk_data['average_disk_util'],
            'Avg Memory Usage (%)': sar_data['average_memory_usage']
        })

    if threads:
        df = pd.DataFrame(threads)
        df = df.sort_values('Threads')  # Sort by thread count
        return df
    else:
        print("No data found to analyze.")
        return pd.DataFrame()

if __name__ == "__main__":
    output_dir = "." 
    results = analyze_metrics(output_dir)
    if not results.empty:
        print("===== PageRank Metrics Summary =====")
        print(results)
        results.to_csv(os.path.join(output_dir, "pr_metrics_summary.csv"), index=False)
    else:
        print("No metrics data processed. Please check the log files.")
