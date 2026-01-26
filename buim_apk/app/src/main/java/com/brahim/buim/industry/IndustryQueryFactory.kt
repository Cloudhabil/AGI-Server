/**
 * Industry Query Factory
 * =======================
 *
 * Factory to create pre-configured DeterministicQueryEngine
 * with all embedded databases connected.
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-26
 */

package com.brahim.buim.industry

import com.brahim.buim.industry.db.*

/**
 * Factory for creating fully configured query engines
 */
object IndustryQueryFactory {

    // Singleton instances of databases
    private val standardsDB = StandardsDatabaseImpl()
    private val datasheetDB = DatasheetDatabaseImpl()
    private val formulaDB = FormulaDatabaseImpl()
    private val mlAgent = MLPredictionAgentImpl()

    /**
     * Create a fully configured DeterministicQueryEngine
     */
    fun createEngine(): DeterministicQueryEngine {
        return DeterministicQueryEngine(
            standardsDB = standardsDB,
            datasheetDB = datasheetDB,
            handbookDB = formulaDB,
            mlAgent = mlAgent
        )
    }

    /**
     * Get direct access to standards database
     */
    fun getStandardsDB(): StandardsDatabaseImpl = standardsDB

    /**
     * Get direct access to datasheet database
     */
    fun getDatasheetDB(): DatasheetDatabaseImpl = datasheetDB

    /**
     * Get direct access to formula database
     */
    fun getFormulaDB(): FormulaDatabaseImpl = formulaDB

    /**
     * Get database statistics
     */
    fun getStatistics(): DatabaseStatistics {
        return DatabaseStatistics(
            standardsCount = standardsDB.getStandardCount(),
            datasheetsCount = datasheetDB.getDatasheetCount(),
            formulasCount = formulaDB.getFormulaCount(),
            unitsCount = UnitConversionTable.getUnitCount(),
            sectorsCount = Sector.values().size,
            dataTypesCount = DataType.values().size,
            sourcesCount = Source.values().size
        )
    }

    /**
     * Quick query helper - creates engine and runs query
     */
    suspend fun query(text: String, sector: Sector? = null): QueryResult {
        val engine = createEngine()
        val query = IndustryQuery(
            text = text,
            expectedSector = sector
        )
        return engine.query(query)
    }

    /**
     * Quick deterministic-only query
     */
    suspend fun queryDeterministic(text: String, sector: Sector? = null): QueryResult? {
        val engine = createEngine()
        val query = IndustryQuery(
            text = text,
            expectedSector = sector,
            requireDeterministic = true
        )
        return engine.queryDeterministic(query)
    }

    /**
     * Convert units
     */
    fun convertUnits(value: Double, from: String, to: String): Double? {
        return UnitConversionTable.convert(value, from, to)
    }

    /**
     * Convert temperature
     */
    fun convertTemperature(value: Double, from: String, to: String): Double? {
        return UnitConversionTable.convertTemperature(value, from, to)
    }

    /**
     * Create a BIL for a standard reference
     */
    fun createStandardBIL(standardBody: String, standardNumber: String, sector: Sector): BrahimIndustryLabel {
        return standardToBIL(standardBody, standardNumber, sector)
    }
}

/**
 * Database statistics
 */
data class DatabaseStatistics(
    val standardsCount: Int,
    val datasheetsCount: Int,
    val formulasCount: Int,
    val unitsCount: Int,
    val sectorsCount: Int,
    val dataTypesCount: Int,
    val sourcesCount: Int
) {
    val totalEntries: Int get() = standardsCount + datasheetsCount + formulasCount + unitsCount

    override fun toString(): String = """
        |BUIM Industry Database Statistics
        |==================================
        |Standards:   $standardsCount entries
        |Datasheets:  $datasheetsCount entries
        |Formulas:    $formulasCount entries
        |Units:       $unitsCount conversions
        |Sectors:     $sectorsCount defined
        |Data Types:  $dataTypesCount defined
        |Sources:     $sourcesCount defined
        |----------------------------------
        |Total:       $totalEntries entries
    """.trimMargin()
}
