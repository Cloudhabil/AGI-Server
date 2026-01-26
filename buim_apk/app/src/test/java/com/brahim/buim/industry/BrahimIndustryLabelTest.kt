/**
 * Unit Tests for Brahim Industry Label System
 * =============================================
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-26
 */

package com.brahim.buim.industry

import org.junit.Assert.*
import org.junit.Test

class BrahimIndustryLabelTest {

    // =========================================================================
    // Sector Tests
    // =========================================================================

    @Test
    fun `sector codes match Brahim sequence`() {
        val expectedCodes = listOf(27, 42, 60, 75, 97, 121, 136, 154, 172, 187)
        val actualCodes = Sector.values().map { it.code }
        assertEquals(expectedCodes, actualCodes)
    }

    @Test
    fun `sector Brahim indices are 1 to 10`() {
        val indices = Sector.values().map { it.brahimIndex }
        assertEquals((1..10).toList(), indices)
    }

    @Test
    fun `sector fromCode returns correct sector`() {
        assertEquals(Sector.ELECTRICAL, Sector.fromCode(27))
        assertEquals(Sector.ENERGY, Sector.fromCode(136))
        assertEquals(Sector.TRANSPORT, Sector.fromCode(187))
        assertNull(Sector.fromCode(999))
    }

    @Test
    fun `sector fromBrahimIndex returns correct sector`() {
        assertEquals(Sector.ELECTRICAL, Sector.fromBrahimIndex(1))
        assertEquals(Sector.ENERGY, Sector.fromBrahimIndex(7))
        assertNull(Sector.fromBrahimIndex(0))
        assertNull(Sector.fromBrahimIndex(11))
    }

    // =========================================================================
    // DataType Tests
    // =========================================================================

    @Test
    fun `dataType codes are 1 to 9`() {
        val codes = DataType.values().map { it.code }
        assertEquals((1..9).toList(), codes)
    }

    @Test
    fun `dataType fromCode returns correct type`() {
        assertEquals(DataType.SPECIFICATION, DataType.fromCode(1))
        assertEquals(DataType.FORMULA, DataType.fromCode(3))
        assertEquals(DataType.LEARNED, DataType.fromCode(9))
        assertNull(DataType.fromCode(0))
    }

    // =========================================================================
    // Source Tests
    // =========================================================================

    @Test
    fun `deterministic sources have codes below 600`() {
        Source.deterministicSources().forEach { source ->
            assertTrue("${source.name} should have code < 600", source.code < 600)
            assertTrue("${source.name} should be deterministic", source.isDeterministic)
        }
    }

    @Test
    fun `ML sources have codes 900+`() {
        Source.mlSources().forEach { source ->
            assertTrue("${source.name} should have code >= 900", source.code >= 900)
            assertFalse("${source.name} should not be deterministic", source.isDeterministic)
        }
    }

    @Test
    fun `source fromCode returns correct source`() {
        assertEquals(Source.IEC_STANDARD, Source.fromCode(100))
        assertEquals(Source.ML_PREDICTION, Source.fromCode(900))
        assertNull(Source.fromCode(555))
    }

    // =========================================================================
    // BIL Creation Tests
    // =========================================================================

    @Test
    fun `create BIL generates correct format`() {
        val bil = BrahimIndustryLabelFactory.create(
            sector = Sector.ELECTRICAL,
            dataType = DataType.SPECIFICATION,
            source = Source.IEC_STANDARD,
            itemId = 60617
        )

        assertTrue(bil.fullLabel.startsWith("BIL:27:1:100:60617"))
        assertEquals(Sector.ELECTRICAL, bil.sector)
        assertEquals(DataType.SPECIFICATION, bil.dataType)
        assertEquals(Source.IEC_STANDARD, bil.source)
        assertEquals(60617L, bil.itemId)
        assertTrue(bil.isDeterministic)
        assertNull(bil.warning)
    }

    @Test
    fun `ML-derived BIL has warning`() {
        val bil = BrahimIndustryLabelFactory.create(
            sector = Sector.ENERGY,
            dataType = DataType.LEARNED,
            source = Source.ML_PREDICTION,
            itemId = 12345
        )

        assertFalse(bil.isDeterministic)
        assertNotNull(bil.warning)
        assertTrue(bil.warning!!.contains("ML-derived"))
    }

    @Test
    fun `BIL confidence reflects source type`() {
        val iecBil = BrahimIndustryLabelFactory.create(
            Sector.ELECTRICAL, DataType.SPECIFICATION, Source.IEC_STANDARD, 1
        )
        assertEquals(1.0, iecBil.confidence, 0.001)

        val mfgBil = BrahimIndustryLabelFactory.create(
            Sector.ELECTRICAL, DataType.DATASHEET, Source.MANUFACTURER_SPEC, 1
        )
        assertEquals(0.99, mfgBil.confidence, 0.001)

        val mlBil = BrahimIndustryLabelFactory.create(
            Sector.ELECTRICAL, DataType.LEARNED, Source.ML_PREDICTION, 1
        )
        assertEquals(0.70, mlBil.confidence, 0.001)
    }

    // =========================================================================
    // BIL Parsing Tests
    // =========================================================================

    @Test
    fun `parse valid BIL string`() {
        val original = BrahimIndustryLabelFactory.create(
            Sector.MECHANICAL, DataType.FORMULA, Source.ENGINEERING_HANDBOOK, 286
        )

        val parsed = BrahimIndustryLabelFactory.parse(original.fullLabel)

        assertNotNull(parsed)
        assertEquals(original.sector, parsed!!.sector)
        assertEquals(original.dataType, parsed.dataType)
        assertEquals(original.source, parsed.source)
        assertEquals(original.itemId, parsed.itemId)
    }

    @Test
    fun `parse rejects invalid BIL string`() {
        assertNull(BrahimIndustryLabelFactory.parse("invalid"))
        assertNull(BrahimIndustryLabelFactory.parse("BIL:999:1:100:1-X"))  // Invalid sector
        assertNull(BrahimIndustryLabelFactory.parse("BIL:27:99:100:1-X"))  // Invalid dataType
    }

    @Test
    fun `verify returns true for valid BIL`() {
        val bil = BrahimIndustryLabelFactory.create(
            Sector.DIGITAL, DataType.SPECIFICATION, Source.IEEE_STANDARD, 80211
        )
        assertTrue(BrahimIndustryLabelFactory.verify(bil.fullLabel))
    }

    @Test
    fun `verify returns false for tampered BIL`() {
        val bil = BrahimIndustryLabelFactory.create(
            Sector.DIGITAL, DataType.SPECIFICATION, Source.IEEE_STANDARD, 80211
        )
        // Tamper with check digit
        val tampered = bil.fullLabel.dropLast(1) + "Z"
        assertFalse(BrahimIndustryLabelFactory.verify(tampered))
    }

    // =========================================================================
    // BIL Upgrade Tests
    // =========================================================================

    @Test
    fun `upgrade ML BIL to deterministic source`() {
        val mlBil = BrahimIndustryLabelFactory.create(
            Sector.ENERGY, DataType.SPECIFICATION, Source.ML_PREDICTION, 61215
        )
        assertFalse(mlBil.isDeterministic)

        val upgradedBil = BrahimIndustryLabelFactory.upgradeSource(mlBil, Source.IEC_STANDARD)

        assertTrue(upgradedBil.isDeterministic)
        assertEquals(Source.IEC_STANDARD, upgradedBil.source)
        assertEquals(mlBil.sector, upgradedBil.sector)
        assertEquals(mlBil.itemId, upgradedBil.itemId)
    }

    @Test(expected = IllegalArgumentException::class)
    fun `upgrade rejects non-deterministic target`() {
        val bil = BrahimIndustryLabelFactory.create(
            Sector.ENERGY, DataType.SPECIFICATION, Source.ML_PREDICTION, 1
        )
        BrahimIndustryLabelFactory.upgradeSource(bil, Source.ML_CLASSIFICATION)
    }

    // =========================================================================
    // Helper Function Tests
    // =========================================================================

    @Test
    fun `standardToBIL creates correct BIL`() {
        val bil = standardToBIL("IEC", "60617", Sector.ELECTRICAL)

        assertEquals(Sector.ELECTRICAL, bil.sector)
        assertEquals(DataType.SPECIFICATION, bil.dataType)
        assertEquals(Source.IEC_STANDARD, bil.source)
        assertTrue(bil.isDeterministic)
    }

    @Test
    fun `mlClassifiedToBIL is flagged correctly`() {
        val bil = mlClassifiedToBIL(Sector.MECHANICAL, DataType.DATASHEET, 12345)

        assertEquals(Source.ML_CLASSIFICATION, bil.source)
        assertFalse(bil.isDeterministic)
        assertNotNull(bil.warning)
    }

    // =========================================================================
    // Cantor Pairing Tests
    // =========================================================================

    @Test
    fun `different inputs produce different Brahim numbers`() {
        val bil1 = BrahimIndustryLabelFactory.create(Sector.ELECTRICAL, DataType.SPECIFICATION, Source.IEC_STANDARD, 1)
        val bil2 = BrahimIndustryLabelFactory.create(Sector.ELECTRICAL, DataType.SPECIFICATION, Source.IEC_STANDARD, 2)
        val bil3 = BrahimIndustryLabelFactory.create(Sector.MECHANICAL, DataType.SPECIFICATION, Source.IEC_STANDARD, 1)

        assertNotEquals(bil1.brahimNumber, bil2.brahimNumber)
        assertNotEquals(bil1.brahimNumber, bil3.brahimNumber)
        assertNotEquals(bil2.brahimNumber, bil3.brahimNumber)
    }

    @Test
    fun `same inputs produce same Brahim number`() {
        val bil1 = BrahimIndustryLabelFactory.create(Sector.ENERGY, DataType.FORMULA, Source.ENGINEERING_HANDBOOK, 100)
        val bil2 = BrahimIndustryLabelFactory.create(Sector.ENERGY, DataType.FORMULA, Source.ENGINEERING_HANDBOOK, 100)

        assertEquals(bil1.brahimNumber, bil2.brahimNumber)
        assertEquals(bil1.fullLabel, bil2.fullLabel)
    }
}
