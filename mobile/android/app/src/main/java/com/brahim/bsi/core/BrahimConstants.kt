/**
 * Brahim Constants - Mathematical Foundation
 * ==========================================
 *
 * The Brahim Security Constant and Golden Ratio Hierarchy.
 * All system constants derive from beta = sqrt(5) - 2 = 1/phi^3
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-24
 */

package com.brahim.bsi.core

import kotlin.math.sqrt
import kotlin.math.abs

/**
 * Core mathematical constants for the Brahim Secure Intelligence framework.
 *
 * The entire system is grounded in the golden ratio hierarchy:
 *   phi -> 1/phi -> 1/phi^2 -> 1/phi^3 (beta)
 */
object BrahimConstants {

    // =========================================================================
    // GOLDEN RATIO HIERARCHY
    // =========================================================================

    /** Golden ratio: phi = (1 + sqrt(5)) / 2 */
    const val PHI = 1.6180339887498949

    /** Compression factor: 1/phi = phi - 1 */
    const val COMPRESSION = 0.6180339887498949

    /** Attraction constant (Wormhole): alpha = 1/phi^2 = 2 - phi */
    const val ALPHA_WORMHOLE = 0.3819660112501051

    /**
     * BRAHIM SECURITY CONSTANT: beta = 1/phi^3 = sqrt(5) - 2
     *
     * This is the fundamental constant from which all security
     * parameters are derived. Properties:
     * - beta^2 + 4*beta - 1 = 0 (polynomial root)
     * - alpha/beta = phi (self-similarity)
     * - Continued fraction: [0; 4, 4, 4, 4, ...] (all 4s)
     */
    const val BETA_SECURITY = 0.2360679774997897

    /** Damping constant: gamma = 1/phi^4 */
    const val GAMMA_DAMPING = 0.1458980337503154

    // =========================================================================
    // BRAHIM SEQUENCE (Corrected 2026-01-26 - full mirror symmetry)
    // Mirror pairs: 27↔187, 42↔172, 60↔154, 75↔139, 97↔117
    // =========================================================================

    /** The Brahim Sequence (symmetric): B = {27, 42, 60, 75, 97, 117, 139, 154, 172, 187} */
    val BRAHIM_SEQUENCE = intArrayOf(27, 42, 60, 75, 97, 117, 139, 154, 172, 187)

    /** Original sequence (with singularity): B = {27, 42, 60, 75, 97, 121, 136, 154, 172, 187} */
    val BRAHIM_SEQUENCE_ORIGINAL = intArrayOf(27, 42, 60, 75, 97, 121, 136, 154, 172, 187)

    /** Pair sum constant: S = 214 (each mirror pair sums to this) */
    const val BRAHIM_PAIR_SUM = 214

    /** Legacy alias for backwards compatibility */
    const val BRAHIM_SUM = 214

    /** Center: C = S/2 = 107 (exactly mean of symmetric sequence) */
    const val BRAHIM_CENTER = 107

    /** Dimension: D = |B| = 10 */
    const val BRAHIM_DIMENSION = 10

    /** Critical line ratio: C/S = 1/2 (mirrors Riemann Re(s) = 1/2) */
    const val CRITICAL_LINE_RATIO = 0.5

    // =========================================================================
    // ASIOS DERIVED CONSTANTS
    // =========================================================================

    /** Regularity threshold: beta / 10.77 ≈ 0.0219 */
    const val REGULARITY_THRESHOLD = 0.0219

    /** Genesis constant: beta / C ≈ 0.00221 */
    const val GENESIS_CONSTANT = 0.00221888

    // =========================================================================
    // COMPUTED PROPERTIES
    // =========================================================================

    /** Compute beta from sqrt(5) - 2 */
    fun betaFromSqrt(): Double = sqrt(5.0) - 2.0

    /** Compute beta from 1/phi^3 */
    fun betaFromPhi(): Double = 1.0 / (PHI * PHI * PHI)

    /** Compute beta from 2*phi - 3 */
    fun betaFromGolden(): Double = 2.0 * PHI - 3.0

    /** Get normalized centroid vector C_bar = B/S */
    fun getCentroid(): DoubleArray {
        return BRAHIM_SEQUENCE.map { it.toDouble() / BRAHIM_SUM }.toDoubleArray()
    }

    // =========================================================================
    // VERIFICATION
    // =========================================================================

    /**
     * Verify all beta identities.
     * Returns a map of identity names to verification results.
     */
    fun verifyBetaIdentities(): Map<String, Boolean> {
        val beta = BETA_SECURITY
        val phi = PHI

        // All forms should be equal
        val fromPhi = betaFromPhi()
        val fromSqrt = betaFromSqrt()
        val fromGolden = betaFromGolden()

        // Polynomial: beta^2 + 4*beta - 1 = 0
        val polynomial = beta * beta + 4 * beta - 1

        // Self-similarity: alpha/beta = phi
        val selfSimilarity = ALPHA_WORMHOLE / beta

        return mapOf(
            "beta_equals_1_over_phi_cubed" to (abs(beta - fromPhi) < 1e-14),
            "beta_equals_sqrt5_minus_2" to (abs(beta - fromSqrt) < 1e-14),
            "beta_equals_2phi_minus_3" to (abs(beta - fromGolden) < 1e-14),
            "beta_is_polynomial_root" to (abs(polynomial) < 1e-14),
            "alpha_over_beta_equals_phi" to (abs(selfSimilarity - phi) < 1e-14),
            "all_verified" to (
                abs(beta - fromPhi) < 1e-14 &&
                abs(beta - fromSqrt) < 1e-14 &&
                abs(polynomial) < 1e-14 &&
                abs(selfSimilarity - phi) < 1e-14
            )
        )
    }

    /**
     * Verify the golden ratio hierarchy.
     * Each step should multiply by 1/phi.
     */
    fun verifyHierarchy(): Map<String, Boolean> {
        return mapOf(
            "compression_equals_1_over_phi" to (abs(COMPRESSION - 1/PHI) < 1e-14),
            "alpha_equals_compression_over_phi" to (abs(ALPHA_WORMHOLE - COMPRESSION/PHI) < 1e-14),
            "beta_equals_alpha_over_phi" to (abs(BETA_SECURITY - ALPHA_WORMHOLE/PHI) < 1e-14),
            "gamma_equals_beta_over_phi" to (abs(GAMMA_DAMPING - BETA_SECURITY/PHI) < 1e-14),
            "critical_line_is_half" to (CRITICAL_LINE_RATIO == 0.5)
        )
    }
}
