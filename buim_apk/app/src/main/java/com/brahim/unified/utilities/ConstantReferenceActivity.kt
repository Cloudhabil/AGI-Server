package com.brahim.unified.utilities

import android.os.Bundle
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.brahim.unified.R
import com.brahim.unified.engine.BrahimEngine

class ConstantReferenceActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_calculator)

        title = "Constant Reference"

        val resultText = findViewById<TextView>(R.id.resultText)
        val formulaText = findViewById<TextView>(R.id.formulaText)
        val accuracyText = findViewById<TextView>(R.id.accuracyText)

        resultText.text = buildString {
            append("BRAHIM CONSTANTS LIBRARY\n")
            append("════════════════════════════════════\n\n")

            append("FUNDAMENTAL SEQUENCE:\n")
            append("─────────────────────────────────────\n")
            append("B = {${BrahimEngine.SEQUENCE.joinToString(", ")}}\n\n")

            append("DERIVED CONSTANTS:\n")
            append("─────────────────────────────────────\n")
            append("S (Sum)     = ${BrahimEngine.SUM}\n")
            append("C (Center)  = ${BrahimEngine.CENTER}\n")
            append("Δ₄         = ${BrahimEngine.DELTA_4}\n")
            append("Δ₅         = ${BrahimEngine.DELTA_5}\n\n")

            append("GOLDEN HIERARCHY:\n")
            append("─────────────────────────────────────\n")
            append("φ (phi)    = ${String.format("%.15f", BrahimEngine.PHI)}\n")
            append("α (alpha)  = ${String.format("%.15f", BrahimEngine.ALPHA)}\n")
            append("β (beta)   = ${String.format("%.15f", BrahimEngine.BETA)}\n")
            append("γ (gamma)  = ${String.format("%.15f", BrahimEngine.GAMMA)}\n")
        }

        formulaText.text = buildString {
            append("PHYSICS CONSTANTS:\n")
            append("════════════════════════════════════\n\n")

            append("Fine Structure (α⁻¹):\n")
            append("  Calculated: ${String.format("%.6f", BrahimEngine.Physics.fineStructureInverse())}\n")
            append("  CODATA:     137.035999084\n\n")

            append("Weinberg Angle (sin²θ_W):\n")
            append("  Calculated: ${String.format("%.6f", BrahimEngine.Physics.weinbergAngle())}\n")
            append("  CODATA:     0.23122\n\n")

            append("Muon/Electron Mass Ratio:\n")
            append("  Calculated: ${String.format("%.2f", BrahimEngine.Physics.muonElectronRatio())}\n")
            append("  CODATA:     206.7682830\n\n")

            append("Proton/Electron Mass Ratio:\n")
            append("  Calculated: ${String.format("%.1f", BrahimEngine.Physics.protonElectronRatio())}\n")
            append("  CODATA:     1836.152673\n")
        }

        accuracyText.text = buildString {
            append("COSMOLOGY CONSTANTS:\n")
            append("════════════════════════════════════\n\n")

            val cosmo = BrahimEngine.Cosmology

            append("Matter Fraction (Ωₘ):\n")
            append("  Value: ${String.format("%.4f", cosmo.matterFraction())}\n")
            append("  Planck: 0.315\n\n")

            append("Dark Energy Fraction (Ω_Λ):\n")
            append("  Value: ${String.format("%.4f", cosmo.darkEnergyFraction())}\n")
            append("  Planck: 0.685\n\n")

            append("Hubble Constant (H₀):\n")
            append("  Value: ${String.format("%.1f", cosmo.hubbleConstant())} km/s/Mpc\n")
            append("  Planck: 67.4 km/s/Mpc\n\n")

            append("RESONANCE:\n")
            append("─────────────────────────────────────\n")
            append("Genesis: ${BrahimEngine.GENESIS}\n")
        }
    }
}
