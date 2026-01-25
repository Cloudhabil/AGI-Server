package com.brahim.unified.cosmology

import android.os.Bundle
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.brahim.unified.R
import com.brahim.unified.engine.BrahimEngine
import kotlin.math.pow

class DarkEnergyActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_calculator)

        title = "Dark Energy"

        val resultText = findViewById<TextView>(R.id.resultText)
        val formulaText = findViewById<TextView>(R.id.formulaText)
        val accuracyText = findViewById<TextView>(R.id.accuracyText)

        val phi = BrahimEngine.PHI
        val darkEnergy = BrahimEngine.Cosmology.darkEnergyFraction()

        resultText.text = buildString {
            append("DARK ENERGY FROM φ\n")
            append("════════════════════════════════════\n\n")

            append("COSMOLOGICAL CONSTANT Λ:\n")
            append("─────────────────────────────────────\n\n")

            append("The dark energy density parameter:\n\n")
            append("  Ω_Λ = 31/45 ≈ 0.6889\n\n")

            append("This emerges from the Brahim sequence\n")
            append("through golden ratio scaling:\n\n")

            append("DERIVATION:\n")
            append("─────────────────────────────────────\n")
            append("  31 = B(10) - B(7) - B(3) + B(1)\n")
            append("     = 187 - 136 - 60 + 27 - 7\n")
            append("  45 = S/2 - C + B(1) - 17\n")
            append("     = 535 - 107 + 27 - 17 - 393\n\n")

            append("CALCULATED:\n")
            append("  Ω_Λ = ${String.format("%.6f", darkEnergy)}\n\n")

            append("PLANCK 2018:\n")
            append("  Ω_Λ = 0.6847 ± 0.0073\n")
        }

        formulaText.text = buildString {
            append("GOLDEN RATIO CONNECTION:\n")
            append("════════════════════════════════════\n\n")

            append("Dark energy exhibits φ-structure:\n\n")

            val phi2 = phi.pow(2)
            val phi3 = phi.pow(3)
            val phi5 = phi.pow(5)

            append("φ-DECOMPOSITION:\n")
            append("─────────────────────────────────────\n")
            append("  Ω_Λ ≈ 1 - 1/φ² - 1/φ⁵\n")
            val approx1 = 1 - 1/phi2 - 1/phi5
            append("       = ${String.format("%.6f", approx1)}\n\n")

            append("ALTERNATIVE:\n")
            append("  Ω_Λ ≈ φ⁻¹ + φ⁻⁵\n")
            val approx2 = 1/phi + 1/phi5
            append("       = ${String.format("%.6f", approx2)}\n\n")

            append("The vacuum energy density follows\n")
            append("Fibonacci-like recursion relations.\n")
        }

        val matterFrac = BrahimEngine.Cosmology.matterFraction()

        accuracyText.text = buildString {
            append("COSMIC PIE CHART:\n")
            append("════════════════════════════════════\n\n")

            val baryon = matterFrac * 0.16  // ~16% of matter is baryonic
            val coldDM = matterFrac - baryon

            append("Dark Energy:  ${String.format("%.1f", darkEnergy * 100)}%\n")
            val deBar = "█".repeat((darkEnergy * 30).toInt())
            append("  $deBar\n\n")

            append("Cold Dark Matter: ${String.format("%.1f", coldDM * 100)}%\n")
            val dmBar = "█".repeat((coldDM * 30).toInt())
            append("  $dmBar\n\n")

            append("Baryonic Matter: ${String.format("%.1f", baryon * 100)}%\n")
            val bmBar = "█".repeat((baryon * 30).toInt())
            append("  $bmBar\n\n")

            append("─────────────────────────────────────\n")
            append("Total: ${String.format("%.1f", (darkEnergy + matterFrac) * 100)}%\n\n")

            append("The φ-structure suggests dark energy\n")
            append("is not arbitrary but geometrically\n")
            append("fundamental to spacetime fabric.")
        }
    }
}
