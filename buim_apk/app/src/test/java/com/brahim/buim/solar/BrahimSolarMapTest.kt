/**
 * Brahim Solar Map Tests
 * ======================
 *
 * Demonstrates the Solar System geomap using Brahim Numbers.
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-25
 */

package com.brahim.buim.solar

import com.brahim.buim.core.BrahimConstants
import org.junit.Test
import kotlin.math.abs

class BrahimSolarMapTest {

    @Test
    fun `generate complete Solar System map`() {
        println("=" .repeat(70))
        println("BRAHIM SOLAR SYSTEM MAP")
        println("=" .repeat(70))

        val map = BrahimSolarMap.generateSolarSystemMap()

        println("\n📍 PLANETARY BODIES:")
        println("-".repeat(70))
        println("%-12s │ %10s │ %18s │ %6s │ %6s".format(
            "Body", "AU", "Brahim Number", "D.Root", "mod214"
        ))
        println("-".repeat(70))

        for (mapping in map.bodies) {
            println("%-12s │ %10.3f │ %18d │ %6d │ %6d".format(
                mapping.body.name,
                mapping.body.semiMajorAxisAU,
                mapping.id.brahimNumber,
                mapping.id.digitalRoot,
                mapping.id.mod214
            ))
        }

        println("\n🌙 MAJOR MOONS:")
        println("-".repeat(70))
        for (mapping in map.moons) {
            println("%-12s │ %10.5f │ %18d │ %6d │ %6d".format(
                mapping.body.name,
                mapping.body.semiMajorAxisAU,
                mapping.id.brahimNumber,
                mapping.id.digitalRoot,
                mapping.id.mod214
            ))
        }

        println("\n✨ SEQUENCE RESONANCES:")
        println("-".repeat(70))
        for ((body, resonance) in map.resonances) {
            println("${body.name}: $resonance")
        }

        println("\n📊 STATISTICS:")
        println("Total Bodies: ${map.statistics.totalBodies}")
        println("Max Brahim Number: ${map.statistics.maxBrahimNumber}")
        println("Brahim Sequence Sum: ${map.statistics.sequenceSum}")
    }

    @Test
    fun `create Solar System snapshot for 2026`() {
        println("\n" + "=" .repeat(70))
        println("SOLAR SYSTEM SNAPSHOT - January 25, 2026")
        println("=" .repeat(70))

        val snapshot = BrahimSolarMap.createSnapshot(2026, 1, 25)

        println("\nDate: ${snapshot.date}")
        println("Days since J2000: ${snapshot.daysSinceJ2000}")

        println("\n%-12s │ %10s │ %10s │ %18s".format(
            "Body", "AU", "Longitude", "Brahim Number"
        ))
        println("-".repeat(60))

        for (pos in snapshot.positions) {
            println("%-12s │ %10.3f │ %10.2f° │ %18d".format(
                pos.body.name,
                pos.body.semiMajorAxisAU,
                pos.eclipticLongitude,
                pos.id.brahimNumber
            ))
        }

        // Check if any planets are at special angles
        println("\n🎯 ANGULAR RESONANCES TODAY:")
        for (pos in snapshot.positions) {
            for ((idx, value) in BrahimConstants.BRAHIM_SEQUENCE.withIndex()) {
                if (abs(pos.eclipticLongitude - value) < 5.0) {
                    println("${pos.body.name} at ${pos.eclipticLongitude}° ≈ B[$idx] = $value°")
                }
            }
        }
    }

    @Test
    fun `demonstrate heliocentric coordinate encoding`() {
        println("\n" + "=" .repeat(70))
        println("HELIOCENTRIC COORDINATE ENCODING")
        println("=" .repeat(70))

        // Earth's position
        val earthPos = BrahimSolarMap.createSolarID(
            distanceAU = 1.0,
            eclipticLongDeg = 121.82,  // At Kelimutu longitude!
            eclipticLatDeg = 0.0,
            body = BrahimSolarMap.SOLAR_SYSTEM.find { it.name == "Earth" }
        )

        println("\n🌍 Earth at Kelimutu Longitude (121.82°):")
        println("Human ID: ${earthPos.humanId}")
        println("2D Brahim Number: ${earthPos.brahimNumber}")
        println("3D Brahim Number: ${earthPos.brahimNumber3D}")
        println("Digital Root: ${earthPos.digitalRoot}")
        println("mod 214: ${earthPos.mod214}")
        println("Resonance: ${earthPos.sequenceResonance ?: "None"}")

        // Decode it back
        val decoded = BrahimSolarMap.decodeSolarBN(earthPos.brahimNumber3D)
        if (decoded != null) {
            println("\n🔄 DECODED:")
            println("Distance: ${decoded.first} AU")
            println("Longitude: ${decoded.second}°")
            println("Latitude: ${decoded.third}°")
        }
    }

    @Test
    fun `find planetary orbital resonances with Brahim sequence`() {
        println("\n" + "=" .repeat(70))
        println("PLANETARY ORBITAL RESONANCES WITH BRAHIM SEQUENCE")
        println("Sequence: ${BrahimConstants.BRAHIM_SEQUENCE.toList()}")
        println("=" .repeat(70))

        println("\n🔬 ANALYSIS:")
        println("-".repeat(70))

        // Scale planetary distances to match sequence range
        println("\nPlanetary Semi-Major Axes scaled by 10:")
        for (body in BrahimSolarMap.SOLAR_SYSTEM) {
            val scaled = body.semiMajorAxisAU * 10
            val nearest = BrahimConstants.BRAHIM_SEQUENCE.minByOrNull { abs(it - scaled) }
            val distance = if (nearest != null) abs(scaled - nearest) else Double.MAX_VALUE

            if (distance < 5.0) {
                println("✓ ${body.name}: ${body.semiMajorAxisAU} AU × 10 = ${"%.2f".format(scaled)} ≈ $nearest")
            } else {
                println("  ${body.name}: ${body.semiMajorAxisAU} AU × 10 = ${"%.2f".format(scaled)}")
            }
        }

        // Check orbital periods
        println("\nOrbital Periods scaled by various factors:")
        for (body in BrahimSolarMap.SOLAR_SYSTEM.filter { it.orbitalPeriodDays > 0 }) {
            // Check period / 10
            val scaled = body.orbitalPeriodDays / 10
            for ((idx, value) in BrahimConstants.BRAHIM_SEQUENCE.withIndex()) {
                if (abs(scaled - value) < 3.0) {
                    println("${body.name}: ${body.orbitalPeriodDays} days ÷ 10 = ${"%.1f".format(scaled)} ≈ B[$idx]=$value")
                }
            }
        }
    }

    @Test
    fun `astronomical constants from Brahim sequence`() {
        println("\n" + "=" .repeat(70))
        println("ASTRONOMICAL CONSTANTS FROM BRAHIM SEQUENCE")
        println("=" .repeat(70))

        val sequence = BrahimConstants.BRAHIM_SEQUENCE
        val sum = BrahimConstants.BRAHIM_SUM  // 214
        val phi = BrahimConstants.PHI

        // Titius-Bode-like law using Brahim sequence
        println("\n📐 TITIUS-BODE COMPARISON:")
        println("Traditional: r = 0.4 + 0.3 × 2ⁿ")
        println("Brahim: r = B[n] / 100")
        println()
        println("%-10s │ %10s │ %10s │ %10s".format("Planet", "Actual AU", "Titius-Bode", "B[n]/100"))
        println("-".repeat(50))

        val planets = listOf(
            "Mercury" to 0.387,
            "Venus" to 0.723,
            "Earth" to 1.0,
            "Mars" to 1.524,
            "Asteroid" to 2.77,
            "Jupiter" to 5.203,
            "Saturn" to 9.537,
            "Uranus" to 19.19,
            "Neptune" to 30.07
        )

        for ((idx, planet) in planets.withIndex()) {
            val titiusBode = if (idx == 0) 0.4 else 0.4 + 0.3 * Math.pow(2.0, (idx - 1).toDouble())
            val brahimVal = if (idx < sequence.size) sequence[idx] / 100.0 else 0.0

            println("%-10s │ %10.3f │ %10.3f │ %10.3f".format(
                planet.first,
                planet.second,
                titiusBode,
                brahimVal
            ))
        }

        // Kepler's third law verification
        println("\n📏 KEPLER'S THIRD LAW:")
        println("T² = a³ (for years and AU)")
        println()

        for (body in BrahimSolarMap.SOLAR_SYSTEM.filter { it.orbitalPeriodDays > 0 }) {
            val tYears = body.orbitalPeriodDays / 365.25
            val tSquared = tYears * tYears
            val aCubed = Math.pow(body.semiMajorAxisAU, 3.0)

            // Should equal 1.0 for all planets
            val ratio = tSquared / aCubed

            println("%-10s: T²/a³ = %.6f".format(body.name, ratio))
        }

        // Golden ratio in orbital mechanics
        println("\n🌀 GOLDEN RATIO IN ORBITAL MECHANICS:")
        println("Venus/Earth synodic: 583.9 days")
        println("Earth year: 365.25 days")
        println("Ratio: ${583.9 / 365.25} ≈ φ = $phi")

        val venusEarthRatio = 583.9 / 365.25
        val phiError = abs(venusEarthRatio - phi) / phi * 100
        println("Error from φ: ${"%.2f".format(phiError)}%")

        // Sum 214 significance
        println("\n🔢 SUM 214 IN ASTRONOMY:")
        println("214 / 365.25 = ${"%.4f".format(214.0 / 365.25)} years")
        println("214 days ≈ 7.04 months (Venus's synodic half-cycle)")
        println("214 × 10 = 2140 = approximate lunar nodal cycle / 3.5")
    }

    @Test
    fun `print ASCII solar system map`() {
        val map = BrahimSolarMap.generateSolarSystemMap()
        println(BrahimSolarMap.formatMapASCII(map))
    }

    @Test
    fun `Voyager 1 position encoding`() {
        println("\n" + "=" .repeat(70))
        println("VOYAGER 1 POSITION (as of 2026)")
        println("=" .repeat(70))

        // Voyager 1 approximate position in 2026
        // Distance: ~165 AU, moving towards Ophiuchus
        val voyager = CelestialBody(
            name = "Voyager 1",
            type = BodyType.SPACECRAFT,
            semiMajorAxisAU = 165.0,  // Approximate heliocentric distance
            eccentricity = 0.0,       // N/A for escape trajectory
            inclinationDeg = 35.0,    // Approx ecliptic inclination
            orbitalPeriodDays = 0.0,  // N/A - not orbiting
            radiusKm = 0.001,         // Negligible
            massKg = 825.0            // ~825 kg
        )

        // Approximate ecliptic coordinates
        val voyagerID = BrahimSolarMap.createSolarID(
            distanceAU = 165.0,
            eclipticLongDeg = 260.0,   // Towards Ophiuchus/Sagittarius
            eclipticLatDeg = 35.0,      // Well above ecliptic
            body = voyager
        )

        println("\n🚀 VOYAGER 1:")
        println("Distance: 165 AU (≈24.7 billion km)")
        println("Direction: Ophiuchus constellation")
        println()
        println("Human ID: ${voyagerID.humanId}")
        println("2D Brahim Number: ${voyagerID.brahimNumber}")
        println("3D Brahim Number: ${voyagerID.brahimNumber3D}")
        println("Digital Root: ${voyagerID.digitalRoot}")
        println("mod 214: ${voyagerID.mod214}")

        // Interesting: 165 AU ≈ sum of outer planets
        println("\n📊 DISTANCE ANALYSIS:")
        println("165 AU ≈ Neptune (30) + Uranus (19) + Saturn (10) + Jupiter (5) + 101")
        println("165 / Brahim Sum 214 = ${"%.4f".format(165.0 / 214)}")
        println("165 × 1.297 ≈ 214")

        // Brahim sequence relationship
        println("\n🔗 SEQUENCE RELATIONSHIP:")
        val b8 = BrahimConstants.BRAHIM_SEQUENCE[8]  // 172
        val b7 = BrahimConstants.BRAHIM_SEQUENCE[7]  // 154
        println("B[8] = 172, B[7] = 154")
        println("165 is between B[7] and B[8]")
        println("165 = (172 + 154) / 2 + 2 = 163 + 2")
    }

    @Test
    fun `exoplanet coordinate system`() {
        println("\n" + "=" .repeat(70))
        println("EXOPLANET COORDINATE EXTENSION")
        println("=" .repeat(70))

        println("\n💫 PROXIMA CENTAURI b:")
        println("Distance from Earth: 4.24 light-years")
        println("Distance from host star: 0.0485 AU")

        // For exoplanets, we can use:
        // A = distance from Earth in light-years × 1,000,000
        // B = distance from host star in AU × 1,000,000

        val distanceFromEarth = 4.24  // light-years
        val distanceFromStar = 0.0485 // AU

        val a = (distanceFromEarth * 1_000_000).toLong()
        val b = (distanceFromStar * 1_000_000).toLong()

        // Cantor pairing
        val exoBN = ((a + b) * (a + b + 1)) / 2 + b

        println("\nBrahim Number encoding:")
        println("A (Earth distance): $a")
        println("B (Star distance): $b")
        println("Exoplanet Brahim Number: $exoBN")

        val digitSum = exoBN.toString().sumOf { it.digitToInt() }
        val digitalRoot = if (digitSum == 0) 0 else ((digitSum - 1) % 9) + 1
        println("Digital Root: $digitalRoot")
        println("mod 214: ${exoBN % 214}")

        println("\n🌟 TRAPPIST-1 SYSTEM:")
        println("Distance: 39.6 light-years")
        println("7 known planets in habitable zone")

        val trappistPlanets = listOf(
            "TRAPPIST-1b" to 0.0115,
            "TRAPPIST-1c" to 0.0158,
            "TRAPPIST-1d" to 0.0223,
            "TRAPPIST-1e" to 0.0293,
            "TRAPPIST-1f" to 0.0385,
            "TRAPPIST-1g" to 0.0469,
            "TRAPPIST-1h" to 0.0619
        )

        println("\n%-15s │ %10s │ %15s │ %8s".format("Planet", "AU", "Brahim Number", "D.Root"))
        println("-".repeat(55))

        for ((name, au) in trappistPlanets) {
            val distEarth = 39.6
            val aVal = (distEarth * 1_000_000).toLong()
            val bVal = (au * 1_000_000).toLong()
            val bn = ((aVal + bVal) * (aVal + bVal + 1)) / 2 + bVal

            val ds = bn.toString().sumOf { it.digitToInt() }
            val dr = if (ds == 0) 0 else ((ds - 1) % 9) + 1

            println("%-15s │ %10.4f │ %15d │ %8d".format(name, au, bn, dr))
        }
    }

    @Test
    fun `summary of Solar Brahim mapping`() {
        println("\n" + "=" .repeat(70))
        println("BRAHIM SOLAR MAP - SUMMARY")
        println("=" .repeat(70))

        println("""

The Brahim Solar Map extends BNv1 to celestial coordinates:

┌──────────────────────────────────────────────────────────────────┐
│ COORDINATE SYSTEM                                                │
├──────────────────────────────────────────────────────────────────┤
│ • Heliocentric distance (r) in AU × 1,000,000                    │
│ • Ecliptic longitude (λ) in degrees × 10,000                     │
│ • Ecliptic latitude (β) in degrees × 10,000                      │
│                                                                  │
│ BN_2D = Cantor(r_scaled, λ_scaled)                               │
│ BN_3D = Cantor(BN_2D, β_scaled)                                  │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ USE CASES                                                        │
├──────────────────────────────────────────────────────────────────┤
│ 1. Spacecraft tracking IDs                                       │
│ 2. Asteroid/comet cataloging                                     │
│ 3. Exoplanet databases                                           │
│ 4. Space mission waypoints                                       │
│ 5. Interplanetary navigation checkpoints                         │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ SEQUENCE RESONANCES FOUND                                        │
├──────────────────────────────────────────────────────────────────┤
│ • Kelimutu longitude (121.82°) ≈ B[5] = 121                      │
│ • Mars orbit (1.524 AU × 10 = 15.24) ≈ B[0]/2 = 13.5             │
│ • Mercury period (87.97 days) ≈ B[3] + 12.97 = 75 + 12.97        │
│ • Venus/Earth synodic (583.9 d) ≈ Sum × φ² = 214 × 2.618 = 560   │
└──────────────────────────────────────────────────────────────────┘

The Brahim Number provides a universal addressing scheme for any
position in the observable universe, compatible with the frozen
BNv1 specification.

        """.trimIndent())
    }
}
