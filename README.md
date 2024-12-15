# ece1724-group-project-f24

## 1.GraphX Configuration Instruction On Linux System

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
