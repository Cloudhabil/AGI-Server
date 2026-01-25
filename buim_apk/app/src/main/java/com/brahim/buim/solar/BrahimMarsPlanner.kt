/**
 * Brahim Mars Mission Planner
 * ===========================
 *
 * Calculates optimal Mars travel windows using orbital mechanics
 * and Brahim Number resonances.
 *
 * Key Constants:
 * - Mars-Earth synodic period: 779.9 days ≈ 4S - 77 = 779 (0.1% error)
 * - Mars orbital period: 687 days = 3S + 45 (0.0% error)
 * - Earth orbital period: 365.25 days
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-25
 */

package com.brahim.buim.solar

import com.brahim.buim.core.BrahimConstants
import kotlin.math.*

/**
 * Mission scenario types.
 */
enum class MissionType {
    DIRECT_HOHMANN,           // Direct Earth-Mars Hohmann transfer
    MOON_STAGING,             // Moon as staging point
    FAST_CONJUNCTION,         // Faster transfer (more fuel)
    OPPOSITION_CLASS,         // Short stay mission
    CONJUNCTION_CLASS,        // Long stay mission
    FREE_RETURN              // Free-return trajectory
}

/**
 * Launch window data.
 */
data class LaunchWindow(
    val windowId: String,
    val openDate: MarsDate,
    val closeDate: MarsDate,
    val optimalDate: MarsDate,
    val missionType: MissionType,
    val transferTimeDays: Double,
    val stayTimeDays: Double,
    val returnTimeDays: Double,
    val totalMissionDays: Double,
    val deltaVTotal: Double,           // km/s
    val phaseAngle: Double,            // degrees
    val brahimResonance: BrahimResonance?,
    val moonAlignmentScore: Double     // 0-1, how well Moon is positioned
)

/**
 * Simple date representation.
 */
data class MarsDate(
    val year: Int,
    val month: Int,
    val day: Int
) {
    fun toJulianDay(): Double {
        val a = (14 - month) / 12
        val y = year + 4800 - a
        val m = month + 12 * a - 3
        return day + (153 * m + 2) / 5 + 365 * y + y / 4 - y / 100 + y / 400 - 32045.0
    }

    fun daysSinceJ2000(): Double = toJulianDay() - 2451545.0

    override fun toString(): String = "$year-${month.toString().padStart(2, '0')}-${day.toString().padStart(2, '0')}"

    companion object {
        fun fromJulianDay(jd: Double): MarsDate {
            val z = (jd + 0.5).toLong()
            val a = if (z < 2299161) z else {
                val alpha = ((z - 1867216.25) / 36524.25).toLong()
                z + 1 + alpha - alpha / 4
            }
            val b = a + 1524
            val c = ((b - 122.1) / 365.25).toLong()
            val d = (365.25 * c).toLong()
            val e = ((b - d) / 30.6001).toLong()

            val day = (b - d - (30.6001 * e).toLong()).toInt()
            val month = if (e < 14) e - 1 else e - 13
            val year = if (month > 2) c - 4716 else c - 4715

            return MarsDate(year.toInt(), month.toInt(), day)
        }

        fun fromDaysSinceJ2000(days: Double): MarsDate {
            return fromJulianDay(days + 2451545.0)
        }
    }
}

/**
 * Brahim resonance for a date/mission.
 */
data class BrahimResonance(
    val description: String,
    val brahimValue: Double,
    val actualValue: Double,
    val errorPercent: Double,
    val significance: String
)

/**
 * Brahim Mars Mission Planner.
 */
object BrahimMarsPlanner {

    // =========================================================================
    // ORBITAL CONSTANTS
    // =========================================================================

    // Semi-major axes (AU)
    const val EARTH_SMA = 1.0
    const val MARS_SMA = 1.524
    const val MOON_SMA_AU = 0.00257  // Moon's distance from Earth in AU

    // Orbital periods (days)
    const val EARTH_PERIOD = 365.25
    const val MARS_PERIOD = 687.0           // = 3×214 + 45 (Brahim formula!)
    const val SYNODIC_PERIOD = 779.9        // = 4×214 - 77 (Brahim formula!)
    const val MOON_PERIOD = 27.32           // ≈ B[0] = 27

    // Mean motions (degrees per day)
    val EARTH_MOTION = 360.0 / EARTH_PERIOD
    val MARS_MOTION = 360.0 / MARS_PERIOD

    // Gravitational parameter (km³/s²)
    const val MU_SUN = 1.32712440018e11
    const val AU_KM = 149597870.7

    // Brahim constants
    val S = BrahimConstants.BRAHIM_SUM  // 214
    val B = BrahimConstants.BRAHIM_SEQUENCE
    val PHI = BrahimConstants.PHI

    // =========================================================================
    // HOHMANN TRANSFER CALCULATIONS
    // =========================================================================

    /**
     * Calculate Hohmann transfer parameters.
     */
    fun calculateHohmannTransfer(): HohmannTransfer {
        val r1 = EARTH_SMA * AU_KM  // Earth orbit radius in km
        val r2 = MARS_SMA * AU_KM   // Mars orbit radius in km

        // Transfer orbit semi-major axis
        val aTransfer = (r1 + r2) / 2

        // Transfer time (half the transfer orbit period)
        val transferPeriod = 2 * PI * sqrt(aTransfer.pow(3) / MU_SUN)
        val transferTimeSec = transferPeriod / 2
        val transferTimeDays = transferTimeSec / 86400.0

        // Velocities
        val vEarth = sqrt(MU_SUN / r1)  // Earth's orbital velocity
        val vMars = sqrt(MU_SUN / r2)   // Mars's orbital velocity

        // Transfer orbit velocities at perihelion and aphelion
        val vTransferPeri = sqrt(MU_SUN * (2 / r1 - 1 / aTransfer))
        val vTransferApo = sqrt(MU_SUN * (2 / r2 - 1 / aTransfer))

        // Delta-V requirements
        val deltaV1 = abs(vTransferPeri - vEarth) / 1000  // Earth departure (km/s)
        val deltaV2 = abs(vMars - vTransferApo) / 1000    // Mars insertion (km/s)

        // Phase angle (angle Mars needs to be ahead of Earth at launch)
        val phaseAngle = 180.0 - (180.0 * transferTimeDays / MARS_PERIOD) * (360.0 / MARS_PERIOD) * (MARS_PERIOD / 360.0)
        val correctPhaseAngle = 180.0 * (1 - sqrt((1 + EARTH_SMA / MARS_SMA).pow(3) / 8))

        return HohmannTransfer(
            transferTimeDays = transferTimeDays,
            deltaV1 = deltaV1,
            deltaV2 = deltaV2,
            totalDeltaV = deltaV1 + deltaV2,
            phaseAngle = correctPhaseAngle,
            transferSMA = aTransfer / AU_KM
        )
    }

    data class HohmannTransfer(
        val transferTimeDays: Double,
        val deltaV1: Double,
        val deltaV2: Double,
        val totalDeltaV: Double,
        val phaseAngle: Double,
        val transferSMA: Double
    )

    // =========================================================================
    // LAUNCH WINDOW CALCULATIONS
    // =========================================================================

    /**
     * Find all launch windows in a date range.
     */
    fun findLaunchWindows(
        startYear: Int,
        endYear: Int,
        missionType: MissionType = MissionType.DIRECT_HOHMANN
    ): List<LaunchWindow> {
        val windows = mutableListOf<LaunchWindow>()

        // Calculate base Hohmann parameters
        val hohmann = calculateHohmannTransfer()

        // Start from a known opposition (Aug 2003 was a great one)
        // Synodic period means windows repeat every ~26 months
        val referenceOpposition = MarsDate(2003, 8, 28).daysSinceJ2000()

        var currentOpposition = referenceOpposition
        var windowCount = 0

        while (true) {
            val oppositionDate = MarsDate.fromDaysSinceJ2000(currentOpposition)

            if (oppositionDate.year > endYear) break
            if (oppositionDate.year >= startYear) {
                // Launch window is typically 1-2 months before opposition
                val optimalLaunchDays = currentOpposition - hohmann.transferTimeDays

                val window = createLaunchWindow(
                    windowId = "MW-${oppositionDate.year}-${++windowCount}",
                    optimalLaunchDays = optimalLaunchDays,
                    missionType = missionType,
                    hohmann = hohmann
                )

                windows.add(window)
            }

            currentOpposition += SYNODIC_PERIOD
        }

        return windows
    }

    /**
     * Create a launch window with full details.
     */
    private fun createLaunchWindow(
        windowId: String,
        optimalLaunchDays: Double,
        missionType: MissionType,
        hohmann: HohmannTransfer
    ): LaunchWindow {
        val optimalDate = MarsDate.fromDaysSinceJ2000(optimalLaunchDays)

        // Window is typically ±2 weeks around optimal
        val windowHalfWidth = when (missionType) {
            MissionType.DIRECT_HOHMANN -> 14.0
            MissionType.MOON_STAGING -> 21.0  // Wider window with Moon staging
            MissionType.FAST_CONJUNCTION -> 10.0
            MissionType.OPPOSITION_CLASS -> 14.0
            MissionType.CONJUNCTION_CLASS -> 21.0
            MissionType.FREE_RETURN -> 7.0
        }

        val openDate = MarsDate.fromDaysSinceJ2000(optimalLaunchDays - windowHalfWidth)
        val closeDate = MarsDate.fromDaysSinceJ2000(optimalLaunchDays + windowHalfWidth)

        // Mission parameters based on type
        val (transferTime, stayTime, returnTime, deltaV) = when (missionType) {
            MissionType.DIRECT_HOHMANN -> Quadruple(
                hohmann.transferTimeDays,
                455.0,  // Wait for next window
                hohmann.transferTimeDays,
                hohmann.totalDeltaV * 2  // Round trip
            )
            MissionType.MOON_STAGING -> Quadruple(
                hohmann.transferTimeDays + 3,  // +3 days for Moon departure
                455.0,
                hohmann.transferTimeDays + 3,
                hohmann.totalDeltaV * 2 - 0.5  // Save ~0.5 km/s with Moon gravity assist
            )
            MissionType.FAST_CONJUNCTION -> Quadruple(
                180.0,  // Faster transfer
                30.0,   // Short stay
                180.0,
                hohmann.totalDeltaV * 2 + 2.0  // More fuel needed
            )
            MissionType.OPPOSITION_CLASS -> Quadruple(
                hohmann.transferTimeDays,
                30.0,   // Short stay
                hohmann.transferTimeDays + 60,  // Longer return
                hohmann.totalDeltaV * 2 + 1.0
            )
            MissionType.CONJUNCTION_CLASS -> Quadruple(
                hohmann.transferTimeDays,
                500.0,  // Long stay
                hohmann.transferTimeDays,
                hohmann.totalDeltaV * 2
            )
            MissionType.FREE_RETURN -> Quadruple(
                hohmann.transferTimeDays,
                0.0,    // No landing, flyby only
                hohmann.transferTimeDays,
                hohmann.totalDeltaV + 1.0  // One-way with free return
            )
        }

        // Check for Brahim resonances
        val resonance = findBrahimResonance(optimalDate, transferTime, stayTime)

        // Calculate Moon alignment
        val moonAlignment = calculateMoonAlignment(optimalLaunchDays)

        return LaunchWindow(
            windowId = windowId,
            openDate = openDate,
            closeDate = closeDate,
            optimalDate = optimalDate,
            missionType = missionType,
            transferTimeDays = transferTime,
            stayTimeDays = stayTime,
            returnTimeDays = returnTime,
            totalMissionDays = transferTime + stayTime + returnTime,
            deltaVTotal = deltaV,
            phaseAngle = hohmann.phaseAngle,
            brahimResonance = resonance,
            moonAlignmentScore = moonAlignment
        )
    }

    data class Quadruple<A, B, C, D>(val first: A, val second: B, val third: C, val fourth: D)

    // =========================================================================
    // BRAHIM RESONANCE DETECTION
    // =========================================================================

    /**
     * Find Brahim resonances for a mission.
     */
    private fun findBrahimResonance(
        launchDate: MarsDate,
        transferDays: Double,
        stayDays: Double
    ): BrahimResonance? {
        val resonances = mutableListOf<BrahimResonance>()

        // Check if launch date has special properties
        val dayOfYear = calculateDayOfYear(launchDate)

        // Day of year resonances
        for ((i, b) in B.withIndex()) {
            if (abs(dayOfYear - b) <= 3) {
                resonances.add(BrahimResonance(
                    description = "Launch day of year ≈ B[$i]",
                    brahimValue = b.toDouble(),
                    actualValue = dayOfYear.toDouble(),
                    errorPercent = abs(dayOfYear - b) / b.toDouble() * 100,
                    significance = "Auspicious launch day matching Brahim sequence"
                ))
            }
        }

        // Total mission duration resonances
        val totalDays = transferDays * 2 + stayDays

        // Check against multiples of S = 214
        val sMultiple = totalDays / S
        if (abs(sMultiple - sMultiple.roundToInt()) < 0.05) {
            resonances.add(BrahimResonance(
                description = "Total mission ≈ ${sMultiple.roundToInt()}×S days",
                brahimValue = sMultiple.roundToInt() * S.toDouble(),
                actualValue = totalDays,
                errorPercent = abs(totalDays - sMultiple.roundToInt() * S) / totalDays * 100,
                significance = "Mission duration is a multiple of Brahim Sum"
            ))
        }

        // Check for B[i] combinations
        if (abs(transferDays - B[5]) <= 5) {  // B[5] = 121
            resonances.add(BrahimResonance(
                description = "Transfer time ≈ B[5] = 121 days",
                brahimValue = B[5].toDouble(),
                actualValue = transferDays,
                errorPercent = abs(transferDays - B[5]) / B[5].toDouble() * 100,
                significance = "Transfer matches Kelimutu resonance element"
            ))
        }

        // Year resonance (2026 = 9×214 + 100)
        val yearRemainder = launchDate.year % S
        if (yearRemainder == 100) {  // Qof
            resonances.add(BrahimResonance(
                description = "Launch year mod 214 = 100 (Qof)",
                brahimValue = 100.0,
                actualValue = yearRemainder.toDouble(),
                errorPercent = 0.0,
                significance = "Year resonates with holiness cycle"
            ))
        }

        return resonances.minByOrNull { it.errorPercent }
    }

    private fun calculateDayOfYear(date: MarsDate): Int {
        val daysInMonth = intArrayOf(0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
        val isLeap = (date.year % 4 == 0 && date.year % 100 != 0) || (date.year % 400 == 0)
        if (isLeap) daysInMonth[2] = 29

        var dayOfYear = date.day
        for (m in 1 until date.month) {
            dayOfYear += daysInMonth[m]
        }
        return dayOfYear
    }

    // =========================================================================
    // MOON STAGING CALCULATIONS
    // =========================================================================

    /**
     * Calculate Moon alignment score (0-1).
     * Higher score = Moon is better positioned for gravity assist.
     */
    private fun calculateMoonAlignment(launchDaysSinceJ2000: Double): Double {
        // Moon's position (simplified circular orbit)
        val moonAngle = (launchDaysSinceJ2000 / MOON_PERIOD) * 360.0 % 360.0

        // Best alignment is when Moon is in the direction of Mars
        // Mars position at launch
        val marsAngle = (launchDaysSinceJ2000 / MARS_PERIOD) * 360.0 % 360.0

        // Angular difference
        val diff = abs(moonAngle - marsAngle) % 360.0
        val normalizedDiff = if (diff > 180) 360 - diff else diff

        // Score: 1.0 when aligned, 0.0 when opposite
        return 1.0 - (normalizedDiff / 180.0)
    }

    /**
     * Calculate optimal Moon departure windows within a Mars launch window.
     */
    fun findMoonDepartureWindows(launchWindow: LaunchWindow): List<MoonDepartureWindow> {
        val windows = mutableListOf<MoonDepartureWindow>()

        val startDays = launchWindow.openDate.daysSinceJ2000()
        val endDays = launchWindow.closeDate.daysSinceJ2000()

        // Moon completes orbit every ~27 days, so check each lunar phase
        var currentDay = startDays

        while (currentDay <= endDays) {
            val moonAlignment = calculateMoonAlignment(currentDay)

            if (moonAlignment > 0.7) {  // Good alignment threshold
                val departureDate = MarsDate.fromDaysSinceJ2000(currentDay)

                // Calculate delta-V savings from Moon gravity assist
                val deltaVSaving = calculateMoonGravityAssist(currentDay)

                windows.add(MoonDepartureWindow(
                    date = departureDate,
                    moonPhaseAngle = (currentDay / MOON_PERIOD * 360.0) % 360.0,
                    alignmentScore = moonAlignment,
                    deltaVSaving = deltaVSaving,
                    travelTimeToMoonDays = 3.0,  // Typical Earth-Moon transit
                    lunarStayDays = 2.0  // Refuel/stage time
                ))
            }

            currentDay += 1.0  // Check each day
        }

        return windows.sortedByDescending { it.alignmentScore }
    }

    data class MoonDepartureWindow(
        val date: MarsDate,
        val moonPhaseAngle: Double,
        val alignmentScore: Double,
        val deltaVSaving: Double,  // km/s saved via gravity assist
        val travelTimeToMoonDays: Double,
        val lunarStayDays: Double
    )

    /**
     * Calculate delta-V savings from Moon gravity assist.
     */
    private fun calculateMoonGravityAssist(launchDays: Double): Double {
        // Simplified model: Moon can provide up to ~0.5 km/s boost
        // depending on trajectory alignment
        val moonAlignment = calculateMoonAlignment(launchDays)
        return 0.5 * moonAlignment
    }

    // =========================================================================
    // MISSION COMPARISON
    // =========================================================================

    /**
     * Compare all mission types for a given launch window.
     */
    fun compareMissionTypes(baseWindow: LaunchWindow): List<MissionComparison> {
        return MissionType.values().map { type ->
            val window = createLaunchWindow(
                windowId = "${baseWindow.windowId}-${type.name}",
                optimalLaunchDays = baseWindow.optimalDate.daysSinceJ2000(),
                missionType = type,
                hohmann = calculateHohmannTransfer()
            )

            MissionComparison(
                missionType = type,
                totalDuration = window.totalMissionDays,
                deltaV = window.deltaVTotal,
                surfaceTime = window.stayTimeDays,
                riskLevel = calculateRiskLevel(type),
                crewSupport = calculateCrewSupport(window.totalMissionDays),
                brahimScore = calculateBrahimScore(window)
            )
        }
    }

    data class MissionComparison(
        val missionType: MissionType,
        val totalDuration: Double,
        val deltaV: Double,
        val surfaceTime: Double,
        val riskLevel: String,
        val crewSupport: String,
        val brahimScore: Double
    )

    private fun calculateRiskLevel(type: MissionType): String = when (type) {
        MissionType.DIRECT_HOHMANN -> "MEDIUM"
        MissionType.MOON_STAGING -> "LOW-MEDIUM"
        MissionType.FAST_CONJUNCTION -> "HIGH"
        MissionType.OPPOSITION_CLASS -> "HIGH"
        MissionType.CONJUNCTION_CLASS -> "MEDIUM"
        MissionType.FREE_RETURN -> "LOW"
    }

    private fun calculateCrewSupport(totalDays: Double): String = when {
        totalDays < 400 -> "Minimal resupply"
        totalDays < 700 -> "1 resupply mission"
        totalDays < 1000 -> "2 resupply missions"
        else -> "Extended support required"
    }

    /**
     * Calculate Brahim Score (0-10) for mission auspiciousness.
     */
    private fun calculateBrahimScore(window: LaunchWindow): Double {
        var score = 5.0  // Base score

        // Bonus for resonances
        window.brahimResonance?.let {
            score += (2.0 - it.errorPercent / 10.0).coerceIn(0.0, 2.0)
        }

        // Bonus for Moon alignment
        score += window.moonAlignmentScore * 2.0

        // Bonus if total mission is near Brahim multiple
        val sMultiple = window.totalMissionDays / S
        if (abs(sMultiple - sMultiple.roundToInt()) < 0.1) {
            score += 1.0
        }

        return score.coerceIn(0.0, 10.0)
    }

    // =========================================================================
    // NEXT BEST WINDOW FINDER
    // =========================================================================

    /**
     * Find the next best launch window from a given date.
     */
    fun findNextBestWindow(
        fromDate: MarsDate,
        missionType: MissionType = MissionType.DIRECT_HOHMANN,
        requireMoonAlignment: Boolean = false
    ): NextWindowResult {
        val windows = findLaunchWindows(fromDate.year, fromDate.year + 5, missionType)

        val validWindows = windows.filter { window ->
            window.optimalDate.daysSinceJ2000() > fromDate.daysSinceJ2000() &&
            (!requireMoonAlignment || window.moonAlignmentScore > 0.6)
        }

        if (validWindows.isEmpty()) {
            return NextWindowResult(
                found = false,
                window = null,
                daysUntil = 0.0,
                recommendation = "No suitable windows found in range"
            )
        }

        val bestWindow = validWindows.maxByOrNull {
            calculateBrahimScore(it) + it.moonAlignmentScore
        }!!

        val daysUntil = bestWindow.optimalDate.daysSinceJ2000() - fromDate.daysSinceJ2000()

        return NextWindowResult(
            found = true,
            window = bestWindow,
            daysUntil = daysUntil,
            recommendation = generateRecommendation(bestWindow, daysUntil)
        )
    }

    data class NextWindowResult(
        val found: Boolean,
        val window: LaunchWindow?,
        val daysUntil: Double,
        val recommendation: String
    )

    private fun generateRecommendation(window: LaunchWindow, daysUntil: Double): String {
        val sb = StringBuilder()

        sb.appendLine("RECOMMENDED: ${window.missionType.name}")
        sb.appendLine("Launch: ${window.optimalDate} (in ${daysUntil.toInt()} days)")
        sb.appendLine("Total mission: ${window.totalMissionDays.toInt()} days")

        window.brahimResonance?.let {
            sb.appendLine("Brahim resonance: ${it.description}")
        }

        if (window.moonAlignmentScore > 0.7) {
            sb.appendLine("Moon alignment: EXCELLENT (${(window.moonAlignmentScore * 100).toInt()}%)")
        }

        return sb.toString()
    }
}
