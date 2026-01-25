package com.brahim.unified.cosmology

import android.os.Bundle
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.brahim.unified.R
import com.brahim.unified.engine.BrahimEngine
import kotlin.math.pow

class DarkMatterActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_calculator)

        title = "Dark Matter"

        val resultText = findViewById<TextView>(R.id.resultText)
        val formulaText = findViewById<TextView>(R.id.formulaText)
        val accuracyText = findViewById<TextView>(R.id.accuracyText)

        val phi = BrahimEngine.PHI
        val matterFrac = BrahimEngine.Cosmology.matterFraction()

        resultText.text = buildString {
            append("COLD DARK MATTER\n")
            append("════════════════════════════════════\n\n")

            append("MATTER DENSITY PARAMETER:\n")
            append("─────────────────────────────────────\n\n")

            append("From the Brahim golden hierarchy:\n\n")

            append("  Ω_m = φ⁵/200 ≈ 0.0551\n")
            val phi5 = phi.pow(5)
            append("  φ⁵ = ${String.format("%.6f", phi5)}\n")
            append("  φ⁵/200 = ${String.format("%.6f", phi5/200)}\n\n")

            append("REFINED CALCULATION:\n")
            append("  Ω_m = ${String.format("%.4f", matterFrac)}\n\n")

            append("PLANCK 2018:\n")
            append("  Ω_m = 0.3153 ± 0.0073\n\n")

            append("Note: The simple φ⁵/200 gives ~5.5%\n")
            append("which represents baryonic fraction.\n")
            append("Total matter ~31.5% includes CDM.")
        }

        formulaText.text = buildString {
            append("BARYONIC vs DARK MATTER:\n")
            append("════════════════════════════════════\n\n")

            val baryonFrac = phi.pow(5) / 200  // ~5.5%
            val totalMatter = 0.315
            val darkMatter = totalMatter - baryonFrac

            append("COMPOSITION BREAKDOWN:\n")
            append("─────────────────────────────────────\n\n")

            append("Baryonic (φ⁵/200):\n")
            append("  Ω_b = ${String.format("%.4f", baryonFrac)}\n")
            append("  (Stars, gas, planets, us)\n\n")

            append("Cold Dark Matter:\n")
            append("  Ω_CDM = Ω_m - Ω_b\n")
            append("        = ${String.format("%.4f", darkMatter)}\n")
            append("  (Unknown particles)\n\n")

            append("RATIO:\n")
            append("  Ω_CDM / Ω_b ≈ ${String.format("%.1f", darkMatter / baryonFrac)}\n")
            append("  Dark matter is ~5× baryonic!\n")
        }

        accuracyText.text = buildString {
            append("GALACTIC EVIDENCE:\n")
            append("════════════════════════════════════\n\n")

            append("ROTATION CURVES:\n")
            append("─────────────────────────────────────\n")
            append("Expected (Keplerian): v ∝ 1/√r\n")
            append("Observed: v ≈ constant\n\n")

            append("ASCII Rotation Curve:\n")
            append("v │     ●●●●●●●●●● (observed)\n")
            append("  │   ●\n")
            append("  │  ●   ╲ (expected)\n")
            append("  │ ●      ╲\n")
            append("  │●         ╲\n")
            append("  └────────────────→ r\n\n")

            append("BRAHIM INTERPRETATION:\n")
            append("─────────────────────────────────────\n")
            append("The φ-structure of matter density\n")
            append("suggests dark matter may emerge\n")
            append("from geometric properties of space\n")
            append("rather than new particles.\n\n")

            append("B(4)/B(7) = ${BrahimEngine.B(4)}/${BrahimEngine.B(7)}\n")
            append("          = ${String.format("%.4f", BrahimEngine.B(4).toDouble() / BrahimEngine.B(7))}\n")
            append("          ≈ CDM/baryon ratio ÷ 10")
        }
    }
}
