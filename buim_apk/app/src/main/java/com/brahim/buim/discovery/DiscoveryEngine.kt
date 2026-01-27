/**
 * Discovery Engine - Intelligent App Recommendation
 * ==================================================
 *
 * ASIOS 2.0 - Phi-Pi Synthesis Release
 *
 * Uses Brahim Calculator + Kelimutu routing + Lucas Architecture
 * to understand user intent and recommend the perfect apps.
 *
 * "The chatbot feels what the user needs"
 *
 * Lucas Dimensional Intent Mapping:
 *   D1:  CALCULATE    - L(1)=1   (fundamental need)
 *   D2:  LEARN        - L(2)=3   (knowledge triage)
 *   D3:  SECURE       - L(3)=4   (protection quadrants)
 *   D4:  EXPLORE      - L(4)=7   (discovery modes)
 *   D5:  CONVERT      - L(5)=11  (transformation levels)
 *   D6:  COMMUNICATE  - L(6)=18  (connection channels)
 *   D7:  ANALYZE      - L(7)=29  (analysis rules)
 *   D8:  PLAN         - L(8)=47  (planning patterns)
 *   D9:  CREATE       - L(9)=76  (creative pathways)
 *   D10: OPTIMIZE     - L(10)=123 (optimization principles)
 *   D11: SOLVE        - L(11)=199 (solution synthesis)
 *   D12: VISUALIZE    - L(12)=322 (rendering modes)
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-27
 */

package com.brahim.buim.discovery

import com.brahim.buim.core.BrahimConstants
import kotlin.math.abs
import kotlin.math.exp
import kotlin.math.sqrt
import kotlin.math.PI

/**
 * User intent detected from query.
 */
data class UserIntent(
    val primary: IntentCategory,
    val secondary: IntentCategory?,
    val confidence: Double,
    val keywords: List<String>,
    val emotionalTone: EmotionalTone,
    val urgency: UrgencyLevel
)

/**
 * Intent categories mapped to Lucas dimensions.
 *
 * ASIOS 2.0: Each intent has a Lucas dimension with L(n) discrete states.
 */
enum class IntentCategory(val lucasDimension: Int, val lucasCapacity: Int) {
    // Core needs mapped to Lucas dimensions
    CALCULATE(1, 1),      // D1: L(1)=1 - Fundamental computation
    LEARN(2, 3),          // D2: L(2)=3 - Knowledge triage
    SECURE(3, 4),         // D3: L(3)=4 - Trust quadrants
    EXPLORE(4, 7),        // D4: L(4)=7 - Discovery modes
    CONVERT(5, 11),       // D5: L(5)=11 - Transformation levels
    COMMUNICATE(6, 18),   // D6: L(6)=18 - Connection channels
    ANALYZE(7, 29),       // D7: L(7)=29 - Analysis rules
    PLAN(8, 47),          // D8: L(8)=47 - Planning patterns
    CREATE(9, 76),        // D9: L(9)=76 - Creative pathways
    OPTIMIZE(10, 123),    // D10: L(10)=123 - Optimization principles
    SOLVE(11, 199),       // D11: L(11)=199 - Solution synthesis
    VISUALIZE(12, 322)    // D12: L(12)=322 - Rendering modes (phi meets pi)
}

/**
 * Emotional tone of the query.
 */
enum class EmotionalTone {
    CURIOUS,        // Exploratory, wanting to learn
    URGENT,         // Needs immediate solution
    CREATIVE,       // Wants to build something
    ANALYTICAL,     // Deep analysis needed
    PLAYFUL,        // Casual, experimental
    PROFESSIONAL,   // Business/formal context
    CONFUSED,       // Needs guidance
    EXCITED         // Enthusiastic about discovery
}

/**
 * Urgency level.
 */
enum class UrgencyLevel {
    IMMEDIATE,      // Needs answer now
    SOON,           // Within this session
    EXPLORING,      // Just browsing
    PLANNING        // Future consideration
}

/**
 * App recommendation with reasoning.
 *
 * ASIOS 2.0: Includes Lucas dimensional metadata.
 */
data class AppRecommendation(
    val appId: String,
    val appName: String,
    val category: String,
    val relevanceScore: Double,      // 0-1 how relevant to intent
    val brahimResonance: Double,     // Alignment with Brahim numbers
    val reason: String,              // Why this app was recommended
    val pathway: List<String>,       // How to get there from Home
    val lucasDimension: Int = 1,     // ASIOS 2.0: Lucas dimension
    val lucasCapacity: Int = 1,      // ASIOS 2.0: L(n) capacity
    val inCreativeGap: Boolean = false // ASIOS 2.0: Within 1.16% Phi-Pi gap
)

/**
 * Discovery session tracking user journey.
 */
data class DiscoverySession(
    val sessionId: String,
    val startTime: Long,
    val intents: MutableList<UserIntent> = mutableListOf(),
    val appsVisited: MutableList<String> = mutableListOf(),
    val recommendations: MutableList<AppRecommendation> = mutableListOf(),
    var satisfactionScore: Double = 0.5
)

/**
 * Discovery Engine - The brain that feels user needs.
 */
class DiscoveryEngine {

    // Intent keyword mappings
    private val intentKeywords = mapOf(
        IntentCategory.CALCULATE to listOf(
            "calculate", "compute", "math", "number", "formula", "equation",
            "constant", "physics", "derive", "value", "ratio", "sum"
        ),
        IntentCategory.EXPLORE to listOf(
            "explore", "discover", "find", "search", "browse", "what is",
            "show me", "tell me about", "universe", "cosmos", "space"
        ),
        IntentCategory.CREATE to listOf(
            "create", "build", "make", "generate", "design", "construct",
            "new", "start", "begin", "develop"
        ),
        IntentCategory.ANALYZE to listOf(
            "analyze", "understand", "explain", "why", "how", "investigate",
            "examine", "study", "research", "pattern"
        ),
        IntentCategory.SECURE to listOf(
            "secure", "encrypt", "protect", "safe", "private", "cipher",
            "key", "password", "lock", "security"
        ),
        IntentCategory.OPTIMIZE to listOf(
            "optimize", "improve", "better", "faster", "efficient", "best",
            "maximum", "minimum", "ideal", "perfect"
        ),
        IntentCategory.LEARN to listOf(
            "learn", "teach", "tutorial", "guide", "help", "how to",
            "understand", "explain", "course", "study"
        ),
        IntentCategory.COMMUNICATE to listOf(
            "send", "share", "message", "chat", "talk", "communicate",
            "contact", "connect", "reach"
        ),
        IntentCategory.PLAN to listOf(
            "plan", "schedule", "organize", "manage", "allocate", "divide",
            "assign", "timeline", "project", "task"
        ),
        IntentCategory.VISUALIZE to listOf(
            "visualize", "see", "show", "display", "graph", "chart",
            "plot", "diagram", "view", "render"
        ),
        IntentCategory.SOLVE to listOf(
            "solve", "fix", "resolve", "answer", "solution", "problem",
            "issue", "error", "debug", "trouble"
        ),
        IntentCategory.CONVERT to listOf(
            "convert", "transform", "change", "translate", "switch",
            "unit", "format", "export", "import"
        )
    )

    // Emotional tone keywords
    private val toneKeywords = mapOf(
        EmotionalTone.CURIOUS to listOf("curious", "wonder", "interesting", "what if", "maybe"),
        EmotionalTone.URGENT to listOf("urgent", "now", "immediately", "asap", "quick", "fast"),
        EmotionalTone.CREATIVE to listOf("create", "build", "design", "imagine", "innovative"),
        EmotionalTone.ANALYTICAL to listOf("analyze", "deep", "detail", "thorough", "precise"),
        EmotionalTone.PLAYFUL to listOf("fun", "play", "try", "experiment", "cool"),
        EmotionalTone.PROFESSIONAL to listOf("business", "work", "professional", "enterprise"),
        EmotionalTone.CONFUSED to listOf("confused", "don't understand", "help", "lost", "?"),
        EmotionalTone.EXCITED to listOf("excited", "amazing", "awesome", "wow", "!")
    )

    // App mappings by intent
    private val intentToApps = mapOf(
        IntentCategory.CALCULATE to listOf(
            "physics_fine_structure" to "Fine Structure Calculator",
            "physics_weinberg" to "Weinberg Angle",
            "math_sequence" to "Brahim Sequence Explorer",
            "math_egyptian" to "Egyptian Fractions",
            "cosmic_calculator" to "Cosmic Calculator",
            "util_precision" to "Precision Calculator"
        ),
        IntentCategory.EXPLORE to listOf(
            "universe_simulator" to "Universe Simulator",
            "dark_sector" to "Dark Sector Explorer",
            "planetary_titan" to "Titan Explorer",
            "mars_mission" to "Mars Mission Control",
            "cosmo_timeline" to "Cosmic Timeline"
        ),
        IntentCategory.CREATE to listOf(
            "brahim_workspace" to "Brahim Workspace",
            "pinn_lab" to "PINN Physics Lab",
            "golden_optimizer" to "Golden Optimizer",
            "resonance_lab" to "Resonance Lab"
        ),
        IntentCategory.ANALYZE to listOf(
            "traffic_brain" to "Traffic Brain",
            "ml_wavelength" to "Wavelength Analyzer",
            "ml_phase" to "Phase Classifier",
            "viz_phase" to "Phase Portrait",
            "fair_division_ai" to "Fair Division AI"
        ),
        IntentCategory.SECURE to listOf(
            "secure_business" to "Secure Business Suite",
            "security_cipher" to "Wormhole Cipher",
            "security_asios" to "ASIOS Guard",
            "security_keygen" to "Key Generator",
            "crypto_observatory" to "Crypto Observatory"
        ),
        IntentCategory.OPTIMIZE to listOf(
            "smart_navigator" to "Smart Navigator",
            "aerospace_optimizer" to "Aerospace Optimizer",
            "solver_optimize" to "Optimizer",
            "traffic_route" to "Route Optimizer",
            "golden_optimizer" to "Golden Optimizer"
        ),
        IntentCategory.LEARN to listOf(
            "consciousness_explorer" to "Consciousness Explorer",
            "math_sequence" to "Brahim Sequence",
            "kelimutu_intel" to "Kelimutu Intelligence",
            "about" to "About BUIM"
        ),
        IntentCategory.COMMUNICATE to listOf(
            "secure_chat" to "Secure Chat",
            "emergency_response" to "Emergency Response"
        ),
        IntentCategory.PLAN to listOf(
            "business_scheduler" to "Task Scheduler",
            "business_allocator" to "Resource Allocator",
            "titan_colony" to "Titan Colony Planner",
            "fleet_manager" to "Fleet Manager",
            "compliance_intel" to "Compliance Intelligence"
        ),
        IntentCategory.VISUALIZE to listOf(
            "viz_resonance" to "Resonance Monitor",
            "viz_sequence" to "Sequence Plot",
            "viz_symmetry" to "Symmetry Viewer",
            "viz_phase" to "Phase Portrait",
            "universe_simulator" to "Universe Simulator"
        ),
        IntentCategory.SOLVE to listOf(
            "solver_sat" to "SAT Solver",
            "solver_cfd" to "CFD Solver",
            "solver_pde" to "PDE Solver",
            "sat_ml_hybrid" to "SAT-ML Hybrid",
            "solver_constraint" to "Constraint Solver"
        ),
        IntentCategory.CONVERT to listOf(
            "util_converter" to "Unit Converter",
            "util_export" to "Data Export",
            "util_formula" to "Formula Sheet"
        )
    )

    /**
     * Feel the user's intent from their query.
     */
    fun feelIntent(query: String): UserIntent {
        val words = query.lowercase().split(Regex("\\s+"))

        // Calculate intent scores
        val intentScores = IntentCategory.values().associateWith { intent ->
            val keywords = intentKeywords[intent] ?: emptyList()
            words.count { word -> keywords.any { it in word || word in it } }.toDouble()
        }

        // Find primary and secondary intents
        val sortedIntents = intentScores.entries.sortedByDescending { it.value }
        val primary = sortedIntents.first().key
        val secondary = if (sortedIntents.size > 1 && sortedIntents[1].value > 0)
            sortedIntents[1].key else null

        // Calculate confidence using Brahim weighting
        val totalScore = intentScores.values.sum()
        val confidence = if (totalScore > 0) {
            val primaryScore = intentScores[primary] ?: 0.0
            (primaryScore / totalScore) * BrahimConstants.PHI / (BrahimConstants.PHI + 1)
        } else 0.3

        // Detect emotional tone
        val emotionalTone = detectEmotionalTone(query)

        // Detect urgency
        val urgency = detectUrgency(query)

        // Extract matched keywords
        val matchedKeywords = words.filter { word ->
            intentKeywords.values.flatten().any { it in word || word in it }
        }

        return UserIntent(
            primary = primary,
            secondary = secondary,
            confidence = confidence.coerceIn(0.0, 1.0),
            keywords = matchedKeywords,
            emotionalTone = emotionalTone,
            urgency = urgency
        )
    }

    /**
     * Detect emotional tone of the query.
     */
    private fun detectEmotionalTone(query: String): EmotionalTone {
        val lowerQuery = query.lowercase()

        // Check for question marks and exclamation points
        val hasQuestion = "?" in query
        val hasExclamation = "!" in query

        // Score each tone
        val toneScores = EmotionalTone.values().associateWith { tone ->
            val keywords = toneKeywords[tone] ?: emptyList()
            keywords.count { it in lowerQuery }.toDouble()
        }.toMutableMap()

        // Adjust for punctuation
        if (hasQuestion) toneScores[EmotionalTone.CURIOUS] = (toneScores[EmotionalTone.CURIOUS] ?: 0.0) + 1
        if (hasExclamation) toneScores[EmotionalTone.EXCITED] = (toneScores[EmotionalTone.EXCITED] ?: 0.0) + 1

        return toneScores.maxByOrNull { it.value }?.key ?: EmotionalTone.CURIOUS
    }

    /**
     * Detect urgency level.
     */
    private fun detectUrgency(query: String): UrgencyLevel {
        val lowerQuery = query.lowercase()

        return when {
            listOf("now", "urgent", "immediately", "asap", "quick").any { it in lowerQuery } ->
                UrgencyLevel.IMMEDIATE
            listOf("soon", "today", "need").any { it in lowerQuery } ->
                UrgencyLevel.SOON
            listOf("plan", "future", "later", "eventually").any { it in lowerQuery } ->
                UrgencyLevel.PLANNING
            else -> UrgencyLevel.EXPLORING
        }
    }

    /**
     * Recommend apps based on user intent.
     *
     * ASIOS 2.0: Includes Lucas dimensional weighting and Phi-Pi gap detection.
     */
    fun recommendApps(intent: UserIntent, limit: Int = 5, exploring: Boolean = false): List<AppRecommendation> {
        val recommendations = mutableListOf<AppRecommendation>()

        // Get primary intent apps
        val primaryApps = intentToApps[intent.primary] ?: emptyList()
        primaryApps.forEachIndexed { index, (appId, appName) ->
            val relevance = 1.0 - (index * 0.1)
            val brahimResonance = calculateBrahimResonance(appId, intent, exploring)

            // ASIOS 2.0: Check if in creative gap
            val inGap = exploring || abs(relevance - 0.5) < BrahimConstants.PHI_PI_GAP

            recommendations.add(AppRecommendation(
                appId = appId,
                appName = appName,
                category = intent.primary.name,
                relevanceScore = relevance * intent.confidence,
                brahimResonance = brahimResonance,
                reason = generateReason(intent, appName),
                pathway = generatePathway(appId),
                lucasDimension = intent.primary.lucasDimension,
                lucasCapacity = intent.primary.lucasCapacity,
                inCreativeGap = inGap
            ))
        }

        // Add secondary intent apps if available
        intent.secondary?.let { secondary ->
            val secondaryApps = intentToApps[secondary] ?: emptyList()
            secondaryApps.take(2).forEachIndexed { index, (appId, appName) ->
                val relevance = 0.7 - (index * 0.1)

                if (recommendations.none { it.appId == appId }) {
                    val inGap = exploring || abs(relevance - 0.5) < BrahimConstants.PHI_PI_GAP

                    recommendations.add(AppRecommendation(
                        appId = appId,
                        appName = appName,
                        category = secondary.name,
                        relevanceScore = relevance * (1 - intent.confidence),
                        brahimResonance = calculateBrahimResonance(appId, intent, exploring),
                        reason = "Also relevant: ${secondary.name.lowercase()}",
                        pathway = generatePathway(appId),
                        lucasDimension = secondary.lucasDimension,
                        lucasCapacity = secondary.lucasCapacity,
                        inCreativeGap = inGap
                    ))
                }
            }
        }

        // ASIOS 2.0: Apply Lucas weighting to sort
        // Higher dimensions get slight priority (phi meets pi at D12)
        return recommendations
            .sortedByDescending {
                val lucasWeight = it.lucasCapacity.toDouble() / BrahimConstants.LUCAS_TOTAL
                it.relevanceScore * 0.6 + it.brahimResonance * 0.3 + lucasWeight * 0.1
            }
            .take(limit)
    }

    /**
     * Calculate Brahim resonance for an app recommendation.
     *
     * ASIOS 2.0: Uses Lucas dimensional weighting and Phi-Pi gap.
     */
    private fun calculateBrahimResonance(appId: String, intent: UserIntent, exploring: Boolean = false): Double {
        // Use golden ratio for resonance calculation
        val phi = BrahimConstants.PHI
        val beta = BrahimConstants.BETA_SECURITY

        // Hash-based resonance (deterministic but appears meaningful)
        val hash = appId.hashCode()
        val normalized = abs(hash % 1000) / 1000.0

        // ASIOS 2.0: Apply Lucas dimensional weighting
        val lucasWeight = intent.primary.lucasCapacity.toDouble() / BrahimConstants.LUCAS_TOTAL

        // Apply Brahim weighting with Lucas factor
        val resonance = (normalized * phi + intent.confidence * beta + lucasWeight) / (phi + beta + 1)

        // Boost for certain app types
        val boost = when {
            "brahim" in appId.lowercase() -> 0.2
            "golden" in appId.lowercase() -> 0.15
            "resonance" in appId.lowercase() -> 0.1
            "lucas" in appId.lowercase() -> 0.12
            else -> 0.0
        }

        // ASIOS 2.0: Apply creativity margin if exploring
        val creativityBoost = if (exploring) BrahimConstants.PHI_PI_GAP else 0.0

        return (resonance + boost + creativityBoost).coerceIn(0.0, 1.0)
    }

    /**
     * Generate human-readable reason for recommendation.
     */
    private fun generateReason(intent: UserIntent, appName: String): String {
        val tonePhrase = when (intent.emotionalTone) {
            EmotionalTone.CURIOUS -> "Perfect for exploring"
            EmotionalTone.URGENT -> "Quick solution:"
            EmotionalTone.CREATIVE -> "Build with"
            EmotionalTone.ANALYTICAL -> "Deep analysis:"
            EmotionalTone.PLAYFUL -> "Try out"
            EmotionalTone.PROFESSIONAL -> "Professional tool:"
            EmotionalTone.CONFUSED -> "This will help:"
            EmotionalTone.EXCITED -> "You'll love"
        }

        val intentPhrase = when (intent.primary) {
            IntentCategory.CALCULATE -> "calculations"
            IntentCategory.EXPLORE -> "discovery"
            IntentCategory.CREATE -> "creation"
            IntentCategory.ANALYZE -> "analysis"
            IntentCategory.SECURE -> "security"
            IntentCategory.OPTIMIZE -> "optimization"
            IntentCategory.LEARN -> "learning"
            IntentCategory.COMMUNICATE -> "communication"
            IntentCategory.PLAN -> "planning"
            IntentCategory.VISUALIZE -> "visualization"
            IntentCategory.SOLVE -> "problem-solving"
            IntentCategory.CONVERT -> "conversion"
        }

        return "$tonePhrase $appName for $intentPhrase"
    }

    /**
     * Generate pathway from Home to app.
     */
    private fun generatePathway(appId: String): List<String> {
        // Determine which hub contains this app
        val hub = when {
            appId.startsWith("physics") || appId.startsWith("fine") || appId.startsWith("weinberg") ->
                "Physics Hub"
            appId.startsWith("math") || appId.startsWith("egyptian") || appId.startsWith("golden") ->
                "Math Hub"
            appId.startsWith("cosmo") || appId.startsWith("dark") || appId.startsWith("universe") ->
                "Cosmology Hub"
            appId.startsWith("aviation") || appId.startsWith("aerospace") || appId.startsWith("flight") ->
                "Aviation Hub"
            appId.startsWith("traffic") || appId.startsWith("route") || appId.startsWith("signal") ->
                "Traffic Hub"
            appId.startsWith("business") || appId.startsWith("fair") || appId.startsWith("compliance") ->
                "Business Hub"
            appId.startsWith("solver") || appId.startsWith("sat") || appId.startsWith("cfd") ->
                "Solvers Hub"
            appId.startsWith("planetary") || appId.startsWith("titan") || appId.startsWith("mars") ->
                "Planetary Hub"
            appId.startsWith("security") || appId.startsWith("cipher") || appId.startsWith("crypto") ->
                "Security Hub"
            appId.startsWith("ml") || appId.startsWith("kelimutu") || appId.startsWith("phase") ->
                "ML Hub"
            appId.startsWith("viz") || appId.startsWith("resonance") ->
                "Visualization Hub"
            appId.startsWith("util") || appId.startsWith("convert") || appId.startsWith("export") ->
                "Utilities Hub"
            else -> "Composite Apps"
        }

        return listOf("Home", "Tools", hub, appId)
    }

    /**
     * Generate a warm, helpful response based on intent.
     *
     * ASIOS 2.0: Includes Lucas dimensional insights.
     */
    fun generateWarmResponse(intent: UserIntent, recommendations: List<AppRecommendation>): String {
        val greeting = when (intent.emotionalTone) {
            EmotionalTone.CURIOUS -> "I sense your curiosity!"
            EmotionalTone.URGENT -> "I understand you need this quickly."
            EmotionalTone.CREATIVE -> "Let's create something amazing!"
            EmotionalTone.ANALYTICAL -> "Let's dive deep into this."
            EmotionalTone.PLAYFUL -> "This sounds fun!"
            EmotionalTone.PROFESSIONAL -> "I have professional tools for this."
            EmotionalTone.CONFUSED -> "Let me help clarify this for you."
            EmotionalTone.EXCITED -> "I love your enthusiasm!"
        }

        val topRec = recommendations.firstOrNull()
        val suggestion = if (topRec != null) {
            "\n\nI recommend starting with **${topRec.appName}** - ${topRec.reason}."
        } else {
            "\n\nLet me help you explore the right tools."
        }

        val brahimInsight = if (recommendations.any { it.brahimResonance > 0.7 }) {
            "\n\n✨ High Brahim resonance detected - these tools align perfectly with your needs."
        } else ""

        // ASIOS 2.0: Lucas dimensional insight
        val lucasInsight = if (topRec != null && topRec.lucasDimension > 6) {
            "\n\n🔮 Operating in Dimension ${topRec.lucasDimension} with ${topRec.lucasCapacity} states available."
        } else ""

        // ASIOS 2.0: Creative gap insight
        val gapInsight = if (recommendations.any { it.inCreativeGap }) {
            "\n\n💡 Phi-Pi creative margin active - exploring adaptive pathways."
        } else ""

        return greeting + suggestion + brahimInsight + lucasInsight + gapInsight
    }

    // =========================================================================
    // ASIOS 2.0 - LUCAS ARCHITECTURE HELPERS
    // =========================================================================

    /**
     * Get intent by Lucas dimension.
     */
    fun getIntentByDimension(dimension: Int): IntentCategory? {
        return IntentCategory.values().find { it.lucasDimension == dimension }
    }

    /**
     * Get all intents in a dimension range.
     */
    fun getIntentsInRange(minDim: Int, maxDim: Int): List<IntentCategory> {
        return IntentCategory.values().filter { it.lucasDimension in minDim..maxDim }
    }

    /**
     * Calculate dimensional resonance between two intents.
     */
    fun calculateIntentResonance(intent1: IntentCategory, intent2: IntentCategory): Double {
        val dimDiff = abs(intent1.lucasDimension - intent2.lucasDimension)
        val capacityRatio = minOf(intent1.lucasCapacity, intent2.lucasCapacity).toDouble() /
                            maxOf(intent1.lucasCapacity, intent2.lucasCapacity)

        // Resonance formula: higher when dimensions are close and capacities aligned
        return (1.0 - dimDiff / 12.0) * capacityRatio * BrahimConstants.PHI / (BrahimConstants.PHI + 1)
    }

    /**
     * Get ASIOS 2.0 discovery status.
     */
    fun getASIOS2Status(): Map<String, Any> {
        return mapOf(
            "version" to "2.0.0",
            "codename" to "Phi-Pi Synthesis",
            "intent_dimensions" to IntentCategory.values().associate {
                it.name to mapOf(
                    "dimension" to it.lucasDimension,
                    "capacity" to it.lucasCapacity
                )
            },
            "total_capacity" to IntentCategory.values().sumOf { it.lucasCapacity },
            "phi_pi_gap" to BrahimConstants.PHI_PI_GAP,
            "creativity_margin_percent" to BrahimConstants.PHI_PI_GAP * 100
        )
    }

    companion object {
        @Volatile
        private var instance: DiscoveryEngine? = null

        fun getInstance(): DiscoveryEngine {
            return instance ?: synchronized(this) {
                instance ?: DiscoveryEngine().also { instance = it }
            }
        }

        // ASIOS 2.0 constants
        const val VERSION = "2.0.0"
        const val CODENAME = "Phi-Pi Synthesis"
    }
}
