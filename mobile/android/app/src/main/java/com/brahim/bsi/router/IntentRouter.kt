/**
 * Intent Router - Territory-Based Query Classification
 * =====================================================
 *
 * Routes user queries to appropriate handlers using the Brahim Sequence
 * for territory partitioning. Each territory corresponds to a value in
 * the sequence B = {27, 42, 60, 75, 97, 121, 136, 154, 172, 187}.
 *
 * Uses the Perfect Wormhole Transform for semantic compression.
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-24
 */

package com.brahim.bsi.router

import com.brahim.bsi.core.BrahimConstants
import kotlin.math.abs
import kotlin.math.sqrt

/**
 * Territory definitions based on Brahim Sequence.
 */
enum class Territory(val index: Int, val brahimValue: Int, val description: String) {
    GENERAL(0, 27, "General queries and greetings"),
    MATH(1, 42, "Mathematical and computational"),
    CODE(2, 60, "Programming and software"),
    SCIENCE(3, 75, "Scientific and research"),
    CREATIVE(4, 97, "Creative and artistic"),
    ANALYSIS(5, 121, "Analysis and reasoning"),
    SYSTEM(6, 136, "System and technical"),
    SECURITY(7, 154, "Security and privacy"),
    DATA(8, 172, "Data and information"),
    META(9, 187, "Meta and self-referential");

    companion object {
        fun fromIndex(index: Int): Territory {
            return values().find { it.index == index } ?: GENERAL
        }
    }
}

/**
 * Routing result with confidence.
 */
data class RoutingResult(
    val territory: Territory,
    val confidence: Double,
    val distances: Map<Territory, Double>,
    val wormholeVector: DoubleArray
) {
    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (other !is RoutingResult) return false
        return territory == other.territory &&
               confidence == other.confidence
    }

    override fun hashCode(): Int {
        return territory.hashCode() * 31 + confidence.hashCode()
    }
}

/**
 * Intent Router using Brahim Sequence territories.
 *
 * The router:
 * 1. Converts text to embedding vector
 * 2. Applies wormhole transform for compression
 * 3. Computes distance to each territory centroid
 * 4. Routes to nearest territory with confidence score
 */
class IntentRouter {

    // Territory centroids derived from Brahim Sequence
    private val territoryCentroids: Map<Territory, DoubleArray>

    init {
        territoryCentroids = computeTerritoryCentroids()
    }

    /**
     * Compute centroid for each territory based on Brahim values.
     */
    private fun computeTerritoryCentroids(): Map<Territory, DoubleArray> {
        val centroids = mutableMapOf<Territory, DoubleArray>()

        for (territory in Territory.values()) {
            // Create centroid vector with territory value as primary feature
            val centroid = DoubleArray(BrahimConstants.BRAHIM_DIMENSION)
            val value = territory.brahimValue.toDouble() / BrahimConstants.BRAHIM_SUM

            // Primary dimension gets the territory value
            centroid[territory.index] = value

            // Other dimensions get golden-ratio scaled values
            for (i in centroid.indices) {
                if (i != territory.index) {
                    val distance = abs(i - territory.index)
                    centroid[i] = value * kotlin.math.pow(BrahimConstants.COMPRESSION, distance.toDouble())
                }
            }

            // Normalize
            val norm = sqrt(centroid.map { it * it }.sum())
            if (norm > 0) {
                for (i in centroid.indices) {
                    centroid[i] /= norm
                }
            }

            centroids[territory] = centroid
        }

        return centroids
    }

    /**
     * Apply Perfect Wormhole Transform to a vector.
     *
     * W*(sigma) = sigma/phi + C_bar * alpha
     */
    private fun wormholeTransform(sigma: DoubleArray): DoubleArray {
        val centroid = BrahimConstants.getCentroid()
        return DoubleArray(sigma.size) { i ->
            sigma[i] / BrahimConstants.PHI +
            centroid[i % centroid.size] * BrahimConstants.ALPHA_WORMHOLE
        }
    }

    /**
     * Convert text to embedding vector.
     *
     * Simple hash-based embedding for demonstration.
     * In production, use proper sentence embeddings.
     */
    fun textToEmbedding(text: String): DoubleArray {
        val embedding = DoubleArray(BrahimConstants.BRAHIM_DIMENSION)

        // Simple character-based features
        val lower = text.lowercase()

        // Feature extraction based on content
        embedding[0] = if (lower.contains("hello") || lower.contains("hi")) 1.0 else 0.0
        embedding[1] = if (lower.contains("math") || lower.contains("calculate")) 1.0 else 0.0
        embedding[2] = if (lower.contains("code") || lower.contains("program")) 1.0 else 0.0
        embedding[3] = if (lower.contains("science") || lower.contains("research")) 1.0 else 0.0
        embedding[4] = if (lower.contains("create") || lower.contains("write")) 1.0 else 0.0
        embedding[5] = if (lower.contains("analyze") || lower.contains("explain")) 1.0 else 0.0
        embedding[6] = if (lower.contains("system") || lower.contains("config")) 1.0 else 0.0
        embedding[7] = if (lower.contains("secure") || lower.contains("encrypt")) 1.0 else 0.0
        embedding[8] = if (lower.contains("data") || lower.contains("info")) 1.0 else 0.0
        embedding[9] = if (lower.contains("how") || lower.contains("what")) 1.0 else 0.0

        // Add hash-based noise for uniqueness
        val hash = text.hashCode()
        for (i in embedding.indices) {
            embedding[i] += ((hash shr i) and 0xF).toDouble() / 16.0 * 0.1
        }

        // Normalize
        val norm = sqrt(embedding.map { it * it }.sum())
        if (norm > 0) {
            for (i in embedding.indices) {
                embedding[i] /= norm
            }
        }

        return embedding
    }

    /**
     * Compute distance between two vectors.
     */
    private fun distance(a: DoubleArray, b: DoubleArray): Double {
        var sum = 0.0
        for (i in a.indices) {
            val diff = a[i] - b.getOrElse(i) { 0.0 }
            sum += diff * diff
        }
        return sqrt(sum)
    }

    /**
     * Route a query to the appropriate territory.
     *
     * @param query User query text
     * @return Routing result with territory and confidence
     */
    fun route(query: String): RoutingResult {
        // Convert to embedding
        val embedding = textToEmbedding(query)

        // Apply wormhole transform
        val wormholeVector = wormholeTransform(embedding)

        // Compute distances to all territories
        val distances = mutableMapOf<Territory, Double>()
        for ((territory, centroid) in territoryCentroids) {
            distances[territory] = distance(wormholeVector, centroid)
        }

        // Find nearest territory
        val nearest = distances.minByOrNull { it.value }!!
        val territory = nearest.key
        val minDistance = nearest.value

        // Compute confidence (inverse of distance, normalized)
        val maxDistance = distances.values.maxOrNull() ?: 1.0
        val confidence = if (maxDistance > 0) {
            1.0 - (minDistance / maxDistance)
        } else {
            1.0
        }

        return RoutingResult(
            territory = territory,
            confidence = confidence,
            distances = distances,
            wormholeVector = wormholeVector
        )
    }

    /**
     * Route with detailed analysis.
     */
    fun routeWithAnalysis(query: String): Map<String, Any> {
        val result = route(query)

        return mapOf(
            "query" to query,
            "territory" to result.territory.name,
            "territory_description" to result.territory.description,
            "brahim_value" to result.territory.brahimValue,
            "confidence" to result.confidence,
            "confidence_percent" to "${(result.confidence * 100).toInt()}%",
            "all_distances" to result.distances.map { (t, d) ->
                t.name to "%.4f".format(d)
            }.toMap(),
            "wormhole_compression" to BrahimConstants.COMPRESSION
        )
    }

    /**
     * Get router info.
     */
    fun getRouterInfo(): Map<String, Any> {
        return mapOf(
            "territories" to Territory.values().map { t ->
                mapOf(
                    "name" to t.name,
                    "index" to t.index,
                    "brahim_value" to t.brahimValue,
                    "description" to t.description
                )
            },
            "brahim_sequence" to BrahimConstants.BRAHIM_SEQUENCE.toList(),
            "total_sum" to BrahimConstants.BRAHIM_SUM,
            "center" to BrahimConstants.BRAHIM_CENTER,
            "compression_factor" to BrahimConstants.COMPRESSION
        )
    }
}
