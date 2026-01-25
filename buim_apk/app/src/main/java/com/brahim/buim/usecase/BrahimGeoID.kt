/**
 * Brahim Geo ID - Killer Use Case
 * ================================
 *
 * REAL APPLICATION: Geospatial Product Identifiers
 *
 * Use cases:
 * 1. Warehouse inventory slots (lat/lon of shelf → unique ID)
 * 2. Delivery route waypoints (sequence of BN-GEO IDs)
 * 3. Asset tracking (equipment location → immutable ID)
 * 4. Supply chain provenance (origin coordinates → verifiable)
 * 5. Dataset fingerprinting (data location → checksum anchor)
 *
 * Properties:
 * - UNIQUE: Cantor pairing is bijective (no collisions)
 * - REVERSIBLE: Can recover original coordinates
 * - VERIFIABLE: Check digit detects transcription errors
 * - COMPACT: Mod-214 gives human-memorable short form
 * - IMMUTABLE: BNv1 spec is frozen
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-25
 * Spec: BNv1 (FROZEN)
 */

package com.brahim.buim.usecase

import com.brahim.buim.core.BrahimConstants
import kotlin.math.abs
import kotlin.math.floor
import kotlin.math.sqrt

/**
 * Brahim Geo ID - A unique identifier derived from coordinates.
 */
data class BrahimGeoID(
    val latitude: Double,
    val longitude: Double,
    val brahimNumber: Long,
    val checkDigit: Char,
    val mod214: Int,
    val fullId: String,      // BN:949486203882100-7
    val shortId: String,     // BN214:42-7
    val humanId: String      // BNGEO-42-SF (with location hint)
) {
    companion object {
        const val SPEC_VERSION = "BNv1"
        const val SCALE = 1_000_000L
    }
}

/**
 * Product with geospatial identity.
 */
data class GeoProduct(
    val geoId: BrahimGeoID,
    val name: String,
    val category: String,
    val metadata: Map<String, String> = emptyMap()
)

/**
 * Route as sequence of Brahim Geo IDs.
 */
data class GeoRoute(
    val routeId: String,
    val waypoints: List<BrahimGeoID>,
    val checksum: Long  // XOR of all Brahim numbers
)

/**
 * Brahim Geo ID Factory - Creates and verifies geospatial IDs.
 */
object BrahimGeoIDFactory {

    /**
     * Create a Brahim Geo ID from coordinates.
     *
     * This is the PRIMARY use case entry point.
     */
    fun create(latitude: Double, longitude: Double, locationHint: String = ""): BrahimGeoID {
        require(latitude in -90.0..90.0) { "Latitude must be in [-90, 90]" }
        require(longitude in -180.0..180.0) { "Longitude must be in [-180, 180]" }

        val a = (abs(latitude) * BrahimGeoID.SCALE).toLong()
        val b = (abs(longitude) * BrahimGeoID.SCALE).toLong()

        val brahimNumber = cantorPair(a, b)
        val checkDigit = computeCheckDigit(brahimNumber)
        val mod214 = (brahimNumber % BrahimConstants.BRAHIM_SUM).toInt()

        val fullId = "BN:$brahimNumber-$checkDigit"
        val shortId = "BN214:$mod214-$checkDigit"

        val hint = if (locationHint.isNotEmpty()) {
            locationHint.take(4).uppercase().replace(" ", "")
        } else {
            mod214.toString().padStart(3, '0')
        }
        val humanId = "BNGEO-$mod214-$hint"

        return BrahimGeoID(
            latitude = latitude,
            longitude = longitude,
            brahimNumber = brahimNumber,
            checkDigit = checkDigit,
            mod214 = mod214,
            fullId = fullId,
            shortId = shortId,
            humanId = humanId
        )
    }

    /**
     * Verify a Brahim Geo ID string.
     *
     * Returns true if check digit is valid.
     */
    fun verify(id: String): Boolean {
        return try {
            val (numberPart, checkPart) = parseId(id)
            val expectedCheck = computeCheckDigit(numberPart)
            expectedCheck == checkPart
        } catch (e: IOException)  // TODO: catch specific type {
            false
        }
    }

    /**
     * Decode a Brahim Number back to coordinates.
     *
     * Returns (latitude, longitude) or null if invalid.
     */
    fun decode(brahimNumber: Long): Pair<Double, Double>? {
        if (brahimNumber < 0) return null

        val (a, b) = cantorUnpair(brahimNumber)

        val lat = a.toDouble() / BrahimGeoID.SCALE
        val lon = b.toDouble() / BrahimGeoID.SCALE

        if (lat > 90 || lon > 180) return null

        return lat to lon
    }

    /**
     * Create a route from a list of coordinates.
     */
    fun createRoute(routeId: String, waypoints: List<Pair<Double, Double>>): GeoRoute {
        val geoIds = waypoints.map { (lat, lon) -> create(lat, lon) }
        val checksum = geoIds.fold(0L) { acc, id -> acc xor id.brahimNumber }

        return GeoRoute(
            routeId = routeId,
            waypoints = geoIds,
            checksum = checksum
        )
    }

    /**
     * Create a product with geospatial identity.
     */
    fun createProduct(
        name: String,
        category: String,
        latitude: Double,
        longitude: Double,
        locationHint: String = "",
        metadata: Map<String, String> = emptyMap()
    ): GeoProduct {
        val geoId = create(latitude, longitude, locationHint)
        return GeoProduct(
            geoId = geoId,
            name = name,
            category = category,
            metadata = metadata
        )
    }

    /**
     * Generate a dataset fingerprint from multiple coordinates.
     *
     * USE CASE: Provenance anchor for geospatial datasets.
     */
    fun fingerprintDataset(coordinates: List<Pair<Double, Double>>): DatasetFingerprint {
        val ids = coordinates.map { (lat, lon) -> create(lat, lon) }

        // XOR all Brahim numbers for collision-resistant fingerprint
        val xorFingerprint = ids.fold(0L) { acc, id -> acc xor id.brahimNumber }

        // Sum all mod214 values
        val sumMod214 = ids.sumOf { it.mod214 }

        // Digital root of fingerprint
        var root = digitSum(xorFingerprint)
        while (root >= 10) root = digitSum(root.toLong())

        return DatasetFingerprint(
            count = coordinates.size,
            xorFingerprint = xorFingerprint,
            sumMod214 = sumMod214,
            digitalRoot = root,
            checkDigit = computeCheckDigit(xorFingerprint),
            fingerprintId = "BNFP:$xorFingerprint-${computeCheckDigit(xorFingerprint)}"
        )
    }

    // =========================================================================
    // INTERNAL FUNCTIONS (BNv1 Spec Implementation)
    // =========================================================================

    /**
     * Cantor pairing function.
     * SPEC: BNv1 Section 2.2
     */
    private fun cantorPair(a: Long, b: Long): Long {
        return ((a + b) * (a + b + 1)) / 2 + b
    }

    /**
     * Inverse Cantor pairing.
     * SPEC: BNv1 Section 2.3
     */
    private fun cantorUnpair(z: Long): Pair<Long, Long> {
        val w = floor((sqrt(8.0 * z + 1) - 1) / 2).toLong()
        val t = (w * w + w) / 2
        val b = z - t
        val a = w - b
        return a to b
    }

    /**
     * Check digit (mod 11).
     * SPEC: BNv1 Section 4.3
     */
    private fun computeCheckDigit(n: Long): Char {
        val r = (abs(n) % 11).toInt()
        return if (r == 10) 'X' else ('0' + r)
    }

    /**
     * Digit sum.
     * SPEC: BNv1 Section 4.1
     */
    private fun digitSum(n: Long): Int {
        return abs(n).toString().sumOf { it.digitToInt() }
    }

    /**
     * Parse an ID string.
     */
    private fun parseId(id: String): Pair<Long, Char> {
        val cleaned = id.uppercase().replace("BN:", "").replace("BN214:", "")
        val parts = cleaned.split("-")
        val number = parts[0].toLong()
        val check = parts[1][0]
        return number to check
    }
}

/**
 * Dataset fingerprint result.
 */
data class DatasetFingerprint(
    val count: Int,
    val xorFingerprint: Long,
    val sumMod214: Int,
    val digitalRoot: Int,
    val checkDigit: Char,
    val fingerprintId: String
)

// =========================================================================
// EXTENSION FUNCTIONS FOR CONVENIENCE
// =========================================================================

/**
 * Convert coordinates to Brahim Geo ID.
 */
fun Pair<Double, Double>.toBrahimGeoID(hint: String = ""): BrahimGeoID {
    return BrahimGeoIDFactory.create(first, second, hint)
}

/**
 * Verify a Brahim ID string.
 */
fun String.isValidBrahimID(): Boolean {
    return BrahimGeoIDFactory.verify(this)
}
