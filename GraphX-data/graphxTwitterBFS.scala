import org.apache.spark.graphx._
import org.apache.spark.rdd.RDD
import org.apache.spark.sql.SparkSession

object graphxTwitterBFS {
  def main(args: Array[String]): Unit = {
    if (args.length < 2) {
      System.err.println("Usage: graphxTwitterBFS <input_file> <source_vertex_id>")
      System.exit(1)
    }

    // Parse command-line arguments
    val inputFile = args(0)
    val sourceVertexId = args(1).toLong

    // Initialize SparkSession
    val spark = SparkSession.builder
      .appName("TwitterGraphBFS")
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

    // Initialize the BFS algorithm by setting all vertices to an infinite distance, except the source
    val initialGraph = graph.mapVertices((id, _) =>
      if (id == sourceVertexId) 0.0 else Double.PositiveInfinity
    )

    // Perform BFS using Pregel
    val bfsResult = initialGraph.pregel(Double.PositiveInfinity)(
      // Vertex program: update the vertex value with the smallest distance
      (id, currentDistance, newDistance) => math.min(currentDistance, newDistance),
      // Send message: propagate the distance to neighboring vertices
      triplet => {
        if (triplet.srcAttr + 1 < triplet.dstAttr) {
          Iterator((triplet.dstId, triplet.srcAttr + 1))
        } else {
          Iterator.empty
        }
      },
      // Merge message: take the minimum distance
      (a, b) => math.min(a, b)
    )

    // Print the results of the BFS
    println(s"Vertices reachable from source vertex $sourceVertexId:")
    bfsResult.vertices.filter { case (_, distance) => distance < Double.PositiveInfinity }
      .collect()
      .sortBy(_._2) // Sort by distance
      .foreach { case (id, distance) =>
        println(s"Vertex $id is at distance $distance")
      }

    // Stop SparkSession
    spark.stop()
  }
}
