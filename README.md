# ece1724-group-project-f24
## 1.Gemini Configuration Instructions

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


## 2.GraphX Configuration Instructions

### Step 1 Programming Languages Preparatin: Java & Python & Scala Installation
```
sudo apt update && sudo apt update && sudo apt upgrade -y
sudo apt install openjdk-11-jdk -y
java -version # Check Java version
sudo apt install python3 python3-pip -y
python3 --version
pip3 --version # Check Python version
sudo apt install scala -y
scala -version # Check Scala version

```

### Step2: Spark Installation
```
## Get the packages
wget https://downloads.apache.org/spark/spark-3.4.4/spark-3.4.4-bin-hadoop3.tgz
tar -xvzf spark-3.4.4-bin-hadoop3.tgz
sudo mv spark-3.4.4-bin-hadoop3 /opt/spark

## Set Environmental Variables
vim ~/.bashrc
# insert into the first line of the file
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
export SPARK_HOME=/opt/spark
export PATH=$SPARK_HOME/bin:$SPARK_HOME/sbin:$PATH
export PYSPARK_PYTHON=python3
# save and exit

source ~/.bashrc
```

### Step3: Verify Installtion

```
spark-shell
```


## 2. GraphX Running Instruction




### Step 1: Compile the scala script 
```
scalac -classpath "/opt/spark/jars/*" graphx-twitter-1k.scala
```
### Step 2: Package All Class Files to a Jar File
```
jar -cf graphx-twitter-1k.jar *.class
```

### Step 3: Run the Spark Job Use spark-submit with specification of driver memory of 1G, Apache Package of Graph X.  
```
spark-submit --class TwitterGraphProcessing1k --master local[*] --driver-memory 1g --packages org.apache.spark:spark-graphx_2.12:3.4.4,graphframes:graphframes:0.8.3-spark3.4-s_2.12 graphx-twitter-1k.jar
```
where -class is the objectname of your scala script.





## General Running Instruction
```
scalac -classpath "/opt/spark/jars/*" graphx-twitter-PR.scala
jar -cf graphXtwitterPR\.jar *.class

spark-submit --class graphXtwitterPR --master local[*] --driver-memory 2g --packages org.apache.spark:spark-graphx_2.12:3.4.4,graphframes:graphframes:0.8.3-spark3.4-s_2.12 graphXtwitterPR.jar file:///home/zengyuyang1999/ece1724-group-project-f24/ece1724-project/data/twitter-2010-1k.txt 1
 ```
