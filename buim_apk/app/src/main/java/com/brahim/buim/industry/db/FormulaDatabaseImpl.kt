/**
 * Engineering Formulas Database
 * ==============================
 *
 * Embedded engineering formulas and equations.
 * Deterministic source - handbook level trust.
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-26
 */

package com.brahim.buim.industry.db

import com.brahim.buim.industry.*
import kotlin.math.*

/**
 * Engineering formula entry
 */
data class FormulaEntry(
    val name: String,
    val formula: String,          // LaTeX-like notation
    val description: String,
    val variables: Map<String, String>,  // variable -> description
    val sector: Sector,
    val keywords: List<String>,
    val example: String?,
    val itemId: Long
)

/**
 * Embedded Engineering Formulas Database
 */
class FormulaDatabaseImpl : HandbookDatabase {

    private val formulas: List<FormulaEntry> = listOf(
        // =====================================================================
        // ELECTRICAL FORMULAS
        // =====================================================================
        FormulaEntry(
            name = "Ohm's Law",
            formula = "V = I × R",
            description = "Relationship between voltage, current, and resistance",
            variables = mapOf(
                "V" to "Voltage (Volts)",
                "I" to "Current (Amperes)",
                "R" to "Resistance (Ohms)"
            ),
            sector = Sector.ELECTRICAL,
            keywords = listOf("ohm", "voltage", "current", "resistance", "law"),
            example = "If R = 10Ω and I = 2A, then V = 20V",
            itemId = 1001
        ),
        FormulaEntry(
            name = "Electrical Power",
            formula = "P = V × I = I²R = V²/R",
            description = "Electrical power calculation",
            variables = mapOf(
                "P" to "Power (Watts)",
                "V" to "Voltage (Volts)",
                "I" to "Current (Amperes)",
                "R" to "Resistance (Ohms)"
            ),
            sector = Sector.ELECTRICAL,
            keywords = listOf("power", "watt", "electrical", "energy"),
            example = "If V = 230V and I = 10A, then P = 2300W",
            itemId = 1002
        ),
        FormulaEntry(
            name = "Three-Phase Power",
            formula = "P = √3 × V_L × I_L × cos(φ)",
            description = "Three-phase AC power calculation",
            variables = mapOf(
                "P" to "Active Power (Watts)",
                "V_L" to "Line Voltage (Volts)",
                "I_L" to "Line Current (Amperes)",
                "cos(φ)" to "Power Factor"
            ),
            sector = Sector.ELECTRICAL,
            keywords = listOf("three phase", "power", "ac", "line", "power factor"),
            example = "If V_L = 400V, I_L = 10A, pf = 0.85, then P = 5.9kW",
            itemId = 1003
        ),
        FormulaEntry(
            name = "Capacitor Reactance",
            formula = "X_C = 1 / (2πfC)",
            description = "Capacitive reactance at given frequency",
            variables = mapOf(
                "X_C" to "Capacitive Reactance (Ohms)",
                "f" to "Frequency (Hz)",
                "C" to "Capacitance (Farads)"
            ),
            sector = Sector.ELECTRICAL,
            keywords = listOf("capacitor", "reactance", "frequency", "impedance"),
            example = "If f = 50Hz, C = 100µF, then X_C = 31.8Ω",
            itemId = 1004
        ),
        FormulaEntry(
            name = "Inductor Reactance",
            formula = "X_L = 2πfL",
            description = "Inductive reactance at given frequency",
            variables = mapOf(
                "X_L" to "Inductive Reactance (Ohms)",
                "f" to "Frequency (Hz)",
                "L" to "Inductance (Henries)"
            ),
            sector = Sector.ELECTRICAL,
            keywords = listOf("inductor", "reactance", "frequency", "impedance", "coil"),
            example = "If f = 50Hz, L = 100mH, then X_L = 31.4Ω",
            itemId = 1005
        ),
        FormulaEntry(
            name = "Transformer Ratio",
            formula = "V1/V2 = N1/N2 = I2/I1",
            description = "Transformer voltage and current ratios",
            variables = mapOf(
                "V1" to "Primary Voltage",
                "V2" to "Secondary Voltage",
                "N1" to "Primary Turns",
                "N2" to "Secondary Turns",
                "I1" to "Primary Current",
                "I2" to "Secondary Current"
            ),
            sector = Sector.ELECTRICAL,
            keywords = listOf("transformer", "ratio", "turns", "voltage", "step"),
            example = "If N1=1000, N2=100, V1=230V, then V2=23V",
            itemId = 1006
        ),

        // =====================================================================
        // ENERGY / RENEWABLE FORMULAS
        // =====================================================================
        FormulaEntry(
            name = "Solar Panel Output",
            formula = "P = A × η × G × PR",
            description = "Photovoltaic power output calculation",
            variables = mapOf(
                "P" to "Power Output (Watts)",
                "A" to "Panel Area (m²)",
                "η" to "Panel Efficiency (decimal)",
                "G" to "Solar Irradiance (W/m²)",
                "PR" to "Performance Ratio (0.75-0.85)"
            ),
            sector = Sector.ENERGY,
            keywords = listOf("solar", "pv", "photovoltaic", "panel", "output", "irradiance"),
            example = "If A=2m², η=0.20, G=1000W/m², PR=0.8, then P=320W",
            itemId = 2001
        ),
        FormulaEntry(
            name = "Wind Turbine Power",
            formula = "P = 0.5 × ρ × A × v³ × Cp",
            description = "Wind turbine power extraction",
            variables = mapOf(
                "P" to "Power (Watts)",
                "ρ" to "Air Density (kg/m³, ~1.225)",
                "A" to "Rotor Swept Area (m²)",
                "v" to "Wind Speed (m/s)",
                "Cp" to "Power Coefficient (max 0.593 Betz limit)"
            ),
            sector = Sector.ENERGY,
            keywords = listOf("wind", "turbine", "power", "betz", "rotor"),
            example = "If ρ=1.225, A=5000m², v=12m/s, Cp=0.4, then P=4.2MW",
            itemId = 2002
        ),
        FormulaEntry(
            name = "Battery Energy",
            formula = "E = V × Ah",
            description = "Battery energy capacity",
            variables = mapOf(
                "E" to "Energy (Watt-hours)",
                "V" to "Nominal Voltage (Volts)",
                "Ah" to "Amp-hour Capacity"
            ),
            sector = Sector.ENERGY,
            keywords = listOf("battery", "energy", "capacity", "watt hour", "storage"),
            example = "If V=48V, Ah=100Ah, then E=4.8kWh",
            itemId = 2003
        ),
        FormulaEntry(
            name = "Battery State of Charge",
            formula = "SoC = (Ah_remaining / Ah_total) × 100%",
            description = "Battery state of charge percentage",
            variables = mapOf(
                "SoC" to "State of Charge (%)",
                "Ah_remaining" to "Remaining Capacity (Ah)",
                "Ah_total" to "Total Capacity (Ah)"
            ),
            sector = Sector.ENERGY,
            keywords = listOf("battery", "soc", "state", "charge", "remaining"),
            example = "If 80Ah remaining of 100Ah total, SoC = 80%",
            itemId = 2004
        ),
        FormulaEntry(
            name = "Grid Frequency Droop",
            formula = "ΔP = -K × Δf",
            description = "Power-frequency droop control for grid stability",
            variables = mapOf(
                "ΔP" to "Power Change (MW)",
                "K" to "Droop Coefficient (MW/Hz)",
                "Δf" to "Frequency Deviation (Hz)"
            ),
            sector = Sector.ENERGY,
            keywords = listOf("grid", "frequency", "droop", "control", "stability"),
            example = "If K=100MW/Hz and Δf=-0.1Hz, then ΔP=+10MW",
            itemId = 2005
        ),

        // =====================================================================
        // MECHANICAL FORMULAS
        // =====================================================================
        FormulaEntry(
            name = "Torque",
            formula = "τ = F × r",
            description = "Torque from force and radius",
            variables = mapOf(
                "τ" to "Torque (N·m)",
                "F" to "Force (Newtons)",
                "r" to "Radius (meters)"
            ),
            sector = Sector.MECHANICAL,
            keywords = listOf("torque", "force", "radius", "moment", "rotation"),
            example = "If F=100N at r=0.5m, then τ=50N·m",
            itemId = 3001
        ),
        FormulaEntry(
            name = "Rotational Power",
            formula = "P = τ × ω = (2π × n × τ) / 60",
            description = "Power from torque and angular velocity",
            variables = mapOf(
                "P" to "Power (Watts)",
                "τ" to "Torque (N·m)",
                "ω" to "Angular Velocity (rad/s)",
                "n" to "Rotational Speed (RPM)"
            ),
            sector = Sector.MECHANICAL,
            keywords = listOf("power", "torque", "rpm", "angular", "motor"),
            example = "If τ=10N·m at 3000RPM, then P=3.14kW",
            itemId = 3002
        ),
        FormulaEntry(
            name = "Stress",
            formula = "σ = F / A",
            description = "Mechanical stress from force over area",
            variables = mapOf(
                "σ" to "Stress (Pa or N/m²)",
                "F" to "Force (Newtons)",
                "A" to "Cross-sectional Area (m²)"
            ),
            sector = Sector.MECHANICAL,
            keywords = listOf("stress", "force", "area", "tension", "compression"),
            example = "If F=10kN on A=0.001m², then σ=10MPa",
            itemId = 3003
        ),
        FormulaEntry(
            name = "Strain",
            formula = "ε = ΔL / L₀",
            description = "Mechanical strain from deformation",
            variables = mapOf(
                "ε" to "Strain (dimensionless)",
                "ΔL" to "Change in Length",
                "L₀" to "Original Length"
            ),
            sector = Sector.MECHANICAL,
            keywords = listOf("strain", "deformation", "elongation", "stretch"),
            example = "If ΔL=0.1mm on L₀=100mm, then ε=0.001",
            itemId = 3004
        ),
        FormulaEntry(
            name = "Young's Modulus",
            formula = "E = σ / ε",
            description = "Elastic modulus relating stress to strain",
            variables = mapOf(
                "E" to "Young's Modulus (Pa)",
                "σ" to "Stress (Pa)",
                "ε" to "Strain (dimensionless)"
            ),
            sector = Sector.MECHANICAL,
            keywords = listOf("young", "modulus", "elastic", "stiffness", "material"),
            example = "Steel: E ≈ 200 GPa, Aluminum: E ≈ 70 GPa",
            itemId = 3005
        ),
        FormulaEntry(
            name = "Reynolds Number",
            formula = "Re = (ρ × v × L) / μ = (v × L) / ν",
            description = "Dimensionless number for flow regime",
            variables = mapOf(
                "Re" to "Reynolds Number",
                "ρ" to "Fluid Density (kg/m³)",
                "v" to "Velocity (m/s)",
                "L" to "Characteristic Length (m)",
                "μ" to "Dynamic Viscosity (Pa·s)",
                "ν" to "Kinematic Viscosity (m²/s)"
            ),
            sector = Sector.MECHANICAL,
            keywords = listOf("reynolds", "flow", "laminar", "turbulent", "viscosity"),
            example = "Re < 2300: laminar, Re > 4000: turbulent",
            itemId = 3006
        ),

        // =====================================================================
        // CHEMICAL FORMULAS
        // =====================================================================
        FormulaEntry(
            name = "Ideal Gas Law",
            formula = "PV = nRT",
            description = "Relationship between pressure, volume, and temperature for ideal gases",
            variables = mapOf(
                "P" to "Pressure (Pa)",
                "V" to "Volume (m³)",
                "n" to "Amount of substance (mol)",
                "R" to "Gas constant (8.314 J/(mol·K))",
                "T" to "Temperature (Kelvin)"
            ),
            sector = Sector.CHEMICAL,
            keywords = listOf("gas", "pressure", "volume", "temperature", "ideal"),
            example = "1 mol at STP: P=101325Pa, T=273K, V=22.4L",
            itemId = 4001
        ),
        FormulaEntry(
            name = "Heat Transfer",
            formula = "Q = m × c × ΔT",
            description = "Heat energy for temperature change",
            variables = mapOf(
                "Q" to "Heat Energy (Joules)",
                "m" to "Mass (kg)",
                "c" to "Specific Heat Capacity (J/(kg·K))",
                "ΔT" to "Temperature Change (K or °C)"
            ),
            sector = Sector.CHEMICAL,
            keywords = listOf("heat", "temperature", "specific", "thermal", "energy"),
            example = "Water: c=4186 J/(kg·K)",
            itemId = 4002
        ),

        // =====================================================================
        // DIGITAL/COMPUTING FORMULAS
        // =====================================================================
        FormulaEntry(
            name = "Shannon Capacity",
            formula = "C = B × log₂(1 + S/N)",
            description = "Maximum channel capacity",
            variables = mapOf(
                "C" to "Channel Capacity (bits/s)",
                "B" to "Bandwidth (Hz)",
                "S/N" to "Signal-to-Noise Ratio"
            ),
            sector = Sector.DIGITAL,
            keywords = listOf("shannon", "capacity", "bandwidth", "channel", "snr"),
            example = "If B=1MHz, SNR=100, then C≈6.66Mbps",
            itemId = 5001
        ),
        FormulaEntry(
            name = "Nyquist Sampling",
            formula = "f_s ≥ 2 × f_max",
            description = "Minimum sampling frequency to avoid aliasing",
            variables = mapOf(
                "f_s" to "Sampling Frequency (Hz)",
                "f_max" to "Maximum Signal Frequency (Hz)"
            ),
            sector = Sector.DIGITAL,
            keywords = listOf("nyquist", "sampling", "frequency", "aliasing", "adc"),
            example = "For audio (20kHz max), f_s ≥ 40kHz (CD uses 44.1kHz)",
            itemId = 5002
        )
    )

    override suspend fun search(keywords: List<String>, sector: Sector): SearchHit? {
        val normalizedKeywords = keywords.map { it.lowercase() }

        val scored = formulas
            .filter { it.sector == sector }
            .map { formula ->
                val keywordMatches = formula.keywords.count { kw ->
                    normalizedKeywords.any { it.contains(kw) || kw.contains(it) }
                }
                val nameMatch = if (normalizedKeywords.any { formula.name.lowercase().contains(it) }) 3 else 0

                val score = (keywordMatches + nameMatch).toDouble() /
                           (formula.keywords.size + 3).toDouble()

                formula to score
            }
            .filter { it.second > 0.15 }
            .maxByOrNull { it.second }

        return scored?.let { (formula, score) ->
            SearchHit(
                value = "${formula.name}: ${formula.formula}",
                source = Source.ENGINEERING_HANDBOOK,
                itemId = formula.itemId,
                citation = "Engineering Handbook - ${formula.description}",
                relevanceScore = score.coerceIn(0.0, 1.0)
            )
        }
    }

    override suspend fun getByTopic(topic: String): SearchHit? {
        val formula = formulas.find {
            it.name.equals(topic, ignoreCase = true) ||
            it.keywords.any { kw -> kw.equals(topic, ignoreCase = true) }
        }

        return formula?.let {
            SearchHit(
                value = "${it.name}: ${it.formula}",
                source = Source.ENGINEERING_HANDBOOK,
                itemId = it.itemId,
                citation = "Engineering Handbook - ${it.description}",
                relevanceScore = 1.0
            )
        }
    }

    /**
     * Get formula with full details including variables
     */
    fun getFormulaDetails(name: String): FormulaEntry? {
        return formulas.find { it.name.equals(name, ignoreCase = true) }
    }

    /**
     * Get all formulas for a sector
     */
    fun getFormulasBySector(sector: Sector): List<FormulaEntry> {
        return formulas.filter { it.sector == sector }
    }

    /**
     * Calculate formula result (for simple formulas)
     */
    fun calculate(formulaName: String, values: Map<String, Double>): Double? {
        return when (formulaName.lowercase()) {
            "ohm's law" -> values["I"]?.let { i -> values["R"]?.let { r -> i * r } }
            "electrical power" -> values["V"]?.let { v -> values["I"]?.let { i -> v * i } }
            "torque" -> values["F"]?.let { f -> values["r"]?.let { r -> f * r } }
            "stress" -> values["F"]?.let { f -> values["A"]?.let { a -> f / a } }
            "battery energy" -> values["V"]?.let { v -> values["Ah"]?.let { ah -> v * ah } }
            else -> null
        }
    }

    fun getFormulaCount(): Int = formulas.size
}
