import org.apache.spark.graphx._
import org.apache.spark.rdd.RDD
import org.apache.spark.sql.SparkSession

object graphXtwitterPR {
  def main(args: Array[String]): Unit = {
    if (args.length < 2) {
      System.err.println("Usage: graphX_twitter_PR <input_file> <num_iterations>")
      System.exit(1)
    }

    // Parse command-line arguments
    val inputFile = args(0)
    val numIterations = args(1).toInt

    // Initialize SparkSession
    val spark = SparkSession.builder
      .appName("TwitterGraphProcessing")
      .master("local[*]")
      .getOrCreate()

    val sc = spark.sparkContext

    // Load the edge list from the input file
    val edgeList = sc.textFile(inputFile)

    // Create edges RDD from the file
    val edges: RDD[Edge[Int]] = edgeList.map { line =>
      val parts = line.split("\\s+")
      Edge(parts(0).toLong, parts(1).toLong, 1) // Use weight = 1 for all edges
    }

    // Create vertices RDD by extracting unique node IDs
    val vertices: RDD[(VertexId, String)] = edges.flatMap(edge => Seq(edge.srcId, edge.dstId))
      .distinct()
      .map(id => (id, s"Node $id")) // Assign node labels like "Node 1"

    // Create the graph
    val graph = Graph(vertices, edges)

    // Print the graph's basic information
    println(s"Number of vertices: ${graph.vertices.count()}")
    println(s"Number of edges: ${graph.edges.count()}")

    // Run PageRank algorithm with the specified number of iterations
    val ranks = graph.staticPageRank(numIterations).vertices

    // Print the top-ranked vertices
    println("Top-ranked vertices:")
    ranks.sortBy(_._2, ascending = false).take(10).foreach { case (id, rank) =>
      println(s"Vertex $id has rank $rank")
    }

    // Stop SparkSession
    spark.stop()
  }
}
