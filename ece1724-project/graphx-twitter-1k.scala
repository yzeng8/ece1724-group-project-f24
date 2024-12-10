import org.apache.spark.graphx._
import org.apache.spark.rdd.RDD
import org.apache.spark.sql.SparkSession

object TwitterGraphProcessing1k {
  def main(args: Array[String]): Unit = {
    // Initialize SparkSession
    val spark = SparkSession.builder
      .appName("TwitterGraphProcessing")
      .master("local[*]")
      .getOrCreate()

    val sc = spark.sparkContext

    // Load the edge list from the file
    val edgeList = sc.textFile("file:///home/zengyuyang1999/ece1724-project/data/twitter-2010-1k.txt")


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

    // Run PageRank algorithm
    val ranks = graph.pageRank(0.0001).vertices

    // Print the top-ranked vertices
    println("Top-ranked vertices:")
    ranks.sortBy(_._2, ascending = false).take(10).foreach { case (id, rank) =>
      println(s"Vertex $id has rank $rank")
    }

    // Stop SparkSession
    spark.stop()
  }
}
