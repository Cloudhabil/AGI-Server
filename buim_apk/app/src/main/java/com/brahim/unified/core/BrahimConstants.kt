package com.brahim.unified.core

import kotlin.math.sqrt
import kotlin.math.pow
import kotlin.math.exp
import kotlin.math.abs
import kotlin.math.PI

/**
 * Brahim Mathematical Constants and Calculations
 * Foundation for all 88 applications in the Brahim Unified APK.
 * Author: Elias Oulad Brahim
 */
object BrahimConstants {
    
    // FUNDAMENTAL CONSTANTS
    val PHI: Double = (1.0 + sqrt(5.0)) / 2.0
    val PHI_INV: Double = 1.0 / PHI
    val ALPHA_WORMHOLE: Double = 1.0 / (PHI * PHI)
    val BETA_SECURITY: Double = sqrt(5.0) - 2.0
    val GAMMA_DAMPING: Double = 1.0 / PHI.pow(4)
    const val GENESIS_CONSTANT: Double = 0.0219
    const val SUM_CONSTANT: Int = 214
    const val CENTER: Int = 107
    
    // BRAHIM SEQUENCE (Corrected 2026-01-26 - full mirror symmetry)
    val SEQUENCE: IntArray = intArrayOf(27, 42, 60, 75, 97, 117, 139, 154, 172, 187)
    val SEQUENCE_ORIGINAL: IntArray = intArrayOf(27, 42, 60, 75, 97, 121, 136, 154, 172, 187)  // Historical

    fun B(n: Int): Int = if (n in 1..10) SEQUENCE[n - 1] else 0
    fun B_original(n: Int): Int = if (n in 1..10) SEQUENCE_ORIGINAL[n - 1] else 0
    fun mirror(x: Double): Double = SUM_CONSTANT - x
    fun mirror(x: Int): Int = SUM_CONSTANT - x
    fun isMirrorPair(a: Int, b: Int): Boolean = (a + b) == SUM_CONSTANT
    
    // PHYSICS CALCULATORS
    fun fineStructureInverse(): Double = B(7) + 1.0 + 1.0 / (B(1) + 1.0)
    fun weinbergAngle(): Double = B(1).toDouble() / (B(7) - 19).toDouble()
    fun strongCouplingInverse(): Double = (B(2) - B(1)).toDouble() / 2.0 + 1.0
    fun weakCouplingInverse(): Double = (B(1) + B(2)).toDouble() / 2.0 - 3.0
    fun muonElectronRatio(): Double = B(4).toDouble().pow(2) / B(7).toDouble() * 5.0
    fun protonElectronRatio(): Double = (B(5) + B(10)).toDouble() * PHI * 4.0
    fun hubbleConstant(): Double = (B(2) * B(9)).toDouble() / SUM_CONSTANT * 2.0
    fun couplingHierarchy(): Double = (B(7) * mirror(B(7))).toDouble().pow(9)
    fun massHierarchy(): Double = (B(1) * B(10)).toDouble().pow(6)
    
    fun yangMillsMassGap(): Double {
        // Uses original sequence with broken symmetry (magnitude = 7)
        val magnitude = deviationMagnitude_original()
        return (magnitude.toDouble() / CENTER) * 3000 * 8
    }
    
    // COSMOLOGY
    fun darkMatterPercent(): Double = B(1).toDouble() / 100.0
    fun darkEnergyPercent(): Double = 31.0 / 45.0
    fun normalMatterPercent(): Double = PHI.pow(5) / 200.0
    fun universeAge(): Double = 977.8 / hubbleConstant()
    
    // RESONANCE (ASI-OS)
    fun resonance(distances: List<Double>, timeDiffs: List<Double>, epsilon: Double = 1e-6, lambda: Double = GENESIS_CONSTANT): Double {
        var total = 0.0
        for (i in distances.indices) {
            val distTerm = 1.0 / (distances[i] * distances[i] + epsilon)
            val decayTerm = exp(-lambda * timeDiffs[i])
            total += distTerm * decayTerm
        }
        return total
    }
    
    fun axiologicalAlignment(observedResonance: Double): Double = abs(observedResonance - GENESIS_CONSTANT)
    
    // SYMMETRY (Symmetric sequence: all deltas = 0)
    fun delta4(): Int = (B(4) + B(7)) - SUM_CONSTANT  // 75 + 139 - 214 = 0
    fun delta5(): Int = (B(5) + B(6)) - SUM_CONSTANT  // 97 + 117 - 214 = 0
    fun deviationMagnitude(): Int = abs(delta4()) + abs(delta5())
    fun deviationProduct(): Int = delta4() * delta5()
    fun netAsymmetry(): Int = delta4() + delta5()

    // SYMMETRY (Original sequence: broken symmetry for consciousness studies)
    fun delta4_original(): Int = (B_original(4) + B_original(7)) - SUM_CONSTANT  // 75 + 136 - 214 = -3
    fun delta5_original(): Int = (B_original(5) + B_original(6)) - SUM_CONSTANT  // 97 + 121 - 214 = +4
    fun deviationMagnitude_original(): Int = abs(delta4_original()) + abs(delta5_original())  // = 7
    fun netAsymmetry_original(): Int = delta4_original() + delta5_original()  // = +1 (observer signature)
    
    // VERIFICATION
    fun verifyMirrorSymmetry(): Boolean = (1..3).all { B(it) + B(11 - it) == SUM_CONSTANT }
    fun verifyAlphaOmega(): Boolean = B(10) == 7 * B(1) - 2
    fun verifyBekensteinHawking(): Boolean = CENTER == 4 * B(1) - 1
    fun verifyBetaIdentities(): Boolean = abs(BETA_SECURITY * BETA_SECURITY + 4 * BETA_SECURITY - 1) < 1e-10
    
    // UTILITY
    fun formatScientific(value: Double): String = if (abs(value) > 1e6 || abs(value) < 1e-4) String.format("%.3e", value) else String.format("%.6f", value)
    
    fun accuracy(computed: Double, experimental: Double): Pair<Double, String> {
        val deviation = abs(computed - experimental) / experimental
        return if (deviation < 0.001) Pair(deviation * 1e6, "ppm") else Pair(deviation * 100, "%")
    }
}
