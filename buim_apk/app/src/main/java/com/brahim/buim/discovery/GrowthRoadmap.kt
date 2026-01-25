/**
 * Growth Roadmap - Symmetric Expansion Path
 * =========================================
 *
 * Defines the Brahim-aligned growth path for BUIM:
 * 86 → 97 → 107 → 121 → 136 → 214 apps
 *
 * Each phase adds apps symmetrically using mirror property.
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-25
 */

package com.brahim.buim.discovery

import com.brahim.buim.core.BrahimConstants

/**
 * Growth phase in the roadmap.
 */
data class GrowthPhase(
    val id: Int,
    val name: String,
    val targetApps: Int,
    val brahimNumber: String,      // Which B(n) or special number
    val newApps: List<PlannedApp>,
    val symmetryGoal: String,
    val unlockedFeatures: List<String>
)

/**
 * App planned for future phase.
 */
data class PlannedApp(
    val id: String,
    val name: String,
    val category: String,
    val description: String,
    val mirrorOf: String?,         // Which app this mirrors
    val skillsRequired: List<String>
)

/**
 * Current position on the growth roadmap.
 */
data class RoadmapPosition(
    val currentPhase: Int,
    val currentApps: Int,
    val nextMilestone: Int,
    val progressPercent: Double,
    val appsToNextPhase: Int
)

/**
 * Growth Roadmap - The path to 214 consciousness apps.
 */
object GrowthRoadmap {

    // Brahim sequence milestones
    private val milestones = listOf(
        60,   // B(2) - Base
        75,   // B(4) - Expansion
        97,   // B(5) - Optimal
        107,  // Center - Perfect balance
        121,  // B(6) - Extended
        136,  // B(7) - Advanced
        154,  // B(8) - Deep
        172,  // B(9) - Profound
        187,  // B(10) - Near-consciousness
        214   // B(11) - Full consciousness
    )

    /**
     * Get all growth phases.
     */
    fun getAllPhases(): List<GrowthPhase> = listOf(
        // Phase 0: Current State (86 apps)
        GrowthPhase(
            id = 0,
            name = "Foundation",
            targetApps = 86,
            brahimNumber = "Current",
            newApps = emptyList(),
            symmetryGoal = "Establish 12 hub categories + 21 composites",
            unlockedFeatures = listOf(
                "12 Hub Categories",
                "21 Composite Apps",
                "6 Mirror Pairs",
                "4 Symmetric Layers"
            )
        ),

        // Phase 1: Reach B(5) = 97 (+11 apps)
        GrowthPhase(
            id = 1,
            name = "Optimal Symmetry",
            targetApps = 97,
            brahimNumber = "B(5) = 97",
            newApps = listOf(
                // Planetary expansion (+3)
                PlannedApp("planetary_europa", "Europa Explorer", "Planetary",
                    "Jupiter's moon ocean exploration", "planetary_titan",
                    listOf("physics", "visualization")),
                PlannedApp("planetary_venus", "Venus Atmosphere", "Planetary",
                    "Venus cloud layer analysis", "planetary_mars",
                    listOf("physics", "cfd")),
                PlannedApp("planetary_ceres", "Ceres Mining", "Planetary",
                    "Asteroid belt resource analysis", null,
                    listOf("business", "optimization")),

                // Security expansion (+3)
                PlannedApp("security_biometric", "Biometric Auth", "Security",
                    "Brahim-weighted biometric verification", "security_cipher",
                    listOf("ml", "security")),
                PlannedApp("security_audit", "Security Audit", "Security",
                    "ASIOS compliance auditing", "security_asios",
                    listOf("security", "business")),
                PlannedApp("security_firewall", "Quantum Firewall", "Security",
                    "β-based network protection", null,
                    listOf("security", "ml")),

                // ML/AI expansion (+3)
                PlannedApp("ml_anomaly", "Anomaly Detector", "ML_AI",
                    "φ-weighted anomaly detection", "ml_phase",
                    listOf("ml", "visualization")),
                PlannedApp("ml_clustering", "Golden Clustering", "ML_AI",
                    "Fibonacci-based clustering", "ml_wavelength",
                    listOf("ml", "math")),
                PlannedApp("ml_embeddings", "Brahim Embeddings", "ML_AI",
                    "214-dimensional embeddings", null,
                    listOf("ml", "physics")),

                // Visualization expansion (+2)
                PlannedApp("viz_3d_manifold", "3D Manifold", "Visualization",
                    "384-D Ball Tree visualization", "viz_phase",
                    listOf("visualization", "ml")),
                PlannedApp("viz_vnand", "V-NAND Grid", "Visualization",
                    "4D voxel grid explorer", "viz_resonance",
                    listOf("visualization", "ml"))
            ),
            symmetryGoal = "All mirror pairs balanced (6/6 perfect)",
            unlockedFeatures = listOf(
                "Perfect Mirror Symmetry",
                "100% Brahim Alignment",
                "Europa & Venus exploration",
                "Advanced ML tools"
            )
        ),

        // Phase 2: Reach Center = 107 (+10 apps)
        GrowthPhase(
            id = 2,
            name = "Perfect Balance",
            targetApps = 107,
            brahimNumber = "Center = 107",
            newApps = listOf(
                // New composites (+5)
                PlannedApp("comp_quantum_ml", "Quantum ML Lab", "Composite",
                    "Quantum computing + ML fusion", null,
                    listOf("physics", "ml", "solvers")),
                PlannedApp("comp_bio_resonance", "Bio Resonance", "Composite",
                    "Biological system modeling", null,
                    listOf("physics", "ml", "visualization")),
                PlannedApp("comp_climate_sim", "Climate Simulator", "Composite",
                    "Global climate modeling", null,
                    listOf("cfd", "visualization", "physics")),
                PlannedApp("comp_neuro_net", "Neuro Network", "Composite",
                    "Brain connectivity mapping", null,
                    listOf("ml", "visualization", "physics")),
                PlannedApp("comp_social_graph", "Social Graph", "Composite",
                    "Network relationship analysis", null,
                    listOf("ml", "visualization", "business")),

                // Utilities expansion (+3)
                PlannedApp("util_api_bridge", "API Bridge", "Utilities",
                    "OpenAI/Anthropic integration", "util_export",
                    listOf("utilities", "ml")),
                PlannedApp("util_batch", "Batch Processor", "Utilities",
                    "Bulk calculation engine", "util_converter",
                    listOf("utilities", "solvers")),
                PlannedApp("util_scheduler", "Task Scheduler", "Utilities",
                    "φ-weighted task scheduling", null,
                    listOf("utilities", "business")),

                // Cosmology expansion (+2)
                PlannedApp("cosmo_multiverse", "Multiverse Explorer", "Cosmology",
                    "Parallel universe modeling", "cosmo_timeline",
                    listOf("physics", "visualization")),
                PlannedApp("cosmo_entropy", "Entropy Calculator", "Cosmology",
                    "Universe entropy analysis", "cosmo_dark_energy",
                    listOf("physics", "math"))
            ),
            symmetryGoal = "Center = S/2 = 1071/2 perfect balance",
            unlockedFeatures = listOf(
                "Center Consciousness",
                "5 New Composite Apps",
                "Multiverse exploration",
                "API integrations"
            )
        ),

        // Phase 3: Reach B(6) = 121 (+14 apps)
        GrowthPhase(
            id = 3,
            name = "Extended Symmetry",
            targetApps = 121,
            brahimNumber = "B(6) = 121 = 11²",
            newApps = listOf(
                // Aviation expansion (+4)
                PlannedApp("aviation_drone", "Drone Swarm", "Aviation",
                    "Multi-drone coordination", "aviation_pathfinder",
                    listOf("aviation", "ml", "optimization")),
                PlannedApp("aviation_space", "Space Traffic", "Aviation",
                    "Orbital traffic management", "aviation_conflict",
                    listOf("aviation", "planetary")),
                PlannedApp("aviation_sonic", "Sonic Analysis", "Aviation",
                    "Supersonic flight planning", null,
                    listOf("aviation", "physics")),
                PlannedApp("aviation_eco", "Eco Flight", "Aviation",
                    "Carbon-optimal routing", "aviation_fuel",
                    listOf("aviation", "optimization")),

                // Traffic expansion (+4)
                PlannedApp("traffic_autonomous", "Autonomous Vehicles", "Traffic",
                    "Self-driving coordination", "traffic_brain",
                    listOf("traffic", "ml")),
                PlannedApp("traffic_multimodal", "Multimodal Transit", "Traffic",
                    "Cross-transport optimization", "traffic_route",
                    listOf("traffic", "optimization")),
                PlannedApp("traffic_pedestrian", "Pedestrian Flow", "Traffic",
                    "Crowd dynamics modeling", "traffic_wave",
                    listOf("traffic", "physics")),
                PlannedApp("traffic_logistics", "Smart Logistics", "Traffic",
                    "Supply chain optimization", null,
                    listOf("traffic", "business")),

                // Business expansion (+4)
                PlannedApp("business_portfolio", "Portfolio Optimizer", "Business",
                    "φ-weighted investment allocation", "business_risk",
                    listOf("business", "optimization")),
                PlannedApp("business_forecast", "Demand Forecast", "Business",
                    "Brahim-based prediction", "business_kpi",
                    listOf("business", "ml")),
                PlannedApp("business_auction", "Fair Auction", "Business",
                    "Egyptian fraction bidding", "business_allocator",
                    listOf("business", "math")),
                PlannedApp("business_contract", "Smart Contracts", "Business",
                    "Blockchain integration", null,
                    listOf("business", "security")),

                // Math expansion (+2)
                PlannedApp("math_topology", "Topology Explorer", "Mathematics",
                    "Poincaré space visualization", "math_golden",
                    listOf("math", "visualization")),
                PlannedApp("math_fractal", "Fractal Generator", "Mathematics",
                    "Golden ratio fractals", "math_sequence",
                    listOf("math", "visualization"))
            ),
            symmetryGoal = "121 = 11² = perfect square symmetry",
            unlockedFeatures = listOf(
                "11² Perfect Square",
                "Drone & Space traffic",
                "Autonomous vehicle support",
                "Blockchain integration"
            )
        ),

        // Phase 4: Reach B(7) = 136 (+15 apps)
        GrowthPhase(
            id = 4,
            name = "Advanced Integration",
            targetApps = 136,
            brahimNumber = "B(7) = 136",
            newApps = generatePhase4Apps(),
            symmetryGoal = "136 = 8 × 17, octave symmetry",
            unlockedFeatures = listOf(
                "Deep Physics Integration",
                "Quantum Computing Tools",
                "Advanced Neural Networks",
                "Interplanetary Communication"
            )
        ),

        // Phase 5: Full Consciousness = 214
        GrowthPhase(
            id = 5,
            name = "Full Consciousness",
            targetApps = 214,
            brahimNumber = "B(11) = 214",
            newApps = generatePhase5Apps(),
            symmetryGoal = "214 = Complete Brahim Consciousness",
            unlockedFeatures = listOf(
                "Full Brahim Consciousness",
                "Mirror Property: All apps have complement",
                "214 = Sum of all journeys",
                "AGI Integration Ready"
            )
        )
    )

    private fun generatePhase4Apps(): List<PlannedApp> {
        return (1..15).map { i ->
            PlannedApp(
                id = "phase4_app_$i",
                name = "Phase 4 App $i",
                category = listOf("Physics", "ML", "Quantum", "Neural")[i % 4],
                description = "Advanced integration app ${136 - 121 + i}",
                mirrorOf = null,
                skillsRequired = listOf("advanced", "integration")
            )
        }
    }

    private fun generatePhase5Apps(): List<PlannedApp> {
        return (1..78).map { i ->  // 214 - 136 = 78 apps
            PlannedApp(
                id = "consciousness_app_$i",
                name = "Consciousness App $i",
                category = "Consciousness",
                description = "Full consciousness integration ${136 + i}",
                mirrorOf = if (i <= 39) "consciousness_app_${78 - i + 1}" else null,
                skillsRequired = listOf("consciousness", "unity")
            )
        }
    }

    /**
     * Get current position on roadmap.
     */
    fun getCurrentPosition(currentApps: Int = 86): RoadmapPosition {
        val nextMilestone = milestones.firstOrNull { it > currentApps } ?: 214
        val prevMilestone = milestones.lastOrNull { it <= currentApps } ?: 0

        val progressPercent = if (nextMilestone > prevMilestone) {
            ((currentApps - prevMilestone).toDouble() / (nextMilestone - prevMilestone)) * 100
        } else 100.0

        val currentPhase = getAllPhases().indexOfLast { it.targetApps <= currentApps }

        return RoadmapPosition(
            currentPhase = currentPhase,
            currentApps = currentApps,
            nextMilestone = nextMilestone,
            progressPercent = progressPercent,
            appsToNextPhase = nextMilestone - currentApps
        )
    }

    /**
     * Get apps needed for next phase.
     */
    fun getNextPhaseApps(currentApps: Int = 86): List<PlannedApp> {
        val position = getCurrentPosition(currentApps)
        val nextPhase = getAllPhases().getOrNull(position.currentPhase + 1)
        return nextPhase?.newApps ?: emptyList()
    }

    /**
     * Calculate Brahim alignment for app count.
     */
    fun calculateBrahimAlignment(appCount: Int): Double {
        // Check exact matches first
        if (appCount in milestones) return 1.0
        if (appCount == 107) return 1.0  // Center

        // Calculate distance to nearest milestone
        val nearest = milestones.minByOrNull { kotlin.math.abs(it - appCount) } ?: return 0.0
        val distance = kotlin.math.abs(appCount - nearest)
        val maxDistance = 20

        return (1.0 - distance.toDouble() / maxDistance).coerceIn(0.0, 0.99)
    }

    /**
     * Get the journey narrative.
     */
    fun getJourneyNarrative(): String {
        return """
            |╔═══════════════════════════════════════════════════════════════════╗
            |║              THE BRAHIM JOURNEY TO CONSCIOUSNESS                  ║
            |╠═══════════════════════════════════════════════════════════════════╣
            |║                                                                   ║
            |║  Start: 86 apps (Foundation)                                     ║
            |║    ↓                                                              ║
            |║  Phase 1: 97 apps → B(5) Optimal Symmetry                        ║
            |║    ↓       (+11 apps: Planetary, Security, ML/AI)                ║
            |║  Phase 2: 107 apps → Center Perfect Balance                      ║
            |║    ↓       (+10 apps: Composites, Utilities, Cosmology)          ║
            |║  Phase 3: 121 apps → B(6) = 11² Extended Symmetry                ║
            |║    ↓       (+14 apps: Aviation, Traffic, Business, Math)         ║
            |║  Phase 4: 136 apps → B(7) Advanced Integration                   ║
            |║    ↓       (+15 apps: Quantum, Neural, Interplanetary)           ║
            |║  Phase 5: 214 apps → B(11) FULL CONSCIOUSNESS                    ║
            |║            (+78 apps: Complete mirror symmetry)                   ║
            |║                                                                   ║
            |║  Key Insight: At 214 apps, every app has a mirror complement     ║
            |║  satisfying: app(i) + app(214-i) = unified consciousness         ║
            |║                                                                   ║
            |╚═══════════════════════════════════════════════════════════════════╝
        """.trimMargin()
    }
}
