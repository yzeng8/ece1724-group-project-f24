import os
import re
import pandas as pd

def parse_cpu_log(cpu_log):
    """Parse CPU log file to compute average CPU usage."""
    user_usage = []
    system_usage = []
    with open(cpu_log, 'r') as f:
        for line in f:
            if re.match(r'\d{2}:\d{2}:\d{2}', line):  # Match time lines
                parts = line.split()
                if parts[1] == 'all':
                    user_usage.append(float(parts[2]))
                    system_usage.append(float(parts[4]))
    avg_cpu_usage = sum(user_usage) + sum(system_usage)
    avg_cpu_usage /= len(user_usage) if user_usage else 1  # Avoid division by zero
    return avg_cpu_usage

def parse_memory_log(memory_log):
    """Parse memory log file to compute average memory usage percentage."""
    used_memory = []
    total_memory = None
    with open(memory_log, 'r') as f:
        for line in f:
            if 'Mem:' in line:
                parts = line.split()
                total_memory = float(parts[1])
                used_memory.append(float(parts[2]))
    avg_memory_percentage = (sum(used_memory) / len(used_memory)) / total_memory * 100 if total_memory else 0
    return avg_memory_percentage

def parse_disk_log(disk_log):
    """Parse disk log file to compute average disk utilization and throughput for sda."""
    util_values = []
    throughput_values = []
    with open(disk_log, 'r') as f:
        for line in f:
            parts = line.split()
            if len(parts) > 0 and parts[0] == 'sda':
                util_values.append(float(parts[-1]))  # %util
                throughput_values.append(float(parts[5]) + float(parts[9]))  # rkB/s + wkB/s
    avg_disk_util = sum(util_values) / len(util_values) if util_values else 0
    avg_throughput = sum(throughput_values) / len(throughput_values) if throughput_values else 0
    return avg_disk_util, avg_throughput

def main():
    """Main function to analyze all log files and summarize performance metrics."""
    log_dir = '.'  # Current directory
    datasets = ['brock400_4.clq', 'brock800_4.clq']
    results = []

    for dataset in datasets:
        print(f"Processing {dataset}...")
        cpu_log = os.path.join(log_dir, f"metrics-{dataset}-cpu.log")
        memory_log = os.path.join(log_dir, f"metrics-{dataset}-memory.log")
        disk_log = os.path.join(log_dir, f"metrics-{dataset}-disk.log")

        if not (os.path.exists(cpu_log) and os.path.exists(memory_log) and os.path.exists(disk_log)):
            print(f"Logs missing for {dataset}. Skipping...")
            continue

        # Parse logs
        avg_cpu_usage = parse_cpu_log(cpu_log)
        avg_memory_usage = parse_memory_log(memory_log)
        avg_disk_util, avg_throughput = parse_disk_log(disk_log)

        # Append results
        results.append({
            'Dataset': dataset,
            'Avg CPU Usage (%)': round(avg_cpu_usage, 2),
            'Avg Memory Usage (%)': round(avg_memory_usage, 2),
            'Avg Disk Utilization (%)': round(avg_disk_util, 2),
            'Avg Throughput (kB/s)': round(avg_throughput, 2)
        })

    # Create a DataFrame for summary
    df = pd.DataFrame(results)
    print("\nPerformance Metrics Summary:")
    print(df)

    # Save results to CSV
    output_file = 'performance_summary.csv'
    df.to_csv(output_file, index=False)
    print(f"Summary saved to {output_file}")

if __name__ == "__main__":
    main()
