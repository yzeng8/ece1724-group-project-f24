import org.apache.spark.graphx._
import org.apache.spark.rdd.RDD
import org.apache.spark.sql.SparkSession

object GraphXTest {
  def main(args: Array[String]): Unit = {
    // Create SparkSession
    val spark = SparkSession.builder
      .appName("GraphX Example")
      .master("local[*]") // Adjust master for cluster setups
      .getOrCreate()

    val sc = spark.sparkContext

    // Load vertices
    val vertices: RDD[(VertexId, String)] = sc.parallelize(Seq(
      (1L, "Alice"),
      (2L, "Bob"),
      (3L, "Charlie"),
      (4L, "David"),
      (5L, "Eve"),
      (6L, "Frank"),
      (7L, "Grace"),
      (8L, "Hank")
    ))

    // Load edges
    val edges: RDD[Edge[Int]] = sc.parallelize(Seq(
      Edge(1L, 2L, 1), // Alice -> Bob
      Edge(2L, 3L, 1), // Bob -> Charlie
      Edge(3L, 1L, 1), // Charlie -> Alice
      Edge(3L, 4L, 1), // Charlie -> David
      Edge(4L, 5L, 1), // David -> Eve
      Edge(5L, 6L, 1), // Eve -> Frank
      Edge(6L, 4L, 1), // Frank -> David
      Edge(7L, 8L, 1), // Grace -> Hank
      Edge(8L, 7L, 1)  // Hank -> Grace
    ))

    // Create the graph
    val graph = Graph(vertices, edges)

    // Print vertices
    println("Vertices:")
    graph.vertices.collect.foreach(println)

    // Print edges
    println("Edges:")
    graph.edges.collect.foreach(println)

    // Run PageRank
    println("Running PageRank...")
    val ranks = graph.pageRank(0.0001).vertices
    println("PageRank Results:")
    ranks.collect.foreach(println)

    // Stop SparkSession
    spark.stop()
  }
}
