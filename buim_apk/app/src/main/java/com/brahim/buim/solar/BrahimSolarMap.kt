/**
 * Brahim Solar Map - Celestial Coordinate System
 * ===============================================
 *
 * Extends Brahim Numbers to map the Solar System using:
 * - Heliocentric coordinates (distance from Sun, ecliptic angle)
 * - Orbital elements (semi-major axis, eccentricity)
 * - Nested pairing for 3D positions
 *
 * BNv1 Spec: FROZEN for Earth coordinates
 * BNv1-Solar: Extension for celestial bodies (compatible)
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-25
 */

package com.brahim.buim.solar

import com.brahim.buim.core.BrahimConstants
import kotlin.math.*

/**
 * Celestial body in the Solar System.
 */
data class CelestialBody(
    val name: String,
    val type: BodyType,
    val semiMajorAxisAU: Double,      // Distance from Sun in AU
    val eccentricity: Double,          // Orbital eccentricity
    val inclinationDeg: Double,        // Orbital inclination
    val orbitalPeriodDays: Double,     // Orbital period
    val radiusKm: Double,              // Body radius
    val massKg: Double                 // Body mass
)

enum class BodyType {
    STAR,
    PLANET,
    DWARF_PLANET,
    MOON,
    ASTEROID,
    COMET,
    SPACECRAFT
}

/**
 * Solar System Brahim ID - Unique identifier for any position in the Solar System.
 */
data class SolarBrahimID(
    val body: CelestialBody?,
    val heliocentricDistanceAU: Double,
    val eclipticLongitudeDeg: Double,
    val eclipticLatitudeDeg: Double,
    val brahimNumber: Long,
    val brahimNumber3D: Long,          // Full 3D position encoding
    val humanId: String,
    val digitalRoot: Int,
    val mod214: Int,
    val sequenceResonance: String?     // If near a Brahim sequence value
)

/**
 * Brahim Solar Map - Maps the Solar System using Brahim Numbers.
 */
object BrahimSolarMap {

    // =========================================================================
    // SOLAR SYSTEM DATA (J2000 epoch)
    // =========================================================================

    val SOLAR_SYSTEM = listOf(
        CelestialBody("Sun", BodyType.STAR, 0.0, 0.0, 0.0, 0.0, 696340.0, 1.989e30),
        CelestialBody("Mercury", BodyType.PLANET, 0.387, 0.206, 7.0, 87.97, 2439.7, 3.301e23),
        CelestialBody("Venus", BodyType.PLANET, 0.723, 0.007, 3.4, 224.7, 6051.8, 4.867e24),
        CelestialBody("Earth", BodyType.PLANET, 1.0, 0.017, 0.0, 365.25, 6371.0, 5.972e24),
        CelestialBody("Mars", BodyType.PLANET, 1.524, 0.093, 1.85, 687.0, 3389.5, 6.417e23),
        CelestialBody("Jupiter", BodyType.PLANET, 5.203, 0.049, 1.3, 4332.59, 69911.0, 1.898e27),
        CelestialBody("Saturn", BodyType.PLANET, 9.537, 0.054, 2.49, 10759.22, 58232.0, 5.683e26),
        CelestialBody("Uranus", BodyType.PLANET, 19.19, 0.047, 0.77, 30688.5, 25362.0, 8.681e25),
        CelestialBody("Neptune", BodyType.PLANET, 30.07, 0.009, 1.77, 60182.0, 24622.0, 1.024e26),
        CelestialBody("Pluto", BodyType.DWARF_PLANET, 39.48, 0.249, 17.16, 90560.0, 1188.3, 1.303e22),
        CelestialBody("Ceres", BodyType.DWARF_PLANET, 2.77, 0.076, 10.59, 1682.0, 473.0, 9.39e20),
        CelestialBody("Eris", BodyType.DWARF_PLANET, 67.67, 0.436, 44.04, 203830.0, 1163.0, 1.66e22)
    )

    // Major moons
    val MOONS = listOf(
        CelestialBody("Moon", BodyType.MOON, 0.00257, 0.055, 5.14, 27.32, 1737.4, 7.342e22),
        CelestialBody("Io", BodyType.MOON, 0.00282, 0.004, 0.04, 1.77, 1821.6, 8.93e22),
        CelestialBody("Europa", BodyType.MOON, 0.00449, 0.009, 0.47, 3.55, 1560.8, 4.80e22),
        CelestialBody("Ganymede", BodyType.MOON, 0.00716, 0.001, 0.18, 7.15, 2634.1, 1.48e23),
        CelestialBody("Callisto", BodyType.MOON, 0.01258, 0.007, 0.19, 16.69, 2410.3, 1.08e23),
        CelestialBody("Titan", BodyType.MOON, 0.00817, 0.029, 0.35, 15.95, 2574.7, 1.35e23),
        CelestialBody("Triton", BodyType.MOON, 0.00237, 0.000, 156.87, -5.88, 1353.4, 2.14e22)
    )

    // =========================================================================
    // CORE FORMULA (Compatible with BNv1)
    // =========================================================================

    /**
     * Cantor pairing function - same as BNv1.
     */
    private fun cantorPair(a: Long, b: Long): Long {
        return ((a + b) * (a + b + 1)) / 2 + b
    }

    /**
     * Inverse Cantor pairing.
     */
    private fun cantorUnpair(z: Long): Pair<Long, Long> {
        val w = ((sqrt(8.0 * z + 1) - 1) / 2).toLong()
        val t = (w * w + w) / 2
        val b = z - t
        val a = w - b
        return Pair(a, b)
    }

    /**
     * Scale factor for Solar System distances.
     * 1 AU = 1,000,000 units (micro-AU precision)
     */
    private const val AU_SCALE = 1_000_000L

    /**
     * Scale factor for angles.
     * 1 degree = 10,000 units (0.0001 degree precision)
     */
    private const val ANGLE_SCALE = 10_000L

    // =========================================================================
    // SOLAR BRAHIM NUMBER GENERATION
    // =========================================================================

    /**
     * Create a Brahim Number for a heliocentric position.
     *
     * @param distanceAU Distance from Sun in AU
     * @param eclipticLongDeg Ecliptic longitude (0-360°)
     * @param eclipticLatDeg Ecliptic latitude (-90 to +90°)
     * @return SolarBrahimID with full encoding
     */
    fun createSolarID(
        distanceAU: Double,
        eclipticLongDeg: Double,
        eclipticLatDeg: Double,
        body: CelestialBody? = null
    ): SolarBrahimID {
        // Scale to integers
        val r = (distanceAU * AU_SCALE).toLong()
        val lon = ((eclipticLongDeg % 360 + 360) % 360 * ANGLE_SCALE).toLong()
        val lat = ((eclipticLatDeg + 90) * ANGLE_SCALE).toLong()  // Shift to 0-180

        // 2D Brahim Number (distance, longitude) - comparable to Earth lat/lon
        val bn2D = cantorPair(r, lon)

        // 3D Brahim Number - nested pairing with latitude
        val bn3D = cantorPair(bn2D, lat)

        // Digital properties
        val digitSum = bn3D.toString().sumOf { it.digitToInt() }
        val digitalRoot = if (digitSum == 0) 0 else ((digitSum - 1) % 9) + 1
        val mod214 = (bn3D % 214).toInt()

        // Check sequence resonance
        val resonance = findSequenceResonance(distanceAU, eclipticLongDeg)

        // Human-readable ID
        val humanId = formatSolarHumanId(distanceAU, eclipticLongDeg, eclipticLatDeg, body)

        return SolarBrahimID(
            body = body,
            heliocentricDistanceAU = distanceAU,
            eclipticLongitudeDeg = eclipticLongDeg,
            eclipticLatitudeDeg = eclipticLatDeg,
            brahimNumber = bn2D,
            brahimNumber3D = bn3D,
            humanId = humanId,
            digitalRoot = digitalRoot,
            mod214 = mod214,
            sequenceResonance = resonance
        )
    }

    /**
     * Create a Brahim ID for a known celestial body at mean position.
     */
    fun createBodyID(body: CelestialBody, meanLongitudeDeg: Double = 0.0): SolarBrahimID {
        return createSolarID(
            distanceAU = body.semiMajorAxisAU,
            eclipticLongDeg = meanLongitudeDeg,
            eclipticLatDeg = 0.0,  // Simplified - assume ecliptic plane
            body = body
        )
    }

    /**
     * Decode a 3D Solar Brahim Number back to coordinates.
     */
    fun decodeSolarBN(bn3D: Long): Triple<Double, Double, Double>? {
        return try {
            val (bn2D, latScaled) = cantorUnpair(bn3D)
            val (rScaled, lonScaled) = cantorUnpair(bn2D)

            val distanceAU = rScaled.toDouble() / AU_SCALE
            val eclipticLong = lonScaled.toDouble() / ANGLE_SCALE
            val eclipticLat = latScaled.toDouble() / ANGLE_SCALE - 90.0

            Triple(distanceAU, eclipticLong, eclipticLat)
        } catch (e: IOException)  // TODO: catch specific type {
            null
        }
    }

    // =========================================================================
    // BRAHIM SEQUENCE RESONANCE
    // =========================================================================

    /**
     * Check if position resonates with Brahim sequence values.
     *
     * The sequence {27, 42, 60, 75, 97, 121, 136, 154, 172, 187}
     * may correspond to orbital radii or angular positions.
     */
    private fun findSequenceResonance(distanceAU: Double, longitudeDeg: Double): String? {
        val resonances = mutableListOf<String>()

        // Check if distance (scaled) is near sequence values
        // Scale: sequence values as 0.1 AU increments
        val distanceScaled = distanceAU * 10
        for ((idx, value) in BrahimConstants.BRAHIM_SEQUENCE.withIndex()) {
            if (abs(distanceScaled - value) < 0.5) {
                resonances.add("Distance ≈ B[$idx]=$value (${value/10.0} AU)")
            }
        }

        // Check longitude
        for ((idx, value) in BrahimConstants.BRAHIM_SEQUENCE.withIndex()) {
            val lonMod = longitudeDeg % 360
            if (abs(lonMod - value) < 1.0 || abs(lonMod - (360 - value)) < 1.0) {
                resonances.add("Longitude ≈ B[$idx]=$value°")
            }
        }

        // Check sum relationship
        if (abs(distanceAU * 10 + longitudeDeg - BrahimConstants.BRAHIM_SUM) < 1.0) {
            resonances.add("Distance + Longitude ≈ 214 (Sum)")
        }

        return if (resonances.isNotEmpty()) resonances.joinToString("; ") else null
    }

    /**
     * Find bodies with orbital radii matching Brahim sequence.
     */
    fun findSequenceResonantBodies(): List<Pair<CelestialBody, String>> {
        val results = mutableListOf<Pair<CelestialBody, String>>()

        for (body in SOLAR_SYSTEM + MOONS) {
            val auScaled = body.semiMajorAxisAU * 10  // Scale to match sequence range

            for ((idx, value) in BrahimConstants.BRAHIM_SEQUENCE.withIndex()) {
                if (abs(auScaled - value) < 2.0) {
                    results.add(body to "Semi-major axis ${body.semiMajorAxisAU} AU ≈ B[$idx]=$value/10")
                }
            }

            // Also check if period matches
            val periodScaled = body.orbitalPeriodDays / 10
            for ((idx, value) in BrahimConstants.BRAHIM_SEQUENCE.withIndex()) {
                if (abs(periodScaled - value) < 2.0) {
                    results.add(body to "Period ${body.orbitalPeriodDays} days ≈ B[$idx]=${value}0")
                }
            }
        }

        return results
    }

    // =========================================================================
    // SOLAR SYSTEM MAP GENERATION
    // =========================================================================

    /**
     * Generate a complete Brahim map of the Solar System.
     */
    fun generateSolarSystemMap(): SolarSystemMap {
        val bodyMappings = SOLAR_SYSTEM.map { body ->
            val id = createBodyID(body)
            BodyMapping(body, id)
        }

        val moonMappings = MOONS.map { moon ->
            val id = createBodyID(moon)
            BodyMapping(moon, id)
        }

        // Find interesting resonances
        val resonances = findSequenceResonantBodies()

        // Calculate map statistics
        val totalBodies = bodyMappings.size + moonMappings.size
        val maxBN = (bodyMappings + moonMappings).maxOfOrNull { it.id.brahimNumber3D } ?: 0

        return SolarSystemMap(
            bodies = bodyMappings,
            moons = moonMappings,
            resonances = resonances,
            statistics = MapStatistics(
                totalBodies = totalBodies,
                maxBrahimNumber = maxBN,
                sequenceSum = BrahimConstants.BRAHIM_SUM
            )
        )
    }

    /**
     * Calculate position of a body at a given time (simplified).
     *
     * @param body Celestial body
     * @param daysSinceJ2000 Days since J2000 epoch (Jan 1, 2000 12:00 TT)
     * @return Approximate ecliptic longitude in degrees
     */
    fun calculateMeanLongitude(body: CelestialBody, daysSinceJ2000: Double): Double {
        if (body.orbitalPeriodDays == 0.0) return 0.0

        val meanMotion = 360.0 / body.orbitalPeriodDays  // degrees per day
        val meanAnomaly = (meanMotion * daysSinceJ2000) % 360

        // Simplified - ignoring longitude of perihelion for now
        return (meanAnomaly + 360) % 360
    }

    /**
     * Create a snapshot of the Solar System at a given date.
     *
     * @param year Year (e.g., 2026)
     * @param month Month (1-12)
     * @param day Day (1-31)
     */
    fun createSnapshot(year: Int, month: Int, day: Int): SolarSystemSnapshot {
        // Calculate days since J2000
        val daysSinceJ2000 = calculateDaysSinceJ2000(year, month, day)

        val positions = SOLAR_SYSTEM.map { body ->
            val longitude = calculateMeanLongitude(body, daysSinceJ2000)
            val id = createSolarID(body.semiMajorAxisAU, longitude, 0.0, body)
            BodyPosition(body, longitude, id)
        }

        return SolarSystemSnapshot(
            date = "$year-${month.toString().padStart(2, '0')}-${day.toString().padStart(2, '0')}",
            daysSinceJ2000 = daysSinceJ2000,
            positions = positions
        )
    }

    private fun calculateDaysSinceJ2000(year: Int, month: Int, day: Int): Double {
        // Simplified Julian Day calculation
        val a = (14 - month) / 12
        val y = year + 4800 - a
        val m = month + 12 * a - 3

        val jd = day + (153 * m + 2) / 5 + 365 * y + y / 4 - y / 100 + y / 400 - 32045

        // J2000 = JD 2451545.0
        return jd - 2451545.0
    }

    // =========================================================================
    // FORMATTING
    // =========================================================================

    private fun formatSolarHumanId(
        distanceAU: Double,
        longitudeDeg: Double,
        latitudeDeg: Double,
        body: CelestialBody?
    ): String {
        val bodyPrefix = body?.name?.take(3)?.uppercase() ?: "SOL"
        val distStr = "%.2f".format(distanceAU)
        val lonStr = "%.1f".format(longitudeDeg)
        val latStr = if (latitudeDeg >= 0) "+%.1f".format(latitudeDeg) else "%.1f".format(latitudeDeg)

        return "$bodyPrefix:${distStr}AU@${lonStr}°/${latStr}°"
    }

    /**
     * Format a Solar System map as ASCII art.
     */
    fun formatMapASCII(map: SolarSystemMap): String {
        val sb = StringBuilder()

        sb.appendLine("╔══════════════════════════════════════════════════════════════════╗")
        sb.appendLine("║           BRAHIM SOLAR SYSTEM MAP (BNv1-Solar)                   ║")
        sb.appendLine("╠══════════════════════════════════════════════════════════════════╣")

        sb.appendLine("║  Body        │ Distance (AU) │ Brahim Number    │ Digital Root  ║")
        sb.appendLine("╠══════════════╪═══════════════╪══════════════════╪═══════════════╣")

        for (mapping in map.bodies) {
            val name = mapping.body.name.padEnd(12)
            val dist = "%.3f".format(mapping.body.semiMajorAxisAU).padStart(13)
            val bn = mapping.id.brahimNumber.toString().padStart(16)
            val dr = mapping.id.digitalRoot.toString().padStart(13)
            sb.appendLine("║  $name│$dist │$bn │$dr ║")
        }

        sb.appendLine("╠══════════════════════════════════════════════════════════════════╣")
        sb.appendLine("║  MOONS                                                           ║")
        sb.appendLine("╠══════════════╪═══════════════╪══════════════════╪═══════════════╣")

        for (mapping in map.moons.take(5)) {
            val name = mapping.body.name.padEnd(12)
            val dist = "%.5f".format(mapping.body.semiMajorAxisAU).padStart(13)
            val bn = mapping.id.brahimNumber.toString().padStart(16)
            val dr = mapping.id.digitalRoot.toString().padStart(13)
            sb.appendLine("║  $name│$dist │$bn │$dr ║")
        }

        sb.appendLine("╠══════════════════════════════════════════════════════════════════╣")
        sb.appendLine("║  SEQUENCE RESONANCES                                             ║")
        sb.appendLine("╠══════════════════════════════════════════════════════════════════╣")

        for ((body, resonance) in map.resonances.take(5)) {
            val line = "${body.name}: $resonance".take(64).padEnd(64)
            sb.appendLine("║  $line║")
        }

        sb.appendLine("╠══════════════════════════════════════════════════════════════════╣")
        sb.appendLine("║  STATISTICS                                                      ║")
        sb.appendLine("║  Total Bodies: ${map.statistics.totalBodies.toString().padEnd(49)}║")
        sb.appendLine("║  Max BN: ${map.statistics.maxBrahimNumber.toString().padEnd(55)}║")
        sb.appendLine("║  Sequence Sum: ${map.statistics.sequenceSum.toString().padEnd(49)}║")
        sb.appendLine("╚══════════════════════════════════════════════════════════════════╝")

        return sb.toString()
    }
}

// =========================================================================
// DATA CLASSES
// =========================================================================

data class BodyMapping(
    val body: CelestialBody,
    val id: SolarBrahimID
)

data class BodyPosition(
    val body: CelestialBody,
    val eclipticLongitude: Double,
    val id: SolarBrahimID
)

data class MapStatistics(
    val totalBodies: Int,
    val maxBrahimNumber: Long,
    val sequenceSum: Int
)

data class SolarSystemMap(
    val bodies: List<BodyMapping>,
    val moons: List<BodyMapping>,
    val resonances: List<Pair<CelestialBody, String>>,
    val statistics: MapStatistics
)

data class SolarSystemSnapshot(
    val date: String,
    val daysSinceJ2000: Double,
    val positions: List<BodyPosition>
)
