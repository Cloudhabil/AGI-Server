/**
 * Wormhole Observer - FitzHugh-Nagumo Dynamics
 * =============================================
 *
 * Implements the phase space dynamics for system governance:
 * - κ (kappa): Activity level (0 = quiet, 1 = active)
 * - D (debt): Accumulated computational debt
 *
 * The FitzHugh-Nagumo model provides:
 * - Throttle signals when debt accumulates
 * - Purge signals when system overloads
 * - Natural oscillation between active and recovery phases
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-25
 */

package com.brahim.buim.dynamics

import com.brahim.buim.core.BrahimConstants
import kotlin.math.abs
import kotlin.math.exp
import kotlin.math.pow
import kotlin.math.tanh

/**
 * Governance signals from the wormhole observer.
 */
data class Governance(
    val throttle: Double,    // 0 = no throttle, 1 = full throttle
    val purge: Boolean,      // True if purge needed
    val phase: Phase,        // Current phase
    val recommendation: String
)

/**
 * System phases.
 */
enum class Phase(val description: String) {
    ACTIVE("Normal operation"),
    THROTTLED("Reduced throughput"),
    RECOVERY("System recovering"),
    PURGING("Clearing debt"),
    STABLE("At equilibrium")
}

/**
 * Phase space state.
 */
data class PhaseSpaceState(
    val kappa: Double,  // Activity level
    val debt: Double,   // Accumulated debt
    val time: Double    // System time
)

/**
 * Wormhole Observer implementing FitzHugh-Nagumo dynamics.
 *
 * The system evolves according to:
 *   dκ/dt = κ - κ³/3 - D + I
 *   dD/dt = ε(κ + a - bD)
 *
 * Where:
 *   κ = activity (fast variable)
 *   D = debt (slow variable)
 *   I = input current
 *   ε = time scale separation (uses beta)
 *   a, b = parameters
 */
class WormholeObserver(
    initialKappa: Double = 0.5,
    initialDebt: Double = 0.0
) {

    companion object {
        // FitzHugh-Nagumo parameters
        const val EPSILON = BrahimConstants.BETA_SECURITY  // Time scale separation
        const val A = 0.7    // Threshold parameter
        const val B = 0.8    // Debt recovery rate

        // Thresholds
        const val THROTTLE_THRESHOLD = 0.7
        const val PURGE_THRESHOLD = 1.5
        const val RECOVERY_THRESHOLD = 0.3
    }

    // State variables
    var kappa: Double = initialKappa
        private set
    var debt: Double = initialDebt
        private set
    var time: Double = 0.0
        private set

    // Input current
    private var inputCurrent = 0.0

    // History for analysis
    private val stateHistory = mutableListOf<PhaseSpaceState>()
    private val maxHistorySize = 1000

    /**
     * Set the input current (external drive).
     */
    fun setInput(current: Double) {
        inputCurrent = current.coerceIn(-2.0, 2.0)
    }

    /**
     * Step the dynamics forward.
     *
     * @param dt Time step
     */
    fun step(dt: Double = 0.01) {
        // FitzHugh-Nagumo equations
        val dKappa = kappa - kappa.pow(3) / 3 - debt + inputCurrent
        val dDebt = EPSILON * (kappa + A - B * debt)

        // Euler integration
        kappa += dKappa * dt
        debt += dDebt * dt
        time += dt

        // Clamp values
        kappa = kappa.coerceIn(-2.0, 2.0)
        debt = debt.coerceIn(-2.0, 3.0)

        // Record state
        if (stateHistory.size >= maxHistorySize) {
            stateHistory.removeAt(0)
        }
        stateHistory.add(PhaseSpaceState(kappa, debt, time))
    }

    /**
     * Get current governance recommendation.
     */
    fun getGovernance(): Governance {
        val phase = determinePhase()
        val throttle = computeThrottle()
        val purge = debt > PURGE_THRESHOLD

        val recommendation = when (phase) {
            Phase.ACTIVE -> "System operating normally"
            Phase.THROTTLED -> "Reduce request rate by ${(throttle * 100).toInt()}%"
            Phase.RECOVERY -> "System recovering, avoid heavy operations"
            Phase.PURGING -> "Critical: Clear caches and reduce load"
            Phase.STABLE -> "System at equilibrium"
        }

        return Governance(throttle, purge, phase, recommendation)
    }

    /**
     * Determine the current phase.
     */
    private fun determinePhase(): Phase {
        return when {
            debt > PURGE_THRESHOLD -> Phase.PURGING
            debt > THROTTLE_THRESHOLD -> Phase.THROTTLED
            kappa < RECOVERY_THRESHOLD && debt > 0.5 -> Phase.RECOVERY
            abs(kappa) < 0.1 && abs(debt - (A / B)) < 0.1 -> Phase.STABLE
            else -> Phase.ACTIVE
        }
    }

    /**
     * Compute throttle level.
     */
    private fun computeThrottle(): Double {
        return if (debt > THROTTLE_THRESHOLD) {
            ((debt - THROTTLE_THRESHOLD) / (PURGE_THRESHOLD - THROTTLE_THRESHOLD)).coerceIn(0.0, 1.0)
        } else {
            0.0
        }
    }

    /**
     * Apply a load spike.
     */
    fun applyLoad(intensity: Double) {
        inputCurrent += intensity * BrahimConstants.PHI
    }

    /**
     * Reset the observer.
     */
    fun reset(kappa: Double = 0.5, debt: Double = 0.0) {
        this.kappa = kappa
        this.debt = debt
        this.time = 0.0
        this.inputCurrent = 0.0
        stateHistory.clear()
    }

    /**
     * Get stability analysis.
     */
    fun getStabilityAnalysis(): Map<String, Any> {
        // Fixed point: (κ*, D*) where dκ/dt = dD/dt = 0
        // Linearize and compute eigenvalues
        val kappaStar = -A + B * (A / B)  // Simplified
        val debtStar = A / B

        // Jacobian at fixed point
        val j11 = 1 - kappaStar.pow(2)
        val j12 = -1.0
        val j21 = EPSILON
        val j22 = -EPSILON * B

        // Trace and determinant
        val trace = j11 + j22
        val det = j11 * j22 - j12 * j21

        // Discriminant
        val discriminant = trace.pow(2) - 4 * det

        val stabilityType = when {
            det < 0 -> "saddle"
            trace > 0 -> "unstable"
            discriminant < 0 -> "spiral (oscillatory)"
            else -> "stable node"
        }

        return mapOf(
            "fixed_point" to mapOf("kappa" to kappaStar, "debt" to debtStar),
            "trace" to trace,
            "determinant" to det,
            "discriminant" to discriminant,
            "stability_type" to stabilityType,
            "current_distance_from_fixed_point" to kotlin.math.sqrt(
                (kappa - kappaStar).pow(2) + (debt - debtStar).pow(2)
            )
        )
    }

    /**
     * Get observer statistics.
     */
    fun getStats(): Map<String, Any> {
        val governance = getGovernance()

        return mapOf(
            "kappa" to kappa,
            "debt" to debt,
            "time" to time,
            "input_current" to inputCurrent,
            "phase" to governance.phase.name,
            "throttle" to governance.throttle,
            "purge_needed" to governance.purge,
            "history_size" to stateHistory.size,
            "epsilon" to EPSILON,
            "stability" to getStabilityAnalysis()
        )
    }

    /**
     * Get recent state history.
     */
    fun getHistory(n: Int = 100): List<PhaseSpaceState> {
        return stateHistory.takeLast(n)
    }
}
