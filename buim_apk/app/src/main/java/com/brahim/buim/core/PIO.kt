/**
 * Personal Intelligent Operator (PIO)
 * ====================================
 *
 * The unified core merging ASIOS + BUIM into ONE system.
 *
 * THREE CORE IDEAS:
 *     1. ONE EQUATION  - The Transponder: D(x), Θ(x)
 *     2. ONE LATTICE   - The 840 Lucas States
 *     3. ONE GAP       - The 1.16% Creativity Margin
 *
 * ONE SENTENCE:
 *     "A Personal Intelligent Operator that locates any task in 12 dimensions
 *      using one equation, operates across 840 discrete states, and adapts
 *      within a 1.16% creativity margin."
 *
 * Author: Elias Oulad Brahim
 * Version: 1.0.0
 * Date: 2026-01-27
 */

package com.brahim.buim.core

import kotlin.math.abs
import kotlin.math.ln
import kotlin.math.pow
import kotlin.math.sqrt
import kotlin.math.PI
import kotlin.math.roundToInt
import kotlin.random.Random

// =============================================================================
// CONSTANTS - The Mathematical Foundation
// =============================================================================

/** Golden ratio φ = (1 + √5) / 2 */
const val PHI = 1.6180339887498949

/** Conjugate ψ = -1/φ */
const val PSI = -0.6180339887498949

/** Security constant β = 1/φ³ = 23.6% */
const val BETA = 0.2360679774997897

/** Grand Unification Φ₁₂ = 1/φ¹² = 0.31% */
const val PHI_12 = 0.003115169857645614

/** The Lucas Lattice - 840 total states */
val LUCAS = intArrayOf(1, 3, 4, 7, 11, 18, 29, 47, 76, 123, 199, 322)

/** Total operational states */
const val LUCAS_TOTAL = 840

/** The Phi-Pi Gap - 1.16% creativity margin */
val PHI_PI_GAP = (322 * PI - 1000) / 1000  // ~0.0116


// =============================================================================
// CORE IDEA 1: THE TRANSPONDER (One Equation)
// =============================================================================

/**
 * Dimensional Position: D(x) = -ln(x) / ln(φ)
 *
 * WHERE in 12-dimensional space.
 *
 * @param x Value in (0, 1]
 * @return Continuous dimensional position
 */
fun D(x: Double): Double {
    require(x > 0 && x <= 1) { "x must be in (0, 1], got $x" }
    return -ln(x) / ln(PHI)
}

/**
 * Angular Phase: Θ(x) = 2πx
 *
 * WHEN in the cycle.
 *
 * @param x Any value
 * @return Phase in radians [0, 2π)
 */
fun Theta(x: Double): Double = 2 * PI * (x % 1)

/**
 * A location in PIO space: dimension + phase.
 */
data class Location(
    val x: Double,
    val dimension: Double,      // Continuous D(x)
    val dimensionInt: Int,      // Discrete dimension 1-12
    val phase: Double,          // Θ(x) in radians
    val phaseDegrees: Double,   // Θ(x) in degrees
    val threshold: Double       // 1/φⁿ threshold
) {
    /** Lucas capacity L(n) for this dimension */
    val capacity: Int get() = LUCAS[dimensionInt - 1]
}

/**
 * THE TRANSPONDER: Locate any value in PIO space.
 *
 * This is the ONE EQUATION that unifies the system.
 *
 * @param x Value in (0, 1]
 * @return Location with dimension and phase
 */
fun locate(x: Double): Location {
    val d = D(x)
    val theta = Theta(x)
    val dimInt = minOf(12, maxOf(1, d.roundToInt()))

    return Location(
        x = x,
        dimension = d,
        dimensionInt = dimInt,
        phase = theta,
        phaseDegrees = theta * 180 / PI,
        threshold = 1.0 / PHI.pow(dimInt.toDouble())
    )
}


// =============================================================================
// CORE IDEA 2: THE LUCAS LATTICE (840 States)
// =============================================================================

/**
 * The 12 dimensions with their Lucas capacities.
 */
enum class Dimension(
    val n: Int,
    val capacity: Int,
    val domain: String,
    val description: String
) {
    D1(1, 1, "Perception", "Binary awareness"),
    D2(2, 3, "Attention", "Focus triage"),
    D3(3, 4, "Security", "Trust quadrants"),
    D4(4, 7, "Stability", "Balance modes"),
    D5(5, 11, "Compression", "Data reduction"),
    D6(6, 18, "Harmony", "Frequency alignment"),
    D7(7, 29, "Reasoning", "Logic chains"),
    D8(8, 47, "Prediction", "Future modeling"),
    D9(9, 76, "Creativity", "Novel patterns"),
    D10(10, 123, "Wisdom", "Deep principles"),
    D11(11, 199, "Integration", "System synthesis"),
    D12(12, 322, "Unification", "Total coherence");

    /** Dimensional threshold 1/φⁿ */
    val threshold: Double get() = 1.0 / PHI.pow(n.toDouble())

    companion object {
        /** Get dimension by number */
        fun fromN(n: Int): Dimension = values()[n - 1]
    }
}

/**
 * A discrete state in the Lucas Lattice.
 */
data class State(
    val dimension: Dimension,
    val state: Int,           // State index [0, L(n))
    val phase: Double,        // Angular phase
    val exploring: Boolean,   // In creative mode?
    val inGap: Boolean        // Within 1.16% creativity margin?
) {
    /** Unique state address */
    val address: String get() = "D${dimension.n}:S$state/${dimension.capacity}"

    override fun toString(): String {
        val mode = if (exploring) "~" else "="
        return "<State $address $mode ${dimension.domain}>"
    }
}

/**
 * Map value x to a discrete Lucas state.
 *
 * @param x Value in (0, 1]
 * @param dimension Target dimension 1-12
 * @param exploring If true, apply creativity margin
 * @return Discrete State in the Lucas Lattice
 */
fun stateAt(x: Double, dimension: Int, exploring: Boolean = false): State {
    require(dimension in 1..12) { "Dimension must be 1-12, got $dimension" }

    val dim = Dimension.fromN(dimension)
    val d = D(x)
    val capacity = dim.capacity

    // Map to discrete state
    var stateIdx = ((d / dimension) * capacity).toInt() % capacity

    // Apply creativity margin if exploring
    if (exploring) {
        val gapBand = capacity * PHI_PI_GAP
        val delta = Random.nextDouble(-gapBand, gapBand)
        stateIdx = maxOf(0, minOf(capacity - 1, (stateIdx + delta).toInt()))
    }

    val phase = Theta(x)
    val inGap = abs(d - d.roundToInt()) < PHI_PI_GAP

    return State(
        dimension = dim,
        state = stateIdx,
        phase = phase,
        exploring = exploring,
        inGap = inGap
    )
}

/**
 * The 840-state operational lattice.
 */
class LucasLattice {
    val dimensions = Dimension.values().toList()
    val totalStates = LUCAS_TOTAL

    /** Get the state for value x (auto-selects dimension) */
    fun getState(x: Double, exploring: Boolean = false): State {
        val loc = locate(x)
        return stateAt(x, loc.dimensionInt, exploring)
    }

    /** Get state at specific dimension */
    fun getStateAt(x: Double, dimension: Int, exploring: Boolean = false): State {
        return stateAt(x, dimension, exploring)
    }

    /** Enumerate all states in a dimension */
    fun enumerateStates(dimension: Int): List<Int> {
        require(dimension in 1..12) { "Dimension must be 1-12, got $dimension" }
        return (0 until LUCAS[dimension - 1]).toList()
    }

    /** Total capacity from D1 to Dn */
    fun capacityUpTo(dimension: Int): Int {
        return LUCAS.slice(0 until dimension).sum()
    }

    /** Get global index [0, 840) for a state */
    fun globalStateIndex(state: State): Int {
        val offset = if (state.dimension.n > 1) capacityUpTo(state.dimension.n - 1) else 0
        return offset + state.state
    }

    override fun toString(): String {
        return "<LucasLattice: $totalStates states across 12 dimensions>"
    }
}


// =============================================================================
// CORE IDEA 3: THE PHI-PI GAP (1.16% Soul)
// =============================================================================

/**
 * Result with creativity margin applied.
 */
data class CreativeResult(
    val value: Double,
    val original: Double,
    val delta: Double,
    val inGap: Boolean,
    val exploring: Boolean
)

/**
 * Apply the 1.16% creativity margin.
 *
 * The GAP is where φ (structure) and π (form) almost meet but don't.
 * This is the space for adaptation, emergence, and learning.
 *
 * @param value Base value to adjust
 * @param intensity How much of the gap to use (0-1)
 * @return CreativeResult with adjusted value
 */
fun creativeAdjust(value: Double, intensity: Double = 1.0): CreativeResult {
    val delta = Random.nextDouble(-PHI_PI_GAP, PHI_PI_GAP) * intensity
    val adjusted = value * (1 + delta)

    return CreativeResult(
        value = adjusted,
        original = value,
        delta = delta,
        inGap = true,
        exploring = true
    )
}

/**
 * Check if x is within the creativity margin of a dimension boundary.
 */
fun isInGap(x: Double): Boolean {
    val d = D(x)
    return abs(d - d.roundToInt()) < PHI_PI_GAP
}


// =============================================================================
// THE UNIFIED PIO (Personal Intelligent Operator)
// =============================================================================

/**
 * Response from PIO processing.
 */
data class PIOResponse(
    val input: Any,
    val location: Location,
    val state: State,
    val output: Any?,
    val exploring: Boolean,
    val trace: List<String> = emptyList()
)

/**
 * Handler type for dimension processing.
 */
typealias DimensionHandler = (State, Any) -> Any?

/**
 * Personal Intelligent Operator
 *
 * The unified system merging ASIOS + BUIM.
 *
 * THREE CORE IDEAS:
 *     1. ONE EQUATION  - The Transponder: D(x), Θ(x)
 *     2. ONE LATTICE   - The 840 Lucas States
 *     3. ONE GAP       - The 1.16% Creativity Margin
 *
 * Usage:
 *     val pio = PIO()
 *     val response = pio.process(0.236)  // Process any input
 *
 *     // Or with creative exploration
 *     val response = pio.process(0.236, exploring = true)
 */
class PIO(val name: String = "PIO") {

    companion object {
        const val VERSION = "1.0.0"
        const val CODENAME = "Unified Intelligence"

        @Volatile
        private var instance: PIO? = null

        fun getInstance(): PIO {
            return instance ?: synchronized(this) {
                instance ?: PIO().also { instance = it }
            }
        }
    }

    val lattice = LucasLattice()
    private val handlers = mutableMapOf<Int, DimensionHandler>()

    init {
        // Register default handlers
        Dimension.values().forEach { dim ->
            handlers[dim.n] = { state, input -> defaultHandler(state, input) }
        }
    }

    private fun defaultHandler(state: State, inputVal: Any): Map<String, Any?> {
        return mapOf(
            "dimension" to state.dimension.n,
            "domain" to state.dimension.domain,
            "state" to state.state,
            "capacity" to state.dimension.capacity,
            "input" to inputVal
        )
    }

    /** Register a custom handler for a dimension */
    fun registerHandler(dimension: Int, handler: DimensionHandler) {
        require(dimension in 1..12) { "Dimension must be 1-12, got $dimension" }
        handlers[dimension] = handler
    }

    /** Locate value in PIO space (Transponder) */
    fun locate(x: Double): Location = com.brahim.buim.core.locate(x)

    /**
     * Process input through PIO.
     *
     * This is the main entry point that unifies all three core ideas.
     *
     * @param x Input value in (0, 1] or will be normalized
     * @param exploring Enable creativity margin
     * @param targetDimension Force specific dimension (optional)
     * @return PIOResponse with full processing trace
     */
    fun process(
        x: Double,
        exploring: Boolean = false,
        targetDimension: Int? = null
    ): PIOResponse {
        val trace = mutableListOf<String>()

        // Normalize input to (0, 1]
        var normalizedX = x
        if (x <= 0 || x > 1) {
            normalizedX = abs(x) % 1
            if (normalizedX == 0.0) normalizedX = 0.5
            trace.add("Normalized input to $normalizedX")
        }

        // 1. TRANSPONDER: Locate in PIO space
        val location = locate(normalizedX)
        trace.add("Located: D${location.dimensionInt} @ ${String.format("%.1f", location.phaseDegrees)}°")

        // 2. LATTICE: Get discrete state
        val dim = targetDimension ?: location.dimensionInt
        val state = lattice.getStateAt(normalizedX, dim, exploring)
        trace.add("State: ${state.address}")

        // 3. GAP: Apply creativity if exploring
        if (exploring && state.inGap) {
            trace.add("Creative margin active (±${String.format("%.2f", PHI_PI_GAP * 100)}%)")
        }

        // Process through dimension handler
        val handler = handlers[dim] ?: { s, i -> defaultHandler(s, i) }
        val output = handler(state, normalizedX)
        trace.add("Processed by ${state.dimension.domain}")

        return PIOResponse(
            input = normalizedX,
            location = location,
            state = state,
            output = output,
            exploring = exploring,
            trace = trace
        )
    }

    /** Process multiple values */
    fun batchProcess(values: List<Double>, exploring: Boolean = false): List<PIOResponse> {
        return values.map { process(it, exploring) }
    }

    /** Get PIO status */
    fun status(): Map<String, Any> {
        return mapOf(
            "name" to name,
            "version" to VERSION,
            "codename" to CODENAME,
            "coreIdeas" to mapOf(
                "transponder" to "D(x) = -ln(x)/ln(φ), Θ(x) = 2πx",
                "lattice" to "$LUCAS_TOTAL states across 12 dimensions",
                "gap" to "${String.format("%.2f", PHI_PI_GAP * 100)}% creativity margin"
            ),
            "constants" to mapOf(
                "phi" to PHI,
                "beta" to BETA,
                "phiPiGap" to PHI_PI_GAP,
                "lucasTotal" to LUCAS_TOTAL
            ),
            "dimensions" to Dimension.values().map { d ->
                mapOf(
                    "n" to d.n,
                    "capacity" to d.capacity,
                    "domain" to d.domain,
                    "threshold" to d.threshold
                )
            }
        )
    }

    override fun toString(): String {
        return "<PIO '$name' v$VERSION: 840 states, 12 dimensions, 1.16% gap>"
    }
}


// =============================================================================
// VERIFICATION
// =============================================================================

/**
 * Verify PIO mathematical foundations.
 */
fun verifyPIO(): Map<String, Boolean> {
    val results = mutableMapOf<String, Boolean>()

    // Verify φ² = φ + 1
    results["phi_squared"] = abs(PHI * PHI - (PHI + 1)) < 1e-14

    // Verify Lucas recurrence
    results["lucas_recurrence"] = (2..11).all { n ->
        LUCAS[n] == LUCAS[n - 1] + LUCAS[n - 2]
    }

    // Verify Lucas total = 840
    results["lucas_total"] = LUCAS.sum() == 840

    // Verify L(n) ≈ φⁿ
    results["lucas_phi_approx"] = (0..11).all { n ->
        abs(LUCAS[n] - (PHI.pow(n + 1) + PSI.pow(n + 1))) < 0.5
    }

    // Verify Phi-Pi gap formula
    val expectedGap = (322 * PI - 1000) / 1000
    results["phi_pi_gap"] = abs(PHI_PI_GAP - expectedGap) < 1e-10

    // Verify grand unification: β⁴ ≈ 1/φ¹²
    results["grand_unification"] = abs(BETA.pow(4) - PHI_12) < 1e-14

    // Verify transponder invertibility
    listOf(0.1, 0.236, 0.5, 0.618, 0.9).forEach { x ->
        val d = D(x)
        val xBack = 1.0 / PHI.pow(d)
        results["transponder_x=$x"] = abs(x - xBack) < 1e-10
    }

    results["all_valid"] = results.values.all { it }
    return results
}
