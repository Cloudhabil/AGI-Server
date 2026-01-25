/**
 * Geometric Firewall - Forbidden Zone Detection
 * ==============================================
 *
 * Implements geometric safety boundaries using the Brahim manifold.
 * Detects when content enters "forbidden zones" in semantic space.
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-25
 */

package com.brahim.buim.safety

import com.brahim.buim.core.BrahimConstants
import kotlin.math.sqrt
import kotlin.math.abs
import kotlin.math.pow

/**
 * Forbidden zone definition.
 */
data class ForbiddenZone(
    val id: String,
    val center: DoubleArray,
    val radius: Double,
    val severity: SafetyVerdict,
    val description: String
) {
    fun contains(point: DoubleArray): Boolean {
        val distance = euclideanDistance(center, point)
        return distance < radius
    }

    private fun euclideanDistance(a: DoubleArray, b: DoubleArray): Double {
        require(a.size == b.size) { "Vectors must have same dimension" }
        return sqrt(a.zip(b.toTypedArray()).map { (ai, bi) -> (ai - bi).pow(2) }.sum())
    }

    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (other !is ForbiddenZone) return false
        return id == other.id
    }

    override fun hashCode(): Int = id.hashCode()
}

/**
 * Firewall check result.
 */
data class FirewallResult(
    val isBlocked: Boolean,
    val matchedZone: ForbiddenZone?,
    val distanceToNearestZone: Double,
    val allDistances: Map<String, Double>
)

/**
 * Geometric Firewall using Brahim manifold geometry.
 */
class GeometricFirewall {

    companion object {
        /** Minimum safe distance from any forbidden zone */
        const val SAFE_MARGIN = 0.1
    }

    // Registered forbidden zones
    private val forbiddenZones = mutableListOf<ForbiddenZone>()

    init {
        // Initialize with default forbidden zones
        initializeDefaultZones()
    }

    /**
     * Initialize default forbidden zones in the Brahim manifold.
     */
    private fun initializeDefaultZones() {
        // High-severity zones (BLOCKED)
        addZone(
            id = "harmful_content",
            center = DoubleArray(BrahimConstants.BRAHIM_DIMENSION) { 0.9 },
            radius = 0.2,
            severity = SafetyVerdict.BLOCKED,
            description = "Harmful content zone"
        )

        addZone(
            id = "pii_leakage",
            center = DoubleArray(BrahimConstants.BRAHIM_DIMENSION) { i ->
                if (i == 7) 0.95 else 0.1  // High security dimension
            },
            radius = 0.15,
            severity = SafetyVerdict.BLOCKED,
            description = "PII/sensitive data zone"
        )

        // Medium-severity zones (UNSAFE)
        addZone(
            id = "controversial",
            center = DoubleArray(BrahimConstants.BRAHIM_DIMENSION) { i ->
                if (i == 4) 0.8 else 0.3  // High creative dimension
            },
            radius = 0.25,
            severity = SafetyVerdict.UNSAFE,
            description = "Controversial content zone"
        )

        // Low-severity zones (CAUTION)
        addZone(
            id = "speculative",
            center = DoubleArray(BrahimConstants.BRAHIM_DIMENSION) { i ->
                if (i == 3) 0.7 else 0.2  // High science dimension
            },
            radius = 0.3,
            severity = SafetyVerdict.CAUTION,
            description = "Speculative/unverified zone"
        )
    }

    /**
     * Add a forbidden zone.
     */
    fun addZone(
        id: String,
        center: DoubleArray,
        radius: Double,
        severity: SafetyVerdict,
        description: String
    ) {
        require(center.size == BrahimConstants.BRAHIM_DIMENSION) {
            "Zone center must have dimension ${BrahimConstants.BRAHIM_DIMENSION}"
        }
        require(radius > 0) { "Radius must be positive" }

        forbiddenZones.add(ForbiddenZone(id, center, radius, severity, description))
    }

    /**
     * Remove a forbidden zone by ID.
     */
    fun removeZone(id: String): Boolean {
        return forbiddenZones.removeIf { it.id == id }
    }

    /**
     * Check if a point is in any forbidden zone.
     */
    fun check(point: DoubleArray): FirewallResult {
        require(point.size == BrahimConstants.BRAHIM_DIMENSION) {
            "Point must have dimension ${BrahimConstants.BRAHIM_DIMENSION}"
        }

        val distances = mutableMapOf<String, Double>()
        var nearestDistance = Double.MAX_VALUE
        var matchedZone: ForbiddenZone? = null

        for (zone in forbiddenZones) {
            val distance = euclideanDistance(zone.center, point)
            distances[zone.id] = distance

            if (distance < nearestDistance) {
                nearestDistance = distance
            }

            if (zone.contains(point) && (matchedZone == null || zone.severity.level > matchedZone.severity.level)) {
                matchedZone = zone
            }
        }

        return FirewallResult(
            isBlocked = matchedZone != null,
            matchedZone = matchedZone,
            distanceToNearestZone = nearestDistance,
            allDistances = distances
        )
    }

    /**
     * Compute distance between two points.
     */
    private fun euclideanDistance(a: DoubleArray, b: DoubleArray): Double {
        return sqrt(a.zip(b.toTypedArray()).map { (ai, bi) -> (ai - bi).pow(2) }.sum())
    }

    /**
     * Apply wormhole transform to move point away from forbidden zones.
     * Returns a safe version of the point.
     */
    fun projectToSafe(point: DoubleArray): DoubleArray {
        val result = check(point)

        if (!result.isBlocked) {
            return point.copyOf()
        }

        // Project point away from matched zone
        val zone = result.matchedZone!!
        val direction = DoubleArray(point.size) { i ->
            point[i] - zone.center[i]
        }

        // Normalize direction
        val norm = sqrt(direction.map { it * it }.sum())
        if (norm < 1e-10) {
            // Random direction if at center
            return DoubleArray(point.size) { i ->
                zone.center[i] + (zone.radius + SAFE_MARGIN) * BrahimConstants.getCentroid()[i]
            }
        }

        // Move to safe distance
        val safeDistance = zone.radius + SAFE_MARGIN
        return DoubleArray(point.size) { i ->
            zone.center[i] + direction[i] / norm * safeDistance
        }
    }

    /**
     * Get all registered zones.
     */
    fun getZones(): List<ForbiddenZone> = forbiddenZones.toList()

    /**
     * Get firewall info.
     */
    fun getInfo(): Map<String, Any> {
        return mapOf(
            "num_zones" to forbiddenZones.size,
            "dimension" to BrahimConstants.BRAHIM_DIMENSION,
            "safe_margin" to SAFE_MARGIN,
            "zones" to forbiddenZones.map { zone ->
                mapOf(
                    "id" to zone.id,
                    "radius" to zone.radius,
                    "severity" to zone.severity.name,
                    "description" to zone.description
                )
            }
        )
    }
}
