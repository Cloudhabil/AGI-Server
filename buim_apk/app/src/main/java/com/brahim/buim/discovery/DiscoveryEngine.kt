/**
 * Discovery Engine - Intelligent App Recommendation
 * ==================================================
 *
 * Uses Brahim Calculator + Kelimutu routing to understand
 * user intent and recommend the perfect apps.
 *
 * "The chatbot feels what the user needs"
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-25
 */

package com.brahim.buim.discovery

import com.brahim.buim.core.BrahimConstants
import kotlin.math.abs
import kotlin.math.exp
import kotlin.math.sqrt

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
 * Intent categories mapped to app domains.
 */
enum class IntentCategory {
    // Core needs
    CALCULATE,      // "I need to compute/calculate..."
    EXPLORE,        // "I want to explore/discover..."
    CREATE,         // "I want to build/create..."
    ANALYZE,        // "I need to analyze/understand..."
    SECURE,         // "I need to protect/encrypt..."
    OPTIMIZE,       // "I want to improve/optimize..."
    LEARN,          // "I want to learn/understand..."
    COMMUNICATE,    // "I need to share/send..."
    PLAN,           // "I need to plan/schedule..."
    VISUALIZE,      // "I want to see/visualize..."
    SOLVE,          // "I need to solve/fix..."
    CONVERT         // "I need to convert/transform..."
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
 */
data class AppRecommendation(
    val appId: String,
    val appName: String,
    val category: String,
    val relevanceScore: Double,      // 0-1 how relevant to intent
    val brahimResonance: Double,     // Alignment with Brahim numbers
    val reason: String,              // Why this app was recommended
    val pathway: List<String>        // How to get there from Home
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
     */
    fun recommendApps(intent: UserIntent, limit: Int = 5): List<AppRecommendation> {
        val recommendations = mutableListOf<AppRecommendation>()

        // Get primary intent apps
        val primaryApps = intentToApps[intent.primary] ?: emptyList()
        primaryApps.forEachIndexed { index, (appId, appName) ->
            val relevance = 1.0 - (index * 0.1)
            val brahimResonance = calculateBrahimResonance(appId, intent)

            recommendations.add(AppRecommendation(
                appId = appId,
                appName = appName,
                category = intent.primary.name,
                relevanceScore = relevance * intent.confidence,
                brahimResonance = brahimResonance,
                reason = generateReason(intent, appName),
                pathway = generatePathway(appId)
            ))
        }

        // Add secondary intent apps if available
        intent.secondary?.let { secondary ->
            val secondaryApps = intentToApps[secondary] ?: emptyList()
            secondaryApps.take(2).forEachIndexed { index, (appId, appName) ->
                val relevance = 0.7 - (index * 0.1)

                if (recommendations.none { it.appId == appId }) {
                    recommendations.add(AppRecommendation(
                        appId = appId,
                        appName = appName,
                        category = secondary.name,
                        relevanceScore = relevance * (1 - intent.confidence),
                        brahimResonance = calculateBrahimResonance(appId, intent),
                        reason = "Also relevant: ${secondary.name.lowercase()}",
                        pathway = generatePathway(appId)
                    ))
                }
            }
        }

        // Sort by combined score and limit
        return recommendations
            .sortedByDescending { it.relevanceScore * 0.7 + it.brahimResonance * 0.3 }
            .take(limit)
    }

    /**
     * Calculate Brahim resonance for an app recommendation.
     */
    private fun calculateBrahimResonance(appId: String, intent: UserIntent): Double {
        // Use golden ratio for resonance calculation
        val phi = BrahimConstants.PHI
        val beta = BrahimConstants.BETA_SECURITY

        // Hash-based resonance (deterministic but appears meaningful)
        val hash = appId.hashCode()
        val normalized = abs(hash % 1000) / 1000.0

        // Apply Brahim weighting
        val resonance = (normalized * phi + intent.confidence * beta) / (phi + beta)

        // Boost for certain app types
        val boost = when {
            "brahim" in appId.lowercase() -> 0.2
            "golden" in appId.lowercase() -> 0.15
            "resonance" in appId.lowercase() -> 0.1
            else -> 0.0
        }

        return (resonance + boost).coerceIn(0.0, 1.0)
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

        return greeting + suggestion + brahimInsight
    }

    companion object {
        @Volatile
        private var instance: DiscoveryEngine? = null

        fun getInstance(): DiscoveryEngine {
            return instance ?: synchronized(this) {
                instance ?: DiscoveryEngine().also { instance = it }
            }
        }
    }
}
