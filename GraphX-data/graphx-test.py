from pyspark.sql import SparkSession
from graphframes import GraphFrame

# Initialize SparkSession with the GraphFrames JAR
spark = SparkSession.builder \
    .appName("GraphFramesExample") \
    .config("spark.jars", "/usr/local/spark/jars/graphframes-0.8.3-spark3.4-s_2.12.jar") \
    .getOrCreate()

# Create vertices and edges DataFrames
vertices = spark.createDataFrame([
    ("1", "Alice"),
    ("2", "Bob"),
    ("3", "Charlie"),
    ("4", "David"),
    ("5", "Eve"),
    ("6", "Frank"),
    ("7", "Grace"),
    ("8", "Hank")
], ["id", "name"])

edges = spark.createDataFrame([
    ("1", "2"),  # Alice -> Bob
    ("2", "3"),  # Bob -> Charlie
    ("3", "1"),  # Charlie -> Alice
    ("3", "4"),  # Charlie -> David
    ("4", "5"),  # David -> Eve
    ("5", "6"),  # Eve -> Frank
    ("6", "4"),  # Frank -> David
    ("7", "8"),  # Grace -> Hank
    ("8", "7")   # Hank -> Grace
], ["src", "dst"])

# Create a GraphFrame
graph = GraphFrame(vertices, edges)

# Run PageRank
results = graph.pageRank(resetProbability=0.15, maxIter=10)
results.vertices.show()

print("Running PageRank...")
results = graph.pageRank(resetProbability=0.15, maxIter=10)

print("PageRank Results (Vertices with Ranks):")
results.vertices.select("id", "name", "pagerank").show()