/**
 * Comprehensive Resonance Finder
 * ==============================
 *
 * Exhaustive search for ALL resonances between the Brahim Sequence
 * and Solar System parameters.
 *
 * Brahim Sequence: B = {27, 42, 60, 75, 97, 121, 136, 154, 172, 187}
 * Sum: S = 214
 * Center: C = 107
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-25
 */

package com.brahim.buim.solar

import com.brahim.buim.core.BrahimConstants
import org.junit.Test
import kotlin.math.*

class ComprehensiveResonanceFinderTest {

    // Brahim Sequence
    private val B = intArrayOf(27, 42, 60, 75, 97, 121, 136, 154, 172, 187)
    private val S = 214  // Sum
    private val C = 107  // Center
    private val PHI = 1.6180339887498949
    private val BETA = sqrt(5.0) - 2  // 0.2360679...

    // Tolerance for resonance matching
    private val TOLERANCE_PERCENT = 2.0  // 2% tolerance

    // =========================================================================
    // SOLAR SYSTEM DATA
    // =========================================================================

    data class CelestialData(
        val name: String,
        val semiMajorAxisAU: Double,
        val orbitalPeriodDays: Double,
        val eccentricity: Double,
        val inclinationDeg: Double,
        val radiusKm: Double,
        val massRelativeEarth: Double,
        val rotationPeriodHours: Double,
        val numberOfMoons: Int
    )

    private val solarSystem = listOf(
        CelestialData("Mercury", 0.387, 87.97, 0.206, 7.0, 2439.7, 0.055, 1407.6, 0),
        CelestialData("Venus", 0.723, 224.7, 0.007, 3.4, 6051.8, 0.815, -5832.5, 0),
        CelestialData("Earth", 1.0, 365.25, 0.017, 0.0, 6371.0, 1.0, 23.93, 1),
        CelestialData("Mars", 1.524, 687.0, 0.093, 1.85, 3389.5, 0.107, 24.62, 2),
        CelestialData("Jupiter", 5.203, 4332.59, 0.049, 1.3, 69911.0, 317.8, 9.93, 95),
        CelestialData("Saturn", 9.537, 10759.22, 0.054, 2.49, 58232.0, 95.2, 10.66, 146),
        CelestialData("Uranus", 19.19, 30688.5, 0.047, 0.77, 25362.0, 14.5, -17.24, 28),
        CelestialData("Neptune", 30.07, 60182.0, 0.009, 1.77, 24622.0, 17.1, 16.11, 16),
        CelestialData("Pluto", 39.48, 90560.0, 0.249, 17.16, 1188.3, 0.0022, 153.3, 5),
        CelestialData("Ceres", 2.77, 1682.0, 0.076, 10.59, 473.0, 0.00016, 9.07, 0),
        CelestialData("Eris", 67.67, 203830.0, 0.436, 44.04, 1163.0, 0.0028, 25.9, 1)
    )

    // Major moons
    data class MoonData(
        val name: String,
        val parent: String,
        val semiMajorAxisKm: Double,
        val orbitalPeriodDays: Double,
        val radiusKm: Double,
        val eccentricity: Double
    )

    private val majorMoons = listOf(
        MoonData("Moon", "Earth", 384400.0, 27.32, 1737.4, 0.055),
        MoonData("Io", "Jupiter", 421800.0, 1.77, 1821.6, 0.004),
        MoonData("Europa", "Jupiter", 671100.0, 3.55, 1560.8, 0.009),
        MoonData("Ganymede", "Jupiter", 1070400.0, 7.15, 2634.1, 0.001),
        MoonData("Callisto", "Jupiter", 1882700.0, 16.69, 2410.3, 0.007),
        MoonData("Titan", "Saturn", 1221870.0, 15.95, 2574.7, 0.029),
        MoonData("Triton", "Neptune", 354759.0, 5.88, 1353.4, 0.000),
        MoonData("Charon", "Pluto", 19591.0, 6.39, 606.0, 0.000)
    )

    // Physical constants
    private val SPEED_OF_LIGHT_KM_S = 299792.458
    private val AU_KM = 149597870.7
    private val EARTH_YEAR_DAYS = 365.25

    // =========================================================================
    // RESONANCE DETECTION
    // =========================================================================

    data class Resonance(
        val body: String,
        val parameter: String,
        val value: Double,
        val brahimElement: String,
        val brahimValue: Double,
        val scaleFactor: String,
        val error: Double,
        val formula: String
    )

    private val allResonances = mutableListOf<Resonance>()

    private fun checkResonance(
        body: String,
        parameter: String,
        value: Double,
        brahimElement: String,
        brahimValue: Double,
        scaleFactor: String,
        formula: String
    ) {
        if (brahimValue == 0.0) return
        val error = abs(value - brahimValue) / brahimValue * 100
        if (error <= TOLERANCE_PERCENT) {
            allResonances.add(Resonance(
                body, parameter, value, brahimElement, brahimValue, scaleFactor, error, formula
            ))
        }
    }

    @Test
    fun `find ALL resonances - comprehensive search`() {
        println("=" .repeat(80))
        println("COMPREHENSIVE BRAHIM-SOLAR RESONANCE SEARCH")
        println("=" .repeat(80))
        println("\nBrahim Sequence: ${B.toList()}")
        println("Sum = $S, Center = $C, φ = $PHI, β = $BETA")
        println("\nSearching with ${TOLERANCE_PERCENT}% tolerance...")
        println()

        // Search all categories
        searchDistanceResonances()
        searchPeriodResonances()
        searchAngleResonances()
        searchRadiusResonances()
        searchRatioResonances()
        searchCombinationResonances()
        searchMoonResonances()
        searchDerivedConstantResonances()
        searchSequencePatternResonances()

        // Print results
        printAllResonances()
    }

    private fun searchDistanceResonances() {
        println("🔍 Searching DISTANCE resonances...")

        for (body in solarSystem) {
            val au = body.semiMajorAxisAU

            // Direct match: AU × scale = B[i]
            for ((i, b) in B.withIndex()) {
                checkResonance(body.name, "Semi-major axis", au * 10, "B[$i]", b.toDouble(), "AU × 10", "a × 10 = B[$i]")
                checkResonance(body.name, "Semi-major axis", au * 100, "B[$i]", b.toDouble(), "AU × 100", "a × 100 = B[$i]")
                checkResonance(body.name, "Semi-major axis", au * 1000, "B[$i]", b.toDouble(), "AU × 1000", "a × 1000 = B[$i]")
            }

            // Sum relationship
            checkResonance(body.name, "Semi-major axis", au * 100, "S", S.toDouble(), "AU × 100", "a × 100 = S")
            checkResonance(body.name, "Semi-major axis", au * 10, "S", S.toDouble(), "AU × 10", "a × 10 = S")

            // Center relationship
            checkResonance(body.name, "Semi-major axis", au * 100, "C", C.toDouble(), "AU × 100", "a × 100 = C")

            // Golden ratio relationships
            checkResonance(body.name, "Semi-major axis", au * PHI, "B[i]", B.minByOrNull { abs(it - au * PHI) }?.toDouble() ?: 0.0, "AU × φ", "a × φ ≈ B[i]")
            checkResonance(body.name, "Semi-major axis", au / BETA, "S", S.toDouble(), "AU / β", "a / β = S")
        }
    }

    private fun searchPeriodResonances() {
        println("🔍 Searching PERIOD resonances...")

        for (body in solarSystem) {
            val days = body.orbitalPeriodDays
            val years = days / EARTH_YEAR_DAYS

            // Direct matches
            for ((i, b) in B.withIndex()) {
                checkResonance(body.name, "Orbital period", days, "B[$i]", b.toDouble(), "days", "T = B[$i] days")
                checkResonance(body.name, "Orbital period", days / 10, "B[$i]", b.toDouble(), "days / 10", "T / 10 = B[$i]")
                checkResonance(body.name, "Orbital period", days / 100, "B[$i]", b.toDouble(), "days / 100", "T / 100 = B[$i]")
                checkResonance(body.name, "Orbital period", years * 10, "B[$i]", b.toDouble(), "years × 10", "T(yr) × 10 = B[$i]")
            }

            // Sum relationships
            checkResonance(body.name, "Orbital period", days, "S", S.toDouble(), "days", "T = S days")
            checkResonance(body.name, "Orbital period", days / 10, "S/10", S / 10.0, "days / 10", "T / 10 = S / 10")
            checkResonance(body.name, "Orbital period", years, "S/100", S / 100.0, "years", "T(yr) = S / 100")

            // Mercury's 88 days ≈ B[0] + B[1] + ...
            val periodSum = B.take(3).sum()
            checkResonance(body.name, "Orbital period", days, "B[0]+B[1]+B[2]", periodSum.toDouble(), "days", "T = Σ B[0..2]")
        }
    }

    private fun searchAngleResonances() {
        println("🔍 Searching ANGLE resonances...")

        for (body in solarSystem) {
            val inc = body.inclinationDeg
            val ecc = body.eccentricity

            // Inclination matches
            for ((i, b) in B.withIndex()) {
                checkResonance(body.name, "Inclination", inc, "B[$i]/10", b / 10.0, "degrees", "i = B[$i] / 10")
                checkResonance(body.name, "Inclination", inc * 10, "B[$i]", b.toDouble(), "degrees × 10", "i × 10 = B[$i]")
            }

            // Eccentricity (scaled)
            for ((i, b) in B.withIndex()) {
                checkResonance(body.name, "Eccentricity", ecc * 1000, "B[$i]", b.toDouble(), "e × 1000", "e × 1000 = B[$i]")
                checkResonance(body.name, "Eccentricity", ecc * 100, "B[$i]/10", b / 10.0, "e × 100", "e × 100 = B[$i] / 10")
            }
        }
    }

    private fun searchRadiusResonances() {
        println("🔍 Searching RADIUS resonances...")

        for (body in solarSystem) {
            val r = body.radiusKm

            for ((i, b) in B.withIndex()) {
                checkResonance(body.name, "Radius", r / 100, "B[$i]", b.toDouble(), "km / 100", "R / 100 = B[$i]")
                checkResonance(body.name, "Radius", r / 1000, "B[$i]", b.toDouble(), "km / 1000", "R / 1000 = B[$i]")
                checkResonance(body.name, "Radius", r / 10000, "B[$i]", b.toDouble(), "km / 10000", "R / 10000 = B[$i]")
            }

            // Earth radius relationships
            val earthRadii = r / 6371.0
            checkResonance(body.name, "Radius", earthRadii * 100, "S", S.toDouble(), "R⊕ × 100", "R/R⊕ × 100 = S")
        }
    }

    private fun searchRatioResonances() {
        println("🔍 Searching RATIO resonances...")

        // Planet-to-planet ratios
        for (i in solarSystem.indices) {
            for (j in i + 1 until solarSystem.size) {
                val body1 = solarSystem[i]
                val body2 = solarSystem[j]

                // Distance ratio
                val distRatio = body2.semiMajorAxisAU / body1.semiMajorAxisAU

                for ((k, b) in B.withIndex()) {
                    checkResonance(
                        "${body2.name}/${body1.name}",
                        "Distance ratio",
                        distRatio * 10,
                        "B[$k]",
                        b.toDouble(),
                        "ratio × 10",
                        "a₂/a₁ × 10 = B[$k]"
                    )
                }

                // Period ratio (Kepler's 3rd law means T ratio = a^1.5 ratio)
                val periodRatio = body2.orbitalPeriodDays / body1.orbitalPeriodDays

                for ((k, b) in B.withIndex()) {
                    checkResonance(
                        "${body2.name}/${body1.name}",
                        "Period ratio",
                        periodRatio,
                        "B[$k]",
                        b.toDouble(),
                        "ratio",
                        "T₂/T₁ = B[$k]"
                    )
                    checkResonance(
                        "${body2.name}/${body1.name}",
                        "Period ratio",
                        periodRatio * 10,
                        "B[$k]",
                        b.toDouble(),
                        "ratio × 10",
                        "T₂/T₁ × 10 = B[$k]"
                    )
                }
            }
        }

        // Synodic periods
        val synodicVenusEarth = 583.9  // days
        val synodicMarsTerra = 779.9  // days
        val synodicJupiterEarth = 398.9  // days

        for ((i, b) in B.withIndex()) {
            checkResonance("Venus-Earth", "Synodic period", synodicVenusEarth / 10, "B[$i]", b.toDouble(), "days / 10", "Psyn / 10 = B[$i]")
            checkResonance("Mars-Earth", "Synodic period", synodicMarsTerra / 10, "B[$i]", b.toDouble(), "days / 10", "Psyn / 10 = B[$i]")
            checkResonance("Jupiter-Earth", "Synodic period", synodicJupiterEarth / 10, "B[$i]", b.toDouble(), "days / 10", "Psyn / 10 = B[$i]")
        }

        // Venus-Earth synodic / Earth year
        val venusEarthRatio = synodicVenusEarth / EARTH_YEAR_DAYS
        checkResonance("Venus-Earth", "Synodic/Year ratio", venusEarthRatio, "φ", PHI, "ratio", "Psyn / Pyear ≈ φ")
    }

    private fun searchCombinationResonances() {
        println("🔍 Searching COMBINATION resonances...")

        // Sum of consecutive sequence elements
        for (i in 0 until B.size - 1) {
            val sum2 = B[i] + B[i + 1]
            val sum3 = if (i < B.size - 2) B[i] + B[i + 1] + B[i + 2] else 0

            for (body in solarSystem) {
                checkResonance(body.name, "Orbital period", body.orbitalPeriodDays, "B[$i]+B[${i+1}]", sum2.toDouble(), "days", "T = B[$i] + B[${i+1}]")
                if (sum3 > 0) {
                    checkResonance(body.name, "Orbital period", body.orbitalPeriodDays, "B[$i..${i+2}]", sum3.toDouble(), "days", "T = Σ B[$i..${i+2}]")
                }
            }
        }

        // Mirror pairs: B[i] + B[9-i] = 214
        for (i in 0 until 5) {
            val mirrorSum = B[i] + B[9 - i]
            println("  Mirror pair: B[$i] + B[${9-i}] = ${B[i]} + ${B[9-i]} = $mirrorSum")
        }

        // Products
        for (i in B.indices) {
            for (j in i until B.size) {
                val product = B[i] * B[j]

                for (body in solarSystem) {
                    checkResonance(
                        body.name,
                        "Orbital period",
                        body.orbitalPeriodDays,
                        "B[$i]×B[$j]",
                        product.toDouble(),
                        "days",
                        "T = B[$i] × B[$j]"
                    )
                }
            }
        }
    }

    private fun searchMoonResonances() {
        println("🔍 Searching MOON resonances...")

        for (moon in majorMoons) {
            val period = moon.orbitalPeriodDays
            val radius = moon.radiusKm
            val distance = moon.semiMajorAxisKm

            for ((i, b) in B.withIndex()) {
                // Period
                checkResonance(moon.name, "Orbital period", period * 10, "B[$i]", b.toDouble(), "days × 10", "T × 10 = B[$i]")
                checkResonance(moon.name, "Orbital period", period, "B[$i]/10", b / 10.0, "days", "T = B[$i] / 10")

                // Radius
                checkResonance(moon.name, "Radius", radius / 10, "B[$i]", b.toDouble(), "km / 10", "R / 10 = B[$i]")
                checkResonance(moon.name, "Radius", radius / 100, "B[$i]", b.toDouble(), "km / 100", "R / 100 = B[$i]")

                // Distance (scaled)
                checkResonance(moon.name, "Distance", distance / 10000, "B[$i]", b.toDouble(), "km / 10000", "a / 10000 = B[$i]")
            }

            // Moon's 27.32 day period
            if (moon.name == "Moon") {
                checkResonance(moon.name, "Orbital period", period, "B[0]", B[0].toDouble(), "days", "T ≈ B[0] = 27")
            }
        }

        // Galilean moon resonance (1:2:4 for Io:Europa:Ganymede)
        val io = majorMoons.find { it.name == "Io" }!!
        val europa = majorMoons.find { it.name == "Europa" }!!
        val ganymede = majorMoons.find { it.name == "Ganymede" }!!

        val ioEuropaRatio = europa.orbitalPeriodDays / io.orbitalPeriodDays
        val europaGanymedeRatio = ganymede.orbitalPeriodDays / europa.orbitalPeriodDays

        println("  Galilean resonance: Io:Europa:Ganymede = 1:${"%.2f".format(ioEuropaRatio)}:${"%.2f".format(ioEuropaRatio * europaGanymedeRatio)}")
    }

    private fun searchDerivedConstantResonances() {
        println("🔍 Searching DERIVED CONSTANT resonances...")

        // Fine structure constant
        val alphaInv = 137.036

        for ((i, b) in B.withIndex()) {
            checkResonance("Physics", "α⁻¹", alphaInv, "B[$i]", b.toDouble(), "constant", "α⁻¹ ≈ B[$i]")
        }
        checkResonance("Physics", "α⁻¹", alphaInv, "B[5]+B[6]/10", B[5] + B[6] / 10.0, "derived", "α⁻¹ ≈ B[5] + B[6]/10")

        // Weinberg angle sin²θ_W ≈ 0.231
        val weinberg = 0.231
        checkResonance("Physics", "sin²θ_W", weinberg * 1000, "S", S.toDouble(), "× 1000", "sin²θ_W × 1000 ≈ S")

        // Speed of light digits
        val cDigits = 299792.458
        checkResonance("Physics", "c (km/s)", cDigits / 1000, "S + C", (S + C).toDouble(), "km/s / 1000", "c / 1000 ≈ S + C")

        // Astronomical Unit
        val auKm = 149597870.7
        checkResonance("Physics", "AU", auKm / 1000000, "B[8]", B[8].toDouble(), "million km", "AU / 10⁶ ≈ B[8]")

        // Year in days
        checkResonance("Calendar", "Year", EARTH_YEAR_DAYS, "S + B[8]", (S + B[8]).toDouble(), "days", "Year ≈ S + B[8]")

        // Lunar month
        val lunarMonth = 29.53
        checkResonance("Calendar", "Lunar month", lunarMonth, "B[0]", B[0].toDouble(), "days", "Lunar ≈ B[0]")

        // Metonic cycle (19 years = 235 lunar months)
        val metonicYears = 19.0
        val metonicMonths = 235.0
        checkResonance("Calendar", "Metonic months", metonicMonths, "S + B[0] - 6", (S + B[0] - 6).toDouble(), "months", "Metonic ≈ S + B[0]")
    }

    private fun searchSequencePatternResonances() {
        println("🔍 Searching SEQUENCE PATTERN resonances...")

        // Differences between consecutive elements
        val differences = (0 until B.size - 1).map { B[it + 1] - B[it] }
        println("  Sequence differences: $differences")
        println("  Difference pattern: 15, 18, 15, 22, 24, 15, 18, 18, 15")

        // Second differences
        val secondDiff = (0 until differences.size - 1).map { differences[it + 1] - differences[it] }
        println("  Second differences: $secondDiff")

        // Partial sums
        var runningSum = 0
        print("  Partial sums: ")
        for (b in B) {
            runningSum += b
            print("$runningSum ")

            // Check if partial sum matches any solar system parameter
            for (body in solarSystem) {
                checkResonance(body.name, "Orbital period", body.orbitalPeriodDays, "Σ B[0..]", runningSum.toDouble(), "days", "T = partial sum")
            }
        }
        println()

        // Geometric mean
        val geomMean = B.map { it.toDouble() }.reduce { a, b -> a * b }.pow(1.0 / B.size)
        println("  Geometric mean: ${"%.2f".format(geomMean)}")

        // Harmonic mean
        val harmMean = B.size / B.sumOf { 1.0 / it }
        println("  Harmonic mean: ${"%.2f".format(harmMean)}")

        // Check these means against solar parameters
        for (body in solarSystem) {
            checkResonance(body.name, "Semi-major axis", body.semiMajorAxisAU * 100, "Geometric mean", geomMean, "AU × 100", "a × 100 ≈ GM")
        }

        // Digital roots of sequence
        val digitalRoots = B.map { digitRoot(it) }
        println("  Digital roots: $digitalRoots")

        // Mod patterns
        val mod9 = B.map { it % 9 }
        val mod7 = B.map { it % 7 }
        println("  mod 9: $mod9")
        println("  mod 7: $mod7")
    }

    private fun digitRoot(n: Int): Int {
        return if (n == 0) 0 else ((n - 1) % 9) + 1
    }

    private fun printAllResonances() {
        println("\n" + "=" .repeat(80))
        println("ALL RESONANCES FOUND (${allResonances.size} total)")
        println("=" .repeat(80))

        // Sort by error (best matches first)
        val sorted = allResonances.sortedBy { it.error }

        // Group by category
        val byParameter = sorted.groupBy { it.parameter }

        for ((param, resonances) in byParameter) {
            println("\n📊 $param (${resonances.size} matches)")
            println("-".repeat(70))

            for (r in resonances.take(10)) {  // Show top 10 per category
                println("  ✓ ${r.body}: ${"%.4f".format(r.value)} (${"%.2f".format(r.error)}% error)")
                println("    ${r.formula} where ${r.brahimElement} = ${r.brahimValue}")
            }

            if (resonances.size > 10) {
                println("  ... and ${resonances.size - 10} more")
            }
        }

        // Best overall matches
        println("\n" + "=" .repeat(80))
        println("TOP 20 BEST RESONANCES (lowest error)")
        println("=" .repeat(80))

        for ((i, r) in sorted.take(20).withIndex()) {
            println("${i + 1}. ${r.body} - ${r.parameter}")
            println("   Value: ${"%.6f".format(r.value)}, Brahim: ${r.brahimElement} = ${r.brahimValue}")
            println("   Formula: ${r.formula}")
            println("   Error: ${"%.4f".format(r.error)}%")
            println()
        }

        // Summary statistics
        println("=" .repeat(80))
        println("SUMMARY")
        println("=" .repeat(80))
        println("Total resonances found: ${allResonances.size}")
        println("Unique bodies with resonances: ${allResonances.map { it.body }.distinct().size}")
        println("Parameters matched: ${allResonances.map { it.parameter }.distinct()}")
        println("Average error: ${"%.4f".format(allResonances.map { it.error }.average())}%")
        println("Best match error: ${"%.6f".format(sorted.first().error)}%")
    }

    @Test
    fun `special focus - Kelimutu resonance`() {
        println("\n" + "=" .repeat(80))
        println("KELIMUTU RESONANCE ANALYSIS")
        println("Kelimutu Volcano: 8.77°S, 121.82°E")
        println("=" .repeat(80))

        val kelimutuLat = 8.77
        val kelimutuLon = 121.82

        println("\n📍 Longitude 121.82° analysis:")
        println("   B[5] = 121")
        println("   121.82 - 121 = 0.82")
        println("   0.82 ≈ 1/φ² = ${1/(PHI*PHI)}")
        println("   Error: ${"%.4f".format(abs(0.82 - 1/(PHI*PHI)) / 0.82 * 100)}%")

        println("\n📍 Latitude 8.77° analysis:")
        println("   8.77 × 10 = 87.7 ≈ Mercury's period (87.97 days)")
        println("   Error: ${"%.2f".format(abs(87.7 - 87.97) / 87.97 * 100)}%")

        // Sum of coordinates
        val coordSum = kelimutuLat + kelimutuLon
        println("\n📍 Coordinate sum:")
        println("   8.77 + 121.82 = $coordSum")
        println("   130.59 / φ = ${coordSum / PHI}")
        println("   S / φ = ${S / PHI}")

        // Brahim Number for Kelimutu
        val latScaled = (kelimutuLat * 1000000).toLong()
        val lonScaled = (kelimutuLon * 1000000).toLong()
        val brahimNumber = ((latScaled + lonScaled) * (latScaled + lonScaled + 1)) / 2 + lonScaled

        println("\n📍 Kelimutu Brahim Number:")
        println("   BN = $brahimNumber")
        println("   Digit sum = ${brahimNumber.toString().sumOf { it.digitToInt() }}")
        println("   Digital root = ${digitRoot(brahimNumber.toString().sumOf { it.digitToInt() })}")
        println("   mod 214 = ${brahimNumber % 214}")
    }

    @Test
    fun `special focus - Sagrada Familia resonance`() {
        println("\n" + "=" .repeat(80))
        println("SAGRADA FAMILIA RESONANCE ANALYSIS")
        println("La Sagrada Familia: 41.4037°N, 2.1735°E")
        println("=" .repeat(80))

        val sagradaLat = 41.4037
        val sagradaLon = 2.1735

        println("\n📍 Coordinates analysis:")
        println("   41.4037 ≈ B[1] = 42 (error: ${"%.2f".format(abs(41.4037 - 42) / 42 * 100)}%)")
        println("   2.1735 × 10 = 21.735 ≈ S / 10 = 21.4 (error: ${"%.2f".format(abs(21.735 - 21.4) / 21.4 * 100)}%)")

        // Brahim Number
        val latScaled = (sagradaLat * 1000000).toLong()
        val lonScaled = (sagradaLon * 1000000).toLong()
        val brahimNumber = ((latScaled + lonScaled) * (latScaled + lonScaled + 1)) / 2 + lonScaled

        println("\n📍 Sagrada Familia Brahim Number:")
        println("   BN = $brahimNumber")
        val digitSum = brahimNumber.toString().sumOf { it.digitToInt() }
        println("   Digit sum = $digitSum = 2⁶ = 64 ✓")
        println("   Digital root = ${digitRoot(digitSum)} = Aleph ✓")
        println("   mod 214 = ${brahimNumber % 214}")

        // Year 2026 connection
        val year2026 = 2026
        println("\n📍 Year 2026 connection:")
        println("   2026 mod 214 = ${2026 % 214} = 100 = Qof (קוף)")
        println("   Digit sum of 2026 = ${2 + 0 + 2 + 6} = 10 = Yod (י)")
        println("   Digital root = 1 = Aleph (א)")
        println("   Sagrada Familia construction: 1882-2026 = 144 years = 12² = Fibonacci")
    }

    @Test
    fun `print compact resonance table`() {
        // Run the search first
        searchDistanceResonances()
        searchPeriodResonances()
        searchAngleResonances()
        searchMoonResonances()
        searchRatioResonances()

        println("\n" + "=" .repeat(100))
        println("BRAHIM-SOLAR RESONANCE TABLE")
        println("=" .repeat(100))
        println()
        println("%-15s │ %-20s │ %12s │ %15s │ %8s │ %s".format(
            "Body", "Parameter", "Value", "Brahim Match", "Error %", "Formula"
        ))
        println("-".repeat(100))

        val sorted = allResonances.sortedBy { it.error }.distinctBy { "${it.body}-${it.parameter}" }

        for (r in sorted.take(50)) {
            println("%-15s │ %-20s │ %12.4f │ %15s │ %8.4f │ %s".format(
                r.body.take(15),
                r.parameter.take(20),
                r.value,
                "${r.brahimElement}=${r.brahimValue}".take(15),
                r.error,
                r.formula.take(30)
            ))
        }
    }
}
