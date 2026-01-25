/**
 * Brahim Sequence - Mathematical Operations
 * ==========================================
 *
 * Extended operations on the Brahim Sequence B = {27, 42, 60, 75, 97, 121, 136, 154, 172, 187}
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-25
 */

package com.brahim.buim.core

import kotlin.math.pow

/**
 * Brahim Sequence state representation.
 */
data class BrahimState(
    val index: Int,
    val value: Int,
    val mirrorValue: Int,
    val normalizedValue: Double,
    val distanceFromCenter: Int
) {
    companion object {
        fun fromIndex(index: Int): BrahimState {
            require(index in 0 until BrahimConstants.BRAHIM_DIMENSION) {
                "Index must be in range 0..${BrahimConstants.BRAHIM_DIMENSION - 1}"
            }
            val value = BrahimConstants.BRAHIM_SEQUENCE[index]
            return BrahimState(
                index = index,
                value = value,
                mirrorValue = BrahimConstants.BRAHIM_SUM - value,
                normalizedValue = value.toDouble() / BrahimConstants.BRAHIM_SUM,
                distanceFromCenter = kotlin.math.abs(value - BrahimConstants.BRAHIM_CENTER)
            )
        }

        fun fromValue(value: Int): BrahimState? {
            val index = BrahimConstants.BRAHIM_SEQUENCE.indexOf(value)
            return if (index >= 0) fromIndex(index) else null
        }
    }
}

/**
 * Mirror product: pairing alpha (ascending) with omega (descending).
 */
data class MirrorProduct(
    val alphaState: BrahimState,
    val omegaState: BrahimState,
    val product: Int,
    val conservedQuantity: Int  // Always equals 214
)

/**
 * Extended Brahim Sequence operations.
 */
object BrahimSequence {

    /**
     * Get all states as BrahimState objects.
     */
    fun getAllStates(): List<BrahimState> {
        return (0 until BrahimConstants.BRAHIM_DIMENSION).map { BrahimState.fromIndex(it) }
    }

    /**
     * Get all mirror pairs.
     */
    fun getAllMirrorPairs(): List<MirrorProduct> {
        val states = getAllStates()
        return states.take(5).mapIndexed { i, alphaState ->
            val omegaState = states[states.size - 1 - i]
            MirrorProduct(
                alphaState = alphaState,
                omegaState = omegaState,
                product = alphaState.value * omegaState.value,
                conservedQuantity = alphaState.value + omegaState.value
            )
        }
    }

    /**
     * Apply mirror operator: M(x) = 214 - x
     */
    fun applyMirror(value: Int): Int = BrahimConstants.BRAHIM_SUM - value

    /**
     * Verify mirror conservation law: alpha + omega = 214
     */
    fun verifyMirrorConservation(): Boolean {
        return getAllMirrorPairs().all { it.conservedQuantity == BrahimConstants.BRAHIM_SUM }
    }

    /**
     * Compute phi-adic expansion of a number.
     * Represents number as sum of phi powers: n = sum(a_i * phi^i)
     */
    fun phiAdicExpansion(n: Double, maxTerms: Int = 10): List<Pair<Int, Double>> {
        val expansion = mutableListOf<Pair<Int, Double>>()
        var remaining = n

        for (power in maxTerms downTo -maxTerms) {
            val phiPower = BrahimConstants.PHI.pow(power)
            if (remaining >= phiPower) {
                val coefficient = (remaining / phiPower).toInt()
                expansion.add(power to coefficient.toDouble())
                remaining -= coefficient * phiPower
            }
        }

        return expansion
    }

    /**
     * Check if a value is a candidate Brahim number.
     * Candidates satisfy specific divisibility and symmetry properties.
     */
    fun isCandidate(value: Int): Boolean {
        // Must be positive
        if (value <= 0) return false

        // Must not already be in sequence
        if (value in BrahimConstants.BRAHIM_SEQUENCE) return false

        // Check modular properties
        val mod7 = value % 7
        val mod11 = value % 11

        // Known pattern: sum of digits divisible by 3
        val digitSum = value.toString().sumOf { it.digitToInt() }

        return digitSum % 3 == 0 && (mod7 in listOf(0, 1, 2, 4) || mod11 in listOf(0, 1, 3, 4, 5, 9))
    }

    /**
     * Search for candidate Brahim numbers in a range.
     */
    fun searchCandidates(start: Int, end: Int): List<Int> {
        return (start..end).filter { isCandidate(it) }
    }

    /**
     * Compute the spectral signature of the sequence.
     * Returns eigenvalue-like quantities from the sequence structure.
     */
    fun computeSpectralSignature(): Map<String, Double> {
        val states = getAllStates()

        // First moment (mean)
        val mean = states.map { it.value }.average()

        // Second moment (variance)
        val variance = states.map { (it.value - mean).pow(2) }.average()

        // Autocorrelation
        val autocorr = states.zipWithNext().map { (a, b) ->
            (a.value - mean) * (b.value - mean)
        }.average() / variance

        // Spectral gap (difference between consecutive values)
        val gaps = states.zipWithNext().map { (a, b) -> b.value - a.value }
        val meanGap = gaps.average()
        val gapVariance = gaps.map { (it - meanGap).pow(2) }.average()

        return mapOf(
            "mean" to mean,
            "variance" to variance,
            "autocorrelation" to autocorr,
            "mean_gap" to meanGap,
            "gap_variance" to gapVariance,
            "spectral_density" to (variance / mean)
        )
    }

    /**
     * Get sequence metadata.
     */
    fun getMetadata(): Map<String, Any> {
        return mapOf(
            "name" to "Brahim Sequence",
            "notation" to "B",
            "cardinality" to BrahimConstants.BRAHIM_DIMENSION,
            "sum" to BrahimConstants.BRAHIM_SUM,
            "center" to BrahimConstants.BRAHIM_CENTER,
            "minimum" to BrahimConstants.BRAHIM_SEQUENCE.min(),
            "maximum" to BrahimConstants.BRAHIM_SEQUENCE.max(),
            "is_mirror_conserved" to verifyMirrorConservation(),
            "spectral_signature" to computeSpectralSignature()
        )
    }
}
