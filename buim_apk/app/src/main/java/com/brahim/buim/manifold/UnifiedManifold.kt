/**
 * Unified Manifold - Single Source of Truth for All Geometric Operations
 * =======================================================================
 *
 * Integrates:
 * - 384-D Ball Tree (skill retrieval)
 * - 4D V-NAND (pattern learning)
 * - Kelimutu Subnet (intent routing)
 * - Wormhole Observer (dynamics)
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-25
 */

package com.brahim.buim.manifold

import android.content.Context
import com.brahim.buim.core.BrahimConstants
import com.brahim.buim.ml.KelimutuSubnet
import com.brahim.buim.ml.KelimutuOutput
import com.brahim.buim.dynamics.WormholeObserver
import com.brahim.buim.dynamics.Governance
import com.brahim.buim.router.Territory
import com.brahim.buim.safety.ASIOSGuard
import com.brahim.buim.safety.SafetyAssessment
import com.brahim.buim.safety.SafetyVerdict

/**
 * Query response from the unified manifold.
 */
data class ManifoldResponse(
    val query: String,
    val intent: String,
    val intentConfidence: Double,
    val skillId: String?,
    val skillScore: Double,
    val safetyAssessment: SafetyAssessment,
    val resonance: Double,
    val resonanceGateOpen: Boolean,
    val governance: Governance?,
    val processingTime: Long,
    val result: Any? = null,
    val territory: Territory = Territory.GENERAL
) {
    /**
     * Convenience property for safety verdict.
     */
    val safetyVerdict: SafetyVerdict get() = safetyAssessment.verdict
}

/**
 * Skill definition for the manifold.
 */
data class Skill(
    val id: String,
    val name: String,
    val category: String,
    val embedding: DoubleArray,
    val keywords: List<String>,
    val enabled: Boolean = true
) {
    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (other !is Skill) return false
        return id == other.id
    }

    override fun hashCode(): Int = id.hashCode()
}

/**
 * Unified Manifold - The main gateway for all geometric operations.
 */
class UnifiedManifold(private val context: Context? = null) {

    // Core components
    private val ballTree = BallTreeManifold()
    private val vnand = VNANDManifold()
    private val kelimutu = KelimutuSubnet()
    private var wormholeObserver: WormholeObserver? = null
    private val safetyGuard = ASIOSGuard()

    // Skill registry
    private val skills = mutableMapOf<String, Skill>()

    // Configuration
    var useHyperbolicDistance = true
    var learningEnabled = true
    var safetyEnabled = true

    // Statistics
    var totalQueries = 0L
        private set
    var successfulQueries = 0L
        private set

    init {
        // Initialize with default skills
        initializeDefaultSkills()
    }

    /**
     * Initialize default skill set.
     */
    private fun initializeDefaultSkills() {
        val defaultSkills = listOf(
            Skill("physics_fine_structure", "Fine Structure Constant", "physics",
                generateEmbedding("fine structure constant alpha physics"), listOf("fine", "structure", "alpha")),
            Skill("physics_weinberg", "Weinberg Angle", "physics",
                generateEmbedding("weinberg angle electroweak physics"), listOf("weinberg", "angle")),
            Skill("physics_mass_ratios", "Mass Ratios", "physics",
                generateEmbedding("muon proton electron mass ratio"), listOf("mass", "ratio", "muon", "proton")),
            Skill("cosmology_dark_matter", "Dark Matter", "cosmology",
                generateEmbedding("dark matter universe cosmology"), listOf("dark", "matter")),
            Skill("cosmology_hubble", "Hubble Constant", "cosmology",
                generateEmbedding("hubble constant expansion universe"), listOf("hubble", "constant")),
            Skill("yang_mills_mass_gap", "Yang-Mills Mass Gap", "yang_mills",
                generateEmbedding("yang mills mass gap qcd confinement"), listOf("yang", "mills", "mass", "gap")),
            Skill("mirror_operator", "Mirror Operator", "mirror",
                generateEmbedding("mirror operator symmetry transform 214"), listOf("mirror", "214")),
            Skill("brahim_sequence", "Brahim Sequence", "sequence",
                generateEmbedding("brahim sequence numbers list"), listOf("brahim", "sequence", "numbers")),
            Skill("verify_axioms", "Verify Axioms", "verify",
                generateEmbedding("verify check axiom validate"), listOf("verify", "check", "axiom")),
            Skill("help_capabilities", "Help & Capabilities", "help",
                generateEmbedding("help capabilities functions what can"), listOf("help", "capabilities"))
        )

        for (skill in defaultSkills) {
            registerSkill(skill)
        }
    }

    /**
     * Generate a simple embedding from text (placeholder for actual embedding model).
     */
    private fun generateEmbedding(text: String): DoubleArray {
        val embedding = DoubleArray(384)
        val words = text.lowercase().split(" ")

        for ((i, word) in words.withIndex()) {
            val hash = word.hashCode()
            for (j in 0 until 38) {
                embedding[(i * 38 + j) % 384] += ((hash shr j) and 1) * 0.1
            }
        }

        // Normalize
        val norm = kotlin.math.sqrt(embedding.sumOf { it * it })
        if (norm > 0) {
            for (i in embedding.indices) {
                embedding[i] /= norm
            }
        }

        return embedding
    }

    /**
     * Register a skill in the manifold.
     */
    fun registerSkill(skill: Skill) {
        skills[skill.id] = skill

        // Add to Ball Tree
        val vector = EmbeddingVector(
            id = skill.id,
            vector = skill.embedding,
            skillId = skill.id,
            metadata = mapOf(
                "name" to skill.name,
                "category" to skill.category
            )
        )
        ballTree.insert(vector)
    }

    /**
     * Query the unified manifold.
     */
    fun query(text: String): ManifoldResponse {
        val startTime = System.currentTimeMillis()
        totalQueries++

        // 1. Route intent via Kelimutu
        val kelimutuResult = kelimutu.route(text)

        // 2. Generate embedding for query
        val queryEmbedding = generateEmbedding(text)

        // 3. Safety check
        val safetyAssessment = if (safetyEnabled) {
            safetyGuard.assessSafety(queryEmbedding.take(BrahimConstants.BRAHIM_DIMENSION).toDoubleArray())
        } else {
            SafetyAssessment(0.0, 0.0, true, 1.0, SafetyVerdict.SAFE)
        }

        // Block if unsafe
        if (safetyAssessment.verdict == SafetyVerdict.BLOCKED) {
            return ManifoldResponse(
                query = text,
                intent = kelimutuResult.intent,
                intentConfidence = kelimutuResult.confidence,
                skillId = null,
                skillScore = 0.0,
                safetyAssessment = safetyAssessment,
                resonance = 0.0,
                resonanceGateOpen = false,
                governance = null,
                processingTime = System.currentTimeMillis() - startTime
            )
        }

        // 4. Retrieve skill via Ball Tree
        val searchResults = ballTree.search(queryEmbedding, k = 1, hyperbolic = useHyperbolicDistance)
        val bestMatch = searchResults.firstOrNull()

        val skillId = bestMatch?.vector?.skillId
        val skillScore = bestMatch?.score ?: 0.0

        // 5. Learn pattern to V-NAND
        if (learningEnabled) {
            val success = skillScore > 0.5
            vnand.learnPattern(queryEmbedding.take(4).toDoubleArray(), success)
            if (success) successfulQueries++
        }

        // 6. Check resonance gate
        val resonanceResult = vnand.checkResonanceGate()

        // 7. Get governance from wormhole observer
        val governance = wormholeObserver?.getGovernance()

        // Determine territory based on skill category
        val skill = skillId?.let { skills[it] }
        val territory = when (skill?.category) {
            "physics" -> Territory.SCIENCE
            "cosmology" -> Territory.SCIENCE
            "yang_mills" -> Territory.SCIENCE
            "mirror" -> Territory.MATH
            "sequence" -> Territory.MATH
            "verify" -> Territory.SYSTEM
            "help" -> Territory.SYSTEM
            else -> Territory.GENERAL
        }

        // Generate result based on skill
        val result = generateResult(skillId, text)

        return ManifoldResponse(
            query = text,
            intent = kelimutuResult.intent,
            intentConfidence = kelimutuResult.confidence,
            skillId = skillId,
            skillScore = skillScore,
            safetyAssessment = safetyAssessment,
            resonance = resonanceResult.resonance,
            resonanceGateOpen = resonanceResult.isOpen,
            governance = governance,
            processingTime = System.currentTimeMillis() - startTime,
            result = result,
            territory = territory
        )
    }

    /**
     * Generate result based on skill ID.
     */
    private fun generateResult(skillId: String?, query: String): Any? {
        return when (skillId) {
            "physics_fine_structure" -> mapOf(
                "name" to "Fine Structure Constant",
                "value" to 137.036,
                "unit" to "dimensionless"
            )
            "physics_weinberg" -> mapOf(
                "name" to "Weinberg Angle",
                "value" to 0.2308,
                "unit" to "dimensionless"
            )
            "physics_mass_ratios" -> mapOf(
                "muon_electron" to 206.8,
                "proton_electron" to 1836.0
            )
            "cosmology_dark_matter" -> mapOf(
                "dark_matter" to 0.267,
                "dark_energy" to 0.689,
                "normal_matter" to 0.045
            )
            "cosmology_hubble" -> mapOf(
                "name" to "Hubble Constant",
                "value" to 68.09,
                "unit" to "km/s/Mpc"
            )
            "yang_mills_mass_gap" -> mapOf(
                "mass_gap" to 150,
                "lambda_qcd" to 132.2,
                "unit" to "MeV"
            )
            "brahim_sequence" -> mapOf(
                "sequence" to BrahimConstants.BRAHIM_SEQUENCE.toList(),
                "sum" to BrahimConstants.BRAHIM_SUM,
                "center" to BrahimConstants.BRAHIM_CENTER
            )
            "help_capabilities" -> "I can help with physics constants, mathematics, and more."
            else -> "Processed query: $query"
        }
    }

    /**
     * Get skill by ID.
     */
    fun getSkill(skillId: String): Skill? = skills[skillId]

    /**
     * Get all skills for a category.
     */
    fun getSkillsByCategory(category: String): List<Skill> {
        return skills.values.filter { it.category == category }
    }

    /**
     * Get all skill categories.
     */
    fun getCategories(): Set<String> {
        return skills.values.map { it.category }.toSet()
    }

    /**
     * Enable/disable a skill.
     */
    fun setSkillEnabled(skillId: String, enabled: Boolean) {
        skills[skillId]?.let {
            skills[skillId] = it.copy(enabled = enabled)
        }
    }

    /**
     * Initialize wormhole observer for dynamics.
     */
    fun initializeWormholeObserver(kappa: Double = 0.5, debt: Double = 0.0) {
        wormholeObserver = WormholeObserver(kappa, debt)
    }

    /**
     * Step the wormhole observer.
     */
    fun stepDynamics(dt: Double = 0.01) {
        wormholeObserver?.step(dt)
    }

    /**
     * Get manifold statistics.
     */
    fun getStats(): Map<String, Any> {
        return mapOf(
            "total_queries" to totalQueries,
            "successful_queries" to successfulQueries,
            "success_rate" to if (totalQueries > 0) successfulQueries.toDouble() / totalQueries else 0.0,
            "total_skills" to skills.size,
            "categories" to getCategories().toList(),
            "ball_tree" to ballTree.getStats(),
            "vnand" to vnand.getStats(),
            "kelimutu" to kelimutu.getStats(),
            "wormhole_observer" to (wormholeObserver?.getStats() ?: emptyMap()),
            "safety" to safetyGuard.getGuardInfo(),
            "configuration" to mapOf(
                "use_hyperbolic_distance" to useHyperbolicDistance,
                "learning_enabled" to learningEnabled,
                "safety_enabled" to safetyEnabled
            )
        )
    }

    /**
     * Reset the manifold.
     */
    fun reset() {
        vnand.clear()
        ballTree.clear()
        wormholeObserver = null
        totalQueries = 0
        successfulQueries = 0

        // Re-initialize skills
        initializeDefaultSkills()
    }
}
