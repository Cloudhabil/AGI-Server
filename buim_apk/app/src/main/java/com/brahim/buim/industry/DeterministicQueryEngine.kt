/**
 * Deterministic Query Engine
 * ==========================
 *
 * Core principle: "Retrieve what is known, learn only what isn't."
 *
 * Query priority:
 * 1. DETERMINISTIC: Standards (IEC, ISO, DIN)
 * 2. VALIDATED: Manufacturer specs, handbooks
 * 3. ML FALLBACK: Only when no deterministic source exists (FLAGGED)
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-26
 * Spec: BUIM_UNIFIED_ARCHITECTURE_SPEC.md
 */

package com.brahim.buim.industry

import kotlinx.coroutines.async
import kotlinx.coroutines.coroutineScope

/**
 * Query input from user or system
 */
data class IndustryQuery(
    val text: String,
    val keywords: List<String> = extractKeywords(text),
    val expectedSector: Sector? = null,
    val expectedType: DataType? = null,
    val requireDeterministic: Boolean = false
) {
    companion object {
        private fun extractKeywords(text: String): List<String> {
            return text.lowercase()
                .replace(Regex("[^a-z0-9\\s]"), " ")
                .split(Regex("\\s+"))
                .filter { it.length > 2 }
                .distinct()
        }
    }
}

/**
 * Query result with full provenance tracking
 */
data class QueryResult(
    val answer: String,
    val bil: BrahimIndustryLabel,
    val confidence: Double,
    val isDeterministic: Boolean,
    val citation: String,
    val reasoning: String,
    val alternatives: List<AlternativeAnswer> = emptyList()
) {
    /**
     * Warning if result is not deterministic
     */
    val warning: String? get() = if (!isDeterministic) {
        """
        |⚠️ ML PREDICTION - NOT VERIFIED
        |
        |This answer is derived from machine learning (${bil.source.description}).
        |Confidence: ${(confidence * 100).toInt()}%
        |
        |Recommended: Verify against engineering standards before production use.
        """.trimMargin()
    } else null
}

/**
 * Alternative answer for disambiguation
 */
data class AlternativeAnswer(
    val answer: String,
    val source: Source,
    val confidence: Double,
    val reason: String
)

/**
 * Internal search result from knowledge bases
 */
internal data class SearchHit(
    val value: String,
    val source: Source,
    val itemId: Long,
    val citation: String,
    val relevanceScore: Double
)

/**
 * The Deterministic Query Engine
 *
 * Implements the "deterministic-first" philosophy:
 * - Always prefer known facts over predictions
 * - Always flag ML results clearly
 * - Enable verification workflow
 */
class DeterministicQueryEngine(
    private val standardsDB: StandardsDatabase,
    private val datasheetDB: DatasheetDatabase,
    private val handbookDB: HandbookDatabase,
    private val mlAgent: MLPredictionAgent
) {

    /**
     * Main query method - deterministic first, ML fallback
     */
    suspend fun query(query: IndustryQuery): QueryResult = coroutineScope {
        // Classify the domain if not provided
        val sector = query.expectedSector ?: classifySector(query)
        val dataType = query.expectedType ?: classifyDataType(query)

        // PRIORITY 1: Search deterministic sources (in parallel)
        val standardsSearch = async { standardsDB.search(query.keywords, sector) }
        val datasheetSearch = async { datasheetDB.search(query.keywords, sector) }
        val handbookSearch = async { handbookDB.search(query.keywords, sector) }

        // Collect results
        val standardsHit = standardsSearch.await()
        val datasheetHit = datasheetSearch.await()
        val handbookHit = handbookSearch.await()

        // Return best deterministic result if found
        val deterministicHit = listOfNotNull(standardsHit, datasheetHit, handbookHit)
            .maxByOrNull { it.relevanceScore }

        if (deterministicHit != null && deterministicHit.relevanceScore > 0.7) {
            return@coroutineScope createDeterministicResult(
                hit = deterministicHit,
                sector = sector,
                dataType = dataType,
                query = query
            )
        }

        // PRIORITY 2: If deterministic required, return not found
        if (query.requireDeterministic) {
            return@coroutineScope createNotFoundResult(sector, dataType, query)
        }

        // PRIORITY 3: ML fallback (FLAGGED)
        val mlPrediction = mlAgent.predict(query, sector)

        return@coroutineScope createMLResult(
            prediction = mlPrediction,
            sector = sector,
            dataType = dataType,
            query = query,
            nearestDeterministic = deterministicHit  // Link to closest known fact
        )
    }

    /**
     * Query requiring only deterministic answers
     */
    suspend fun queryDeterministic(query: IndustryQuery): QueryResult? {
        val result = query(query.copy(requireDeterministic = true))
        return if (result.isDeterministic) result else null
    }

    /**
     * Batch query for multiple items
     */
    suspend fun queryBatch(queries: List<IndustryQuery>): List<QueryResult> = coroutineScope {
        queries.map { async { query(it) } }.map { it.await() }
    }

    // =========================================================================
    // Internal: Result creation
    // =========================================================================

    private fun createDeterministicResult(
        hit: SearchHit,
        sector: Sector,
        dataType: DataType,
        query: IndustryQuery
    ): QueryResult {
        val bil = BrahimIndustryLabelFactory.create(
            sector = sector,
            dataType = dataType,
            source = hit.source,
            itemId = hit.itemId
        )

        return QueryResult(
            answer = hit.value,
            bil = bil,
            confidence = 1.0,  // Deterministic = 100%
            isDeterministic = true,
            citation = hit.citation,
            reasoning = "Retrieved from ${hit.source.description}: ${hit.citation}"
        )
    }

    private fun createMLResult(
        prediction: MLPrediction,
        sector: Sector,
        dataType: DataType,
        query: IndustryQuery,
        nearestDeterministic: SearchHit?
    ): QueryResult {
        val bil = BrahimIndustryLabelFactory.create(
            sector = sector,
            dataType = dataType,
            source = Source.ML_PREDICTION,
            itemId = prediction.predictionId
        )

        val alternatives = if (nearestDeterministic != null) {
            listOf(
                AlternativeAnswer(
                    answer = nearestDeterministic.value,
                    source = nearestDeterministic.source,
                    confidence = nearestDeterministic.relevanceScore,
                    reason = "Closest deterministic match (may not be exact)"
                )
            )
        } else emptyList()

        return QueryResult(
            answer = prediction.value,
            bil = bil,
            confidence = prediction.confidence,
            isDeterministic = false,
            citation = "ML Prediction (Model: ${prediction.modelId})",
            reasoning = """
                |No deterministic source found for this query.
                |
                |ML Prediction:
                |  Model: ${prediction.modelId}
                |  Confidence: ${(prediction.confidence * 100).toInt()}%
                |  Reasoning: ${prediction.reasoning}
                |
                |${if (nearestDeterministic != null)
                    "Nearest deterministic: ${nearestDeterministic.citation}"
                  else
                    "No similar deterministic data found."}
            """.trimMargin(),
            alternatives = alternatives
        )
    }

    private fun createNotFoundResult(
        sector: Sector,
        dataType: DataType,
        query: IndustryQuery
    ): QueryResult {
        val bil = BrahimIndustryLabelFactory.create(
            sector = sector,
            dataType = dataType,
            source = Source.UNVERIFIED,
            itemId = query.text.hashCode().toLong() and 0x7FFFFFFF
        )

        return QueryResult(
            answer = "NOT FOUND",
            bil = bil,
            confidence = 0.0,
            isDeterministic = false,
            citation = "No source",
            reasoning = "No deterministic source found and ML fallback was disabled."
        )
    }

    // =========================================================================
    // Internal: Classification helpers
    // =========================================================================

    private fun classifySector(query: IndustryQuery): Sector {
        // Keyword-based classification (could be ML-enhanced)
        val text = query.text.lowercase()

        return when {
            text.containsAny("voltage", "current", "wire", "circuit", "iec", "electrical") ->
                Sector.ELECTRICAL
            text.containsAny("torque", "bearing", "mechanical", "shaft", "iso") ->
                Sector.MECHANICAL
            text.containsAny("chemical", "reaction", "process", "catalyst") ->
                Sector.CHEMICAL
            text.containsAny("software", "digital", "ieee", "protocol", "data") ->
                Sector.DIGITAL
            text.containsAny("aircraft", "flight", "aerospace", "aviation") ->
                Sector.AEROSPACE
            text.containsAny("medical", "biomedical", "patient", "clinical") ->
                Sector.BIOMEDICAL
            text.containsAny("power", "energy", "grid", "renewable", "solar") ->
                Sector.ENERGY
            text.containsAny("material", "steel", "alloy", "composite") ->
                Sector.MATERIALS
            text.containsAny("building", "construction", "concrete", "structural") ->
                Sector.CONSTRUCTION
            text.containsAny("vehicle", "transport", "automotive", "rail") ->
                Sector.TRANSPORT
            else -> Sector.ELECTRICAL  // Default
        }
    }

    private fun classifyDataType(query: IndustryQuery): DataType {
        val text = query.text.lowercase()

        return when {
            text.containsAny("standard", "iec", "iso", "din", "specification") ->
                DataType.SPECIFICATION
            text.containsAny("datasheet", "spec sheet", "product data") ->
                DataType.DATASHEET
            text.containsAny("formula", "equation", "calculate", "compute") ->
                DataType.FORMULA
            text.containsAny("table", "lookup", "values", "reference") ->
                DataType.TABLE
            text.containsAny("diagram", "schematic", "drawing", "p&id") ->
                DataType.DIAGRAM
            text.containsAny("procedure", "instruction", "how to", "step") ->
                DataType.PROCEDURE
            text.containsAny("measurement", "reading", "sensor", "test result") ->
                DataType.MEASUREMENT
            text.containsAny("simulation", "fea", "cfd", "analysis") ->
                DataType.SIMULATION
            else -> DataType.SPECIFICATION  // Default
        }
    }

    private fun String.containsAny(vararg keywords: String): Boolean {
        return keywords.any { this.contains(it) }
    }
}

// =============================================================================
// Database interfaces (to be implemented)
// =============================================================================

/**
 * Standards database interface (IEC, ISO, DIN)
 */
interface StandardsDatabase {
    suspend fun search(keywords: List<String>, sector: Sector): SearchHit?
    suspend fun getByReference(reference: String): SearchHit?
}

/**
 * Datasheet database interface (manufacturer specs)
 */
interface DatasheetDatabase {
    suspend fun search(keywords: List<String>, sector: Sector): SearchHit?
    suspend fun getByPartNumber(partNumber: String): SearchHit?
}

/**
 * Engineering handbook database interface
 */
interface HandbookDatabase {
    suspend fun search(keywords: List<String>, sector: Sector): SearchHit?
    suspend fun getByTopic(topic: String): SearchHit?
}

/**
 * ML prediction agent interface (fallback only)
 */
interface MLPredictionAgent {
    suspend fun predict(query: IndustryQuery, sector: Sector): MLPrediction
}

/**
 * ML prediction result
 */
data class MLPrediction(
    val value: String,
    val confidence: Double,
    val predictionId: Long,
    val modelId: String,
    val reasoning: String
)

// =============================================================================
// Learning loop for verification
// =============================================================================

/**
 * Verification result from human review
 */
sealed class VerificationResult {
    /**
     * ML was correct, and we found the deterministic source
     */
    data class Confirmed(
        val confirmedSource: Source,
        val citation: String
    ) : VerificationResult()

    /**
     * ML was wrong, human provided correct answer
     */
    data class Corrected(
        val correctValue: String,
        val correctSource: Source,
        val citation: String
    ) : VerificationResult()

    /**
     * No deterministic source exists
     */
    object NoDeterministicSource : VerificationResult()
}

/**
 * Learning loop processor
 */
class LearningLoopProcessor {

    /**
     * Process human verification of ML prediction
     */
    fun processVerification(
        originalResult: QueryResult,
        verification: VerificationResult
    ): LearningOutcome {
        require(!originalResult.isDeterministic) {
            "Only ML predictions should be verified"
        }

        return when (verification) {
            is VerificationResult.Confirmed -> {
                // Upgrade BIL to deterministic
                val upgradedBil = BrahimIndustryLabelFactory.upgradeSource(
                    originalResult.bil,
                    verification.confirmedSource
                )

                LearningOutcome.Upgraded(
                    originalBil = originalResult.bil,
                    upgradedBil = upgradedBil,
                    citation = verification.citation
                )
            }

            is VerificationResult.Corrected -> {
                LearningOutcome.Corrected(
                    originalAnswer = originalResult.answer,
                    correctAnswer = verification.correctValue,
                    correctSource = verification.correctSource,
                    citation = verification.citation
                )
            }

            is VerificationResult.NoDeterministicSource -> {
                LearningOutcome.Inconclusive(
                    message = "No deterministic source found. ML prediction remains unverified."
                )
            }
        }
    }
}

/**
 * Outcome of learning loop processing
 */
sealed class LearningOutcome {
    data class Upgraded(
        val originalBil: BrahimIndustryLabel,
        val upgradedBil: BrahimIndustryLabel,
        val citation: String
    ) : LearningOutcome()

    data class Corrected(
        val originalAnswer: String,
        val correctAnswer: String,
        val correctSource: Source,
        val citation: String
    ) : LearningOutcome()

    data class Inconclusive(
        val message: String
    ) : LearningOutcome()
}
