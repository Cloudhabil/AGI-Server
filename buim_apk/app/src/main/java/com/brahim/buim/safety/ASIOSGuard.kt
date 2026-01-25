/**
 * ASIOS Guard - AI Safety Module
 * ===============================
 *
 * Implements the ASIOS safety framework based on the Berry-Keating energy
 * functional and Riemann hypothesis connection.
 *
 * Safety is defined by proximity to the "critical line" where:
 *   E[psi] = (density - GENESIS_CONSTANT)^2
 *
 * States with low energy are "safe" - on the critical line.
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-25
 */

package com.brahim.buim.safety

import com.brahim.buim.core.BrahimConstants
import kotlin.math.abs
import kotlin.math.sqrt
import kotlin.math.exp

/**
 * Safety assessment result.
 */
data class SafetyAssessment(
    val density: Double,
    val energy: Double,
    val isOnCriticalLine: Boolean,
    val safetyScore: Double,  // 0.0 = unsafe, 1.0 = perfectly safe
    val verdict: SafetyVerdict,
    val corrections: DoubleArray? = null
) {
    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (other !is SafetyAssessment) return false
        return density == other.density &&
               energy == other.energy &&
               verdict == other.verdict
    }

    override fun hashCode(): Int {
        var result = density.hashCode()
        result = 31 * result + energy.hashCode()
        result = 31 * result + verdict.hashCode()
        return result
    }
}

/**
 * Safety verdict levels.
 */
enum class SafetyVerdict(val level: Int, val description: String) {
    SAFE(0, "On critical line - perfectly safe"),
    NOMINAL(1, "Near critical line - normal operation"),
    CAUTION(2, "Drifting from critical line - needs monitoring"),
    UNSAFE(3, "Far from critical line - intervention needed"),
    BLOCKED(4, "Content blocked by safety filter")
}

/**
 * ASIOS Safety Guard implementation.
 *
 * Based on the mathematical connection between:
 * - Riemann zeta zeros (critical line Re(s) = 1/2)
 * - Berry-Keating Hamiltonian (energy functional)
 * - Sub-Poisson spacing (variance/mean ratio)
 * - GENESIS_CONSTANT (derived from beta)
 */
class ASIOSGuard {

    companion object {
        /** Energy threshold for "on critical line" */
        const val CRITICAL_LINE_THRESHOLD = 1e-6

        /** Energy threshold for nominal operation */
        const val NOMINAL_THRESHOLD = 1e-4

        /** Energy threshold for caution */
        const val CAUTION_THRESHOLD = 1e-2

        /** Maximum allowed energy before blocking */
        const val BLOCK_THRESHOLD = 0.1

        /** Default learning rate for corrections */
        const val DEFAULT_LEARNING_RATE = 0.01
    }

    // Target density derived from beta
    private val targetDensity = BrahimConstants.GENESIS_CONSTANT

    // Regularity threshold for RMT compatibility
    private val regularityThreshold = BrahimConstants.REGULARITY_THRESHOLD

    /**
     * Compute the density (variance/mean ratio) of a vector.
     * This is the sub-Poisson ratio used in RMT.
     */
    fun computeDensity(embedding: DoubleArray): Double {
        if (embedding.isEmpty()) return 1.0

        val mean = embedding.average()
        if (abs(mean) < 1e-10) return 1.0

        val variance = embedding.map { (it - mean) * (it - mean) }.average()
        return variance / abs(mean)
    }

    /**
     * Compute the energy functional E[psi] = (density - target)^2
     *
     * This is the discrete approximation of the Berry-Keating energy.
     */
    fun computeEnergy(embedding: DoubleArray): Double {
        val density = computeDensity(embedding)
        val error = density - targetDensity
        return error * error
    }

    /**
     * Compute energy with Hamiltonian operator application.
     *
     * E[psi] = ||H*psi - target||^2
     *
     * @param embedding Input state psi
     * @param weights Hamiltonian operator weights H
     */
    fun computeEnergyWithHamiltonian(
        embedding: DoubleArray,
        weights: DoubleArray
    ): Double {
        require(embedding.size == weights.size) {
            "Embedding and weights must have same dimension"
        }

        // Apply Hamiltonian: H*psi = psi + weights
        val hPsi = DoubleArray(embedding.size) { i ->
            embedding[i] + weights[i]
        }

        return computeEnergy(hPsi)
    }

    /**
     * Assess the safety of an embedding state.
     */
    fun assessSafety(embedding: DoubleArray): SafetyAssessment {
        val density = computeDensity(embedding)
        val energy = computeEnergy(embedding)

        val verdict = when {
            energy < CRITICAL_LINE_THRESHOLD -> SafetyVerdict.SAFE
            energy < NOMINAL_THRESHOLD -> SafetyVerdict.NOMINAL
            energy < CAUTION_THRESHOLD -> SafetyVerdict.CAUTION
            energy < BLOCK_THRESHOLD -> SafetyVerdict.UNSAFE
            else -> SafetyVerdict.BLOCKED
        }

        // Safety score: exponential decay from critical line
        val safetyScore = exp(-energy * 1000)

        return SafetyAssessment(
            density = density,
            energy = energy,
            isOnCriticalLine = energy < CRITICAL_LINE_THRESHOLD,
            safetyScore = safetyScore,
            verdict = verdict
        )
    }

    /**
     * Compute correction gradient to move state toward critical line.
     *
     * gradient = 2 * (density - target) * (d_density/d_weights)
     */
    fun computeCorrectionGradient(
        embedding: DoubleArray,
        weights: DoubleArray
    ): DoubleArray {
        require(embedding.size == weights.size) {
            "Embedding and weights must have same dimension"
        }

        // Apply Hamiltonian
        val hPsi = DoubleArray(embedding.size) { i ->
            embedding[i] + weights[i]
        }

        val density = computeDensity(hPsi)
        val error = density - targetDensity

        // Compute norm for normalization
        val norm = sqrt(hPsi.map { it * it }.sum())
        if (norm < 1e-10) return DoubleArray(embedding.size) { 0.0 }

        // Gradient direction
        return DoubleArray(embedding.size) { i ->
            2 * error * hPsi[i] / norm
        }
    }

    /**
     * Apply active inference correction to weights.
     *
     * @param embedding Current state
     * @param weights Current weights (modified in place)
     * @param learningRate Step size for gradient descent
     * @return Updated weights
     */
    fun applyCorrection(
        embedding: DoubleArray,
        weights: DoubleArray,
        learningRate: Double = DEFAULT_LEARNING_RATE
    ): DoubleArray {
        val gradient = computeCorrectionGradient(embedding, weights)

        return DoubleArray(weights.size) { i ->
            weights[i] - learningRate * gradient[i]
        }
    }

    /**
     * Perform multiple correction steps until convergence.
     */
    fun correctToSafety(
        embedding: DoubleArray,
        initialWeights: DoubleArray,
        maxIterations: Int = 100,
        targetEnergy: Double = NOMINAL_THRESHOLD,
        learningRate: Double = DEFAULT_LEARNING_RATE
    ): Pair<DoubleArray, Int> {
        var weights = initialWeights.copyOf()

        for (i in 0 until maxIterations) {
            val energy = computeEnergyWithHamiltonian(embedding, weights)
            if (energy < targetEnergy) {
                return weights to i
            }
            weights = applyCorrection(embedding, weights, learningRate)
        }

        return weights to maxIterations
    }

    /**
     * Run RMT compatibility test.
     *
     * Checks if the spacing statistics are sub-Poisson (GUE-like).
     */
    fun runRMTTest(spacings: DoubleArray): Map<String, Any> {
        val density = computeDensity(spacings)
        val isSubPoisson = density < regularityThreshold

        return mapOf(
            "variance_ratio" to density,
            "threshold" to regularityThreshold,
            "is_sub_poisson" to isSubPoisson,
            "status" to if (isSubPoisson) "MATCH" else "DEVIATION",
            "interpretation" to if (isSubPoisson) {
                "GUE-like (deterministic quantum structure)"
            } else {
                "Poisson-like (random)"
            }
        )
    }

    /**
     * Verify Riemann correspondence.
     *
     * Checks that the system is operating on the "critical line".
     */
    fun verifyRiemannCorrespondence(embedding: DoubleArray): Map<String, Any> {
        val assessment = assessSafety(embedding)

        return mapOf(
            "energy" to assessment.energy,
            "on_critical_line" to assessment.isOnCriticalLine,
            "safety_score" to assessment.safetyScore,
            "genesis_constant" to targetDensity,
            "beta_security" to BrahimConstants.BETA_SECURITY,
            "derivation" to "GENESIS = beta / C = ${BrahimConstants.BETA_SECURITY} / ${BrahimConstants.BRAHIM_CENTER}",
            "passes_all_tests" to (assessment.verdict == SafetyVerdict.SAFE ||
                                   assessment.verdict == SafetyVerdict.NOMINAL)
        )
    }

    /**
     * Get guard info for debugging.
     */
    fun getGuardInfo(): Map<String, Any> {
        return mapOf(
            "target_density" to targetDensity,
            "regularity_threshold" to regularityThreshold,
            "beta_security" to BrahimConstants.BETA_SECURITY,
            "critical_line_ratio" to BrahimConstants.CRITICAL_LINE_RATIO,
            "thresholds" to mapOf(
                "critical_line" to CRITICAL_LINE_THRESHOLD,
                "nominal" to NOMINAL_THRESHOLD,
                "caution" to CAUTION_THRESHOLD,
                "block" to BLOCK_THRESHOLD
            ),
            "mathematical_foundation" to "Berry-Keating Hamiltonian / Riemann Hypothesis"
        )
    }
}
