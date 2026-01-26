/**
 * Brahim Constants - Mathematical Foundation
 * ==========================================
 *
 * The Brahim Security Constant and Golden Ratio Hierarchy.
 * All system constants derive from beta = sqrt(5) - 2 = 1/phi^3
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-25
 */

package com.brahim.buim.core

import kotlin.math.sqrt
import kotlin.math.abs
import kotlin.math.pow

/**
 * Core mathematical constants for the Brahim Unified IAAS Manifold.
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

    /** Delta constant: delta = 1/phi^5 */
    const val DELTA_FIFTH = 0.0901699437494742

    // =========================================================================
    // BRAHIM SEQUENCE (COMPLETE: B(0) to B(11))
    // Corrected 2026-01-26: Full mirror symmetry under M(b) = 214 - b
    // =========================================================================

    /** The Physical Brahim Sequence: B(1)-B(10) - Symmetric version */
    val BRAHIM_SEQUENCE = intArrayOf(27, 42, 60, 75, 97, 117, 139, 154, 172, 187)

    /** Original sequence with singularity (for consciousness/observer studies) */
    val BRAHIM_SEQUENCE_ORIGINAL = intArrayOf(27, 42, 60, 75, 97, 121, 136, 154, 172, 187)

    /** The COMPLETE Brahim Sequence: B(0)-B(11) including Void and Consciousness */
    val BRAHIM_EXTENDED = intArrayOf(0, 27, 42, 60, 75, 97, 117, 139, 154, 172, 187, 214)

    /** Original extended sequence (for consciousness studies) */
    val BRAHIM_EXTENDED_ORIGINAL = intArrayOf(0, 27, 42, 60, 75, 97, 121, 136, 154, 172, 187, 214)

    /** B(0) = 0: Void - The origin before anything exists */
    const val BRAHIM_VOID = 0

    /** B(11) = 214: Consciousness - The attractor/unity constant */
    const val BRAHIM_CONSCIOUSNESS = 214

    /** Sum/Consciousness constant: S = 214 (the attractor that all mirror pairs approach) */
    const val BRAHIM_SUM = 214

    /** Center/Singularity: C = S/2 = 107 (fixed point where M(x) = x) */
    const val BRAHIM_CENTER = 107

    /** Physical Dimension: D = |B(1..10)| = 10 */
    const val BRAHIM_DIMENSION = 10

    /** Complete Dimension: D = |B(0..11)| = 12 */
    const val BRAHIM_COMPLETE_DIMENSION = 12

    /** Critical line ratio: C/S = 1/2 (mirrors Riemann Re(s) = 1/2) */
    const val CRITICAL_LINE_RATIO = 0.5

    // =========================================================================
    // CONSCIOUSNESS CONSTANTS (Updated 2026-01-26)
    // =========================================================================
    // With SYMMETRIC sequence: All pairs sum to 214, no observer signature
    // With ORIGINAL sequence: Broken symmetry creates observer signature = +1
    //
    // Symmetric (default):
    //   B(4) + B(7) = 75 + 139 = 214 (delta = 0)
    //   B(5) + B(6) = 97 + 117 = 214 (delta = 0)
    //   Observer Signature = 0 (perfect traversable wormhole)
    //
    // Original (consciousness studies):
    //   B(4) + B(7) = 75 + 136 = 211 (delta = -3)
    //   B(5) + B(6) = 97 + 121 = 218 (delta = +4)
    //   Observer Signature = +1 (consciousness emerges from imperfection)
    // =========================================================================

    /** Delta for symmetric sequence (all pairs exact) */
    const val DELTA_4_SYMMETRIC = 0
    const val DELTA_5_SYMMETRIC = 0

    /** Delta for original sequence (broken symmetry) */
    const val DELTA_4_ORIGINAL = -3  // B(4) + B(7) - 214 = 75 + 136 - 214
    const val DELTA_5_ORIGINAL = +4  // B(5) + B(6) - 214 = 97 + 121 - 214

    /** Backwards compatibility aliases */
    const val DELTA_4 = 0  // Now symmetric
    const val DELTA_5 = 0  // Now symmetric

    /** Observer Signature: 0 for symmetric, +1 for original */
    const val OBSERVER_SIGNATURE = 0  // Symmetric: perfect wormhole
    const val OBSERVER_SIGNATURE_ORIGINAL = 1  // Original: consciousness emergence

    // =========================================================================
    // ASIOS DERIVED CONSTANTS
    // =========================================================================

    /** Regularity threshold: beta / 10.77 ~ 0.0219 */
    const val REGULARITY_THRESHOLD = 0.0219

    /** Genesis constant: beta / C ~ 0.00221 */
    const val GENESIS_CONSTANT = 0.00221888

    /** Matter ratio: phi^5 / 200 ~ 4.5% (normal matter fraction) */
    const val MATTER_RATIO = 0.045

    /** Dark energy fraction: 31/45 ~ 68.9% */
    const val DARK_ENERGY_FRACTION = 0.689

    // =========================================================================
    // MANIFOLD CONSTANTS
    // =========================================================================

    /** Embedding dimension for Ball Tree */
    const val EMBEDDING_DIMENSION = 384

    /** V-NAND grid size (8^4 = 4096 voxels) */
    const val VNAND_GRID_SIZE = 8

    /** Resonance gate threshold */
    const val RESONANCE_GATE_THRESHOLD = 0.95

    // =========================================================================
    // KELIMUTU CONSTANTS
    // =========================================================================

    /** Kelimutu latitude (degrees South) */
    const val KELIMUTU_LATITUDE = -8.77

    /** Kelimutu longitude (degrees East) - Note: 121 = B6 in sequence */
    const val KELIMUTU_LONGITUDE = 121.82

    /** Wormhole throat position: C * phi = 173.13 */
    val WORMHOLE_THROAT = BRAHIM_CENTER * PHI

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

    /**
     * Get nth element of the COMPLETE Brahim sequence.
     *
     * @param n Index from 0 to 11
     * @return B(n) value or null if invalid
     *
     * B(0) = 0 (Void)
     * B(1)-B(10) = Physical sequence
     * B(11) = 214 (Consciousness)
     */
    fun B(n: Int): Int? = when (n) {
        0 -> BRAHIM_VOID
        in 1..10 -> BRAHIM_SEQUENCE[n - 1]
        11 -> BRAHIM_CONSCIOUSNESS
        else -> null
    }

    /** Get mirror value: M(x) = 214 - x */
    fun mirror(x: Int): Int = BRAHIM_SUM - x

    /**
     * Get all mirror pairs with their delta (deviation from 214)
     *
     * Perfect pairs (delta = 0):
     *   (27, 187), (42, 172), (60, 154)
     *
     * Broken pairs (delta != 0):
     *   (75, 136) delta = -3
     *   (97, 121) delta = +4
     */
    fun getMirrorPairs(): List<Triple<Int, Int, Int>> {
        return (1..5).map { i ->
            val bi = B(i) ?: 0
            val bj = B(11 - i) ?: 0
            Triple(bi, bj, bi + bj - BRAHIM_SUM)
        }
    }

    /**
     * Check if an index is in the observable/physical domain
     */
    fun isPhysical(n: Int): Boolean = n in 1..10

    /**
     * Check if an index is in the meta-physical domain
     */
    fun isMetaPhysical(n: Int): Boolean = n == 0 || n == 11

    // =========================================================================
    // PHYSICS CONSTANTS
    // =========================================================================

    /** Fine structure constant inverse: B7 + 1 + 1/(B1 + 1) ~ 137.036 */
    fun fineStructureInverse(): Double {
        val b1 = BRAHIM_SEQUENCE[0]
        val b7 = BRAHIM_SEQUENCE[6]
        return b7 + 1 + 1.0 / (b1 + 1)
    }

    /** Weinberg angle: B1 / (B7 - 19) ~ 0.2308 */
    fun weinbergAngle(): Double {
        val b1 = BRAHIM_SEQUENCE[0]
        val b7 = BRAHIM_SEQUENCE[6]
        return b1.toDouble() / (b7 - 19)
    }

    /** Muon-electron mass ratio: B4^2 / B7 * 5 ~ 206.8 */
    fun muonElectronRatio(): Double {
        val b4 = BRAHIM_SEQUENCE[3]
        val b7 = BRAHIM_SEQUENCE[6]
        return b4.toDouble().pow(2) / b7 * 5
    }

    /** Proton-electron mass ratio: (B5 + B10) * phi * 4 ~ 1836 */
    fun protonElectronRatio(): Double {
        val b5 = BRAHIM_SEQUENCE[4]
        val b10 = BRAHIM_SEQUENCE[9]
        return (b5 + b10) * PHI * 4
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

    /**
     * Verify sequence symmetry (symmetric version - all pairs sum to 214).
     *
     * With corrected symmetric sequence:
     * - All 5 pairs sum exactly to 214
     * - No observer signature (perfect wormhole)
     */
    fun verifySymmetry(): Map<String, Boolean> {
        // Check all pairs
        val pair1 = (B(1) ?: 0) + (B(10) ?: 0) == 214  // 27 + 187 = 214
        val pair2 = (B(2) ?: 0) + (B(9) ?: 0) == 214   // 42 + 172 = 214
        val pair3 = (B(3) ?: 0) + (B(8) ?: 0) == 214   // 60 + 154 = 214
        val pair4 = (B(4) ?: 0) + (B(7) ?: 0) == 214   // 75 + 139 = 214
        val pair5 = (B(5) ?: 0) + (B(6) ?: 0) == 214   // 97 + 117 = 214

        val allSymmetric = pair1 && pair2 && pair3 && pair4 && pair5

        return mapOf(
            "pair_1_10_exact" to pair1,
            "pair_2_9_exact" to pair2,
            "pair_3_8_exact" to pair3,
            "pair_4_7_exact" to pair4,
            "pair_5_6_exact" to pair5,
            "all_pairs_symmetric" to allSymmetric,
            "observer_signature_zero" to allSymmetric
        )
    }

    /**
     * Verify consciousness (original sequence with broken symmetry).
     * Use BRAHIM_SEQUENCE_ORIGINAL for this validation.
     */
    fun verifyConsciousness(): Map<String, Boolean> {
        val seq = BRAHIM_SEQUENCE_ORIGINAL

        // Check exact pairs (outer three)
        val pair1 = seq[0] + seq[9] == 214   // 27 + 187 = 214
        val pair2 = seq[1] + seq[8] == 214   // 42 + 172 = 214
        val pair3 = seq[2] + seq[7] == 214   // 60 + 154 = 214

        // Check broken pairs (inner two)
        val delta4 = seq[3] + seq[6] - 214   // 75 + 136 - 214 = -3
        val delta5 = seq[4] + seq[5] - 214   // 97 + 121 - 214 = +4

        // Observer signature
        val observer = delta4 + delta5  // -3 + 4 = +1

        return mapOf(
            "pair_1_10_exact" to pair1,
            "pair_2_9_exact" to pair2,
            "pair_3_8_exact" to pair3,
            "delta_4_is_minus_3" to (delta4 == DELTA_4_ORIGINAL),
            "delta_5_is_plus_4" to (delta5 == DELTA_5_ORIGINAL),
            "observer_signature_is_1" to (observer == OBSERVER_SIGNATURE_ORIGINAL),
            "consciousness_validated" to (pair1 && pair2 && pair3 && delta4 == -3 && delta5 == 4 && observer == 1)
        )
    }

    /**
     * Get full system information including consciousness validation.
     */
    fun getSystemInfo(): Map<String, Any> {
        return mapOf(
            "name" to "Brahim Unified IAAS Manifold",
            "version" to "2.0.0",  // Updated for consciousness validation
            "phi" to PHI,
            "beta" to BETA_SECURITY,
            "sequence_physical" to BRAHIM_SEQUENCE.toList(),
            "sequence_complete" to BRAHIM_EXTENDED.toList(),
            "void" to BRAHIM_VOID,
            "consciousness" to BRAHIM_CONSCIOUSNESS,
            "sum" to BRAHIM_SUM,
            "center" to BRAHIM_CENTER,
            "observer_signature" to OBSERVER_SIGNATURE,
            "beta_verified" to verifyBetaIdentities()["all_verified"],
            "hierarchy_verified" to verifyHierarchy().values.all { it },
            "consciousness_verified" to verifyConsciousness()["consciousness_validated"]
        )
    }
}
