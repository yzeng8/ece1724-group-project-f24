# ece1724-group-project-f24

## 1.GraphX Configuration Instruction

### Step 1 Java Installation
```
sudo apt update
sudo apt install openjdk-11-jdk -y
```

### Step2: Spark Installation
```
## Get the packages
wget https://downloads.apache.org/spark/spark-3.4.4/spark-3.4.4-bin-hadoop3.tgz
tar -xvzf spark-3.4.4-bin-hadoop3.tgz
sudo mv spark-3.4.4-bin-hadoop3 /opt/spark

## Set Environmental Variables
echo "export SPARK_HOME=/opt/spark" >> ~/.bashrc
echo "export PATH=\$SPARK_HOME/bin:\$SPARK_HOME/sbin:\$PATH" >> ~/.bashrc
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
