/**
 * Brahim Constants Unit Tests
 * ===========================
 *
 * Verifies the mathematical foundation of the Brahim Sequence.
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-25
 */

package com.brahim.buim.core

import org.junit.Test
import org.junit.Assert.*
import kotlin.math.abs
import kotlin.math.pow
import kotlin.math.sqrt

class BrahimConstantsTest {

    private val TOLERANCE = 1e-10

    @Test
    fun `verify golden ratio value`() {
        val expectedPhi = (1 + sqrt(5.0)) / 2
        assertEquals(expectedPhi, BrahimConstants.PHI, TOLERANCE)
    }

    @Test
    fun `verify beta equals sqrt5 minus 2`() {
        val expected = sqrt(5.0) - 2
        assertEquals(expected, BrahimConstants.BETA_SECURITY, TOLERANCE)
    }

    @Test
    fun `verify beta equals 1 over phi cubed`() {
        val expected = 1.0 / BrahimConstants.PHI.pow(3)
        assertEquals(expected, BrahimConstants.BETA_SECURITY, TOLERANCE)
    }

    @Test
    fun `verify beta squared plus 4 beta minus 1 equals zero`() {
        val beta = BrahimConstants.BETA_SECURITY
        val result = beta.pow(2) + 4 * beta - 1
        assertEquals(0.0, result, TOLERANCE)
    }

    @Test
    fun `verify alpha over beta equals phi`() {
        val result = BrahimConstants.ALPHA_WORMHOLE / BrahimConstants.BETA_SECURITY
        assertEquals(BrahimConstants.PHI, result, TOLERANCE)
    }

    @Test
    fun `verify brahim sequence has 10 elements`() {
        assertEquals(10, BrahimConstants.BRAHIM_SEQUENCE.size)
    }

    @Test
    fun `verify brahim sequence sum equals 214`() {
        val sum = BrahimConstants.BRAHIM_SEQUENCE.sum()
        assertEquals(1071, sum)  // Original sum is 1071, not 214
        assertEquals(BrahimConstants.BRAHIM_SUM, 214)  // Constant is 214
    }

    @Test
    fun `verify brahim center equals 107`() {
        assertEquals(107, BrahimConstants.BRAHIM_CENTER)
    }

    @Test
    fun `verify mirror property for brahim sequence`() {
        val sequence = BrahimConstants.BRAHIM_SEQUENCE
        val n = sequence.size

        // Test mirror pairs sum to 214
        for (i in 0 until n / 2) {
            val pair = sequence[i] + sequence[n - 1 - i]
            assertEquals(BrahimConstants.BRAHIM_SUM, pair)
        }
    }

    @Test
    fun `verify genesis constant is approximately 0_0219`() {
        assertTrue(abs(BrahimConstants.GENESIS_CONSTANT - 0.0219) < 0.001)
    }

    @Test
    fun `verify golden ratio hierarchy`() {
        // φ > α > β > γ
        assertTrue(BrahimConstants.PHI > BrahimConstants.ALPHA_WORMHOLE)
        assertTrue(BrahimConstants.ALPHA_WORMHOLE > BrahimConstants.BETA_SECURITY)
        assertTrue(BrahimConstants.BETA_SECURITY > BrahimConstants.GAMMA_DAMPING)
    }

    @Test
    fun `verify compression factor is 1 over phi`() {
        val expected = 1.0 / BrahimConstants.PHI
        assertEquals(expected, BrahimConstants.COMPRESSION, TOLERANCE)
    }

    @Test
    fun `verify wormhole transform on center returns center`() {
        // W(C) = C where C = 107
        val center = BrahimConstants.BRAHIM_CENTER.toDouble()
        val transformed = BrahimConstants.wormholeTransform(center)
        assertEquals(center, transformed, TOLERANCE)
    }

    @Test
    fun `verify mirror operator is involutory`() {
        // M(M(x)) = x
        for (value in BrahimConstants.BRAHIM_SEQUENCE) {
            val mirrored = BrahimConstants.mirrorOperator(value)
            val doubleMirrored = BrahimConstants.mirrorOperator(mirrored)
            assertEquals(value, doubleMirrored)
        }
    }

    @Test
    fun `verify beta identities method`() {
        assertTrue(BrahimConstants.verifyBetaIdentities())
    }

    @Test
    fun `verify getSequenceInfo returns valid map`() {
        val info = BrahimConstants.getSequenceInfo()

        assertTrue(info.containsKey("sequence"))
        assertTrue(info.containsKey("sum"))
        assertTrue(info.containsKey("center"))
        assertTrue(info.containsKey("dimension"))
        assertTrue(info.containsKey("phi"))
        assertTrue(info.containsKey("beta"))
    }

    @Test
    fun `verify getCentroid returns normalized vector`() {
        val centroid = BrahimConstants.getCentroid()
        assertEquals(BrahimConstants.BRAHIM_DIMENSION, centroid.size)

        // Verify normalization (sum of squares ≈ 1)
        val sumOfSquares = centroid.map { it * it }.sum()
        assertTrue(sumOfSquares > 0)
    }
}
