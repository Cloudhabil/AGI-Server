/**
 * Routing Result - Response Data Classes
 * =======================================
 *
 * Data classes for intent routing responses.
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-25
 */

package com.brahim.buim.router

/**
 * Detailed routing analysis result.
 */
data class RoutingAnalysis(
    val query: String,
    val territory: Territory,
    val territoryDescription: String,
    val brahimValue: Int,
    val confidence: Double,
    val confidencePercent: String,
    val allDistances: Map<String, Double>,
    val wormholeCompression: Double,
    val embedding: DoubleArray,
    val wormholeVector: DoubleArray
) {
    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (other !is RoutingAnalysis) return false
        return query == other.query && territory == other.territory
    }

    override fun hashCode(): Int {
        return query.hashCode() * 31 + territory.hashCode()
    }
}

/**
 * Batch routing result.
 */
data class BatchRoutingResult(
    val results: List<RoutingResult>,
    val dominantTerritory: Territory,
    val averageConfidence: Double,
    val processingTime: Long
)
