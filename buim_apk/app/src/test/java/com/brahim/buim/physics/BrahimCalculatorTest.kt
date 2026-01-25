/**
 * Brahim Calculator Unit Tests
 * ============================
 *
 * Verifies physics constants derived from the Brahim Sequence.
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-25
 */

package com.brahim.buim.physics

import org.junit.Test
import org.junit.Assert.*
import kotlin.math.abs

class BrahimCalculatorTest {

    // CODATA values for comparison
    companion object {
        const val CODATA_ALPHA_INVERSE = 137.035999084
        const val CODATA_WEINBERG = 0.23122
        const val CODATA_MUON_ELECTRON = 206.7682830
        const val CODATA_PROTON_ELECTRON = 1836.15267343
        const val CODATA_HUBBLE = 67.4  // km/s/Mpc
    }

    @Test
    fun `fine structure constant is within 2 percent of CODATA`() {
        val result = BrahimCalculator.fineStructureConstant()
        val error = abs(result.value - CODATA_ALPHA_INVERSE) / CODATA_ALPHA_INVERSE * 100

        assertTrue("Fine structure constant error: $error%", error < 2.0)
        assertEquals("α⁻¹", result.symbol)
        assertEquals("dimensionless", result.unit)
    }

    @Test
    fun `weinberg angle is within 1 percent of CODATA`() {
        val result = BrahimCalculator.weinbergAngle()
        val error = abs(result.value - CODATA_WEINBERG) / CODATA_WEINBERG * 100

        assertTrue("Weinberg angle error: $error%", error < 1.0)
        assertEquals("sin²θ_W", result.symbol)
    }

    @Test
    fun `muon electron ratio is within 1 percent of CODATA`() {
        val result = BrahimCalculator.muonElectronRatio()
        val error = abs(result.value - CODATA_MUON_ELECTRON) / CODATA_MUON_ELECTRON * 100

        assertTrue("Muon-electron ratio error: $error%", error < 1.0)
        assertEquals("m_μ/m_e", result.symbol)
    }

    @Test
    fun `proton electron ratio is within 1 percent of CODATA`() {
        val result = BrahimCalculator.protonElectronRatio()
        val error = abs(result.value - CODATA_PROTON_ELECTRON) / CODATA_PROTON_ELECTRON * 100

        assertTrue("Proton-electron ratio error: $error%", error < 1.0)
        assertEquals("m_p/m_e", result.symbol)
    }

    @Test
    fun `hubble constant is within 5 percent of observations`() {
        val result = BrahimCalculator.hubbleConstant()
        val error = abs(result.value - CODATA_HUBBLE) / CODATA_HUBBLE * 100

        assertTrue("Hubble constant error: $error%", error < 5.0)
        assertEquals("H₀", result.symbol)
        assertEquals("km/s/Mpc", result.unit)
    }

    @Test
    fun `cosmic fractions sum to 1`() {
        val result = BrahimCalculator.cosmicFractions()
        val total = result.darkMatterFraction + result.darkEnergyFraction + result.normalMatterFraction

        assertEquals(1.0, total, 0.01)
    }

    @Test
    fun `dark energy is dominant fraction`() {
        val result = BrahimCalculator.cosmicFractions()

        assertTrue(result.darkEnergyFraction > result.darkMatterFraction)
        assertTrue(result.darkMatterFraction > result.normalMatterFraction)
    }

    @Test
    fun `yang mills mass gap is positive`() {
        val result = BrahimCalculator.yangMillsMassGap()

        assertTrue(result.massGap > 0)
        assertTrue(result.lambdaQCD > 0)
        assertTrue(result.derivationChain.isNotEmpty())
    }

    @Test
    fun `yang mills hypotheses are verified`() {
        val result = BrahimCalculator.yangMillsMassGap()

        assertTrue(result.hypotheses["H2: Mass gap > 0"] == true)
        assertTrue(result.hypotheses["H3: Gap ~ λ_QCD"] == true)
    }

    @Test
    fun `mirror operator preserves sum`() {
        val x = 42
        val mirrored = BrahimCalculator.mirror(x)

        assertEquals(214, x + mirrored)
    }

    @Test
    fun `mirror pairs are symmetric`() {
        val pairs = BrahimCalculator.getMirrorPairs()

        for ((a, b) in pairs) {
            assertEquals(214, a + b)
        }
    }

    @Test
    fun `verify mirror symmetry returns valid map`() {
        val result = BrahimCalculator.verifyMirrorSymmetry()

        assertTrue(result["all_conserved"] as Boolean)
        assertEquals(214, result["sum_constant"])
        assertEquals(107, result["center"])
    }

    @Test
    fun `getAllConstants returns all physics constants`() {
        val constants = BrahimCalculator.getAllConstants()

        assertTrue(constants.isNotEmpty())
        assertTrue(constants.size >= 5)

        // Verify all have names
        for (constant in constants) {
            assertTrue(constant.name.isNotEmpty())
            assertTrue(constant.symbol.isNotEmpty())
        }
    }

    @Test
    fun `verifyAllConstants shows reasonable accuracy`() {
        val verification = BrahimCalculator.verifyAllConstants()

        for ((name, data) in verification) {
            val error = data["error"] as Double
            // All should be within 10% (generous for derived constants)
            assertTrue("$name has error $error%", error < 10.0)
        }
    }

    @Test
    fun `getSequence returns valid sequence info`() {
        val info = BrahimCalculator.getSequence()

        assertTrue(info.containsKey("sequence"))
        assertTrue(info.containsKey("sum"))
        assertTrue(info.containsKey("center"))
        assertTrue(info.containsKey("phi"))
        assertTrue(info.containsKey("mirror_pairs"))
    }
}
