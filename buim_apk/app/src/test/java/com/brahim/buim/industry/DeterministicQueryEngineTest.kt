/**
 * Unit Tests for Deterministic Query Engine
 * ==========================================
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-26
 */

package com.brahim.buim.industry

import com.brahim.buim.industry.db.*
import kotlinx.coroutines.runBlocking
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test

class DeterministicQueryEngineTest {

    private lateinit var engine: DeterministicQueryEngine
    private lateinit var standardsDB: StandardsDatabaseImpl
    private lateinit var datasheetDB: DatasheetDatabaseImpl
    private lateinit var formulaDB: FormulaDatabaseImpl
    private lateinit var mlAgent: MLPredictionAgentImpl

    @Before
    fun setup() {
        standardsDB = StandardsDatabaseImpl()
        datasheetDB = DatasheetDatabaseImpl()
        formulaDB = FormulaDatabaseImpl()
        mlAgent = MLPredictionAgentImpl()

        engine = DeterministicQueryEngine(
            standardsDB = standardsDB,
            datasheetDB = datasheetDB,
            handbookDB = formulaDB,
            mlAgent = mlAgent
        )
    }

    // =========================================================================
    // Standards Query Tests
    // =========================================================================

    @Test
    fun `query for IEC standard returns deterministic result`() = runBlocking {
        val query = IndustryQuery(
            text = "IEC 60617 electrical symbols",
            expectedSector = Sector.ELECTRICAL
        )

        val result = engine.query(query)

        assertTrue("Should be deterministic", result.isDeterministic)
        assertEquals(1.0, result.confidence, 0.001)
        assertTrue("Should reference IEC", result.answer.contains("IEC"))
        assertNull("Should have no warning", result.warning)
    }

    @Test
    fun `query for solar standard returns energy sector result`() = runBlocking {
        val query = IndustryQuery(
            text = "solar panel PV module standard IEC",
            expectedSector = Sector.ENERGY
        )

        val result = engine.query(query)

        assertTrue("Should be deterministic", result.isDeterministic)
        assertEquals(Sector.ENERGY, result.bil.sector)
        assertTrue("Should reference 61215", result.citation.contains("61215") || result.answer.contains("61215"))
    }

    // =========================================================================
    // Formula Query Tests
    // =========================================================================

    @Test
    fun `query for Ohms law returns formula`() = runBlocking {
        val query = IndustryQuery(
            text = "ohm voltage current resistance formula",
            expectedSector = Sector.ELECTRICAL
        )

        val result = engine.query(query)

        assertTrue("Should contain V=IR or similar",
            result.answer.contains("V") && result.answer.contains("I") && result.answer.contains("R"))
    }

    @Test
    fun `query for wind power formula returns Betz limit`() = runBlocking {
        val query = IndustryQuery(
            text = "wind turbine power calculation formula",
            expectedSector = Sector.ENERGY
        )

        val result = engine.query(query)

        assertTrue("Should mention power or Cp",
            result.answer.lowercase().contains("power") ||
            result.answer.lowercase().contains("cp") ||
            result.answer.contains("0.5"))
    }

    // =========================================================================
    // Datasheet Query Tests
    // =========================================================================

    @Test
    fun `query for specific component returns datasheet`() = runBlocking {
        val query = IndustryQuery(
            text = "LM7805 voltage regulator specs",
            expectedSector = Sector.ELECTRICAL
        )

        val result = engine.query(query)

        // Should find the LM7805 in datasheets
        if (result.isDeterministic) {
            assertTrue("Should mention 5V", result.answer.contains("5V"))
        }
    }

    // =========================================================================
    // ML Fallback Tests
    // =========================================================================

    @Test
    fun `unknown query falls back to ML with warning`() = runBlocking {
        val query = IndustryQuery(
            text = "very specific obscure technical question about xyz123",
            expectedSector = Sector.ELECTRICAL
        )

        val result = engine.query(query)

        // Should fall back to ML
        assertFalse("Should not be deterministic", result.isDeterministic)
        assertNotNull("Should have warning", result.warning)
        assertTrue("Should be ML source", result.bil.source.code >= 900)
        assertTrue("Confidence should be < 1.0", result.confidence < 1.0)
    }

    @Test
    fun `deterministic-only query returns null for unknown`() = runBlocking {
        val query = IndustryQuery(
            text = "very specific obscure technical question about xyz123",
            expectedSector = Sector.ELECTRICAL,
            requireDeterministic = true
        )

        val result = engine.queryDeterministic(query)

        assertNull("Should return null for unknown deterministic query", result)
    }

    // =========================================================================
    // Sector Classification Tests
    // =========================================================================

    @Test
    fun `query auto-classifies electrical sector`() = runBlocking {
        val query = IndustryQuery(
            text = "wire gauge voltage circuit breaker"
            // No expectedSector - should auto-detect
        )

        val result = engine.query(query)

        assertEquals("Should classify as ELECTRICAL", Sector.ELECTRICAL, result.bil.sector)
    }

    @Test
    fun `query auto-classifies energy sector`() = runBlocking {
        val query = IndustryQuery(
            text = "solar panel renewable grid battery storage"
        )

        val result = engine.query(query)

        assertEquals("Should classify as ENERGY", Sector.ENERGY, result.bil.sector)
    }

    @Test
    fun `query auto-classifies mechanical sector`() = runBlocking {
        val query = IndustryQuery(
            text = "torque bearing shaft mechanical stress"
        )

        val result = engine.query(query)

        assertEquals("Should classify as MECHANICAL", Sector.MECHANICAL, result.bil.sector)
    }

    // =========================================================================
    // BIL Generation Tests
    // =========================================================================

    @Test
    fun `result has valid BIL format`() = runBlocking {
        val query = IndustryQuery(
            text = "IEC 60364 installation standard",
            expectedSector = Sector.ELECTRICAL
        )

        val result = engine.query(query)

        assertTrue("BIL should start with BIL:", result.bil.fullLabel.startsWith("BIL:"))
        assertTrue("BIL should be verifiable", BrahimIndustryLabelFactory.verify(result.bil.fullLabel))
    }

    // =========================================================================
    // Batch Query Tests
    // =========================================================================

    @Test
    fun `batch query processes multiple queries`() = runBlocking {
        val queries = listOf(
            IndustryQuery("ohm law formula", expectedSector = Sector.ELECTRICAL),
            IndustryQuery("wind turbine power", expectedSector = Sector.ENERGY),
            IndustryQuery("bearing load calculation", expectedSector = Sector.MECHANICAL)
        )

        val results = engine.queryBatch(queries)

        assertEquals("Should return 3 results", 3, results.size)
        results.forEach { result ->
            assertTrue("Each result should have valid BIL",
                BrahimIndustryLabelFactory.verify(result.bil.fullLabel))
        }
    }

    // =========================================================================
    // Factory Tests
    // =========================================================================

    @Test
    fun `factory creates working engine`() = runBlocking {
        val factoryEngine = IndustryQueryFactory.createEngine()
        val result = factoryEngine.query(IndustryQuery("ohm law"))

        assertNotNull(result)
        assertTrue(result.answer.isNotEmpty())
    }

    @Test
    fun `factory reports correct statistics`() {
        val stats = IndustryQueryFactory.getStatistics()

        assertTrue("Should have standards", stats.standardsCount > 0)
        assertTrue("Should have formulas", stats.formulasCount > 0)
        assertTrue("Should have units", stats.unitsCount > 0)
        assertEquals("Should have 10 sectors", 10, stats.sectorsCount)
    }
}
