# # import os
# # import pandas as pd
# # import matplotlib.pyplot as plt

# # # Define a function to plot bar graphs
# # def plot_bar_graph(data, processes, metric, title, ylabel, output_file, dataset_colors):
# #     plt.figure(figsize=(12, 8))
    
# #     bar_width = 0.2
# #     x_positions = {dataset_name: [i + idx * bar_width for i in range(len(processes))] for idx, dataset_name in enumerate(data.keys())}

# #     for dataset_name, values in data.items():
# #         plt.bar(
# #             x_positions[dataset_name],
# #             values,
# #             width=bar_width,
# #             label=dataset_name,
# #             color=dataset_colors.get(dataset_name, None)
# #         )

# #     x_labels = [str(proc) for proc in processes]
# #     plt.xticks([i + bar_width for i in range(len(processes))], x_labels)
    
# #     plt.title(title)
# #     plt.xlabel("Processes")
# #     plt.ylabel(ylabel)
# #     plt.legend(title="Datasets")
# #     plt.tight_layout()
# #     plt.savefig(output_file)
# #     plt.show()

# # # Read all CSV files and process data
# # file_paths = {
# #     "BFS 1k": "bfs_distributed_1k_results.csv",
# #     "BFS 100k": "bfs_distributed_100k_results.csv",
# #     "BFS 100m": "bfs_distributed_100m_results.csv",
# #     "PR 100m": "pr_distributed_100m_results.csv"
# # }

# # metrics_to_plot = {
# #     "Execution Time (s)": "Execution Time (s)",
# #     "Avg CPU Usage (%)": "CPU Usage (%)",
# #     "Avg Disk Utilization (%)": "Disk Utilization (%)",
# #     "Avg Memory Usage (%)": "Memory Usage (%)",
# #     "MPI Communication Time (s)": "MPI Send/Recv Time (s)"
# # }

# # # Initialize a dictionary to store data for plotting
# # processes = [2, 4, 8, 16]
# # plot_data = {metric: {} for metric in metrics_to_plot.keys()}

# # # Load data and prepare for plotting
# # for dataset_name, file_path in file_paths.items():
# #     if os.path.exists(file_path):
# #         df = pd.read_csv(file_path)
# #         for metric in metrics_to_plot.keys():
# #             if metric == "MPI Communication Time (s)":
# #                 if "MPI Send Time (s)" in df.columns and "MPI Recv Time (s)" in df.columns:
# #                     combined_time = df["MPI Send Time (s)"].add(df["MPI Recv Time (s)"], fill_value=0)
# #                     plot_data[metric][dataset_name] = combined_time.tolist()
# #                 else:
# #                     print(f"MPI Send/Recv Time not found in {file_path}. Skipping...")
# #                     continue
# #             elif metric in df.columns:
# #                 plot_data[metric][dataset_name] = df[metric].tolist()
# #             else:
# #                 print(f"Metric '{metric}' not found in {file_path}. Skipping...")

# # # Assign colors to datasets
# # bfs_colors = {"BFS 1k": "blue", "BFS 100k": "green", "BFS 100m": "red"}
# # pr_colors = {"PR 100m": "purple"}

# # # Generate bar graphs for BFS metrics
# # for metric, ylabel in metrics_to_plot.items():
# #     if metric in plot_data:
# #         title = f"{ylabel} by Processes for BFS Datasets"
# #         output_file = f"bfs_{metric.replace(' ', '_').lower()}_bar_graph.png"
# #         plot_bar_graph({k: v for k, v in plot_data[metric].items() if "BFS" in k}, processes, metric, title, ylabel, output_file, bfs_colors)

# # # Generate bar graphs for PR metrics
# # for metric, ylabel in metrics_to_plot.items():
# #     if metric in plot_data:
# #         title = f"{ylabel} by Processes for PR Dataset"
# #         output_file = f"pr_{metric.replace(' ', '_').lower()}_bar_graph.png"
# #         plot_bar_graph({k: v for k, v in plot_data[metric].items() if "PR" in k}, processes, metric, title, ylabel, output_file, pr_colors)
# import pandas as pd
# import matplotlib.pyplot as plt
# import numpy as np

# # Load CSV files
# def load_data(file_path):
#     return pd.read_csv(file_path)

# # Visualization function
# def create_bar_graphs(bfs_data, pr_data):
#     # Macaron color palette
#     macaron_colors = ["#FFB6C1", "#B3D7FF", "#FFDAB9", "#C3FDB8", "#E6E6FA"]

#     bfs_datasets = ["1k", "100k", "100m"]

#     # BFS Metrics
#     bfs_metrics = ["Execution Time (s)", "Avg CPU Usage (%)", "Avg Disk Utilization (%)", "Avg Memory Usage (%)", "MPI Communication Time (s)"]

#     # Prepare data for BFS
#     bfs_combined = []
#     for dataset in bfs_datasets:
#         data = load_data(f"bfs_distributed_{dataset}_results.csv")
#         data["MPI Communication Time (s)"] = data["MPI Send Time (s)"] + data["MPI Recv Time (s)"]
#         data["Dataset"] = dataset
#         bfs_combined.append(data)
#     bfs_combined = pd.concat(bfs_combined, ignore_index=True)

#     # Create BFS graphs
#     for metric, color in zip(bfs_metrics, macaron_colors):
#         plt.figure(figsize=(10, 6))
#         for i, dataset in enumerate(bfs_datasets):
#             subset = bfs_combined[bfs_combined["Dataset"] == dataset]
#             plt.bar(subset["Processes"] + i * 0.2, subset[metric], width=0.2, label=dataset, color=color, alpha=0.8)

#         plt.title(f"BFS {metric} by Processes", fontsize=14)
#         plt.xlabel("Processes", fontsize=12)
#         plt.ylabel(metric, fontsize=12)
#         plt.xticks(bfs_combined["Processes"].unique())
#         plt.legend(title="Dataset Size")
#         plt.tight_layout()
#         plt.savefig(f"bfs_{metric.replace(' ', '_').replace('(', '').replace(')', '').lower()}_bar.png")
#         plt.show()

#     # PR Metrics
#     pr_metrics = ["Execution Time (s)", "Avg CPU Usage (%)", "Avg Disk Utilization (%)", "Avg Memory Usage (%)", "MPI Communication Time (s)"]

#     # Prepare data for PR
#     pr_data["MPI Communication Time (s)"] = pr_data["MPI Send Time (s)"] + pr_data["MPI Recv Time (s)"]

#     # Create PR graphs
#     for metric, color in zip(pr_metrics, macaron_colors):
#         plt.figure(figsize=(10, 6))
#         plt.bar(pr_data["Processes"], pr_data[metric], color=color, alpha=0.8)

#         plt.title(f"PR {metric} by Processes", fontsize=14)
#         plt.xlabel("Processes", fontsize=12)
#         plt.ylabel(metric, fontsize=12)
#         plt.xticks(pr_data["Processes"].unique())
#         plt.tight_layout()
#         plt.savefig(f"pr_{metric.replace(' ', '_').replace('(', '').replace(')', '').lower()}_bar.png")
#         plt.show()

# if __name__ == "__main__":
#     bfs_data_1k = "bfs_distributed_1k_results.csv"
#     bfs_data_100k = "bfs_distributed_100k_results.csv"
#     bfs_data_100m = "bfs_distributed_100m_results.csv"
#     pr_data_file = "pr_distributed_100m_results.csv"

#     pr_data = load_data(pr_data_file)

#     create_bar_graphs([bfs_data_1k, bfs_data_100k, bfs_data_100m], pr_data)
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def plot_combined_bfs(data, output_file):
    metrics = [
        "Execution Time (s)",
        "Avg CPU Usage (%)",
        "Avg Disk Utilization (%)",
        "Avg Memory Usage (%)",
        "MPI Communication Time (s)",
    ]

    # Combine MPI Send and Recv Times
    data["MPI Communication Time (s)"] = data["MPI Send Time (s)"] + data["MPI Recv Time (s)"]

    datasets = data["Dataset"].unique()
    processes = sorted(data["Processes"].unique())

    x = np.arange(len(processes))  # the label locations
    bar_width = 0.15  # Width of each bar

    fig, ax = plt.subplots(len(metrics), 1, figsize=(10, 20))

    for idx, metric in enumerate(metrics):
        for i, dataset in enumerate(datasets):
            subset = data[data["Dataset"] == dataset]
            bars = ax[idx].bar(
                x + i * bar_width,
                subset[metric],
                bar_width,
                label=f"{dataset}",
            )
            # Add values on top of bars
            for bar in bars:
                height = bar.get_height()
                ax[idx].text(
                bar.get_x() + bar.get_width() / 2.0, 
                height + 0.05 * max(0.1, abs(height)), 
                f'{height:.3f}',  # This is the content to display 
                    ha='center', va='bottom', fontsize=8
                )
        ax[idx].set_title(metric, fontsize=12)
        ax[idx].set_xticks(x + bar_width * (len(datasets) - 1) / 2)
        ax[idx].set_xticklabels(processes)
        ax[idx].set_xlabel("Number of Processes")
        ax[idx].set_ylabel(metric)
        ax[idx].legend(title="Dataset", loc="upper left", bbox_to_anchor=(1, 1))

    plt.tight_layout()
    plt.savefig(output_file)
    plt.show()

def plot_combined_pr(data, output_file):
    metrics = [
        "Execution Time (s)",
        "Avg CPU Usage (%)",
        "Avg Disk Utilization (%)",
        "Avg Memory Usage (%)",
        "MPI Communication Time (s)",
    ]

    # Combine MPI Send and Recv Times
    data["MPI Communication Time (s)"] = data["MPI Send Time (s)"] + data["MPI Recv Time (s)"]

    processes = sorted(data["Processes"].unique())
    x = np.arange(len(processes))  # the label locations
    bar_width = 0.15  # Width of each bar

    fig, ax = plt.subplots(len(metrics), 1, figsize=(10, 20))

    for idx, metric in enumerate(metrics):
        bars = ax[idx].bar(
            x,
            data[metric],
            bar_width,
            color="skyblue",
            label="PR 100m",
        )
        # Add values on top of bars
        for bar in bars:
            height = bar.get_height()
            ax[idx].text(
                # bar.get_x() + bar.get_width() / 2.0, 
                bar.get_x() + bar.get_width(), 
                height + 0.05 * max(0.1, abs(height)), 
                f'{height:.3f}',  # This is the content to display 
                ha='center', va='bottom', fontsize=8
            )
        ax[idx].set_title(metric, fontsize=12)
        ax[idx].set_xticks(x)
        ax[idx].set_xticklabels(processes)
        ax[idx].set_xlabel("Number of Processes")
        ax[idx].set_ylabel(metric)
        ax[idx].legend(title="Dataset", loc="upper left", bbox_to_anchor=(1, 1))

    plt.tight_layout()
    plt.savefig(output_file)
    plt.show()

if __name__ == "__main__":
    # Load BFS data
    bfs_files = ["bfs_distributed_1k_results.csv", "bfs_distributed_100k_results.csv", "bfs_distributed_100m_results.csv"]
    bfs_data = pd.concat([pd.read_csv(f).assign(Dataset=f.split("_")[2]) for f in bfs_files])

    plot_combined_bfs(bfs_data, "bfs_combined_results.png")

    # Load PR data
    pr_data = pd.read_csv("pr_distributed_100m_results.csv")
    plot_combined_pr(pr_data, "pr_combined_results.png")
