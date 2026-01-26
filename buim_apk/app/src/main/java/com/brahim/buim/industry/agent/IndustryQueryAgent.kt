/**
 * Industry Query Agent - OpenAI Agents SDK Compatible
 * =====================================================
 *
 * Exposes the BIL/Industry Query system as an OpenAI agent.
 * Enables deterministic-first engineering knowledge lookup
 * through AI function calling.
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-26
 */

package com.brahim.buim.industry.agent

import com.brahim.buim.industry.*
import com.brahim.buim.industry.db.*
import com.brahim.buim.sdk.BOAAgent
import com.brahim.buim.sdk.BaseBOAAgent
import com.brahim.buim.sdk.FunctionSchema
import com.brahim.buim.sdk.AgentSolverResponse
import com.brahim.buim.sdk.AgentRegistry
import kotlinx.coroutines.runBlocking
import kotlinx.serialization.json.*

/**
 * OpenAI Function schemas for Industry Query Agent
 */
val INDUSTRY_QUERY_FUNCTIONS = listOf(
    FunctionSchema(
        name = "query_engineering_knowledge",
        description = "Query the deterministic-first engineering knowledge base. Returns standards, formulas, datasheets with source tracking.",
        parameters = mapOf(
            "type" to "object",
            "properties" to mapOf(
                "query" to mapOf(
                    "type" to "string",
                    "description" to "Engineering question or lookup (e.g., 'IEC 60617 symbols', 'ohm law formula', 'solar panel specifications')"
                ),
                "sector" to mapOf(
                    "type" to "string",
                    "enum" to listOf("ELECTRICAL", "MECHANICAL", "CHEMICAL", "DIGITAL", "AEROSPACE", "BIOMEDICAL", "ENERGY", "MATERIALS", "CONSTRUCTION", "TRANSPORT"),
                    "description" to "Industry sector (optional, auto-detected if not provided)"
                ),
                "deterministic_only" to mapOf(
                    "type" to "boolean",
                    "description" to "If true, only return results from verified sources (no ML predictions)"
                )
            ),
            "required" to listOf("query")
        )
    ),
    FunctionSchema(
        name = "lookup_standard",
        description = "Look up a specific engineering standard by reference (e.g., 'IEC 60617', 'ISO 286')",
        parameters = mapOf(
            "type" to "object",
            "properties" to mapOf(
                "reference" to mapOf(
                    "type" to "string",
                    "description" to "Standard reference (e.g., 'IEC 60617', 'ISO 9001', 'IEEE 802.3')"
                )
            ),
            "required" to listOf("reference")
        )
    ),
    FunctionSchema(
        name = "lookup_formula",
        description = "Look up an engineering formula by name or topic",
        parameters = mapOf(
            "type" to "object",
            "properties" to mapOf(
                "name" to mapOf(
                    "type" to "string",
                    "description" to "Formula name (e.g., 'Ohm\\'s Law', 'Solar Panel Output', 'Reynolds Number')"
                )
            ),
            "required" to listOf("name")
        )
    ),
    FunctionSchema(
        name = "lookup_datasheet",
        description = "Look up component datasheet by part number",
        parameters = mapOf(
            "type" to "object",
            "properties" to mapOf(
                "part_number" to mapOf(
                    "type" to "string",
                    "description" to "Component part number (e.g., 'LM7805', 'ESP32', 'IRFZ44N')"
                )
            ),
            "required" to listOf("part_number")
        )
    ),
    FunctionSchema(
        name = "convert_units",
        description = "Convert between engineering units",
        parameters = mapOf(
            "type" to "object",
            "properties" to mapOf(
                "value" to mapOf(
                    "type" to "number",
                    "description" to "Numeric value to convert"
                ),
                "from_unit" to mapOf(
                    "type" to "string",
                    "description" to "Source unit (e.g., 'kW', 'bar', 'ft', '°C')"
                ),
                "to_unit" to mapOf(
                    "type" to "string",
                    "description" to "Target unit (e.g., 'hp', 'psi', 'm', '°F')"
                )
            ),
            "required" to listOf("value", "from_unit", "to_unit")
        )
    ),
    FunctionSchema(
        name = "create_bil_label",
        description = "Create a Brahim Industry Label (BIL) for data classification with source tracking",
        parameters = mapOf(
            "type" to "object",
            "properties" to mapOf(
                "sector" to mapOf(
                    "type" to "string",
                    "enum" to listOf("ELECTRICAL", "MECHANICAL", "CHEMICAL", "DIGITAL", "AEROSPACE", "BIOMEDICAL", "ENERGY", "MATERIALS", "CONSTRUCTION", "TRANSPORT"),
                    "description" to "Industry sector"
                ),
                "data_type" to mapOf(
                    "type" to "string",
                    "enum" to listOf("SPECIFICATION", "DATASHEET", "FORMULA", "TABLE", "DIAGRAM", "PROCEDURE", "MEASUREMENT", "SIMULATION", "LEARNED"),
                    "description" to "Type of data"
                ),
                "source" to mapOf(
                    "type" to "string",
                    "enum" to listOf("IEC_STANDARD", "ISO_STANDARD", "DIN_STANDARD", "IEEE_STANDARD", "MANUFACTURER_SPEC", "ENGINEERING_HANDBOOK", "VALIDATED_SIMULATION", "PEER_REVIEWED", "ML_PREDICTION", "ML_CLASSIFICATION", "UNVERIFIED"),
                    "description" to "Data source"
                ),
                "item_id" to mapOf(
                    "type" to "integer",
                    "description" to "Unique item identifier"
                )
            ),
            "required" to listOf("sector", "data_type", "source", "item_id")
        )
    ),
    FunctionSchema(
        name = "verify_bil",
        description = "Verify a Brahim Industry Label string",
        parameters = mapOf(
            "type" to "object",
            "properties" to mapOf(
                "bil_string" to mapOf(
                    "type" to "string",
                    "description" to "BIL string to verify (e.g., 'BIL:27:1:100:60617-X')"
                )
            ),
            "required" to listOf("bil_string")
        )
    ),
    FunctionSchema(
        name = "get_database_stats",
        description = "Get statistics about the embedded knowledge base",
        parameters = mapOf(
            "type" to "object",
            "properties" to mapOf(),
            "required" to emptyList<String>()
        )
    )
)

/**
 * Industry Query Agent - Main Agent Implementation
 */
class IndustryQueryAgent : BaseBOAAgent() {

    override val name = "industry_query_agent"
    override val domain = "engineering"
    override val description = "Deterministic-first engineering knowledge lookup with BIL source tracking"
    override val capabilities = listOf(
        "Query engineering standards (IEC, ISO, IEEE, DIN)",
        "Look up engineering formulas",
        "Search component datasheets",
        "Convert engineering units",
        "Create and verify BIL labels",
        "Deterministic-first with ML fallback (flagged)"
    )

    private val queryEngine = IndustryQueryFactory.createEngine()
    private val standardsDB = IndustryQueryFactory.getStandardsDB()
    private val datasheetDB = IndustryQueryFactory.getDatasheetDB()
    private val formulaDB = IndustryQueryFactory.getFormulaDB()

    override suspend fun process(query: String): AgentSolverResponse {
        val startTime = System.currentTimeMillis()

        return try {
            val result = queryEngine.query(IndustryQuery(text = query))
            val executionTime = System.currentTimeMillis() - startTime

            AgentSolverResponse(
                success = true,
                result = mapOf(
                    "answer" to result.answer,
                    "bil" to result.bil.fullLabel,
                    "confidence" to result.confidence,
                    "is_deterministic" to result.isDeterministic,
                    "source" to result.bil.source.description,
                    "citation" to result.citation,
                    "warning" to result.warning
                ),
                error = null,
                executionTime = executionTime,
                metadata = mapOf(
                    "sector" to result.bil.sector.name,
                    "data_type" to result.bil.dataType.name
                )
            )
        } catch (e: Exception) {
            AgentSolverResponse(
                success = false,
                result = null,
                error = e.message,
                executionTime = System.currentTimeMillis() - startTime
            )
        }
    }

    override fun getOpenAISchema(): List<FunctionSchema> = INDUSTRY_QUERY_FUNCTIONS

    override fun canHandle(query: String): Boolean {
        val keywords = listOf(
            "standard", "iec", "iso", "ieee", "din",
            "formula", "calculate", "equation",
            "datasheet", "component", "specification",
            "convert", "unit",
            "bil", "label",
            "electrical", "mechanical", "energy", "solar", "wind"
        )
        return keywords.any { query.lowercase().contains(it) }
    }

    /**
     * Execute a specific function by name (OpenAI function calling)
     */
    fun executeFunction(name: String, arguments: Map<String, Any?>): Map<String, Any?> {
        return when (name) {
            "query_engineering_knowledge" -> executeQueryKnowledge(arguments)
            "lookup_standard" -> executeLookupStandard(arguments)
            "lookup_formula" -> executeLookupFormula(arguments)
            "lookup_datasheet" -> executeLookupDatasheet(arguments)
            "convert_units" -> executeConvertUnits(arguments)
            "create_bil_label" -> executeCreateBil(arguments)
            "verify_bil" -> executeVerifyBil(arguments)
            "get_database_stats" -> executeGetStats()
            else -> mapOf("error" to "Unknown function: $name")
        }
    }

    // =========================================================================
    // Function Implementations
    // =========================================================================

    private fun executeQueryKnowledge(args: Map<String, Any?>): Map<String, Any?> {
        val queryText = args["query"] as? String ?: return mapOf("error" to "query required")
        val sectorName = args["sector"] as? String
        val deterministicOnly = args["deterministic_only"] as? Boolean ?: false

        val sector = sectorName?.let {
            try { Sector.valueOf(it) } catch (e: Exception) { null }
        }

        val query = IndustryQuery(
            text = queryText,
            expectedSector = sector,
            requireDeterministic = deterministicOnly
        )

        return runBlocking {
            val result = queryEngine.query(query)
            mapOf(
                "answer" to result.answer,
                "bil" to result.bil.fullLabel,
                "confidence" to result.confidence,
                "is_deterministic" to result.isDeterministic,
                "source" to result.bil.source.description,
                "citation" to result.citation,
                "warning" to result.warning,
                "sector" to result.bil.sector.name,
                "data_type" to result.bil.dataType.name
            )
        }
    }

    private fun executeLookupStandard(args: Map<String, Any?>): Map<String, Any?> {
        val reference = args["reference"] as? String ?: return mapOf("error" to "reference required")

        return runBlocking {
            val hit = standardsDB.getByReference(reference)
            if (hit != null) {
                mapOf(
                    "found" to true,
                    "reference" to reference,
                    "value" to hit.value,
                    "source" to hit.source.description,
                    "citation" to hit.citation,
                    "is_deterministic" to hit.source.isDeterministic
                )
            } else {
                mapOf(
                    "found" to false,
                    "reference" to reference,
                    "message" to "Standard not found in database"
                )
            }
        }
    }

    private fun executeLookupFormula(args: Map<String, Any?>): Map<String, Any?> {
        val name = args["name"] as? String ?: return mapOf("error" to "name required")

        val formula = formulaDB.getFormulaDetails(name)
        return if (formula != null) {
            mapOf(
                "found" to true,
                "name" to formula.name,
                "formula" to formula.formula,
                "description" to formula.description,
                "variables" to formula.variables,
                "example" to formula.example,
                "sector" to formula.sector.name
            )
        } else {
            mapOf(
                "found" to false,
                "name" to name,
                "message" to "Formula not found"
            )
        }
    }

    private fun executeLookupDatasheet(args: Map<String, Any?>): Map<String, Any?> {
        val partNumber = args["part_number"] as? String ?: return mapOf("error" to "part_number required")

        val datasheet = datasheetDB.getDatasheetDetails(partNumber)
        return if (datasheet != null) {
            mapOf(
                "found" to true,
                "part_number" to datasheet.partNumber,
                "manufacturer" to datasheet.manufacturer,
                "description" to datasheet.description,
                "category" to datasheet.category,
                "specs" to datasheet.specs,
                "sector" to datasheet.sector.name
            )
        } else {
            mapOf(
                "found" to false,
                "part_number" to partNumber,
                "message" to "Datasheet not found"
            )
        }
    }

    private fun executeConvertUnits(args: Map<String, Any?>): Map<String, Any?> {
        val value = (args["value"] as? Number)?.toDouble() ?: return mapOf("error" to "value required")
        val fromUnit = args["from_unit"] as? String ?: return mapOf("error" to "from_unit required")
        val toUnit = args["to_unit"] as? String ?: return mapOf("error" to "to_unit required")

        // Check if temperature conversion
        val isTemperature = listOf("c", "f", "k", "celsius", "fahrenheit", "kelvin")
            .any { fromUnit.lowercase().contains(it) || toUnit.lowercase().contains(it) }

        val result = if (isTemperature) {
            UnitConversionTable.convertTemperature(value, fromUnit, toUnit)
        } else {
            UnitConversionTable.convert(value, fromUnit, toUnit)
        }

        return if (result != null) {
            mapOf(
                "success" to true,
                "input_value" to value,
                "input_unit" to fromUnit,
                "output_value" to result,
                "output_unit" to toUnit,
                "formatted" to "$value $fromUnit = ${"%.6g".format(result)} $toUnit"
            )
        } else {
            mapOf(
                "success" to false,
                "error" to "Cannot convert between $fromUnit and $toUnit (incompatible or unknown units)"
            )
        }
    }

    private fun executeCreateBil(args: Map<String, Any?>): Map<String, Any?> {
        val sectorName = args["sector"] as? String ?: return mapOf("error" to "sector required")
        val dataTypeName = args["data_type"] as? String ?: return mapOf("error" to "data_type required")
        val sourceName = args["source"] as? String ?: return mapOf("error" to "source required")
        val itemId = (args["item_id"] as? Number)?.toLong() ?: return mapOf("error" to "item_id required")

        val sector = try { Sector.valueOf(sectorName) } catch (e: Exception) {
            return mapOf("error" to "Invalid sector: $sectorName")
        }
        val dataType = try { DataType.valueOf(dataTypeName) } catch (e: Exception) {
            return mapOf("error" to "Invalid data_type: $dataTypeName")
        }
        val source = try { Source.valueOf(sourceName) } catch (e: Exception) {
            return mapOf("error" to "Invalid source: $sourceName")
        }

        val bil = BrahimIndustryLabelFactory.create(sector, dataType, source, itemId)

        return mapOf(
            "full_label" to bil.fullLabel,
            "short_label" to bil.shortLabel,
            "brahim_number" to bil.brahimNumber,
            "check_digit" to bil.checkDigit.toString(),
            "is_deterministic" to bil.isDeterministic,
            "confidence" to bil.confidence,
            "warning" to bil.warning
        )
    }

    private fun executeVerifyBil(args: Map<String, Any?>): Map<String, Any?> {
        val bilString = args["bil_string"] as? String ?: return mapOf("error" to "bil_string required")

        val isValid = BrahimIndustryLabelFactory.verify(bilString)
        val parsed = BrahimIndustryLabelFactory.parse(bilString)

        return if (isValid && parsed != null) {
            mapOf(
                "valid" to true,
                "bil" to bilString,
                "sector" to parsed.sector.name,
                "sector_code" to parsed.sector.code,
                "data_type" to parsed.dataType.name,
                "source" to parsed.source.description,
                "is_deterministic" to parsed.isDeterministic,
                "confidence" to parsed.confidence
            )
        } else {
            mapOf(
                "valid" to false,
                "bil" to bilString,
                "error" to "Invalid BIL format or check digit mismatch"
            )
        }
    }

    private fun executeGetStats(): Map<String, Any?> {
        val stats = IndustryQueryFactory.getStatistics()
        return mapOf(
            "standards_count" to stats.standardsCount,
            "datasheets_count" to stats.datasheetsCount,
            "formulas_count" to stats.formulasCount,
            "units_count" to stats.unitsCount,
            "sectors_count" to stats.sectorsCount,
            "data_types_count" to stats.dataTypesCount,
            "sources_count" to stats.sourcesCount,
            "total_entries" to stats.totalEntries,
            "sectors" to Sector.values().map { mapOf("name" to it.name, "code" to it.code, "brahim_index" to it.brahimIndex) },
            "deterministic_sources" to Source.deterministicSources().map { it.name },
            "ml_sources" to Source.mlSources().map { it.name }
        )
    }

    companion object {
        /**
         * Register the agent with the global registry
         */
        fun register() {
            AgentRegistry.register(IndustryQueryAgent())
        }
    }
}

/**
 * Initialize Industry Query Agent and register with AgentRegistry
 */
fun initializeIndustryAgent() {
    IndustryQueryAgent.register()
}
