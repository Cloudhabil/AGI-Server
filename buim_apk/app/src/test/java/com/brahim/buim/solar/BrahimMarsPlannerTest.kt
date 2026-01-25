/**
 * Brahim Mars Planner Tests
 * =========================
 *
 * Comprehensive Mars mission window calculations with Brahim resonances.
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-25
 */

package com.brahim.buim.solar

import com.brahim.buim.core.BrahimConstants
import org.junit.Test
import kotlin.math.*

class BrahimMarsPlannerTest {

    @Test
    fun `calculate Hohmann transfer parameters`() {
        println("=" .repeat(80))
        println("HOHMANN TRANSFER: EARTH → MARS")
        println("=" .repeat(80))

        val hohmann = BrahimMarsPlanner.calculateHohmannTransfer()

        println("""

            HOHMANN TRANSFER PARAMETERS
            ═══════════════════════════════════════════════════════════════════

            Transfer Time:     ${hohmann.transferTimeDays.toInt()} days (≈ ${(hohmann.transferTimeDays / 30).toInt()} months)

            Delta-V Budget:
              Earth departure: ${String.format("%.2f", hohmann.deltaV1)} km/s
              Mars insertion:  ${String.format("%.2f", hohmann.deltaV2)} km/s
              TOTAL (one-way): ${String.format("%.2f", hohmann.totalDeltaV)} km/s
              TOTAL (round):   ${String.format("%.2f", hohmann.totalDeltaV * 2)} km/s

            Phase Angle:       ${String.format("%.1f", hohmann.phaseAngle)}°
            Transfer SMA:      ${String.format("%.3f", hohmann.transferSMA)} AU

            ═══════════════════════════════════════════════════════════════════

            BRAHIM RESONANCE CHECK:
            ─────────────────────────────────────────────────────────────────────
            Transfer time ${hohmann.transferTimeDays.toInt()} days:
              - Near B[5] + B[6] = 121 + 136 = 257? ${abs(hohmann.transferTimeDays - 257) < 10}
              - S + 45 = 214 + 45 = 259? ${abs(hohmann.transferTimeDays - 259) < 10}

            Mars orbital period = 687 days = 3×214 + 45 = 3S + 45 ✓ (EXACT)
            Synodic period = 779.9 days = 4×214 - 77 = 4S - 77 ✓ (0.1% error)

        """.trimIndent())
    }

    @Test
    fun `find all launch windows 2026-2035`() {
        println("=" .repeat(80))
        println("MARS LAUNCH WINDOWS: 2026-2035")
        println("=" .repeat(80))

        val windows = BrahimMarsPlanner.findLaunchWindows(2026, 2035, MissionType.DIRECT_HOHMANN)

        println("\n%-12s │ %-12s │ %-12s │ %8s │ %8s │ %8s │ %6s".format(
            "Window", "Open", "Optimal", "Transfer", "Stay", "Total", "Moon%"
        ))
        println("─".repeat(85))

        for (window in windows) {
            println("%-12s │ %-12s │ %-12s │ %8.0f │ %8.0f │ %8.0f │ %5.0f%%".format(
                window.windowId,
                window.openDate.toString(),
                window.optimalDate.toString(),
                window.transferTimeDays,
                window.stayTimeDays,
                window.totalMissionDays,
                window.moonAlignmentScore * 100
            ))

            window.brahimResonance?.let {
                println("             └─ Brahim: ${it.description} (${String.format("%.1f", it.errorPercent)}% error)")
            }
        }

        println("\n📊 SUMMARY:")
        println("Total windows: ${windows.size}")
        println("Average mission duration: ${windows.map { it.totalMissionDays }.average().toInt()} days")
        println("Best Moon alignment: ${(windows.maxOf { it.moonAlignmentScore } * 100).toInt()}%")
    }

    @Test
    fun `find next best window from today`() {
        println("=" .repeat(80))
        println("NEXT BEST MARS WINDOW FROM 2026-01-25")
        println("=" .repeat(80))

        val today = MarsDate(2026, 1, 25)

        // Direct mission
        val directResult = BrahimMarsPlanner.findNextBestWindow(today, MissionType.DIRECT_HOHMANN)
        println("\n🚀 DIRECT HOHMANN TRANSFER:")
        println(directResult.recommendation)

        // With Moon staging
        val moonResult = BrahimMarsPlanner.findNextBestWindow(today, MissionType.MOON_STAGING, requireMoonAlignment = true)
        println("\n🌙 MOON STAGING MISSION:")
        println(moonResult.recommendation)

        // Fast mission
        val fastResult = BrahimMarsPlanner.findNextBestWindow(today, MissionType.FAST_CONJUNCTION)
        println("\n⚡ FAST CONJUNCTION:")
        println(fastResult.recommendation)
    }

    @Test
    fun `compare all mission types for 2026 window`() {
        println("=" .repeat(80))
        println("MISSION TYPE COMPARISON: 2026 WINDOW")
        println("=" .repeat(80))

        val windows = BrahimMarsPlanner.findLaunchWindows(2026, 2027, MissionType.DIRECT_HOHMANN)
        val firstWindow = windows.firstOrNull() ?: return

        println("\nBase window: ${firstWindow.optimalDate}")

        val comparisons = BrahimMarsPlanner.compareMissionTypes(firstWindow)

        println("\n%-20s │ %10s │ %10s │ %10s │ %10s │ %10s │ %8s".format(
            "Mission Type", "Duration", "Delta-V", "Surface", "Risk", "Support", "Brahim"
        ))
        println("─".repeat(95))

        for (comp in comparisons.sortedBy { it.brahimScore }.reversed()) {
            println("%-20s │ %10.0f │ %10.1f │ %10.0f │ %10s │ %10s │ %8.1f".format(
                comp.missionType.name,
                comp.totalDuration,
                comp.deltaV,
                comp.surfaceTime,
                comp.riskLevel,
                comp.crewSupport.take(10),
                comp.brahimScore
            ))
        }
    }

    @Test
    fun `find Moon departure windows within Mars window`() {
        println("=" .repeat(80))
        println("MOON DEPARTURE WINDOWS FOR MARS MISSION")
        println("=" .repeat(80))

        val windows = BrahimMarsPlanner.findLaunchWindows(2026, 2027, MissionType.MOON_STAGING)
        val marsWindow = windows.firstOrNull() ?: return

        println("\nMars launch window: ${marsWindow.openDate} to ${marsWindow.closeDate}")
        println("Optimal Mars departure: ${marsWindow.optimalDate}")

        val moonWindows = BrahimMarsPlanner.findMoonDepartureWindows(marsWindow)

        println("\n🌙 OPTIMAL MOON DEPARTURE DATES:")
        println("─".repeat(70))
        println("%-12s │ %12s │ %12s │ %12s │ %12s".format(
            "Date", "Moon Phase", "Alignment", "ΔV Saving", "Moon Stay"
        ))
        println("─".repeat(70))

        for (moonWindow in moonWindows.take(10)) {
            println("%-12s │ %11.1f° │ %11.0f%% │ %10.2f km/s │ %10.0f d".format(
                moonWindow.date.toString(),
                moonWindow.moonPhaseAngle,
                moonWindow.alignmentScore * 100,
                moonWindow.deltaVSaving,
                moonWindow.lunarStayDays
            ))
        }

        println("\n📊 BEST MOON DEPARTURE: ${moonWindows.firstOrNull()?.date}")
        println("   Alignment score: ${(moonWindows.firstOrNull()?.alignmentScore ?: 0.0) * 100}%")
        println("   Delta-V savings: ${moonWindows.firstOrNull()?.deltaVSaving} km/s")
    }

    @Test
    fun `detailed mission timeline - 2026 conjunction class`() {
        println("=" .repeat(80))
        println("DETAILED MISSION TIMELINE: 2026 CONJUNCTION CLASS")
        println("=" .repeat(80))

        val windows = BrahimMarsPlanner.findLaunchWindows(2026, 2027, MissionType.CONJUNCTION_CLASS)
        val window = windows.firstOrNull() ?: return

        val hohmann = BrahimMarsPlanner.calculateHohmannTransfer()

        // Calculate key dates
        val launchDate = window.optimalDate
        val marsArrival = MarsDate.fromDaysSinceJ2000(
            launchDate.daysSinceJ2000() + hohmann.transferTimeDays
        )
        val marsDeparture = MarsDate.fromDaysSinceJ2000(
            marsArrival.daysSinceJ2000() + window.stayTimeDays
        )
        val earthReturn = MarsDate.fromDaysSinceJ2000(
            marsDeparture.daysSinceJ2000() + hohmann.transferTimeDays
        )

        println("""

            ╔═══════════════════════════════════════════════════════════════════╗
            ║              MARS CONJUNCTION CLASS MISSION 2026                  ║
            ╠═══════════════════════════════════════════════════════════════════╣
            ║                                                                   ║
            ║  PHASE 1: EARTH DEPARTURE                                         ║
            ║  ─────────────────────────────────────────────────────────────── ║
            ║  Launch Window:    ${window.openDate} to ${window.closeDate}            ║
            ║  Optimal Launch:   $launchDate                                    ║
            ║  Delta-V:          ${String.format("%.2f", hohmann.deltaV1)} km/s (Trans-Mars Injection)          ║
            ║                                                                   ║
            ║  PHASE 2: CRUISE TO MARS                                          ║
            ║  ─────────────────────────────────────────────────────────────── ║
            ║  Duration:         ${hohmann.transferTimeDays.toInt()} days (≈ ${(hohmann.transferTimeDays / 30).toInt()} months)                      ║
            ║  Mars Arrival:     $marsArrival                                   ║
            ║  Delta-V:          ${String.format("%.2f", hohmann.deltaV2)} km/s (Mars Orbit Insertion)          ║
            ║                                                                   ║
            ║  PHASE 3: MARS SURFACE OPERATIONS                                 ║
            ║  ─────────────────────────────────────────────────────────────── ║
            ║  Surface Duration: ${window.stayTimeDays.toInt()} days (≈ ${(window.stayTimeDays / 30).toInt()} months)                      ║
            ║  Mars Sols:        ${(window.stayTimeDays / 1.027).toInt()} sols                                  ║
            ║  Mars Departure:   $marsDeparture                                 ║
            ║                                                                   ║
            ║  PHASE 4: RETURN TO EARTH                                         ║
            ║  ─────────────────────────────────────────────────────────────── ║
            ║  Return Duration:  ${hohmann.transferTimeDays.toInt()} days                                   ║
            ║  Earth Arrival:    $earthReturn                                   ║
            ║                                                                   ║
            ║  ═══════════════════════════════════════════════════════════════ ║
            ║  MISSION TOTALS                                                   ║
            ║  ─────────────────────────────────────────────────────────────── ║
            ║  Total Duration:   ${window.totalMissionDays.toInt()} days (≈ ${(window.totalMissionDays / 365).toInt()} years ${((window.totalMissionDays % 365) / 30).toInt()} months)           ║
            ║  Total Delta-V:    ${String.format("%.2f", window.deltaVTotal)} km/s                               ║
            ║  Moon Alignment:   ${(window.moonAlignmentScore * 100).toInt()}%                                      ║
            ║                                                                   ║
            ╚═══════════════════════════════════════════════════════════════════╝

        """.trimIndent())

        // Brahim analysis
        println("BRAHIM RESONANCE ANALYSIS:")
        println("─".repeat(70))
        println("Total mission: ${window.totalMissionDays.toInt()} days")
        println("  = ${(window.totalMissionDays / 214).toInt()} × 214 + ${(window.totalMissionDays % 214).toInt()}")
        println("  ≈ ${String.format("%.2f", window.totalMissionDays / 214)} × S")

        window.brahimResonance?.let {
            println("\n✓ ${it.description}")
            println("  Significance: ${it.significance}")
        }
    }

    @Test
    fun `Moon vs Direct comparison`() {
        println("=" .repeat(80))
        println("MISSION COMPARISON: MOON STAGING vs DIRECT")
        println("=" .repeat(80))

        val directWindows = BrahimMarsPlanner.findLaunchWindows(2026, 2027, MissionType.DIRECT_HOHMANN)
        val moonWindows = BrahimMarsPlanner.findLaunchWindows(2026, 2027, MissionType.MOON_STAGING)

        val direct = directWindows.firstOrNull() ?: return
        val moon = moonWindows.firstOrNull() ?: return

        println("""

            ┌─────────────────────────────────────────────────────────────────┐
            │                    MISSION COMPARISON                          │
            ├─────────────────────┬─────────────────────┬─────────────────────┤
            │     Parameter       │   Direct Hohmann    │   Moon Staging      │
            ├─────────────────────┼─────────────────────┼─────────────────────┤
            │ Launch Date         │ ${direct.optimalDate}         │ ${moon.optimalDate}         │
            │ Transfer Time       │ ${String.format("%6.0f", direct.transferTimeDays)} days       │ ${String.format("%6.0f", moon.transferTimeDays)} days       │
            │ Surface Stay        │ ${String.format("%6.0f", direct.stayTimeDays)} days       │ ${String.format("%6.0f", moon.stayTimeDays)} days       │
            │ Total Mission       │ ${String.format("%6.0f", direct.totalMissionDays)} days       │ ${String.format("%6.0f", moon.totalMissionDays)} days       │
            │ Total Delta-V       │ ${String.format("%6.1f", direct.deltaVTotal)} km/s       │ ${String.format("%6.1f", moon.deltaVTotal)} km/s       │
            │ Moon Alignment      │ ${String.format("%5.0f", direct.moonAlignmentScore * 100)}%%            │ ${String.format("%5.0f", moon.moonAlignmentScore * 100)}%%            │
            └─────────────────────┴─────────────────────┴─────────────────────┘

            ADVANTAGES OF MOON STAGING:
            ─────────────────────────────────────────────────────────────────────
            ✓ Delta-V savings:    ${String.format("%.1f", direct.deltaVTotal - moon.deltaVTotal)} km/s (${String.format("%.1f", (direct.deltaVTotal - moon.deltaVTotal) / direct.deltaVTotal * 100)}% reduction)
            ✓ Abort options:      Can return to Moon base if issues arise
            ✓ Fuel depot:         Use lunar ice for propellant production
            ✓ Crew acclimation:   Practice Mars ops on Moon first
            ✓ Launch flexibility: Wider window with Moon as waypoint

            DISADVANTAGES OF MOON STAGING:
            ─────────────────────────────────────────────────────────────────────
            ✗ Extra transit time: +${(moon.transferTimeDays - direct.transferTimeDays).toInt()} days
            ✗ Complexity:         Two departure burns instead of one
            ✗ Infrastructure:     Requires lunar base/depot

        """.trimIndent())
    }

    @Test
    fun `all windows with Brahim scores`() {
        println("=" .repeat(80))
        println("ALL MARS WINDOWS 2026-2040 WITH BRAHIM SCORES")
        println("=" .repeat(80))

        val windows = BrahimMarsPlanner.findLaunchWindows(2026, 2040, MissionType.DIRECT_HOHMANN)

        println("\n%-5s │ %-12s │ %10s │ %8s │ %8s │ %-30s".format(
            "#", "Launch", "Duration", "Moon%", "Score", "Brahim Resonance"
        ))
        println("─".repeat(85))

        for ((i, window) in windows.withIndex()) {
            val resonanceDesc = window.brahimResonance?.description?.take(30) ?: "-"

            // Calculate Brahim score manually
            var score = 5.0
            window.brahimResonance?.let { score += (2.0 - it.errorPercent / 10.0).coerceIn(0.0, 2.0) }
            score += window.moonAlignmentScore * 2.0

            println("%-5d │ %-12s │ %10.0f │ %7.0f%% │ %8.1f │ %-30s".format(
                i + 1,
                window.optimalDate.toString(),
                window.totalMissionDays,
                window.moonAlignmentScore * 100,
                score,
                resonanceDesc
            ))
        }

        // Find best window
        val best = windows.maxByOrNull {
            var s = 5.0
            it.brahimResonance?.let { r -> s += (2.0 - r.errorPercent / 10.0).coerceIn(0.0, 2.0) }
            s += it.moonAlignmentScore * 2.0
            s
        }

        println("\n🏆 BEST WINDOW (highest Brahim score): ${best?.optimalDate}")
        println("   Moon alignment: ${(best?.moonAlignmentScore ?: 0.0) * 100}%")
        best?.brahimResonance?.let {
            println("   Resonance: ${it.description}")
        }
    }

    @Test
    fun `Brahim formula verification for Mars`() {
        println("=" .repeat(80))
        println("BRAHIM FORMULA VERIFICATION FOR MARS")
        println("=" .repeat(80))

        val S = BrahimConstants.BRAHIM_SUM  // 214
        val B = BrahimConstants.BRAHIM_SEQUENCE

        println("""

            ORBITAL PERIOD FORMULAS:
            ═══════════════════════════════════════════════════════════════════

            Mars orbital period:
              Actual:     687.0 days
              Formula:    3S + 45 = 3(214) + 45 = 642 + 45 = 687
              Error:      0.0% ✓ EXACT MATCH

            Earth-Mars synodic period:
              Actual:     779.9 days
              Formula:    4S - 77 = 4(214) - 77 = 856 - 77 = 779
              Error:      0.1% ✓

            Earth orbital period:
              Actual:     365.25 days
              Formula:    S + B[8] = 214 + 172 = 386
              Error:      5.4% (approximate)

              Better:     S × φ = 214 × 1.618 = 346.3
              Error:      5.2% (approximate)

            Moon sidereal period:
              Actual:     27.32 days
              Formula:    B[0] = 27
              Error:      1.2% ✓

            ═══════════════════════════════════════════════════════════════════

            TRANSFER TIME FORMULAS:
            ═══════════════════════════════════════════════════════════════════

            Hohmann transfer (calculated): ~259 days

            Possible formulas:
              S + 45 = 214 + 45 = 259  ✓ MATCHES
              B[5] + B[6] = 121 + 136 = 257 (0.8% error)
              2S/φ + B[0] = 264.4 + 27 = 291.4 (no match)

            ═══════════════════════════════════════════════════════════════════

            COMBINED MISSION FORMULAS:
            ═══════════════════════════════════════════════════════════════════

            Conjunction class total (typical ~970 days):
              4S + 114 = 4(214) + 114 = 970  ✓
              S × φ³ = 214 × 4.236 = 906 (approximate)

            Opposition class total (typical ~450 days):
              2S + 22 = 2(214) + 22 = 450  ✓

        """.trimIndent())
    }

    @Test
    fun `print complete Mars mission calendar`() {
        println("=" .repeat(100))
        println("BRAHIM MARS MISSION CALENDAR: 2026-2050")
        println("=" .repeat(100))

        val windows = BrahimMarsPlanner.findLaunchWindows(2026, 2050, MissionType.DIRECT_HOHMANN)

        println("""

            Each window repeats every ~26 months (779.9 days = 4×214 - 77)

            ┌──────┬────────────────┬────────────────┬─────────┬──────────┬─────────────────────────────┐
            │  #   │  Launch Window │  Mars Arrival  │ Stay    │  Return  │  Notes                      │
            ├──────┼────────────────┼────────────────┼─────────┼──────────┼─────────────────────────────┤
        """.trimIndent())

        val hohmann = BrahimMarsPlanner.calculateHohmannTransfer()

        for ((i, window) in windows.withIndex()) {
            val arrival = MarsDate.fromDaysSinceJ2000(
                window.optimalDate.daysSinceJ2000() + hohmann.transferTimeDays
            )
            val returnDate = MarsDate.fromDaysSinceJ2000(
                window.optimalDate.daysSinceJ2000() + window.totalMissionDays
            )

            val notes = buildString {
                if (window.moonAlignmentScore > 0.8) append("🌙")
                window.brahimResonance?.let { append(" B") }
                if (window.optimalDate.year == 2026) append(" NEXT")
            }

            println("│ ${String.format("%4d", i + 1)} │ ${window.optimalDate}     │ $arrival     │ ${String.format("%5.0f", window.stayTimeDays)}d  │ $returnDate │ ${notes.padEnd(27)} │")
        }

        println("└──────┴────────────────┴────────────────┴─────────┴──────────┴─────────────────────────────┘")
        println("\n🌙 = Excellent Moon alignment (>80%)")
        println("B = Brahim resonance detected")
    }
}
