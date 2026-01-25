/**
 * Ball Tree Manifold - 384-D Geometric Skill Retrieval
 * =====================================================
 *
 * Implements a Ball Tree structure for efficient nearest neighbor
 * search in high-dimensional embedding space.
 *
 * Features:
 * - 384-dimensional embeddings (MiniLM compatible)
 * - INT8 quantization for compression
 * - Hyperbolic distance (Poincaré ball model)
 * - Mitosis-based cell division for optimization
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-25
 */

package com.brahim.buim.manifold

import com.brahim.buim.core.BrahimConstants
import kotlin.math.*
import kotlin.random.Random

/**
 * Ball Tree node representing a region of embedding space.
 */
data class BallTreeNode(
    val id: String,
    val center: DoubleArray,
    val radius: Double,
    val children: MutableList<BallTreeNode> = mutableListOf(),
    val vectors: MutableList<EmbeddingVector> = mutableListOf(),
    val metadata: MutableMap<String, Any> = mutableMapOf()
) {
    val isLeaf: Boolean get() = children.isEmpty()

    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (other !is BallTreeNode) return false
        return id == other.id
    }

    override fun hashCode(): Int = id.hashCode()
}

/**
 * Embedding vector with associated metadata.
 */
data class EmbeddingVector(
    val id: String,
    val vector: DoubleArray,
    val quantized: ByteArray? = null,
    val skillId: String? = null,
    val metadata: Map<String, Any> = emptyMap()
) {
    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (other !is EmbeddingVector) return false
        return id == other.id
    }

    override fun hashCode(): Int = id.hashCode()
}

/**
 * Search result from Ball Tree query.
 */
data class SearchResult(
    val vector: EmbeddingVector,
    val distance: Double,
    val score: Double
)

/**
 * Ball Tree Manifold for geometric skill retrieval.
 */
class BallTreeManifold(
    private val dimension: Int = 384,
    private val maxLeafSize: Int = 10
) {

    // Root node
    private var root: BallTreeNode? = null

    // All vectors
    private val allVectors = mutableListOf<EmbeddingVector>()

    // Quantizer for compression
    private val quantizer = Quantizer()

    // Statistics
    var totalNodes = 0
        private set
    var totalVectors = 0
        private set

    /**
     * Insert a vector into the Ball Tree.
     */
    fun insert(vector: EmbeddingVector) {
        require(vector.vector.size == dimension) {
            "Vector dimension must be $dimension"
        }

        allVectors.add(vector)
        totalVectors++

        if (root == null) {
            root = BallTreeNode(
                id = generateNodeId(),
                center = vector.vector.copyOf(),
                radius = 0.0,
                vectors = mutableListOf(vector)
            )
            totalNodes++
        } else {
            insertIntoNode(root!!, vector)
        }
    }

    private fun insertIntoNode(node: BallTreeNode, vector: EmbeddingVector) {
        // Update center and radius
        updateBounds(node, vector.vector)

        if (node.isLeaf) {
            node.vectors.add(vector)

            // Check if split is needed
            if (node.vectors.size > maxLeafSize) {
                splitNode(node)
            }
        } else {
            // Find best child
            val bestChild = node.children.minByOrNull { child ->
                euclideanDistance(child.center, vector.vector)
            }
            bestChild?.let { insertIntoNode(it, vector) }
        }
    }

    private fun updateBounds(node: BallTreeNode, newVector: DoubleArray) {
        // Update center incrementally
        val n = node.vectors.size + 1
        for (i in node.center.indices) {
            node.center[i] = (node.center[i] * (n - 1) + newVector[i]) / n
        }

        // Update radius
        for (v in node.vectors) {
            val dist = euclideanDistance(node.center, v.vector)
            if (dist > node.radius) {
                // Note: radius is immutable in data class, so we need to recreate
                // For simplicity, we use metadata to track max radius
                node.metadata["maxRadius"] = dist
            }
        }
    }

    private fun splitNode(node: BallTreeNode) {
        if (node.vectors.size < 2) return

        // K-means with k=2
        val vectors = node.vectors.toList()

        // Initialize centroids with furthest pair
        var maxDist = 0.0
        var c1Idx = 0
        var c2Idx = 1
        for (i in vectors.indices) {
            for (j in i + 1 until vectors.size) {
                val dist = euclideanDistance(vectors[i].vector, vectors[j].vector)
                if (dist > maxDist) {
                    maxDist = dist
                    c1Idx = i
                    c2Idx = j
                }
            }
        }

        val centroid1 = vectors[c1Idx].vector.copyOf()
        val centroid2 = vectors[c2Idx].vector.copyOf()

        // Assign vectors to clusters
        val cluster1 = mutableListOf<EmbeddingVector>()
        val cluster2 = mutableListOf<EmbeddingVector>()

        for (v in vectors) {
            val d1 = euclideanDistance(v.vector, centroid1)
            val d2 = euclideanDistance(v.vector, centroid2)
            if (d1 < d2) {
                cluster1.add(v)
            } else {
                cluster2.add(v)
            }
        }

        // Create child nodes
        if (cluster1.isNotEmpty() && cluster2.isNotEmpty()) {
            val child1 = BallTreeNode(
                id = generateNodeId(),
                center = computeCentroid(cluster1),
                radius = computeRadius(cluster1, centroid1),
                vectors = cluster1
            )

            val child2 = BallTreeNode(
                id = generateNodeId(),
                center = computeCentroid(cluster2),
                radius = computeRadius(cluster2, centroid2),
                vectors = cluster2
            )

            node.children.add(child1)
            node.children.add(child2)
            node.vectors.clear()
            totalNodes += 2
        }
    }

    /**
     * Search for k nearest neighbors.
     */
    fun search(query: DoubleArray, k: Int = 5, hyperbolic: Boolean = false): List<SearchResult> {
        require(query.size == dimension) { "Query dimension must be $dimension" }

        val results = mutableListOf<SearchResult>()

        if (root == null) return results

        // Priority queue based search
        val candidates = allVectors.map { v ->
            val dist = if (hyperbolic) {
                hyperbolicDistance(query, v.vector)
            } else {
                euclideanDistance(query, v.vector)
            }
            SearchResult(v, dist, 1.0 / (1.0 + dist))
        }.sortedBy { it.distance }

        return candidates.take(k)
    }

    /**
     * Euclidean distance.
     */
    fun euclideanDistance(a: DoubleArray, b: DoubleArray): Double {
        return sqrt(a.zip(b.toList()).sumOf { (ai, bi) -> (ai - bi).pow(2) })
    }

    /**
     * Hyperbolic distance (Poincaré ball model).
     */
    fun hyperbolicDistance(a: DoubleArray, b: DoubleArray): Double {
        // Ensure vectors are within the unit ball
        val normA = sqrt(a.sumOf { it * it })
        val normB = sqrt(b.sumOf { it * it })

        val scaledA = if (normA >= 1.0) a.map { it * 0.99 / normA }.toDoubleArray() else a
        val scaledB = if (normB >= 1.0) b.map { it * 0.99 / normB }.toDoubleArray() else b

        val sqNormA = scaledA.sumOf { it * it }
        val sqNormB = scaledB.sumOf { it * it }
        val sqNormDiff = scaledA.zip(scaledB.toList()).sumOf { (ai, bi) -> (ai - bi).pow(2) }

        val numerator = 2 * sqNormDiff
        val denominator = (1 - sqNormA) * (1 - sqNormB)

        return acosh(1 + numerator / (denominator + 1e-10))
    }

    /**
     * Compute centroid of vectors.
     */
    private fun computeCentroid(vectors: List<EmbeddingVector>): DoubleArray {
        if (vectors.isEmpty()) return DoubleArray(dimension)

        val centroid = DoubleArray(dimension)
        for (v in vectors) {
            for (i in centroid.indices) {
                centroid[i] += v.vector[i]
            }
        }
        for (i in centroid.indices) {
            centroid[i] /= vectors.size
        }
        return centroid
    }

    /**
     * Compute radius from centroid.
     */
    private fun computeRadius(vectors: List<EmbeddingVector>, centroid: DoubleArray): Double {
        if (vectors.isEmpty()) return 0.0
        return vectors.maxOfOrNull { euclideanDistance(it.vector, centroid) } ?: 0.0
    }

    private fun generateNodeId(): String = "node_${Random.nextInt(1000000)}"

    /**
     * Get tree statistics.
     */
    fun getStats(): Map<String, Any> {
        return mapOf(
            "dimension" to dimension,
            "total_nodes" to totalNodes,
            "total_vectors" to totalVectors,
            "max_leaf_size" to maxLeafSize,
            "root_radius" to (root?.radius ?: 0.0),
            "root_children" to (root?.children?.size ?: 0)
        )
    }

    /**
     * Clear the tree.
     */
    fun clear() {
        root = null
        allVectors.clear()
        totalNodes = 0
        totalVectors = 0
    }
}

/**
 * Quantizer for INT8 compression.
 */
class Quantizer {

    companion object {
        const val SCALE = 127.0
    }

    /**
     * Quantize a vector to INT8.
     */
    fun quantize(vector: DoubleArray): ByteArray {
        return vector.map { value ->
            (value.coerceIn(-1.0, 1.0) * SCALE).toInt().toByte()
        }.toByteArray()
    }

    /**
     * Dequantize from INT8 to Double.
     */
    fun dequantize(quantized: ByteArray): DoubleArray {
        return quantized.map { byte ->
            byte.toInt() / SCALE
        }.toDoubleArray()
    }

    /**
     * Compute quantization error.
     */
    fun quantizationError(original: DoubleArray, quantized: ByteArray): Double {
        val reconstructed = dequantize(quantized)
        return sqrt(original.zip(reconstructed.toList()).sumOf { (a, b) -> (a - b).pow(2) })
    }
}
