/**
 * Skill Composer - Skill-Application Fusion Engine
 * =================================================
 *
 * ASIOS 2.0 - Phi-Pi Synthesis Release
 *
 * Composes multiple skills into unified composite applications.
 * Enables skill chaining, parallel execution, and result fusion.
 *
 * Architecture:
 * - Skills are atomic computation units mapped to Lucas dimensions
 * - Each domain has L(n) discrete states (Lucas capacity)
 * - Composite Apps combine 2-4 skills with Phi-Pi gap creativity
 * - SkillComposer orchestrates execution pipelines
 *
 * Lucas Dimensional Mapping:
 *   D1:  PHYSICS       - L(1)=1   states (fundamental constants)
 *   D2:  MATHEMATICS   - L(2)=3   states (triage precision)
 *   D3:  SECURITY      - L(3)=4   states (trust quadrants)
 *   D4:  COSMOLOGY     - L(4)=7   states (cosmic scales)
 *   D5:  SOLVERS       - L(5)=11  states (algorithm levels)
 *   D6:  UTILITIES     - L(6)=18  states (tool variants)
 *   D7:  AVIATION      - L(7)=29  states (flight modes)
 *   D8:  TRAFFIC       - L(8)=47  states (flow patterns)
 *   D9:  PLANETARY     - L(9)=76  states (exploration paths)
 *   D10: BUSINESS      - L(10)=123 states (enterprise rules)
 *   D11: ML_AI         - L(11)=199 states (model architectures)
 *   D12: VISUALIZATION - L(12)=322 states (rendering modes)
 *
 * Total: 840 states across all dimensions
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-27
 */

package com.brahim.buim.skills

import com.brahim.buim.core.BrahimConstants
import kotlinx.coroutines.async
import kotlinx.coroutines.awaitAll
import kotlinx.coroutines.coroutineScope
import kotlin.math.PI

/**
 * Skill categories matching hub domains.
 * Ordered by Lucas dimension for ASIOS 2.0 architecture.
 */
enum class SkillDomain(val lucasDimension: Int, val lucasCapacity: Int) {
    PHYSICS(1, 1),         // D1: L(1)=1
    MATHEMATICS(2, 3),     // D2: L(2)=3
    SECURITY(3, 4),        // D3: L(3)=4
    COSMOLOGY(4, 7),       // D4: L(4)=7
    SOLVERS(5, 11),        // D5: L(5)=11
    UTILITIES(6, 18),      // D6: L(6)=18
    AVIATION(7, 29),       // D7: L(7)=29
    TRAFFIC(8, 47),        // D8: L(8)=47
    PLANETARY(9, 76),      // D9: L(9)=76
    BUSINESS(10, 123),     // D10: L(10)=123
    ML_AI(11, 199),        // D11: L(11)=199
    VISUALIZATION(12, 322) // D12: L(12)=322
}

/**
 * Individual skill definition.
 *
 * Each skill belongs to a Lucas dimension through its domain,
 * inheriting the dimensional capacity L(n) for state mapping.
 */
data class Skill(
    val id: String,
    val name: String,
    val domain: SkillDomain,
    val inputTypes: List<String>,
    val outputType: String,
    val brahimWeight: Double = BrahimConstants.PHI  // Default φ weighting
) {
    /** Lucas dimension from domain */
    val lucasDimension: Int get() = domain.lucasDimension

    /** Lucas capacity L(n) for this skill's dimension */
    val lucasCapacity: Int get() = domain.lucasCapacity

    /** Dimensional threshold 1/φ^n */
    val threshold: Double get() = 1.0 / Math.pow(BrahimConstants.PHI, lucasDimension.toDouble())
}

/**
 * Composite application definition.
 */
data class CompositeApp(
    val id: String,
    val name: String,
    val description: String,
    val skills: List<Skill>,
    val executionMode: ExecutionMode,
    val category: CompositeCategory
)

/**
 * How skills are executed in a composite app.
 */
enum class ExecutionMode {
    SEQUENTIAL,  // Output of skill N feeds into skill N+1
    PARALLEL,    // All skills run simultaneously, results merged
    BRANCHING,   // Conditional execution based on intermediate results
    FUSION       // Skills operate on shared state (V-NAND resonance)
}

/**
 * Categories for composite applications.
 */
enum class CompositeCategory {
    SCIENCE,      // Physics + Cosmology + Math
    NAVIGATION,   // Aviation + Traffic + Solvers
    ENTERPRISE,   // Business + Security + ML
    EXPLORATION,  // Planetary + Visualization + Physics
    INTELLIGENCE  // ML + Solvers + All domains
}

/**
 * Result from skill execution.
 */
data class SkillResult(
    val skillId: String,
    val success: Boolean,
    val output: Any?,
    val resonance: Double,
    val executionTimeMs: Long
)

/**
 * Result from composite app execution.
 *
 * ASIOS 2.0: Includes Lucas dimensional metadata and Phi-Pi gap status.
 */
data class CompositeResult(
    val appId: String,
    val skillResults: List<SkillResult>,
    val fusedOutput: Any?,
    val totalResonance: Double,
    val brahimSignature: String,
    val lucasDimensions: List<Int> = emptyList(),
    val totalCapacity: Int = 0,
    val inCreativeGap: Boolean = false
)

/**
 * Skill Composer - Orchestrates skill composition and execution.
 */
class SkillComposer {

    // Registry of all available skills
    private val skillRegistry = mutableMapOf<String, Skill>()

    // Registry of composite applications
    private val compositeRegistry = mutableMapOf<String, CompositeApp>()

    init {
        registerCoreSkills()
        registerCompositeApps()
    }

    /**
     * Register all core skills from the 12 hubs.
     */
    private fun registerCoreSkills() {
        // Physics Skills (8)
        registerSkill(Skill("physics_fine_structure", "Fine Structure Constant", SkillDomain.PHYSICS,
            listOf("sequence"), "double", 137.036))
        registerSkill(Skill("physics_weinberg", "Weinberg Angle", SkillDomain.PHYSICS,
            listOf("phi"), "double", 0.2312))
        registerSkill(Skill("physics_muon_electron", "Muon/Electron Ratio", SkillDomain.PHYSICS,
            listOf("sequence"), "double", 206.768))
        registerSkill(Skill("physics_proton_electron", "Proton/Electron Ratio", SkillDomain.PHYSICS,
            listOf("sequence"), "double", 1836.15))
        registerSkill(Skill("physics_dark_energy", "Dark Energy Ratio", SkillDomain.PHYSICS,
            listOf("phi"), "double", 0.689))
        registerSkill(Skill("physics_dark_matter", "Dark Matter Ratio", SkillDomain.PHYSICS,
            listOf("phi"), "double", 0.266))
        registerSkill(Skill("physics_hubble", "Hubble Constant", SkillDomain.PHYSICS,
            listOf("sequence"), "double", 67.4))
        registerSkill(Skill("physics_yang_mills", "Yang-Mills Mass Gap", SkillDomain.PHYSICS,
            listOf("beta"), "double", BrahimConstants.BETA_SECURITY))

        // Mathematics Skills (7)
        registerSkill(Skill("math_sequence", "Brahim Sequence", SkillDomain.MATHEMATICS,
            listOf("index"), "int", 214.0))
        registerSkill(Skill("math_egyptian", "Egyptian Fractions", SkillDomain.MATHEMATICS,
            listOf("fraction"), "list", BrahimConstants.PHI))
        registerSkill(Skill("math_mirror", "Mirror Operator", SkillDomain.MATHEMATICS,
            listOf("value"), "int", 214.0))
        registerSkill(Skill("math_golden", "Golden Ratio Operations", SkillDomain.MATHEMATICS,
            listOf("n"), "double", BrahimConstants.PHI))
        registerSkill(Skill("math_convergent", "Convergent Series", SkillDomain.MATHEMATICS,
            listOf("terms"), "double", BrahimConstants.PHI))
        registerSkill(Skill("math_prime", "Prime Analysis", SkillDomain.MATHEMATICS,
            listOf("n"), "boolean", 97.0))
        registerSkill(Skill("math_modular", "Modular Arithmetic", SkillDomain.MATHEMATICS,
            listOf("a", "b", "m"), "int", 107.0))

        // Cosmology Skills (5)
        registerSkill(Skill("cosmo_dark_energy", "Dark Energy Calculator", SkillDomain.COSMOLOGY,
            listOf("density"), "double", 0.689))
        registerSkill(Skill("cosmo_dark_matter", "Dark Matter Calculator", SkillDomain.COSMOLOGY,
            listOf("density"), "double", 0.266))
        registerSkill(Skill("cosmo_cmb", "CMB Temperature", SkillDomain.COSMOLOGY,
            listOf("redshift"), "double", 2.725))
        registerSkill(Skill("cosmo_timeline", "Cosmic Timeline", SkillDomain.COSMOLOGY,
            listOf("epoch"), "string", 13.8))
        registerSkill(Skill("cosmo_hubble", "Hubble Flow", SkillDomain.COSMOLOGY,
            listOf("distance"), "double", 67.4))

        // Aviation Skills (7)
        registerSkill(Skill("aviation_pathfinder", "Flight Pathfinder", SkillDomain.AVIATION,
            listOf("origin", "dest"), "route", BrahimConstants.PHI))
        registerSkill(Skill("aviation_fuel", "Fuel Calculator", SkillDomain.AVIATION,
            listOf("distance", "aircraft"), "double", BrahimConstants.PHI))
        registerSkill(Skill("aviation_weather", "Weather Integration", SkillDomain.AVIATION,
            listOf("location"), "weather", BrahimConstants.PHI))
        registerSkill(Skill("aviation_conflict", "Conflict Detection", SkillDomain.AVIATION,
            listOf("routes"), "conflicts", BrahimConstants.BETA_SECURITY))
        registerSkill(Skill("aviation_altitude", "Altitude Optimizer", SkillDomain.AVIATION,
            listOf("route"), "altitude", BrahimConstants.PHI))
        registerSkill(Skill("aviation_maintenance", "Maintenance Predictor", SkillDomain.AVIATION,
            listOf("aircraft"), "schedule", BrahimConstants.PHI))
        registerSkill(Skill("aviation_runway", "Runway Selection", SkillDomain.AVIATION,
            listOf("airport", "weather"), "runway", BrahimConstants.PHI))

        // Traffic Skills (7)
        registerSkill(Skill("traffic_signal", "Signal Timing", SkillDomain.TRAFFIC,
            listOf("intersection"), "timing", BrahimConstants.PHI))
        registerSkill(Skill("traffic_congestion", "Congestion Predictor", SkillDomain.TRAFFIC,
            listOf("network"), "prediction", BrahimConstants.PHI))
        registerSkill(Skill("traffic_route", "Route Optimizer", SkillDomain.TRAFFIC,
            listOf("origin", "dest"), "route", BrahimConstants.PHI))
        registerSkill(Skill("traffic_parking", "Parking Finder", SkillDomain.TRAFFIC,
            listOf("location"), "parking", BrahimConstants.PHI))
        registerSkill(Skill("traffic_emergency", "Emergency Router", SkillDomain.TRAFFIC,
            listOf("incident"), "route", BrahimConstants.ALPHA_WORMHOLE))
        registerSkill(Skill("traffic_wave", "Traffic Wave Analysis", SkillDomain.TRAFFIC,
            listOf("flow"), "waves", BrahimConstants.PHI))
        registerSkill(Skill("traffic_intersection", "Intersection Analysis", SkillDomain.TRAFFIC,
            listOf("intersection"), "analysis", BrahimConstants.PHI))

        // Business Skills (7)
        registerSkill(Skill("business_allocator", "Resource Allocator", SkillDomain.BUSINESS,
            listOf("resources", "agents"), "allocation", BrahimConstants.PHI))
        registerSkill(Skill("business_salary", "Salary Structure", SkillDomain.BUSINESS,
            listOf("roles"), "structure", BrahimConstants.PHI))
        registerSkill(Skill("business_scheduler", "Task Scheduler", SkillDomain.BUSINESS,
            listOf("tasks"), "schedule", BrahimConstants.PHI))
        registerSkill(Skill("business_risk", "Risk Assessment", SkillDomain.BUSINESS,
            listOf("portfolio"), "risk", BrahimConstants.BETA_SECURITY))
        registerSkill(Skill("business_synergy", "Team Synergy", SkillDomain.BUSINESS,
            listOf("team"), "synergy", BrahimConstants.PHI))
        registerSkill(Skill("business_compliance", "Compliance Check", SkillDomain.BUSINESS,
            listOf("data"), "compliance", BrahimConstants.BETA_SECURITY))
        registerSkill(Skill("business_kpi", "KPI Calculator", SkillDomain.BUSINESS,
            listOf("metrics"), "kpi", BrahimConstants.PHI))

        // Solver Skills (6)
        registerSkill(Skill("solver_sat", "SAT Solver", SkillDomain.SOLVERS,
            listOf("formula"), "assignment", BrahimConstants.PHI))
        registerSkill(Skill("solver_cfd", "CFD Solver", SkillDomain.SOLVERS,
            listOf("mesh", "boundary"), "flow", BrahimConstants.PHI))
        registerSkill(Skill("solver_pde", "PDE Solver", SkillDomain.SOLVERS,
            listOf("equation", "boundary"), "solution", BrahimConstants.PHI))
        registerSkill(Skill("solver_optimize", "Optimizer", SkillDomain.SOLVERS,
            listOf("objective", "constraints"), "optimum", BrahimConstants.PHI))
        registerSkill(Skill("solver_constraint", "Constraint Solver", SkillDomain.SOLVERS,
            listOf("constraints"), "solution", BrahimConstants.PHI))
        registerSkill(Skill("solver_linear", "Linear Algebra", SkillDomain.SOLVERS,
            listOf("matrix"), "result", BrahimConstants.PHI))

        // Planetary Skills (3)
        registerSkill(Skill("planetary_titan", "Titan Explorer", SkillDomain.PLANETARY,
            listOf("query"), "data", BrahimConstants.PHI))
        registerSkill(Skill("planetary_mars", "Mars Habitat", SkillDomain.PLANETARY,
            listOf("scenario"), "plan", BrahimConstants.PHI))
        registerSkill(Skill("planetary_orbital", "Orbital Mechanics", SkillDomain.PLANETARY,
            listOf("bodies"), "transfer", BrahimConstants.PHI))

        // Security Skills (3)
        registerSkill(Skill("security_cipher", "Wormhole Cipher", SkillDomain.SECURITY,
            listOf("plaintext"), "ciphertext", BrahimConstants.BETA_SECURITY))
        registerSkill(Skill("security_asios", "ASIOS Guard", SkillDomain.SECURITY,
            listOf("input"), "verdict", BrahimConstants.BETA_SECURITY))
        registerSkill(Skill("security_keygen", "Key Generator", SkillDomain.SECURITY,
            listOf("params"), "key", BrahimConstants.BETA_SECURITY))

        // ML/AI Skills (3)
        registerSkill(Skill("ml_kelimutu", "Kelimutu Router", SkillDomain.ML_AI,
            listOf("query"), "intent", BrahimConstants.PHI))
        registerSkill(Skill("ml_wavelength", "Wavelength Analyzer", SkillDomain.ML_AI,
            listOf("signal"), "wavelengths", BrahimConstants.PHI))
        registerSkill(Skill("ml_phase", "Phase Classifier", SkillDomain.ML_AI,
            listOf("timeseries"), "phase", BrahimConstants.PHI))

        // Visualization Skills (4)
        registerSkill(Skill("viz_resonance", "Resonance Monitor", SkillDomain.VISUALIZATION,
            listOf("grid"), "visualization", BrahimConstants.GENESIS_CONSTANT))
        registerSkill(Skill("viz_phase", "Phase Portrait", SkillDomain.VISUALIZATION,
            listOf("dynamics"), "portrait", BrahimConstants.PHI))
        registerSkill(Skill("viz_sequence", "Sequence Plot", SkillDomain.VISUALIZATION,
            listOf("sequence"), "plot", 214.0))
        registerSkill(Skill("viz_symmetry", "Symmetry Viewer", SkillDomain.VISUALIZATION,
            listOf("group"), "visualization", 45.0))

        // Utility Skills (5)
        registerSkill(Skill("util_converter", "Unit Converter", SkillDomain.UTILITIES,
            listOf("value", "from", "to"), "converted", BrahimConstants.PHI))
        registerSkill(Skill("util_reference", "Constant Reference", SkillDomain.UTILITIES,
            listOf("constant"), "value", BrahimConstants.PHI))
        registerSkill(Skill("util_export", "Data Export", SkillDomain.UTILITIES,
            listOf("data", "format"), "file", BrahimConstants.PHI))
        registerSkill(Skill("util_formula", "Formula Sheet", SkillDomain.UTILITIES,
            listOf("category"), "formulas", BrahimConstants.PHI))
        registerSkill(Skill("util_precision", "Precision Calculator", SkillDomain.UTILITIES,
            listOf("expression"), "result", BrahimConstants.PHI))
    }

    /**
     * Register the 21 composite applications.
     */
    private fun registerCompositeApps() {
        // 1. Universe Simulator (Physics + Cosmology + Visualization)
        registerComposite(CompositeApp(
            "universe_simulator",
            "Universe Simulator",
            "Interactive cosmic exploration with real physics",
            listOf(
                skillRegistry["physics_dark_energy"]!!,
                skillRegistry["cosmo_timeline"]!!,
                skillRegistry["viz_sequence"]!!
            ),
            ExecutionMode.FUSION,
            CompositeCategory.SCIENCE
        ))

        // 2. Smart Navigator (Aviation + Traffic + Solvers)
        registerComposite(CompositeApp(
            "smart_navigator",
            "Smart Navigator",
            "Multi-modal route optimization",
            listOf(
                skillRegistry["aviation_pathfinder"]!!,
                skillRegistry["traffic_route"]!!,
                skillRegistry["solver_optimize"]!!
            ),
            ExecutionMode.SEQUENTIAL,
            CompositeCategory.NAVIGATION
        ))

        // 3. Secure Business Suite (Security + Business + ML)
        registerComposite(CompositeApp(
            "secure_business",
            "Secure Business Suite",
            "Protected financial operations with AI",
            listOf(
                skillRegistry["security_cipher"]!!,
                skillRegistry["business_risk"]!!,
                skillRegistry["ml_kelimutu"]!!
            ),
            ExecutionMode.PARALLEL,
            CompositeCategory.ENTERPRISE
        ))

        // 4. PINN Physics Lab (Physics + ML + Solvers)
        registerComposite(CompositeApp(
            "pinn_lab",
            "PINN Physics Lab",
            "Physics-informed neural networks",
            listOf(
                skillRegistry["physics_fine_structure"]!!,
                skillRegistry["ml_phase"]!!,
                skillRegistry["solver_pde"]!!
            ),
            ExecutionMode.FUSION,
            CompositeCategory.SCIENCE
        ))

        // 5. Titan Colony Planner (Planetary + Business + Visualization)
        registerComposite(CompositeApp(
            "titan_colony",
            "Titan Colony Planner",
            "Space colony resource management",
            listOf(
                skillRegistry["planetary_titan"]!!,
                skillRegistry["business_allocator"]!!,
                skillRegistry["viz_resonance"]!!
            ),
            ExecutionMode.SEQUENTIAL,
            CompositeCategory.EXPLORATION
        ))

        // 6. Quantum Finance (Physics + Business + Security)
        registerComposite(CompositeApp(
            "quantum_finance",
            "Quantum Finance",
            "Brahim-based trading algorithms",
            listOf(
                skillRegistry["physics_fine_structure"]!!,
                skillRegistry["business_kpi"]!!,
                skillRegistry["security_cipher"]!!
            ),
            ExecutionMode.PARALLEL,
            CompositeCategory.ENTERPRISE
        ))

        // 7. Traffic Brain (Traffic + ML + Visualization)
        registerComposite(CompositeApp(
            "traffic_brain",
            "Traffic Brain",
            "AI-powered signal optimization",
            listOf(
                skillRegistry["traffic_signal"]!!,
                skillRegistry["ml_wavelength"]!!,
                skillRegistry["viz_phase"]!!
            ),
            ExecutionMode.FUSION,
            CompositeCategory.INTELLIGENCE
        ))

        // 8. Aerospace Optimizer (Aviation + Solvers + Physics)
        registerComposite(CompositeApp(
            "aerospace_optimizer",
            "Aerospace Optimizer",
            "CFD + trajectory optimization",
            listOf(
                skillRegistry["aviation_pathfinder"]!!,
                skillRegistry["solver_cfd"]!!,
                skillRegistry["physics_yang_mills"]!!
            ),
            ExecutionMode.SEQUENTIAL,
            CompositeCategory.NAVIGATION
        ))

        // 9. Crypto Observatory (Security + Math + Visualization)
        registerComposite(CompositeApp(
            "crypto_observatory",
            "Crypto Observatory",
            "Cipher strength visualization",
            listOf(
                skillRegistry["security_cipher"]!!,
                skillRegistry["math_prime"]!!,
                skillRegistry["viz_symmetry"]!!
            ),
            ExecutionMode.PARALLEL,
            CompositeCategory.ENTERPRISE
        ))

        // 10. Fair Division AI (Business + ML + Math)
        registerComposite(CompositeApp(
            "fair_division_ai",
            "Fair Division AI",
            "AI-powered resource allocation",
            listOf(
                skillRegistry["business_allocator"]!!,
                skillRegistry["ml_kelimutu"]!!,
                skillRegistry["math_egyptian"]!!
            ),
            ExecutionMode.FUSION,
            CompositeCategory.INTELLIGENCE
        ))

        // 11. Cosmic Calculator (Physics + Cosmology + Math)
        registerComposite(CompositeApp(
            "cosmic_calculator",
            "Cosmic Calculator",
            "Universe-scale computations",
            listOf(
                skillRegistry["physics_hubble"]!!,
                skillRegistry["cosmo_cmb"]!!,
                skillRegistry["math_convergent"]!!
            ),
            ExecutionMode.PARALLEL,
            CompositeCategory.SCIENCE
        ))

        // 12. Mars Mission Control (Planetary + Aviation + Solvers)
        registerComposite(CompositeApp(
            "mars_mission",
            "Mars Mission Control",
            "Interplanetary trajectory planning",
            listOf(
                skillRegistry["planetary_mars"]!!,
                skillRegistry["planetary_orbital"]!!,
                skillRegistry["solver_optimize"]!!
            ),
            ExecutionMode.SEQUENTIAL,
            CompositeCategory.EXPLORATION
        ))

        // 13. Golden Optimizer (Math + Solvers + Visualization)
        registerComposite(CompositeApp(
            "golden_optimizer",
            "Golden Optimizer",
            "Phi-weighted optimization",
            listOf(
                skillRegistry["math_golden"]!!,
                skillRegistry["solver_optimize"]!!,
                skillRegistry["viz_resonance"]!!
            ),
            ExecutionMode.FUSION,
            CompositeCategory.SCIENCE
        ))

        // 14. Emergency Response (Traffic + Aviation + Security)
        registerComposite(CompositeApp(
            "emergency_response",
            "Emergency Response",
            "Crisis routing and coordination",
            listOf(
                skillRegistry["traffic_emergency"]!!,
                skillRegistry["aviation_conflict"]!!,
                skillRegistry["security_asios"]!!
            ),
            ExecutionMode.PARALLEL,
            CompositeCategory.NAVIGATION
        ))

        // 15. Compliance Intelligence (Business + Security + ML)
        registerComposite(CompositeApp(
            "compliance_intel",
            "Compliance Intelligence",
            "AI-driven regulatory validation",
            listOf(
                skillRegistry["business_compliance"]!!,
                skillRegistry["security_asios"]!!,
                skillRegistry["ml_kelimutu"]!!
            ),
            ExecutionMode.SEQUENTIAL,
            CompositeCategory.ENTERPRISE
        ))

        // 16. Resonance Lab (Visualization + Physics + ML)
        registerComposite(CompositeApp(
            "resonance_lab",
            "Resonance Lab",
            "V-NAND resonance experimentation",
            listOf(
                skillRegistry["viz_resonance"]!!,
                skillRegistry["physics_dark_energy"]!!,
                skillRegistry["ml_phase"]!!
            ),
            ExecutionMode.FUSION,
            CompositeCategory.SCIENCE
        ))

        // 17. Fleet Manager (Aviation + Business + Traffic)
        registerComposite(CompositeApp(
            "fleet_manager",
            "Fleet Manager",
            "Multi-vehicle coordination",
            listOf(
                skillRegistry["aviation_maintenance"]!!,
                skillRegistry["business_scheduler"]!!,
                skillRegistry["traffic_congestion"]!!
            ),
            ExecutionMode.PARALLEL,
            CompositeCategory.NAVIGATION
        ))

        // 18. SAT-ML Hybrid (Solvers + ML + Math)
        registerComposite(CompositeApp(
            "sat_ml_hybrid",
            "SAT-ML Hybrid",
            "Neural-guided satisfiability",
            listOf(
                skillRegistry["solver_sat"]!!,
                skillRegistry["ml_wavelength"]!!,
                skillRegistry["math_modular"]!!
            ),
            ExecutionMode.FUSION,
            CompositeCategory.INTELLIGENCE
        ))

        // 19. Dark Sector Explorer (Cosmology + Physics + Visualization)
        registerComposite(CompositeApp(
            "dark_sector",
            "Dark Sector Explorer",
            "Dark matter/energy investigation",
            listOf(
                skillRegistry["cosmo_dark_energy"]!!,
                skillRegistry["cosmo_dark_matter"]!!,
                skillRegistry["viz_symmetry"]!!
            ),
            ExecutionMode.PARALLEL,
            CompositeCategory.EXPLORATION
        ))

        // 20. Brahim Workspace (Utilities + Math + Visualization)
        registerComposite(CompositeApp(
            "brahim_workspace",
            "Brahim Workspace",
            "Complete calculation environment",
            listOf(
                skillRegistry["util_precision"]!!,
                skillRegistry["math_sequence"]!!,
                skillRegistry["viz_sequence"]!!
            ),
            ExecutionMode.SEQUENTIAL,
            CompositeCategory.SCIENCE
        ))

        // 21. Kelimutu Intelligence (ML + Security + Business)
        registerComposite(CompositeApp(
            "kelimutu_intel",
            "Kelimutu Intelligence",
            "Three-lake decision engine",
            listOf(
                skillRegistry["ml_kelimutu"]!!,
                skillRegistry["security_asios"]!!,
                skillRegistry["business_risk"]!!
            ),
            ExecutionMode.FUSION,
            CompositeCategory.INTELLIGENCE
        ))
    }

    private fun registerSkill(skill: Skill) {
        skillRegistry[skill.id] = skill
    }

    private fun registerComposite(app: CompositeApp) {
        compositeRegistry[app.id] = app
    }

    /**
     * Get all registered skills.
     */
    fun getAllSkills(): List<Skill> = skillRegistry.values.toList()

    /**
     * Get skills by domain.
     */
    fun getSkillsByDomain(domain: SkillDomain): List<Skill> =
        skillRegistry.values.filter { it.domain == domain }

    /**
     * Get all composite applications.
     */
    fun getAllCompositeApps(): List<CompositeApp> = compositeRegistry.values.toList()

    /**
     * Get composite apps by category.
     */
    fun getCompositesByCategory(category: CompositeCategory): List<CompositeApp> =
        compositeRegistry.values.filter { it.category == category }

    /**
     * Execute a composite application.
     *
     * ASIOS 2.0: Includes Lucas dimensional tracking and Phi-Pi gap detection.
     */
    suspend fun executeComposite(appId: String, inputs: Map<String, Any>, exploring: Boolean = false): CompositeResult {
        val app = compositeRegistry[appId]
            ?: throw IllegalArgumentException("Unknown composite app: $appId")

        val skillResults = when (app.executionMode) {
            ExecutionMode.SEQUENTIAL -> executeSequential(app.skills, inputs, exploring)
            ExecutionMode.PARALLEL -> executeParallel(app.skills, inputs, exploring)
            ExecutionMode.BRANCHING -> executeBranching(app.skills, inputs, exploring)
            ExecutionMode.FUSION -> executeFusion(app.skills, inputs, exploring)
        }

        val totalResonance = calculateTotalResonance(skillResults)
        val fusedOutput = fuseResults(skillResults, app.executionMode)
        val signature = generateBrahimSignature(app, skillResults)

        // ASIOS 2.0: Lucas dimensional data
        val lucasDimensions = app.skills.map { it.lucasDimension }
        val totalCapacity = app.skills.sumOf { it.lucasCapacity }
        val inCreativeGap = exploring || skillResults.any { it.resonance < BrahimConstants.PHI_PI_GAP }

        return CompositeResult(
            appId = appId,
            skillResults = skillResults,
            fusedOutput = fusedOutput,
            totalResonance = totalResonance,
            brahimSignature = signature,
            lucasDimensions = lucasDimensions,
            totalCapacity = totalCapacity,
            inCreativeGap = inCreativeGap
        )
    }

    private suspend fun executeSequential(skills: List<Skill>, inputs: Map<String, Any>, exploring: Boolean = false): List<SkillResult> {
        val results = mutableListOf<SkillResult>()
        var currentInputs = inputs

        for (skill in skills) {
            val startTime = System.currentTimeMillis()
            val output = executeSkill(skill, currentInputs, exploring)
            val endTime = System.currentTimeMillis()

            // ASIOS 2.0: Apply Lucas-weighted resonance
            val lucasWeight = skill.lucasCapacity.toDouble() / BrahimConstants.LUCAS_TOTAL
            val resonance = skill.brahimWeight * BrahimConstants.GENESIS_CONSTANT * (1 + lucasWeight)

            val result = SkillResult(
                skillId = skill.id,
                success = output != null,
                output = output,
                resonance = resonance,
                executionTimeMs = endTime - startTime
            )
            results.add(result)

            // Pass output to next skill
            if (output != null) {
                currentInputs = currentInputs + ("previous_output" to output)
            }
        }

        return results
    }

    private suspend fun executeParallel(skills: List<Skill>, inputs: Map<String, Any>, exploring: Boolean = false): List<SkillResult> =
        coroutineScope {
            skills.map { skill ->
                async {
                    val startTime = System.currentTimeMillis()
                    val output = executeSkill(skill, inputs, exploring)
                    val endTime = System.currentTimeMillis()

                    // ASIOS 2.0: Apply Lucas-weighted resonance
                    val lucasWeight = skill.lucasCapacity.toDouble() / BrahimConstants.LUCAS_TOTAL
                    val resonance = skill.brahimWeight * BrahimConstants.GENESIS_CONSTANT * (1 + lucasWeight)

                    SkillResult(
                        skillId = skill.id,
                        success = output != null,
                        output = output,
                        resonance = resonance,
                        executionTimeMs = endTime - startTime
                    )
                }
            }.awaitAll()
        }

    private suspend fun executeBranching(skills: List<Skill>, inputs: Map<String, Any>, exploring: Boolean = false): List<SkillResult> {
        // Execute first skill to determine branch
        val firstResult = executeSequential(listOf(skills.first()), inputs, exploring).first()

        // Branch based on result
        val branchSkills = if (firstResult.success) {
            skills.drop(1).take(1)  // Success branch
        } else {
            skills.drop(2).take(1)  // Failure branch
        }

        return listOf(firstResult) + executeSequential(branchSkills, inputs, exploring)
    }

    private suspend fun executeFusion(skills: List<Skill>, inputs: Map<String, Any>, exploring: Boolean = false): List<SkillResult> {
        // Execute all in parallel
        val parallelResults = executeParallel(skills, inputs, exploring)

        // ASIOS 2.0: Apply V-NAND resonance fusion with Phi-Pi gap
        val fusedResonance = parallelResults.sumOf { it.resonance } / parallelResults.size
        val resonanceGate = fusedResonance >= 0.95 * BrahimConstants.GENESIS_CONSTANT

        // Apply creativity margin if exploring
        val creativityBoost = if (exploring) 1.0 + BrahimConstants.PHI_PI_GAP else 1.0

        return parallelResults.map { result ->
            result.copy(
                resonance = if (resonanceGate) {
                    result.resonance * BrahimConstants.PHI * creativityBoost
                } else {
                    result.resonance * creativityBoost
                }
            )
        }
    }

    private fun executeSkill(skill: Skill, inputs: Map<String, Any>, exploring: Boolean = false): Any? {
        // ASIOS 2.0: Include Lucas dimensional metadata
        return mapOf(
            "skill" to skill.name,
            "domain" to skill.domain.name,
            "brahimWeight" to skill.brahimWeight,
            "lucasDimension" to skill.lucasDimension,
            "lucasCapacity" to skill.lucasCapacity,
            "threshold" to skill.threshold,
            "exploring" to exploring,
            "inputs" to inputs.keys.toList()
        )
    }

    private fun calculateTotalResonance(results: List<SkillResult>): Double {
        val sum = results.sumOf { it.resonance }
        val count = results.size
        return if (count > 0) sum / count else 0.0
    }

    private fun fuseResults(results: List<SkillResult>, mode: ExecutionMode): Any {
        return mapOf(
            "mode" to mode.name,
            "skillCount" to results.size,
            "successCount" to results.count { it.success },
            "outputs" to results.mapNotNull { it.output }
        )
    }

    private fun generateBrahimSignature(app: CompositeApp, results: List<SkillResult>): String {
        // ASIOS 2.0: Include Lucas dimensional info in signature
        val lucasDimensions = app.skills.map { it.lucasDimension }
        val totalCapacity = app.skills.sumOf { it.lucasCapacity }
        val resonanceSum = results.sumOf { it.resonance }
        val hash = (lucasDimensions.sum() * 100 + totalCapacity + (resonanceSum * 100).toInt()) % 10000

        return "B2-${app.id.take(4).uppercase()}-${hash.toString().padStart(4, '0')}-L${totalCapacity}"
    }

    // =========================================================================
    // ASIOS 2.0 - LUCAS ARCHITECTURE HELPERS
    // =========================================================================

    /**
     * Get skills for a specific Lucas dimension.
     */
    fun getSkillsForDimension(dimension: Int): List<Skill> {
        require(dimension in 1..12) { "Dimension must be 1-12, got $dimension" }
        return skillRegistry.values.filter { it.lucasDimension == dimension }
    }

    /**
     * Get total Lucas capacity for a list of skills.
     */
    fun getTotalCapacity(skills: List<Skill>): Int = skills.sumOf { it.lucasCapacity }

    /**
     * Get ASIOS 2.0 architecture summary.
     */
    fun getASIOS2Summary(): Map<String, Any> {
        val skillsByDimension = (1..12).associate { dim ->
            dim to skillRegistry.values.filter { it.lucasDimension == dim }.map { it.name }
        }

        return mapOf(
            "version" to "2.0.0",
            "codename" to "Phi-Pi Synthesis",
            "total_skills" to skillRegistry.size,
            "total_composite_apps" to compositeRegistry.size,
            "total_lucas_capacity" to BrahimConstants.LUCAS_TOTAL,
            "phi_pi_gap" to BrahimConstants.PHI_PI_GAP,
            "domains_by_dimension" to SkillDomain.values().associate {
                "D${it.lucasDimension}" to mapOf(
                    "domain" to it.name,
                    "capacity" to it.lucasCapacity,
                    "skills" to skillsByDimension[it.lucasDimension]
                )
            },
            "execution_modes" to ExecutionMode.values().map { it.name },
            "composite_categories" to CompositeCategory.values().map { it.name }
        )
    }

    /**
     * Find apps that span multiple Lucas dimensions.
     */
    fun getMultiDimensionalApps(): List<CompositeApp> {
        return compositeRegistry.values.filter { app ->
            app.skills.map { it.lucasDimension }.distinct().size > 1
        }
    }

    /**
     * Get apps by Lucas dimension range.
     */
    fun getAppsByDimensionRange(minDim: Int, maxDim: Int): List<CompositeApp> {
        return compositeRegistry.values.filter { app ->
            app.skills.any { it.lucasDimension in minDim..maxDim }
        }
    }

    /**
     * Calculate dimensional resonance for an app.
     * Higher resonance when skills span complementary dimensions.
     */
    fun calculateDimensionalResonance(app: CompositeApp): Double {
        val dimensions = app.skills.map { it.lucasDimension }
        val span = dimensions.maxOrNull()!! - dimensions.minOrNull()!!
        val capacitySum = app.skills.sumOf { it.lucasCapacity }

        // Resonance formula: (span/12) * (capacity/840) * phi
        return (span.toDouble() / 12) * (capacitySum.toDouble() / BrahimConstants.LUCAS_TOTAL) * BrahimConstants.PHI
    }

    companion object {
        // Singleton instance
        @Volatile
        private var instance: SkillComposer? = null

        fun getInstance(): SkillComposer {
            return instance ?: synchronized(this) {
                instance ?: SkillComposer().also { instance = it }
            }
        }

        // ASIOS 2.0 constants
        const val VERSION = "2.0.0"
        const val CODENAME = "Phi-Pi Synthesis"
        val TOTAL_LUCAS_CAPACITY = BrahimConstants.LUCAS_TOTAL
    }
}
