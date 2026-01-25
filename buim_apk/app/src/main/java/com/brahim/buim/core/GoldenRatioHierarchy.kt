/**
 * Golden Ratio Hierarchy - φ → α → β → γ
 * =======================================
 *
 * The complete hierarchy of golden ratio derived constants.
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-25
 */

package com.brahim.buim.core

import kotlin.math.abs
import kotlin.math.pow
import kotlin.math.sqrt

/**
 * Hierarchical level in the golden ratio cascade.
 */
data class HierarchyLevel(
    val name: String,
    val symbol: String,
    val value: Double,
    val phiPower: Int,
    val formula: String,
    val continuedFraction: String
)

/**
 * Golden Ratio Hierarchy operations.
 */
object GoldenRatioHierarchy {

    /** All levels in the hierarchy */
    val levels: List<HierarchyLevel> = listOf(
        HierarchyLevel(
            name = "Golden Ratio",
            symbol = "φ",
            value = BrahimConstants.PHI,
            phiPower = 1,
            formula = "(1 + √5) / 2",
            continuedFraction = "[1; 1, 1, 1, ...]"
        ),
        HierarchyLevel(
            name = "Compression",
            symbol = "1/φ",
            value = BrahimConstants.COMPRESSION,
            phiPower = -1,
            formula = "φ - 1 = 1/φ",
            continuedFraction = "[0; 1, 1, 1, ...]"
        ),
        HierarchyLevel(
            name = "Wormhole Alpha",
            symbol = "α",
            value = BrahimConstants.ALPHA_WORMHOLE,
            phiPower = -2,
            formula = "2 - φ = 1/φ²",
            continuedFraction = "[0; 2, 1, 1, 1, ...]"
        ),
        HierarchyLevel(
            name = "Brahim Security",
            symbol = "β",
            value = BrahimConstants.BETA_SECURITY,
            phiPower = -3,
            formula = "√5 - 2 = 1/φ³",
            continuedFraction = "[0; 4, 4, 4, ...]"
        ),
        HierarchyLevel(
            name = "Gamma Damping",
            symbol = "γ",
            value = BrahimConstants.GAMMA_DAMPING,
            phiPower = -4,
            formula = "1/φ⁴",
            continuedFraction = "[0; 6, 1, 6, 1, ...]"
        ),
        HierarchyLevel(
            name = "Delta Fifth",
            symbol = "δ",
            value = BrahimConstants.DELTA_FIFTH,
            phiPower = -5,
            formula = "1/φ⁵",
            continuedFraction = "[0; 11, 11, ...]"
        )
    )

    /**
     * Get level by symbol.
     */
    fun getLevel(symbol: String): HierarchyLevel? {
        return levels.find { it.symbol == symbol }
    }

    /**
     * Get level by phi power.
     */
    fun getLevelByPower(power: Int): HierarchyLevel? {
        return levels.find { it.phiPower == power }
    }

    /**
     * Compute any phi power.
     */
    fun phiPower(n: Int): Double {
        return BrahimConstants.PHI.pow(n)
    }

    /**
     * Compute the continued fraction representation of a value.
     * Returns first n terms.
     */
    fun continuedFraction(value: Double, terms: Int = 10): List<Int> {
        val result = mutableListOf<Int>()
        var x = value

        for (i in 0 until terms) {
            val a = x.toInt()
            result.add(a)
            val frac = x - a
            if (abs(frac) < 1e-10) break
            x = 1.0 / frac
        }

        return result
    }

    /**
     * Verify that beta has continued fraction [0; 4, 4, 4, ...].
     */
    fun verifyBetaContinuedFraction(): Boolean {
        val cf = continuedFraction(BrahimConstants.BETA_SECURITY, 10)
        // Should be [0, 4, 4, 4, ...]
        return cf[0] == 0 && cf.drop(1).all { it == 4 }
    }

    /**
     * Verify the cascade relationship: each level = previous / phi.
     */
    fun verifyCascade(): Map<String, Boolean> {
        val results = mutableMapOf<String, Boolean>()

        for (i in 1 until levels.size) {
            val prev = levels[i - 1]
            val curr = levels[i]
            val expected = prev.value / BrahimConstants.PHI
            val matches = abs(curr.value - expected) < 1e-14
            results["${prev.symbol} / φ = ${curr.symbol}"] = matches
        }

        return results
    }

    /**
     * Verify key algebraic identities.
     */
    fun verifyIdentities(): Map<String, Boolean> {
        val phi = BrahimConstants.PHI
        val beta = BrahimConstants.BETA_SECURITY

        return mapOf(
            // φ² = φ + 1
            "phi_squared_identity" to (abs(phi * phi - (phi + 1)) < 1e-14),

            // φ - 1 = 1/φ
            "phi_reciprocal_identity" to (abs((phi - 1) - 1/phi) < 1e-14),

            // β = √5 - 2
            "beta_sqrt5_identity" to (abs(beta - (sqrt(5.0) - 2)) < 1e-14),

            // β² + 4β - 1 = 0
            "beta_polynomial" to (abs(beta * beta + 4 * beta - 1) < 1e-14),

            // φ³ * β = 1
            "phi_cubed_beta" to (abs(phi * phi * phi * beta - 1) < 1e-14),

            // α / β = φ
            "alpha_beta_ratio" to (abs(BrahimConstants.ALPHA_WORMHOLE / beta - phi) < 1e-14)
        )
    }

    /**
     * Get the hierarchy as a visualization-friendly structure.
     */
    fun getVisualization(): Map<String, Any> {
        return mapOf(
            "title" to "Golden Ratio Hierarchy",
            "root" to "φ = 1.618...",
            "levels" to levels.map { level ->
                mapOf(
                    "name" to level.name,
                    "symbol" to level.symbol,
                    "value" to "%.15f".format(level.value),
                    "phiPower" to "φ^${level.phiPower}",
                    "formula" to level.formula,
                    "continued_fraction" to level.continuedFraction
                )
            },
            "cascade_verified" to verifyCascade().values.all { it },
            "identities_verified" to verifyIdentities().values.all { it },
            "beta_continued_fraction_verified" to verifyBetaContinuedFraction()
        )
    }
}
