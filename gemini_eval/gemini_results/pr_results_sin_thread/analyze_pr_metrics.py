import os
import glob
import pandas as pd

def parse_pr_output(file_path):
    exec_times = []
    delta_values = []
    with open(file_path, 'r') as file:
        for line in file:
            if "exec_time" in line:
                exec_times.append(float(line.split('=')[1].strip().replace('(s)', '')))
            if "delta" in line:
                delta_values.append(float(line.split('=')[1].strip()))
    return {
        'average_exec_time': sum(exec_times) / len(exec_times) if exec_times else 0,
        'exec_times': exec_times,
        'final_delta': delta_values[-1] if delta_values else None
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
    datasets = []
    for pr_file in glob.glob(os.path.join(output_dir, "*_pr_output.log")):
        dataset_name = os.path.basename(pr_file).replace('_pr_output.log', '')
        print(f"Processing dataset: {dataset_name}")  # Debugging info
        cpu_file = pr_file.replace('_pr_output.log', '_cpu_metrics.log')
        disk_file = pr_file.replace('_pr_output.log', '_disk_metrics.log')
        sar_file = pr_file.replace('_pr_output.log', '_sar_metrics.log')

        if not (os.path.exists(cpu_file) and os.path.exists(disk_file) and os.path.exists(sar_file)):
            print(f"Missing files for {dataset_name}. Skipping...")
            continue

        pr_data = parse_pr_output(pr_file)
        cpu_data = parse_cpu_metrics(cpu_file)
        disk_data = parse_disk_metrics(disk_file)
        sar_data = parse_sar_metrics(sar_file)

        datasets.append({
            'Dataset': dataset_name,
            'Avg Execution Time (s)': pr_data['average_exec_time'],
            'Final Delta': pr_data['final_delta'],
            'Avg CPU Usage (%)': cpu_data['average_cpu_usage'],
            'Avg Disk Utilization (%)': disk_data['average_disk_util'],
            'Avg Memory Usage (%)': sar_data['average_memory_usage']
        })

    df = pd.DataFrame(datasets)

    # Sort the results based on dataset size extracted from the name
    df['Dataset Size'] = df['Dataset'].str.extract(r'(\d+[kmb])').iloc[:, 0]
    size_order = {'k': 1, 'm': 1_000, 'b': 1_000_000}
    df['Dataset Size'] = df['Dataset Size'].str[:-1].astype(int) * df['Dataset Size'].str[-1].map(size_order)
    df = df.sort_values('Dataset Size').drop(columns=['Dataset Size'])
    return df

if __name__ == "__main__":
    # output_dir = "pr_results_sin_thread"  # Directory containing the logs
    output_dir = "."
    results = analyze_metrics(output_dir)
    if not results.empty:
        print("===== PageRank Metrics Summary =====")
        print(results)
        results.to_csv(os.path.join(output_dir, "pr_metrics_summary.csv"), index=False)
    else:
        print("No metrics data processed. Please check the log files.")
