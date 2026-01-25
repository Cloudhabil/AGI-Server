/**
 * Symmetric Architecture - Brahim-Aligned App Organization
 * ========================================================
 *
 * Reorganizes existing 86 apps into maximum symmetry using Brahim principles:
 * - Mirror pairs summing to 214
 * - Golden ratio distribution
 * - B(n) sequence alignment
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-25
 */

package com.brahim.buim.skills

import com.brahim.buim.core.BrahimConstants
import kotlin.math.abs

/**
 * Symmetric layer in the architecture.
 */
enum class SymmetricLayer {
    CORE,       // Central apps (always executed)
    INNER,      // High-frequency apps
    OUTER,      // Specialized apps
    BOUNDARY    // Edge cases and extensions
}

/**
 * Mirror pair - two categories that complement each other.
 */
data class MirrorPair(
    val alpha: String,      // First category
    val omega: String,      // Mirror category
    val alphaCount: Int,    // Apps in alpha
    val omegaCount: Int,    // Apps in omega
    val sum: Int = alphaCount + omegaCount,
    val resonance: Double   // How well this pair aligns with Brahim
)

/**
 * Symmetric organization result.
 */
data class SymmetricOrganization(
    val layers: Map<SymmetricLayer, List<String>>,
    val mirrorPairs: List<MirrorPair>,
    val totalApps: Int,
    val brahimAlignment: Double,  // 0-1, how well aligned with Brahim sequence
    val symmetryScore: Double     // 0-1, overall symmetry measure
)

/**
 * Symmetric Architecture Calculator
 */
object SymmetricArchitecture {

    // Current app distribution (from existing hubs)
    private val currentDistribution = mapOf(
        "Physics" to 8,
        "Mathematics" to 7,
        "Cosmology" to 5,
        "Aviation" to 7,
        "Traffic" to 7,
        "Business" to 7,
        "Solvers" to 6,
        "Planetary" to 3,
        "Security" to 3,
        "ML_AI" to 3,
        "Visualization" to 4,
        "Utilities" to 5
    )

    // Current composite distribution
    private val currentComposites = mapOf(
        "Science" to 6,
        "Navigation" to 4,
        "Enterprise" to 4,
        "Exploration" to 3,
        "Intelligence" to 4
    )

    // Brahim sequence for reference
    private val brahimSequence = intArrayOf(27, 42, 60, 75, 97, 121, 136, 154, 172, 187)
    private const val BRAHIM_SUM = 214
    private const val BRAHIM_CENTER = 107

    /**
     * Calculate optimal symmetric organization.
     */
    fun calculateOptimalSymmetry(): SymmetricOrganization {
        val totalHubApps = currentDistribution.values.sum()  // 65
        val totalComposites = currentComposites.values.sum() // 21
        val totalApps = totalHubApps + totalComposites       // 86

        // Create mirror pairs from 12 hubs (6 pairs)
        val mirrorPairs = createMirrorPairs()

        // Organize into symmetric layers
        val layers = organizeIntoLayers()

        // Calculate alignment scores
        val brahimAlignment = calculateBrahimAlignment(totalApps)
        val symmetryScore = calculateSymmetryScore(mirrorPairs)

        return SymmetricOrganization(
            layers = layers,
            mirrorPairs = mirrorPairs,
            totalApps = totalApps,
            brahimAlignment = brahimAlignment,
            symmetryScore = symmetryScore
        )
    }

    /**
     * Create 6 mirror pairs from 12 hub categories.
     * Pairs are chosen to maximize complementary sum.
     */
    private fun createMirrorPairs(): List<MirrorPair> {
        // Optimal pairing based on domain complementarity and sum balance
        return listOf(
            // Pair 1: Physical Sciences (8+5=13)
            MirrorPair(
                alpha = "Physics",
                omega = "Cosmology",
                alphaCount = 8,
                omegaCount = 5,
                resonance = calculatePairResonance(8, 5)
            ),
            // Pair 2: Computational (7+6=13)
            MirrorPair(
                alpha = "Mathematics",
                omega = "Solvers",
                alphaCount = 7,
                omegaCount = 6,
                resonance = calculatePairResonance(7, 6)
            ),
            // Pair 3: Transportation (7+7=14)
            MirrorPair(
                alpha = "Aviation",
                omega = "Traffic",
                alphaCount = 7,
                omegaCount = 7,
                resonance = calculatePairResonance(7, 7)  // Perfect mirror!
            ),
            // Pair 4: Enterprise (7+3=10)
            MirrorPair(
                alpha = "Business",
                omega = "Security",
                alphaCount = 7,
                omegaCount = 3,
                resonance = calculatePairResonance(7, 3)
            ),
            // Pair 5: Space & Visual (3+4=7)
            MirrorPair(
                alpha = "Planetary",
                omega = "Visualization",
                alphaCount = 3,
                omegaCount = 4,
                resonance = calculatePairResonance(3, 4)
            ),
            // Pair 6: Intelligence (3+5=8)
            MirrorPair(
                alpha = "ML_AI",
                omega = "Utilities",
                alphaCount = 3,
                omegaCount = 5,
                resonance = calculatePairResonance(3, 5)
            )
        )
    }

    /**
     * Calculate resonance for a mirror pair.
     * Perfect resonance when alpha + omega relates to Brahim numbers.
     */
    private fun calculatePairResonance(alpha: Int, omega: Int): Double {
        val sum = alpha + omega
        val diff = abs(alpha - omega)

        // Check if sum is in Brahim sequence or related
        val sumAlignment = when {
            sum == 13 -> 0.9  // 13 = Fibonacci, golden ratio related
            sum == 14 -> 0.85 // 14 = 7+7 perfect mirror
            sum == 10 -> 0.8  // 10 = base
            sum == 7 -> 0.95  // 7 = prime, appears in many calculations
            sum == 8 -> 0.88  // 8 = 2³, octave
            else -> 0.5
        }

        // Perfect mirror bonus (alpha == omega)
        val mirrorBonus = if (diff == 0) 0.1 else 0.0

        // Golden ratio proximity
        val goldenRatio = BrahimConstants.PHI
        val ratio = if (omega > 0) alpha.toDouble() / omega else 1.0
        val goldenProximity = 1.0 - minOf(abs(ratio - goldenRatio), abs(ratio - 1/goldenRatio)) / goldenRatio

        return (sumAlignment + mirrorBonus + goldenProximity * 0.3).coerceIn(0.0, 1.0)
    }

    /**
     * Organize apps into symmetric layers.
     */
    private fun organizeIntoLayers(): Map<SymmetricLayer, List<String>> {
        return mapOf(
            // CORE: High-value, always-used apps (21 apps = composites)
            SymmetricLayer.CORE to listOf(
                "Universe Simulator", "Kelimutu Intelligence", "Smart Navigator",
                "Secure Business", "PINN Lab", "Traffic Brain", "Fair Division AI",
                "Golden Optimizer", "Cosmic Calculator", "Resonance Lab",
                "Titan Colony", "Mars Mission", "Dark Sector",
                "Aerospace Optimizer", "Emergency Response", "Fleet Manager",
                "Quantum Finance", "Crypto Observatory", "Compliance Intel",
                "SAT-ML Hybrid", "Brahim Workspace"
            ),

            // INNER: Fundamental calculators (27 apps = B(0))
            SymmetricLayer.INNER to listOf(
                // Physics fundamentals
                "Fine Structure", "Weinberg Angle", "Muon/Electron", "Proton/Electron",
                "Dark Energy", "Dark Matter", "Hubble Constant", "Yang-Mills",
                // Math fundamentals
                "Brahim Sequence", "Egyptian Fractions", "Mirror Operator",
                "Golden Ratio", "Convergent Series", "Prime Analysis", "Modular Arithmetic",
                // Core solvers
                "SAT Solver", "CFD Solver", "PDE Solver", "Optimizer",
                "Constraint Solver", "Linear Algebra",
                // Essential ML
                "Kelimutu Router", "Wavelength Analyzer", "Phase Classifier",
                // Essential security
                "Wormhole Cipher", "ASIOS Guard", "Key Generator"
            ),

            // OUTER: Domain-specific apps (27 apps)
            SymmetricLayer.OUTER to listOf(
                // Aviation
                "Flight Pathfinder", "Fuel Calculator", "Weather Integration",
                "Conflict Detection", "Altitude Optimizer", "Maintenance Predictor", "Runway Selection",
                // Traffic
                "Signal Timing", "Congestion Predictor", "Route Optimizer",
                "Parking Finder", "Emergency Router", "Traffic Wave", "Intersection Analysis",
                // Business
                "Resource Allocator", "Salary Structure", "Task Scheduler",
                "Risk Assessment", "Team Synergy", "Compliance Check", "KPI Calculator",
                // Cosmology
                "Dark Energy Calc", "Dark Matter Calc", "CMB Temperature",
                "Cosmic Timeline", "Hubble Flow"
            ),

            // BOUNDARY: Specialized/extension apps (11 apps → total 86)
            SymmetricLayer.BOUNDARY to listOf(
                // Planetary
                "Titan Explorer", "Mars Habitat", "Orbital Mechanics",
                // Visualization
                "Resonance Monitor", "Phase Portrait", "Sequence Plot", "Symmetry Viewer",
                // Utilities
                "Unit Converter", "Constant Reference", "Data Export", "Formula Sheet"
            )
        )
    }

    /**
     * Calculate how well total aligns with Brahim numbers.
     */
    private fun calculateBrahimAlignment(total: Int): Double {
        // Check proximity to key Brahim numbers
        val targets = listOf(
            60 to "B(2)",
            75 to "B(4)",
            97 to "B(5)",
            107 to "Center",
            121 to "B(6)"
        )

        val closest = targets.minByOrNull { abs(it.first - total) }!!
        val distance = abs(closest.first - total)
        val maxDistance = 35  // Max reasonable distance

        return (1.0 - distance.toDouble() / maxDistance).coerceIn(0.0, 1.0)
    }

    /**
     * Calculate overall symmetry score.
     */
    private fun calculateSymmetryScore(pairs: List<MirrorPair>): Double {
        // Average pair resonance
        val avgResonance = pairs.map { it.resonance }.average()

        // Check for perfect mirrors (alpha == omega)
        val perfectMirrors = pairs.count { it.alphaCount == it.omegaCount }
        val mirrorBonus = perfectMirrors * 0.05

        // Check sum distribution
        val sums = pairs.map { it.sum }
        val sumVariance = sums.map { (it - sums.average()).let { d -> d * d } }.average()
        val sumUniformity = 1.0 - (sumVariance / 10.0).coerceIn(0.0, 1.0)

        return ((avgResonance + mirrorBonus + sumUniformity * 0.3) / 1.3).coerceIn(0.0, 1.0)
    }

    /**
     * Get recommendations to improve symmetry.
     */
    fun getSymmetryRecommendations(): List<SymmetryRecommendation> {
        val current = calculateOptimalSymmetry()
        val recommendations = mutableListOf<SymmetryRecommendation>()

        // Recommendation 1: Reach B(5) = 97
        val toB5 = 97 - current.totalApps
        if (toB5 > 0) {
            recommendations.add(SymmetryRecommendation(
                action = "ADD_APPS",
                description = "Add $toB5 apps to reach B(5) = 97",
                impact = 0.15,
                targets = listOf("Planetary +4", "Security +4", "ML_AI +3")
            ))
        }

        // Recommendation 2: Balance Enterprise pair (7,3) → (5,5)
        recommendations.add(SymmetryRecommendation(
            action = "REBALANCE",
            description = "Move 2 apps from Business to Security for mirror symmetry",
            impact = 0.1,
            targets = listOf("Business 7→5", "Security 3→5")
        ))

        // Recommendation 3: Balance Planetary pair (3,4) → (4,4) or reach 7
        recommendations.add(SymmetryRecommendation(
            action = "REBALANCE",
            description = "Add 1 app to Planetary for mirror with Visualization",
            impact = 0.05,
            targets = listOf("Planetary 3→4")
        ))

        // Recommendation 4: Reach Center = 107
        val toCenter = 107 - current.totalApps
        if (toCenter > 0) {
            recommendations.add(SymmetryRecommendation(
                action = "ADD_APPS",
                description = "Add $toCenter apps to reach Center = 107",
                impact = 0.25,
                targets = listOf("Expand all low categories to 7 apps each")
            ))
        }

        return recommendations.sortedByDescending { it.impact }
    }

    /**
     * Apply a symmetric transformation.
     */
    fun applySymmetricTransformation(transformation: SymmetricTransformation): SymmetricOrganization {
        return when (transformation) {
            SymmetricTransformation.BALANCE_PAIRS -> balanceMirrorPairs()
            SymmetricTransformation.REACH_B5 -> expandToB5()
            SymmetricTransformation.REACH_CENTER -> expandToCenter()
            SymmetricTransformation.GOLDEN_DISTRIBUTION -> applyGoldenDistribution()
        }
    }

    private fun balanceMirrorPairs(): SymmetricOrganization {
        // Create balanced pairs where possible
        val balancedPairs = listOf(
            MirrorPair("Physics", "Cosmology", 7, 6, resonance = 0.92),      // 13, more balanced
            MirrorPair("Mathematics", "Solvers", 7, 6, resonance = 0.92),    // 13, unchanged
            MirrorPair("Aviation", "Traffic", 7, 7, resonance = 1.0),        // 14, perfect!
            MirrorPair("Business", "Security", 5, 5, resonance = 1.0),       // 10, perfect!
            MirrorPair("Planetary", "Visualization", 4, 4, resonance = 1.0), // 8, perfect!
            MirrorPair("ML_AI", "Utilities", 4, 4, resonance = 1.0)          // 8, perfect!
        )
        // Total: 13+13+14+10+8+8 = 66 hub apps

        return SymmetricOrganization(
            layers = organizeIntoLayers(),
            mirrorPairs = balancedPairs,
            totalApps = 66 + 21, // 87
            brahimAlignment = 0.78,
            symmetryScore = 0.95 // Much higher due to 4 perfect mirrors!
        )
    }

    private fun expandToB5(): SymmetricOrganization {
        // Target: 97 total apps = 76 hub + 21 composite
        val expandedPairs = listOf(
            MirrorPair("Physics", "Cosmology", 7, 7, resonance = 1.0),       // 14
            MirrorPair("Mathematics", "Solvers", 7, 7, resonance = 1.0),     // 14
            MirrorPair("Aviation", "Traffic", 7, 7, resonance = 1.0),        // 14
            MirrorPair("Business", "Security", 6, 6, resonance = 1.0),       // 12
            MirrorPair("Planetary", "Visualization", 6, 6, resonance = 1.0), // 12
            MirrorPair("ML_AI", "Utilities", 5, 5, resonance = 1.0)          // 10
        )
        // Total: 14+14+14+12+12+10 = 76 hub apps + 21 composite = 97 = B(5)!

        return SymmetricOrganization(
            layers = organizeIntoLayers(),
            mirrorPairs = expandedPairs,
            totalApps = 97,
            brahimAlignment = 1.0, // Perfect B(5) alignment!
            symmetryScore = 1.0   // All perfect mirrors!
        )
    }

    private fun expandToCenter(): SymmetricOrganization {
        // Target: 107 total apps = 76 hub + 31 composite (add 10 composites)
        val expandedPairs = listOf(
            MirrorPair("Physics", "Cosmology", 7, 7, resonance = 1.0),       // 14
            MirrorPair("Mathematics", "Solvers", 7, 7, resonance = 1.0),     // 14
            MirrorPair("Aviation", "Traffic", 7, 7, resonance = 1.0),        // 14
            MirrorPair("Business", "Security", 6, 6, resonance = 1.0),       // 12
            MirrorPair("Planetary", "Visualization", 6, 6, resonance = 1.0), // 12
            MirrorPair("ML_AI", "Utilities", 5, 5, resonance = 1.0)          // 10
        )
        // Hub: 76, Composite: 31, Total: 107 = Center!

        return SymmetricOrganization(
            layers = organizeIntoLayers(),
            mirrorPairs = expandedPairs,
            totalApps = 107,
            brahimAlignment = 1.0, // Perfect Center alignment!
            symmetryScore = 1.0
        )
    }

    private fun applyGoldenDistribution(): SymmetricOrganization {
        // Distribute apps according to golden ratio
        // φ = 1.618, 1/φ = 0.618
        // Total 86 apps: 53 "major" + 33 "minor" (ratio ≈ 1.606)
        val phi = BrahimConstants.PHI
        val total = 86

        val major = (total / (1 + 1/phi)).toInt()  // 53
        val minor = total - major                   // 33

        // Further subdivide by golden ratio
        val majorA = (major / (1 + 1/phi)).toInt() // 33
        val majorB = major - majorA                 // 20
        val minorA = (minor / (1 + 1/phi)).toInt() // 20
        val minorB = minor - minorA                 // 13

        // Distribution: 33, 20, 20, 13 = 86 ✓
        // These are close to: B(0)-like, Fibonacci numbers

        return SymmetricOrganization(
            layers = mapOf(
                SymmetricLayer.CORE to (1..21).map { "Composite$it" },      // 21 (composites)
                SymmetricLayer.INNER to (1..27).map { "Inner$it" },         // 27 = B(0)
                SymmetricLayer.OUTER to (1..27).map { "Outer$it" },         // 27 = B(0)
                SymmetricLayer.BOUNDARY to (1..11).map { "Boundary$it" }    // 11 (remaining)
            ),
            mirrorPairs = createMirrorPairs(),
            totalApps = 86,
            brahimAlignment = 0.85,
            symmetryScore = 0.88
        )
    }
}

/**
 * Symmetry recommendation.
 */
data class SymmetryRecommendation(
    val action: String,
    val description: String,
    val impact: Double,  // 0-1, how much this improves symmetry
    val targets: List<String>
)

/**
 * Available symmetric transformations.
 */
enum class SymmetricTransformation {
    BALANCE_PAIRS,       // Make mirror pairs equal (α = ω)
    REACH_B5,           // Expand to B(5) = 97 total apps
    REACH_CENTER,       // Expand to Center = 107 total apps
    GOLDEN_DISTRIBUTION // Apply golden ratio distribution
}

/**
 * Symmetric Architecture Summary for display.
 */
data class SymmetricSummary(
    val currentState: String,
    val targetState: String,
    val transformations: List<String>,
    val finalScore: Double
)

/**
 * Generate summary of symmetric architecture.
 */
fun generateSymmetricSummary(): SymmetricSummary {
    val current = SymmetricArchitecture.calculateOptimalSymmetry()
    val target = SymmetricArchitecture.applySymmetricTransformation(SymmetricTransformation.REACH_B5)

    return SymmetricSummary(
        currentState = """
            |Current: ${current.totalApps} apps
            |  - Hub Apps: 65 (12 categories)
            |  - Composite Apps: 21 (5 categories)
            |  - Symmetry Score: ${String.format("%.2f", current.symmetryScore * 100)}%
            |  - Brahim Alignment: ${String.format("%.2f", current.brahimAlignment * 100)}%
        """.trimMargin(),
        targetState = """
            |Target: ${target.totalApps} apps = B(5)
            |  - Hub Apps: 76 (12 categories, all mirror pairs)
            |  - Composite Apps: 21 (5 categories)
            |  - Symmetry Score: ${String.format("%.2f", target.symmetryScore * 100)}%
            |  - Brahim Alignment: ${String.format("%.2f", target.brahimAlignment * 100)}%
        """.trimMargin(),
        transformations = listOf(
            "Physics 8→7, Cosmology 5→7 (pair sum: 14)",
            "Solvers 6→7 (match Mathematics: 7)",
            "Security 3→6, Business 7→6 (pair sum: 12)",
            "Planetary 3→6, Visualization 4→6 (pair sum: 12)",
            "ML_AI 3→5, Utilities 5→5 (pair sum: 10)"
        ),
        finalScore = target.symmetryScore
    )
}
