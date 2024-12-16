import org.apache.spark.graphx._
import org.apache.spark.rdd.RDD
import org.apache.spark.sql.SparkSession

object graphxBrockBFS {
  def main(args: Array[String]): Unit = {
    if (args.length < 2) {
      System.err.println("Usage: graphxBrockBFS <input_file> <source_vertex>")
      System.exit(1)
    }

    // Parse command-line arguments
    val inputFile = args(0)
    val sourceVertexId = args(1).toLong

    // Initialize SparkSession
    val spark = SparkSession.builder
      .appName("BrockGraphBFS")
      .master("local[*]")
      .getOrCreate()

    val sc = spark.sparkContext

    // Load the edge list from the input file
    val edgeList = sc.textFile(inputFile)

    // Parse the .clq input file to create edges RDD
    val edges: RDD[Edge[Int]] = edgeList
      .filter(line => line.startsWith("e")) // Process only lines that define edges
      .map { line =>
        val parts = line.split("\\s+")
        val src = parts(1).toLong
        val dst = parts(2).toLong
        Edge(src, dst, 1) // Use weight = 1 for all edges
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

    // Initialize the graph for BFS
    val initialGraph = graph.mapVertices((id, _) => if (id == sourceVertexId) 0.0 else Double.PositiveInfinity)

    // Run the Pregel API for BFS
    val bfsResult = initialGraph.pregel(Double.PositiveInfinity)(
      // Vertex Program
      (id, currentDistance, newDistance) => math.min(currentDistance, newDistance),

      // Send Message
      triplet => {
        if (triplet.srcAttr + 1 < triplet.dstAttr) {
          Iterator((triplet.dstId, triplet.srcAttr + 1))
        } else {
          Iterator.empty
        }
      },

      // Merge Message
      (a, b) => math.min(a, b)
    )

    // Collect reachable vertices
    val reachableVertices = bfsResult.vertices.filter { case (_, distance) => distance < Double.PositiveInfinity }

    // Print the vertices reachable from the source vertex
    println(s"Vertices reachable from source vertex $sourceVertexId:")
    reachableVertices.collect().foreach { case (id, distance) =>
      println(s"Vertex $id is reachable with distance $distance")
    }

    // Stop SparkSession
    spark.stop()
  }
}
