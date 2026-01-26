/**
 * Brahim Industry Label (BIL) - Deterministic-First Data Classification
 * =====================================================================
 *
 * Universal labeling system for industrial data that:
 * 1. Uses Cantor pairing for unique, reversible codes
 * 2. Tracks data source (deterministic vs ML-derived)
 * 3. Enables backwards-compatible import of legacy data
 *
 * Format: BIL:<sector>:<type>:<source>:<id>-<check>
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-26
 * Spec: BUIM_UNIFIED_ARCHITECTURE_SPEC.md
 */

package com.brahim.buim.industry

import com.brahim.buim.core.BrahimConstants
import kotlin.math.abs
import kotlin.math.floor
import kotlin.math.sqrt

/**
 * Industry Sector - Maps to Brahim Sequence B(1) through B(10)
 */
enum class Sector(val code: Int, val brahimIndex: Int, val description: String) {
    ELECTRICAL(27, 1, "Electrical engineering, power systems, electronics"),
    MECHANICAL(42, 2, "Mechanical engineering, machinery, HVAC"),
    CHEMICAL(60, 3, "Chemical engineering, process industry"),
    DIGITAL(75, 4, "Software, IT, digital systems"),
    AEROSPACE(97, 5, "Aviation, space, defense"),
    BIOMEDICAL(121, 6, "Medical devices, biotechnology"),
    ENERGY(136, 7, "Power generation, renewables, grid"),
    MATERIALS(154, 8, "Materials science, metallurgy"),
    CONSTRUCTION(172, 9, "Civil engineering, architecture"),
    TRANSPORT(187, 10, "Automotive, rail, maritime");

    companion object {
        fun fromCode(code: Int): Sector? = values().find { it.code == code }
        fun fromBrahimIndex(index: Int): Sector? = values().find { it.brahimIndex == index }
    }
}

/**
 * Data Type Classification
 */
enum class DataType(val code: Int, val description: String) {
    SPECIFICATION(1, "Standards (IEC, ISO, DIN)"),
    DATASHEET(2, "Component/product specifications"),
    FORMULA(3, "Engineering equations"),
    TABLE(4, "Lookup tables, reference data"),
    DIAGRAM(5, "Schematics, P&ID, drawings"),
    PROCEDURE(6, "Work instructions, procedures"),
    MEASUREMENT(7, "Sensor data, test results"),
    SIMULATION(8, "FEA, CFD, simulation results"),
    LEARNED(9, "ML-derived data (flagged)");

    companion object {
        fun fromCode(code: Int): DataType? = values().find { it.code == code }
    }
}

/**
 * Knowledge Source - Critically tracks determinism
 */
enum class Source(
    val code: Int,
    val isDeterministic: Boolean,
    val description: String
) {
    // Deterministic sources (100-599)
    IEC_STANDARD(100, true, "IEC International Standard"),
    ISO_STANDARD(101, true, "ISO International Standard"),
    DIN_STANDARD(102, true, "DIN German Standard"),
    IEEE_STANDARD(103, true, "IEEE Standard"),
    MANUFACTURER_SPEC(200, true, "Manufacturer specification"),
    ENGINEERING_HANDBOOK(300, true, "Engineering reference (Perry's, Marks')"),
    VALIDATED_SIMULATION(400, true, "Validated simulation result"),
    PEER_REVIEWED(500, true, "Peer-reviewed publication"),

    // Non-deterministic sources (900+)
    ML_PREDICTION(900, false, "Machine learning prediction"),
    ML_CLASSIFICATION(901, false, "Machine learning classification"),
    ML_SIMILARITY(902, false, "ML-based similarity match"),
    UNVERIFIED(999, false, "Unverified source");

    companion object {
        fun fromCode(code: Int): Source? = values().find { it.code == code }
        fun deterministicSources(): List<Source> = values().filter { it.isDeterministic }
        fun mlSources(): List<Source> = values().filter { !it.isDeterministic }
    }
}

/**
 * The Brahim Industry Label (BIL)
 */
data class BrahimIndustryLabel(
    val sector: Sector,
    val dataType: DataType,
    val source: Source,
    val itemId: Long,
    val brahimNumber: Long,
    val checkDigit: Char,
    val fullLabel: String,
    val shortLabel: String
) {
    /**
     * Is this data from a deterministic (trustworthy) source?
     */
    val isDeterministic: Boolean get() = source.isDeterministic

    /**
     * Warning message if ML-derived
     */
    val warning: String? get() = if (!isDeterministic) {
        "⚠️ This data is ML-derived (Source: ${source.description}). " +
        "Verify against engineering standards before production use."
    } else null

    /**
     * Confidence level based on source
     */
    val confidence: Double get() = when {
        source.code in 100..199 -> 1.0    // Standards: 100%
        source.code in 200..299 -> 0.99   // Manufacturer: 99%
        source.code in 300..399 -> 0.98   // Handbooks: 98%
        source.code in 400..599 -> 0.95   // Validated: 95%
        source.code in 900..998 -> 0.70   // ML: ~70%
        else -> 0.50                       // Unverified: 50%
    }

    override fun toString(): String = fullLabel
}

/**
 * BIL Factory - Creates and parses Brahim Industry Labels
 */
object BrahimIndustryLabelFactory {

    /**
     * Create a new BIL from components
     */
    fun create(
        sector: Sector,
        dataType: DataType,
        source: Source,
        itemId: Long
    ): BrahimIndustryLabel {
        // Cantor pair: (sector, type) → level 1
        val level1 = cantorPair(sector.code.toLong(), dataType.code.toLong())

        // Cantor pair: (level1, source) → level 2
        val level2 = cantorPair(level1, source.code.toLong())

        // Cantor pair: (level2, itemId) → final Brahim number
        val brahimNumber = cantorPair(level2, itemId)

        val checkDigit = computeCheckDigit(brahimNumber)

        val fullLabel = "BIL:${sector.code}:${dataType.code}:${source.code}:$itemId-$checkDigit"
        val shortLabel = "BIL:${sector.code}:${dataType.code}:$itemId"

        return BrahimIndustryLabel(
            sector = sector,
            dataType = dataType,
            source = source,
            itemId = itemId,
            brahimNumber = brahimNumber,
            checkDigit = checkDigit,
            fullLabel = fullLabel,
            shortLabel = shortLabel
        )
    }

    /**
     * Parse a BIL string back to components
     */
    fun parse(bilString: String): BrahimIndustryLabel? {
        return try {
            // Format: BIL:<sector>:<type>:<source>:<id>-<check>
            val cleaned = bilString.removePrefix("BIL:")
            val parts = cleaned.split(":", "-")

            if (parts.size < 4) return null

            val sectorCode = parts[0].toInt()
            val typeCode = parts[1].toInt()
            val sourceCode = parts[2].toInt()
            val itemId = parts[3].toLong()
            val providedCheck = parts.getOrNull(4)?.firstOrNull()

            val sector = Sector.fromCode(sectorCode) ?: return null
            val dataType = DataType.fromCode(typeCode) ?: return null
            val source = Source.fromCode(sourceCode) ?: return null

            val bil = create(sector, dataType, source, itemId)

            // Verify check digit if provided
            if (providedCheck != null && providedCheck != bil.checkDigit) {
                return null  // Check digit mismatch
            }

            bil
        } catch (e: Exception) {
            null
        }
    }

    /**
     * Verify a BIL string is valid
     */
    fun verify(bilString: String): Boolean {
        return parse(bilString) != null
    }

    /**
     * Upgrade a BIL's source (e.g., after human verification)
     */
    fun upgradeSource(bil: BrahimIndustryLabel, newSource: Source): BrahimIndustryLabel {
        require(newSource.isDeterministic) {
            "Can only upgrade to deterministic sources"
        }
        return create(bil.sector, bil.dataType, newSource, bil.itemId)
    }

    // =========================================================================
    // Internal: Cantor pairing functions
    // =========================================================================

    private fun cantorPair(a: Long, b: Long): Long {
        return ((a + b) * (a + b + 1)) / 2 + b
    }

    private fun cantorUnpair(z: Long): Pair<Long, Long> {
        val w = floor((sqrt(8.0 * z + 1) - 1) / 2).toLong()
        val t = (w * w + w) / 2
        val b = z - t
        val a = w - b
        return a to b
    }

    private fun computeCheckDigit(n: Long): Char {
        val r = (abs(n) % 11).toInt()
        return if (r == 10) 'X' else ('0' + r)
    }
}

// =============================================================================
// Extension functions for convenience
// =============================================================================

/**
 * Create a BIL for a standard reference
 */
fun standardToBIL(
    standardBody: String,
    standardNumber: String,
    sector: Sector = Sector.ELECTRICAL
): BrahimIndustryLabel {
    val source = when (standardBody.uppercase()) {
        "IEC" -> Source.IEC_STANDARD
        "ISO" -> Source.ISO_STANDARD
        "DIN" -> Source.DIN_STANDARD
        "IEEE" -> Source.IEEE_STANDARD
        else -> Source.PEER_REVIEWED
    }

    // Generate item ID from standard number hash
    val itemId = standardNumber.hashCode().toLong() and 0x7FFFFFFF

    return BrahimIndustryLabelFactory.create(
        sector = sector,
        dataType = DataType.SPECIFICATION,
        source = source,
        itemId = itemId
    )
}

/**
 * Create a BIL for ML-classified data (automatically flagged)
 */
fun mlClassifiedToBIL(
    sector: Sector,
    dataType: DataType,
    itemId: Long
): BrahimIndustryLabel {
    return BrahimIndustryLabelFactory.create(
        sector = sector,
        dataType = dataType,
        source = Source.ML_CLASSIFICATION,
        itemId = itemId
    )
}
