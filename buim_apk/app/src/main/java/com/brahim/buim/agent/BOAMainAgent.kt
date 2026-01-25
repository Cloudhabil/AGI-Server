/**
 * BOA Main Agent - Brahim Onion Agent
 * ====================================
 *
 * Local AI assistant with 12-wavelength architecture and ASIOS safety.
 * All processing grounded in the golden ratio hierarchy.
 *
 * Wavelengths:
 * 1. Delta (awareness)
 * 2. Theta (prediction)
 * 3. Alpha (attention)
 * 4. Beta (processing)
 * 5. Gamma (integration)
 * 6. Epsilon (error)
 * 7. Ganesha (correction)
 * 8. Lambda (learning)
 * 9. Mu (memory)
 * 10. Nu (novelty)
 * 11. Omega (completion)
 * 12. Phi (golden - synthesis)
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-25
 */

package com.brahim.buim.agent

import com.brahim.buim.core.BrahimConstants
import com.brahim.buim.safety.ASIOSGuard
import com.brahim.buim.safety.SafetyVerdict
import com.brahim.buim.router.IntentRouter
import com.brahim.buim.router.Territory
import kotlin.math.pow

/**
 * Agent response with metadata.
 */
data class AgentResponse(
    val content: String,
    val territory: Territory,
    val confidence: Double,
    val safetyScore: Double,
    val safetyVerdict: SafetyVerdict,
    val wavelengthStates: Map<String, Double>,
    val processingTime: Long
)

/**
 * Wavelength state for agent processing.
 */
data class WavelengthState(
    val name: String,
    val symbol: String,
    val index: Int,
    var activation: Double,
    val frequency: Double  // Related to golden ratio hierarchy
)

/**
 * BOA Main Agent - Core AI assistant class.
 *
 * Implements the 12-wavelength cognitive architecture with
 * ASIOS safety constraints at every step.
 */
class BOAMainAgent {

    companion object {
        const val NUM_WAVELENGTHS = 12

        // Wavelength definitions
        val WAVELENGTH_DEFS = listOf(
            Triple("delta", "Δ", "awareness"),
            Triple("theta", "Θ", "prediction"),
            Triple("alpha", "α", "attention"),
            Triple("beta", "β", "processing"),
            Triple("gamma", "γ", "integration"),
            Triple("epsilon", "ε", "error"),
            Triple("ganesha", "ग", "correction"),
            Triple("lambda", "λ", "learning"),
            Triple("mu", "μ", "memory"),
            Triple("nu", "ν", "novelty"),
            Triple("omega", "Ω", "completion"),
            Triple("phi", "φ", "synthesis")
        )

        val WAVELENGTH_NAMES = WAVELENGTH_DEFS.map { it.first }
    }

    // Core modules
    private val safetyGuard = ASIOSGuard()
    private val intentRouter = IntentRouter()

    // Agent state
    private val wavelengthStates = mutableMapOf<String, WavelengthState>()
    private var memoryBuffer = mutableListOf<String>()
    private var learningRate = BrahimConstants.BETA_SECURITY
    private var totalProcessed = 0L

    init {
        initializeWavelengths()
    }

    /**
     * Initialize wavelength states with golden ratio frequencies.
     */
    private fun initializeWavelengths() {
        for ((index, def) in WAVELENGTH_DEFS.withIndex()) {
            val (name, symbol, _) = def
            // Frequency based on golden ratio powers
            val frequency = BrahimConstants.PHI.pow((index - 6).toDouble())

            wavelengthStates[name] = WavelengthState(
                name = name,
                symbol = symbol,
                index = index,
                activation = 0.0,
                frequency = frequency
            )
        }
    }

    /**
     * Process a user message through the 12-wavelength pipeline.
     */
    fun process(message: String): AgentResponse {
        val startTime = System.currentTimeMillis()
        totalProcessed++

        // Wavelength 1: Delta (awareness)
        activateWavelength("delta", 1.0)
        val embedding = intentRouter.textToEmbedding(message)

        // Wavelength 2: Theta (prediction)
        activateWavelength("theta", 0.8)
        val routingResult = intentRouter.route(message)

        // Wavelength 3: Alpha (attention)
        activateWavelength("alpha", routingResult.confidence)

        // Wavelength 4: Beta (processing)
        activateWavelength("beta", BrahimConstants.BETA_SECURITY)

        // Wavelength 5: Gamma (integration)
        activateWavelength("gamma", BrahimConstants.GAMMA_DAMPING)

        // Wavelength 6: Epsilon (error detection)
        val safetyAssessment = safetyGuard.assessSafety(embedding)
        activateWavelength("epsilon", 1.0 - safetyAssessment.safetyScore)

        // Safety check - block if unsafe
        if (safetyAssessment.verdict == SafetyVerdict.BLOCKED) {
            return AgentResponse(
                content = "I cannot process this request due to safety constraints.",
                territory = Territory.SECURITY,
                confidence = 1.0,
                safetyScore = 0.0,
                safetyVerdict = SafetyVerdict.BLOCKED,
                wavelengthStates = getWavelengthActivations(),
                processingTime = System.currentTimeMillis() - startTime
            )
        }

        // Wavelength 7: Ganesha (correction)
        activateWavelength("ganesha", if (safetyAssessment.verdict == SafetyVerdict.CAUTION) 1.0 else 0.1)

        // Wavelength 8: Lambda (learning)
        activateWavelength("lambda", learningRate)

        // Wavelength 9: Mu (memory)
        memoryBuffer.add(message)
        if (memoryBuffer.size > 10) memoryBuffer.removeAt(0)
        activateWavelength("mu", memoryBuffer.size / 10.0)

        // Wavelength 10: Nu (novelty)
        val novelty = computeNovelty(message)
        activateWavelength("nu", novelty)

        // Wavelength 11: Omega (completion)
        val response = generateResponse(message, routingResult.territory)
        activateWavelength("omega", 1.0)

        // Wavelength 12: Phi (golden synthesis)
        activateWavelength("phi", BrahimConstants.COMPRESSION)

        return AgentResponse(
            content = response,
            territory = routingResult.territory,
            confidence = routingResult.confidence,
            safetyScore = safetyAssessment.safetyScore,
            safetyVerdict = safetyAssessment.verdict,
            wavelengthStates = getWavelengthActivations(),
            processingTime = System.currentTimeMillis() - startTime
        )
    }

    /**
     * Activate a wavelength with given intensity.
     */
    private fun activateWavelength(name: String, activation: Double) {
        wavelengthStates[name]?.let {
            it.activation = activation.coerceIn(0.0, 1.0)
        }
    }

    /**
     * Get current wavelength activations.
     */
    private fun getWavelengthActivations(): Map<String, Double> {
        return wavelengthStates.mapValues { it.value.activation }
    }

    /**
     * Compute novelty score for a message.
     */
    private fun computeNovelty(message: String): Double {
        if (memoryBuffer.isEmpty()) return 1.0

        // Simple novelty: inverse of similarity to recent messages
        val similarities = memoryBuffer.map { prev ->
            val common = message.lowercase().split(" ").intersect(
                prev.lowercase().split(" ").toSet()
            ).size
            val total = message.split(" ").size + prev.split(" ").size
            if (total > 0) common.toDouble() / total else 0.0
        }

        val avgSimilarity = similarities.average()
        return 1.0 - avgSimilarity
    }

    /**
     * Generate response based on territory.
     */
    private fun generateResponse(message: String, territory: Territory): String {
        // Template-based responses (in production, use LLM)
        return when (territory) {
            Territory.GENERAL -> "Hello! I'm BOA, your Brahim Onion Agent. How can I assist you today?"
            Territory.MATH -> "I can help with mathematical computations. The Brahim sequence provides powerful computational tools. What would you like to calculate?"
            Territory.CODE -> "I'm ready to help with programming. What language or problem would you like to work on?"
            Territory.SCIENCE -> "Let's explore this scientific topic together. I can apply physics constants derived from the Brahim sequence."
            Territory.CREATIVE -> "I'd love to help with your creative project! Creativity flows like the golden ratio spiral."
            Territory.ANALYSIS -> "I'll analyze this carefully using the 12-wavelength cognitive architecture. Here's my assessment..."
            Territory.SYSTEM -> "I can help configure system settings using the Brahim manifold infrastructure."
            Territory.SECURITY -> "Security is paramount. I'm protected by the Wormhole Cipher and ASIOS Guard."
            Territory.DATA -> "I can help process and understand data using the V-NAND learning grid."
            Territory.META -> "I'm BOA, operating on a 12-wavelength architecture grounded in the golden ratio hierarchy (φ → α → β → γ)."
        }
    }

    /**
     * Set the learning rate.
     */
    fun setLearningRate(rate: Double) {
        learningRate = rate.coerceIn(0.001, 1.0)
    }

    /**
     * Get agent status and info.
     */
    fun getAgentInfo(): Map<String, Any> {
        return mapOf(
            "name" to "BOA Main Agent",
            "version" to "1.0.0",
            "wavelengths" to NUM_WAVELENGTHS,
            "wavelength_states" to wavelengthStates.map { (name, state) ->
                name to mapOf(
                    "symbol" to state.symbol,
                    "activation" to state.activation,
                    "frequency" to state.frequency
                )
            }.toMap(),
            "memory_size" to memoryBuffer.size,
            "learning_rate" to learningRate,
            "total_processed" to totalProcessed,
            "beta_security" to BrahimConstants.BETA_SECURITY,
            "safety_guard" to safetyGuard.getGuardInfo()
        )
    }

    /**
     * Reset agent state.
     */
    fun reset() {
        memoryBuffer.clear()
        initializeWavelengths()
    }

    /**
     * Clear memory buffer only.
     */
    fun clearMemory() {
        memoryBuffer.clear()
    }
}
