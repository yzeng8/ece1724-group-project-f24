import pandas as pd
import matplotlib.pyplot as plt

def plot_metrics(data, output_file, title):
    metrics = [
        "Avg Execution Time (s)",
        "Avg CPU Usage (%)",
        "Avg Disk Utilization (%)",
        "Avg Memory Usage (%)",
    ]

    fig, ax = plt.subplots(len(metrics), 1, figsize=(10, 20))

    for idx, metric in enumerate(metrics):
        bars = ax[idx].bar(data["Dataset"], data[metric], color='skyblue')
        for bar in bars:
            height = bar.get_height()
            ax[idx].text(
                bar.get_x() + bar.get_width() / 2.0,
                height + 0.02 * max(0.1, abs(height)),
                f'{height:.3f}',
                ha='center', va='bottom', fontsize=8
            )
        ax[idx].set_title(f"{metric}", fontsize=12)
        ax[idx].set_xlabel("Dataset", fontsize=10)
        ax[idx].set_ylabel(metric, fontsize=10)
        ax[idx].tick_params(axis='x', rotation=45)

    plt.suptitle(title, fontsize=16)
    plt.tight_layout(rect=[0, 0, 1, 0.97])
    plt.savefig(output_file)
    plt.show()

if __name__ == "__main__":
    # Load BFS data
    bfs_file = "bfs_metrics_summary.csv"
    bfs_data = pd.read_csv(bfs_file)
    plot_metrics(bfs_data, "bfs_metrics_graph.png", "BFS Metrics")

    # Load PR data
    pr_file = "pr_metrics_summary.csv"
    pr_data = pd.read_csv(pr_file)
    plot_metrics(pr_data, "pr_metrics_graph.png", "PR Metrics")
