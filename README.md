# ece1724-group-project-f24

## GraphX Instruction




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
