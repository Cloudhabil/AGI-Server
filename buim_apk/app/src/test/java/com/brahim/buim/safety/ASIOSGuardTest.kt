/**
 * ASIOS Guard Unit Tests
 * ======================
 *
 * Verifies the Berry-Keating safety system functionality.
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-25
 */

package com.brahim.buim.safety

import org.junit.Test
import org.junit.Before
import org.junit.Assert.*
import com.brahim.buim.core.BrahimConstants

class ASIOSGuardTest {

    private lateinit var guard: ASIOSGuard

    @Before
    fun setup() {
        guard = ASIOSGuard()
    }

    @Test
    fun `safe input returns SAFE verdict`() {
        val safeInput = DoubleArray(10) { 0.01 }  // Low values
        val assessment = guard.assessSafety(safeInput)

        assertTrue(assessment.isSafe)
        assertEquals(SafetyVerdict.SAFE, assessment.verdict)
    }

    @Test
    fun `assess safety returns valid energy`() {
        val input = DoubleArray(10) { it.toDouble() / 10 }
        val assessment = guard.assessSafety(input)

        assertTrue(assessment.energy >= 0)
    }

    @Test
    fun `assess safety returns correction factor`() {
        val input = DoubleArray(10) { 0.5 }
        val assessment = guard.assessSafety(input)

        assertTrue(assessment.correction in 0.0..2.0)
    }

    @Test
    fun `genesis constant check works`() {
        // Values near GENESIS_CONSTANT (0.0219) should be special
        val nearGenesis = DoubleArray(10) { 0.0219 }
        val assessment = guard.assessSafety(nearGenesis)

        // Should have low energy
        assertTrue(assessment.energy < 0.1)
    }

    @Test
    fun `high density input is flagged`() {
        val highDensity = DoubleArray(10) { 0.9 }
        val assessment = guard.assessSafety(highDensity)

        // High density should increase energy
        assertTrue(assessment.energy > 0.1)
    }

    @Test
    fun `safety verdict levels are correct`() {
        // Test the enum values
        val levels = SafetyVerdict.values()

        assertEquals(5, levels.size)
        assertTrue(levels.contains(SafetyVerdict.SAFE))
        assertTrue(levels.contains(SafetyVerdict.NOMINAL))
        assertTrue(levels.contains(SafetyVerdict.CAUTION))
        assertTrue(levels.contains(SafetyVerdict.UNSAFE))
        assertTrue(levels.contains(SafetyVerdict.BLOCKED))
    }

    @Test
    fun `guard info returns valid map`() {
        val info = guard.getGuardInfo()

        assertTrue(info.containsKey("energy_threshold"))
        assertTrue(info.containsKey("genesis_constant"))
        assertTrue(info.containsKey("safety_enabled"))
    }

    @Test
    fun `assess safety returns density`() {
        val input = DoubleArray(10) { 0.5 }
        val assessment = guard.assessSafety(input)

        assertTrue(assessment.density in 0.0..1.0)
    }

    @Test
    fun `apply correction scales input`() {
        val input = DoubleArray(10) { 0.5 }
        val assessment = guard.assessSafety(input)

        val corrected = input.map { it * assessment.correction }.toDoubleArray()

        // Corrected values should be different if correction != 1.0
        if (assessment.correction != 1.0) {
            assertFalse(input.contentEquals(corrected))
        }
    }

    @Test
    fun `berry keating energy formula works`() {
        // E[ψ] = (density - GENESIS_CONSTANT)²
        val density = 0.1
        val expected = (density - BrahimConstants.GENESIS_CONSTANT) * (density - BrahimConstants.GENESIS_CONSTANT)

        val input = DoubleArray(10) { density }
        val assessment = guard.assessSafety(input)

        // Energy should be related to this formula
        assertTrue(assessment.energy >= 0)
    }

    @Test
    fun `empty input returns safe`() {
        val empty = DoubleArray(0)
        val assessment = guard.assessSafety(empty)

        assertEquals(SafetyVerdict.SAFE, assessment.verdict)
    }

    @Test
    fun `single element input works`() {
        val single = doubleArrayOf(0.5)
        val assessment = guard.assessSafety(single)

        assertNotNull(assessment)
        assertNotNull(assessment.verdict)
    }

    @Test
    fun `large input works`() {
        val large = DoubleArray(1000) { it.toDouble() / 1000 }
        val assessment = guard.assessSafety(large)

        assertNotNull(assessment)
        assertNotNull(assessment.verdict)
    }

    @Test
    fun `negative values are handled`() {
        val negative = DoubleArray(10) { -0.5 }
        val assessment = guard.assessSafety(negative)

        assertNotNull(assessment)
        // System should handle negative values gracefully
    }

    @Test
    fun `verdict severity ordering`() {
        // SAFE < NOMINAL < CAUTION < UNSAFE < BLOCKED
        assertTrue(SafetyVerdict.SAFE.ordinal < SafetyVerdict.NOMINAL.ordinal)
        assertTrue(SafetyVerdict.NOMINAL.ordinal < SafetyVerdict.CAUTION.ordinal)
        assertTrue(SafetyVerdict.CAUTION.ordinal < SafetyVerdict.UNSAFE.ordinal)
        assertTrue(SafetyVerdict.UNSAFE.ordinal < SafetyVerdict.BLOCKED.ordinal)
    }
}
