/**
 * ML Prediction Agent Implementation
 * ====================================
 *
 * Fallback ML-based prediction when no deterministic source exists.
 * All predictions are FLAGGED as non-deterministic.
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-26
 */

package com.brahim.buim.industry.db

import com.brahim.buim.industry.*
import kotlin.math.abs
import kotlin.random.Random

/**
 * ML Prediction Agent - Fallback when deterministic sources fail
 *
 * IMPORTANT: All predictions from this agent are flagged with:
 * - source = ML_PREDICTION (code 900)
 * - isDeterministic = false
 * - warning message included
 *
 * This implementation uses rule-based heuristics as a placeholder
 * for actual ML models. In production, replace with:
 * - TensorFlow Lite for on-device inference
 * - API calls to cloud ML services
 * - Local ONNX runtime models
 */
class MLPredictionAgentImpl : MLPredictionAgent {

    private var predictionCounter: Long = System.currentTimeMillis()

    // Confidence multipliers based on query characteristics
    private val sectorConfidence = mapOf(
        Sector.ELECTRICAL to 0.85,     // Well-documented domain
        Sector.MECHANICAL to 0.80,
        Sector.ENERGY to 0.82,
        Sector.DIGITAL to 0.88,
        Sector.CHEMICAL to 0.75,
        Sector.AEROSPACE to 0.70,      // Highly specialized
        Sector.BIOMEDICAL to 0.65,     // Requires verification
        Sector.MATERIALS to 0.72,
        Sector.CONSTRUCTION to 0.78,
        Sector.TRANSPORT to 0.76
    )

    override suspend fun predict(query: IndustryQuery, sector: Sector): MLPrediction {
        // Generate unique prediction ID
        val predictionId = ++predictionCounter

        // Analyze query complexity
        val queryComplexity = analyzeComplexity(query)

        // Generate prediction based on query patterns
        val (prediction, reasoning) = generatePrediction(query, sector)

        // Calculate confidence based on multiple factors
        val baseConfidence = sectorConfidence[sector] ?: 0.70
        val adjustedConfidence = baseConfidence * queryComplexity * 0.85

        return MLPrediction(
            value = prediction,
            confidence = adjustedConfidence.coerceIn(0.50, 0.90),
            predictionId = predictionId,
            modelId = "BUIM-Heuristic-v1.0",
            reasoning = reasoning
        )
    }

    /**
     * Analyze query complexity to adjust confidence
     */
    private fun analyzeComplexity(query: IndustryQuery): Double {
        val text = query.text.lowercase()
        var complexity = 1.0

        // More specific queries = higher confidence
        if (query.keywords.size >= 3) complexity *= 1.1
        if (query.expectedSector != null) complexity *= 1.1
        if (query.expectedType != null) complexity *= 1.05

        // Certain patterns reduce confidence
        if (text.contains("best") || text.contains("optimal")) complexity *= 0.85
        if (text.contains("should") || text.contains("recommend")) complexity *= 0.90
        if (text.contains("always") || text.contains("never")) complexity *= 0.80

        // Technical specificity increases confidence
        if (text.matches(Regex(".*\\d+.*"))) complexity *= 1.05  // Contains numbers
        if (text.contains("iec") || text.contains("iso")) complexity *= 1.1

        return complexity.coerceIn(0.5, 1.3)
    }

    /**
     * Generate prediction based on query patterns
     *
     * This is a rule-based placeholder. In production, replace with actual ML.
     */
    private fun generatePrediction(query: IndustryQuery, sector: Sector): Pair<String, String> {
        val text = query.text.lowercase()
        val keywords = query.keywords

        // Pattern matching for common query types
        return when {
            // Electrical queries
            keywords.any { it in listOf("wire", "cable", "gauge", "awg") } -> {
                Pair(
                    "For general purpose wiring, consider AWG 14 (15A) or AWG 12 (20A) based on load. Verify against NEC/IEC 60364 for specific installation.",
                    "Matched pattern: wire sizing query. Based on common residential/commercial standards."
                )
            }

            keywords.any { it in listOf("fuse", "breaker", "protection") } -> {
                Pair(
                    "Circuit protection should be sized at 125% of continuous load. Use IEC 60898 for MCB selection, IEC 60269 for fuses.",
                    "Matched pattern: protection device sizing. Rule-based on standard practices."
                )
            }

            // Energy/Solar queries
            keywords.any { it in listOf("solar", "panel", "pv") } &&
            keywords.any { it in listOf("size", "calculate", "need") } -> {
                Pair(
                    "Solar system sizing: Annual consumption (kWh) ÷ (Peak sun hours × 365 × 0.8) = Required kWp. Typical: 1kWp produces 1000-1400 kWh/year depending on location.",
                    "Matched pattern: solar sizing calculation. Based on industry rule of thumb."
                )
            }

            keywords.any { it in listOf("battery", "storage") } &&
            keywords.any { it in listOf("size", "capacity") } -> {
                Pair(
                    "Battery sizing: Daily consumption (kWh) × Days of autonomy ÷ DoD ÷ Efficiency = Required capacity. Typical DoD for LiFePO4: 80-90%.",
                    "Matched pattern: battery sizing. Based on standard energy storage calculations."
                )
            }

            keywords.any { it in listOf("inverter") } -> {
                Pair(
                    "Inverter sizing: 1.0-1.3× PV array size for string inverters. Match voltage window to string configuration. Consider IEC 62109 for safety.",
                    "Matched pattern: inverter selection. Based on typical solar installation practices."
                )
            }

            // Mechanical queries
            keywords.any { it in listOf("torque", "bolt", "tighten") } -> {
                Pair(
                    "Bolt torque depends on grade, size, and lubrication. For M8 Grade 8.8 dry: ~25 Nm. Always verify against manufacturer specs or VDI 2230.",
                    "Matched pattern: bolt torque query. General values provided, specific verification needed."
                )
            }

            keywords.any { it in listOf("bearing", "load", "life") } -> {
                Pair(
                    "Bearing life L10 = (C/P)^p × 10^6 revolutions, where p=3 for ball bearings. Select bearing with C > required for target life.",
                    "Matched pattern: bearing selection. Based on ISO 281 life calculation."
                )
            }

            // Chemical/Process queries
            keywords.any { it in listOf("pipe", "flow", "pressure", "drop") } -> {
                Pair(
                    "Pressure drop: ΔP = f × (L/D) × (ρv²/2). Use Darcy-Weisbach equation. For water at moderate flow: 0.1-0.5 bar per 100m typical.",
                    "Matched pattern: fluid flow calculation. Based on standard hydraulics."
                )
            }

            // Default fallback
            else -> {
                val sectorHint = when (sector) {
                    Sector.ELECTRICAL -> "For electrical specifications, consult IEC 60364 series for installations or relevant product standards."
                    Sector.ENERGY -> "For renewable energy systems, refer to IEC 62446 for PV or IEC 61400 for wind."
                    Sector.MECHANICAL -> "For mechanical specifications, ISO 286 for tolerances or relevant product standards."
                    else -> "Consult relevant industry standards (IEC, ISO, IEEE) for your specific application."
                }

                Pair(
                    "Query too general for specific prediction. $sectorHint Provide more details for targeted assistance.",
                    "No specific pattern matched. Generic guidance provided based on sector."
                )
            }
        }
    }

    /**
     * Batch prediction for multiple queries
     */
    suspend fun predictBatch(queries: List<Pair<IndustryQuery, Sector>>): List<MLPrediction> {
        return queries.map { (query, sector) -> predict(query, sector) }
    }

    /**
     * Get model information
     */
    fun getModelInfo(): Map<String, Any> = mapOf(
        "modelId" to "BUIM-Heuristic-v1.0",
        "type" to "Rule-based heuristic (placeholder)",
        "version" to "1.0.0",
        "supportedSectors" to Sector.values().toList(),
        "averageConfidence" to 0.75,
        "note" to "Replace with actual ML model in production"
    )
}
