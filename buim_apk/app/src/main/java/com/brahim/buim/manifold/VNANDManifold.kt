/**
 * V-NAND Manifold - 4D Voxel Grid for Pattern Learning
 * =====================================================
 *
 * Configuration:
 * - Grid: 8×8×8×8 = 4096 voxels (32,768 bits)
 * - Resonance Target: 0.0219 (GENESIS_CONSTANT)
 * - Gate Threshold: 0.95
 *
 * SO(10) Symmetry Constants:
 * - PHI = 1.61803398875 (Golden Ratio)
 * - Matter Ratio = φ⁵/200 ≈ 4.5%
 * - Dark Energy = 31/45 ≈ 68.9%
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-25
 */

package com.brahim.buim.manifold

import com.brahim.buim.core.BrahimConstants
import java.security.MessageDigest
import kotlin.math.abs
import kotlin.math.exp
import kotlin.math.pow

/**
 * Resonance gate result.
 */
data class ResonanceGateResult(
    val isOpen: Boolean,
    val resonance: Double,
    val message: String
)

/**
 * Pattern encoding result.
 */
data class PatternEncoding(
    val hash: String,
    val density: Double,
    val symmetryAlignment: Double,
    val timestamp: Long
)

/**
 * V-NAND Manifold - 4D Voxel Learning Grid.
 *
 * Implements the 8×8×8×8 voxel grid for pattern storage and resonance
 * detection based on SO(10) symmetry and the Golden Ratio.
 */
class VNANDManifold {

    companion object {
        const val GRID_SIZE = 8
        const val TOTAL_VOXELS = GRID_SIZE * GRID_SIZE * GRID_SIZE * GRID_SIZE  // 4096
        const val TOTAL_BITS = TOTAL_VOXELS * 8  // 32,768

        // SO(10) Symmetry Constants
        const val PHI = 1.61803398875
        const val GENESIS_CONSTANT = 0.0219
        const val MATTER_RATIO = 0.045  // φ⁵/200 ≈ 4.5%
        const val DARK_ENERGY_RATIO = 0.689  // 31/45 ≈ 68.9%

        // Resonance parameters
        const val GAMMA = 0.001  // Lorentzian width
        const val RESONANCE_THRESHOLD = 0.95
    }

    // 4D Voxel Grid
    private val grid = Array(GRID_SIZE) {
        Array(GRID_SIZE) {
            Array(GRID_SIZE) {
                ByteArray(GRID_SIZE) { 0 }
            }
        }
    }

    // Pattern history for learning
    private val patternHistory = mutableListOf<PatternEncoding>()

    // Statistics
    var totalPatternsLearned = 0
        private set
    var successfulPatterns = 0
        private set
    var failedPatterns = 0
        private set

    /**
     * Calculate grid resonance based on SO(10) Symmetry.
     *
     * The resonance is computed using:
     * 1. Lorentzian peak centered at the 0.0219 Symmetry Node
     * 2. Symmetry alignment with 4.5% matter ratio
     */
    fun calculateResonance(): Double {
        // Flatten grid to bit array
        val flatBits = mutableListOf<Int>()
        for (i in 0 until GRID_SIZE) {
            for (j in 0 until GRID_SIZE) {
                for (k in 0 until GRID_SIZE) {
                    for (l in 0 until GRID_SIZE) {
                        val byte = grid[i][j][k][l].toInt() and 0xFF
                        // Extract individual bits
                        for (bit in 0..7) {
                            flatBits.add((byte shr bit) and 1)
                        }
                    }
                }
            }
        }

        // Calculate variance
        val mean = flatBits.average()
        val variance = flatBits.map { (it - mean).pow(2) }.average()

        // Lorentzian peak at GENESIS_CONSTANT (0.0219)
        val diffSq = (variance - GENESIS_CONSTANT).pow(2)
        val resonance = (GAMMA.pow(2)) / (diffSq + GAMMA.pow(2))

        // Symmetry check: bit-density matches 4.5% matter ratio
        val density = mean
        val symmetryAlignment = exp(-50 * abs(density - MATTER_RATIO))

        // Combined resonance
        return resonance * 0.7 + symmetryAlignment * 0.3
    }

    /**
     * Check if the resonance gate is open.
     */
    fun checkResonanceGate(): ResonanceGateResult {
        val resonance = calculateResonance()
        val isOpen = resonance >= RESONANCE_THRESHOLD

        val message = if (isOpen) {
            "GATE_OPEN: 0.0219 Symmetry Detected (Resonance: %.4f)".format(resonance)
        } else {
            "GATE_CLOSED: Searching for 0.0219 Ratio (Current: %.4f)".format(resonance)
        }

        return ResonanceGateResult(isOpen, resonance, message)
    }

    /**
     * Encode a pattern vector into the voxel grid.
     */
    fun encodePattern(vector: DoubleArray): PatternEncoding {
        require(vector.size >= 4) { "Vector must have at least 4 dimensions" }

        // Normalize to grid coordinates
        val normalized = vector.map { ((it + 1) / 2 * (GRID_SIZE - 1)).toInt().coerceIn(0, GRID_SIZE - 1) }

        // Map to 4D coordinates
        val i = normalized.getOrElse(0) { 0 }
        val j = normalized.getOrElse(1) { 0 }
        val k = normalized.getOrElse(2) { 0 }
        val l = normalized.getOrElse(3) { 0 }

        // Set voxel (simple encoding)
        grid[i][j][k][l] = (grid[i][j][k][l].toInt() or 0x01).toByte()

        // Compute hash
        val hash = computeGridHash()

        // Get density
        val density = grid.flatMap { it.flatMap { it.flatMap { it.toList() } } }
            .map { it.toInt() and 0xFF }
            .average() / 255.0

        // Get symmetry alignment
        val symmetryAlignment = exp(-50 * abs(density - MATTER_RATIO))

        val encoding = PatternEncoding(
            hash = hash,
            density = density,
            symmetryAlignment = symmetryAlignment,
            timestamp = System.currentTimeMillis()
        )

        patternHistory.add(encoding)
        return encoding
    }

    /**
     * Learn a pattern with success/failure feedback.
     */
    fun learnPattern(vector: DoubleArray, success: Boolean) {
        val encoding = encodePattern(vector)
        totalPatternsLearned++

        if (success) {
            successfulPatterns++
            // Strengthen the pattern
            strengthenPattern(vector)
        } else {
            failedPatterns++
            // Weaken the pattern
            weakenPattern(vector)
        }
    }

    private fun strengthenPattern(vector: DoubleArray) {
        val normalized = vector.map { ((it + 1) / 2 * (GRID_SIZE - 1)).toInt().coerceIn(0, GRID_SIZE - 1) }
        val i = normalized.getOrElse(0) { 0 }
        val j = normalized.getOrElse(1) { 0 }
        val k = normalized.getOrElse(2) { 0 }
        val l = normalized.getOrElse(3) { 0 }

        // Increase voxel value (strengthening)
        val current = grid[i][j][k][l].toInt() and 0xFF
        grid[i][j][k][l] = minOf(current + 16, 255).toByte()
    }

    private fun weakenPattern(vector: DoubleArray) {
        val normalized = vector.map { ((it + 1) / 2 * (GRID_SIZE - 1)).toInt().coerceIn(0, GRID_SIZE - 1) }
        val i = normalized.getOrElse(0) { 0 }
        val j = normalized.getOrElse(1) { 0 }
        val k = normalized.getOrElse(2) { 0 }
        val l = normalized.getOrElse(3) { 0 }

        // Decrease voxel value (weakening)
        val current = grid[i][j][k][l].toInt() and 0xFF
        grid[i][j][k][l] = maxOf(current - 8, 0).toByte()
    }

    /**
     * Compute SHA-256 hash of the grid.
     */
    private fun computeGridHash(): String {
        val bytes = mutableListOf<Byte>()
        for (i in 0 until GRID_SIZE) {
            for (j in 0 until GRID_SIZE) {
                for (k in 0 until GRID_SIZE) {
                    bytes.addAll(grid[i][j][k].toList())
                }
            }
        }

        val digest = MessageDigest.getInstance("SHA-256")
        val hash = digest.digest(bytes.toByteArray())
        return hash.take(16).joinToString("") { "%02x".format(it) }
    }

    /**
     * Clear the grid.
     */
    fun clear() {
        for (i in 0 until GRID_SIZE) {
            for (j in 0 until GRID_SIZE) {
                for (k in 0 until GRID_SIZE) {
                    for (l in 0 until GRID_SIZE) {
                        grid[i][j][k][l] = 0
                    }
                }
            }
        }
        patternHistory.clear()
    }

    /**
     * Get manifold statistics.
     */
    fun getStats(): Map<String, Any> {
        val gateResult = checkResonanceGate()

        return mapOf(
            "grid_size" to "$GRID_SIZE^4 = $TOTAL_VOXELS voxels",
            "total_bits" to TOTAL_BITS,
            "resonance" to gateResult.resonance,
            "gate_open" to gateResult.isOpen,
            "genesis_constant" to GENESIS_CONSTANT,
            "matter_ratio" to MATTER_RATIO,
            "dark_energy_ratio" to DARK_ENERGY_RATIO,
            "total_patterns_learned" to totalPatternsLearned,
            "successful_patterns" to successfulPatterns,
            "failed_patterns" to failedPatterns,
            "success_rate" to if (totalPatternsLearned > 0) {
                successfulPatterns.toDouble() / totalPatternsLearned
            } else 0.0,
            "grid_hash" to computeGridHash(),
            "phi" to PHI
        )
    }

    /**
     * Export grid as byte array for serialization.
     */
    fun exportGrid(): ByteArray {
        val bytes = mutableListOf<Byte>()
        for (i in 0 until GRID_SIZE) {
            for (j in 0 until GRID_SIZE) {
                for (k in 0 until GRID_SIZE) {
                    bytes.addAll(grid[i][j][k].toList())
                }
            }
        }
        return bytes.toByteArray()
    }

    /**
     * Import grid from byte array.
     */
    fun importGrid(bytes: ByteArray) {
        require(bytes.size == TOTAL_VOXELS) { "Invalid grid size" }

        var index = 0
        for (i in 0 until GRID_SIZE) {
            for (j in 0 until GRID_SIZE) {
                for (k in 0 until GRID_SIZE) {
                    for (l in 0 until GRID_SIZE) {
                        grid[i][j][k][l] = bytes[index++]
                    }
                }
            }
        }
    }
}
