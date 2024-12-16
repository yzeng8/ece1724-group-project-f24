# ece1724-group-project-f24

## 1. Gemini Configuration Instructions

This repository contains the setup and execution instructions for running the Gemini graph processing framework in both single-node and distributed environments. The guide provides detailed steps to replicate the environment, execute the workloads, and analyze the results.

### Prerequisites

#### System Requirements
- **Operating System**: Linux-based (tested on Ubuntu 20.04/22.04)
- **VM Instances**:
  - Single-node: 1 VM with 8 vCPUs, 32 GB RAM.
  - Distributed: 2 VMs, each with 8 vCPUs and 32 GB RAM.
- **Storage**: At least 50 GB free for datasets and logs.
- **Network**: High-speed network connectivity between distributed VMs.

#### Software Requirements
- **Compiler**: GCC 7.5+ with OpenMP support
- **MPI**: OpenMPI 4.1+
- **Monitoring Tools**: `mpstat`, `iostat`, `sar`
- **Python**: Version 3.8+ with required libraries (`pandas`, `matplotlib`)
- **Additional Tools**:
  - `scp` for file transfer
  - `md5sum` for integrity checks

### Setup Instructions

#### 1. Clone Repository
Clone the Gemini framework repository:
```bash
$ git clone https://github.com/thu-pacman/GeminiGraph.git
$ cd gemini
```

#### 2. Compile Gemini
Use the provided Makefile to compile the Gemini executables:
```bash
$ make
```
Ensure the executables are generated in the `toolkits/` directory.

#### 3. Prepare Datasets
1. Download datasets:
   - **Twitter-2010** (subsets of 1k, 10k, 100k, 1m, 100m, 200m edges).
   - **DIMACS Brock400_4** and **Brock800_4**.
2. Place the datasets in the `datasets/` directory.

#### 4. Single-Node Setup
1. **Run BFS or PageRank**:
   ```bash
   $ ./toolkits/bfs datasets/twitter_100m.binedgelist <num_vertices> <root_node>
   ```
   Replace `<num_vertices>` and `<root_node>` with appropriate values.

2. **Monitor System Metrics**:
   Use the following commands to log metrics during execution:
   ```bash
   $ mpstat 1 > mpstat.log &
   $ iostat -x 1 > iostat.log &
   $ sar -u -r 1 > sar.log &
   ```
3. **Analyze Logs**:
   Use the Python script to parse and visualize metrics:
   ```bash
   $ python3 analyze_single_node.py
   ```

#### 5. Distributed Setup
1. **Synchronize Files Across VMs**:
   Use `scp` to copy files to all VMs:
   ```bash
   $ scp -r gemini/ user@<vm-ip>:~/
   ```
2. **Verify File Integrity**:
   Run `md5sum` on all VMs to confirm consistency:
   ```bash
   $ md5sum toolkits/bfs
   ```

3. **Modify Hostfile**:
   Add VM IPs to a `hostfile` for MPI:
   ```
   vm1 slots=8
   vm2 slots=8
   ```

4. **Run Distributed BFS/PageRank**:
   Example command for BFS:
   ```bash
   $ mpirun --hostfile hostfile -np 16 ./toolkits/bfs datasets/twitter_100m.binedgelist <num_vertices> <root_node>
   ```

5. **Monitor Metrics**:
   Run the monitoring Bash script to capture logs:
   ```bash
   $ bash monitor_distributed.sh
   ```

6. **Analyze Results**:
   Use the Python script for distributed results analysis:
   ```bash
   $ python3 analyze_distributed_results.py
   ```

### Results
- **Metrics Collected**:
  - Execution time
  - CPU utilization
  - Disk I/O
  - Memory usage
  - MPI communication times
- **Visualization**:
  Results are saved in CSV format and visualized as bar/line graphs.

### Key Notes
- **MPI Wrapping**: Modified Gemini source code to wrap `MPI_Send` and `MPI_Recv` for detailed communication timing.
- **NUMA Awareness**: The current setup does not utilize NUMA-aware optimizations.
- **Trade-offs**:
  - For small, dense datasets, Gemini excels in single-node performance.
  - Distributed setups benefit larger graphs but incur communication overhead.

### References
- [Gemini Paper](https://arxiv.org/abs/1909.03110)
- [Apache GraphX](https://spark.apache.org/graphx/)


## 2. GraphX Configuration Instructions

### Prerequisites

#### System Requirements
- **Operating System**: Linux-based (tested on Ubuntu 20.04/22.04)
- **VM Instances**:
  - Single-node: 1 VM with 8 vCPUs, 32 GB RAM.
  - Distributed: 2 VMs, each with 8 vCPUs and 32 GB RAM.
- **Storage**: At least 50 GB free for datasets and logs.
- **Network**: High-speed network connectivity between distributed VMs.

#### Software Requirements
- **Java**: OpenJDK 11+
- **Python**: Version 3.8+ with libraries (`pandas`, `matplotlib`)
- **Scala**: Version 2.12+
- **Spark**: Apache Spark 3.4.4 (Hadoop 3 support)

### Setup Instructions

#### 1. Programming Languages Installation
Install Java, Python, and Scala:
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install openjdk-11-jdk -y
java -version
sudo apt install python3 python3-pip -y
python3 --version
pip3 --version
sudo apt install scala -y
scala -version
```

#### 2. Spark Installation
1. **Download and Extract Spark**:
   ```bash
   wget https://downloads.apache.org/spark/spark-3.4.4/spark-3.4.4-bin-hadoop3.tgz
   tar -xvzf spark-3.4.4-bin-hadoop3.tgz
   sudo mv spark-3.4.4-bin-hadoop3 /opt/spark
   ```

2. **Configure Environment Variables**:
   Edit `~/.bashrc`:
   ```bash
   export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
   export SPARK_HOME=/opt/spark
   export PATH=$SPARK_HOME/bin:$SPARK_HOME/sbin:$PATH
   export PYSPARK_PYTHON=python3
   ```
   Apply changes:
   ```bash
   source ~/.bashrc
   ```

#### 3. Verify Installation
Run the Spark shell:
```bash
spark-shell
```

### Running GraphX Jobs

#### 1. Compile the Scala Script
Use `scalac` to compile your GraphX script:
```bash
scalac -classpath "/opt/spark/jars/*" graphx-twitter-1k.scala
```

#### 2. Package Class Files into a JAR
Create a JAR file for execution:
```bash
jar -cf graphx-twitter-1k.jar *.class
```

#### 3. Run the Spark Job
Submit the GraphX job using `spark-submit`:
```bash
spark-submit --class TwitterGraphProcessing1k \
  --master local[*] \
  --driver-memory 1g \
  --packages org.apache.spark:spark-graphx_2.12:3.4.4,graphframes:graphframes:0.8.3-spark3.4-s_2.12 \
  graphx-twitter-1k.jar
```

### General Running Instructions
To compile, package, and run GraphX scripts:
```bash
scalac -classpath "/opt/spark/jars/*" graphx-twitter-PR.scala
jar -cf graphXtwitterPR.jar *.class
spark-submit --class graphXtwitterPR \
  --master local[*] \
  --driver-memory 4g \
  --packages org.apache.spark:spark-graphx_2.12:3.4.4,graphframes:graphframes:0.8.3-spark3.4-s_2.12 \
  graphXtwitterPR.jar file:///home/zengyuyang1999/ece1724-group-project-f24/ece1724-project/data/twitter-2010-1k.txt 1
```

### Results
- **Metrics Collected**:
  - Execution time
  - CPU utilization
  - Memory usage
- **Visualization**:
  Results are stored in CSV format and visualized using Python scripts.
