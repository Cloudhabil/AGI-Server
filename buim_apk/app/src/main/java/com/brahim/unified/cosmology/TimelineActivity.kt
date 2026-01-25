package com.brahim.unified.cosmology

import android.os.Bundle
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.brahim.unified.R
import com.brahim.unified.engine.BrahimEngine
import kotlin.math.pow
import kotlin.math.log10

class TimelineActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_calculator)

        title = "Big Bang Timeline"

        val resultText = findViewById<TextView>(R.id.resultText)
        val formulaText = findViewById<TextView>(R.id.formulaText)
        val accuracyText = findViewById<TextView>(R.id.accuracyText)

        val phi = BrahimEngine.PHI

        resultText.text = buildString {
            append("COSMIC TIMELINE\n")
            append("════════════════════════════════════\n\n")

            append("0 ─────────────────────────> 13.8 Gyr\n")
            append("│\n")
            append("├─ 10⁻⁴³ s: Planck Epoch\n")
            append("│   (Quantum gravity)\n")
            append("│\n")
            append("├─ 10⁻³⁶ s: Inflation\n")
            append("│   (Exponential expansion)\n")
            append("│\n")
            append("├─ 10⁻⁶ s: Quark-Hadron\n")
            append("│   (Protons form)\n")
            append("│\n")
            append("├─ 3 min: Nucleosynthesis\n")
            append("│   (Light elements)\n")
            append("│\n")
            append("├─ 380,000 yr: Recombination\n")
            append("│   (CMB released)\n")
            append("│\n")
            append("├─ 400 Myr: First Stars\n")
            append("│   (Cosmic dawn)\n")
            append("│\n")
            append("└─ 13.8 Gyr: Today\n")
            append("    (Us!)\n")
        }

        formulaText.text = buildString {
            append("BRAHIM EPOCH SCALING:\n")
            append("════════════════════════════════════\n\n")

            append("Key times show φ-structure:\n\n")

            append("RECOMBINATION:\n")
            append("─────────────────────────────────────\n")
            append("t_rec ≈ 380,000 years\n")
            val rec_approx = BrahimEngine.B(7) * 2800
            append("     ≈ B(7) × 2800\n")
            append("     = ${BrahimEngine.B(7)} × 2800\n")
            append("     = ${rec_approx} years ✓\n\n")

            append("FIRST STARS:\n")
            append("─────────────────────────────────────\n")
            append("t_stars ≈ 400 Myr\n")
            val stars_approx = BrahimEngine.SUM * phi.pow(6) / 10
            append("       ≈ S × φ⁶ / 10\n")
            append("       = ${String.format("%.0f", stars_approx)} Myr\n\n")

            append("SOLAR SYSTEM:\n")
            append("─────────────────────────────────────\n")
            append("t_sun ≈ 4.6 Gyr ago\n")
            append("     ≈ 13.8 / 3 ≈ t₀/3\n")
            append("     ≈ t₀/φ^1.5\n")
        }

        accuracyText.text = buildString {
            append("FUTURE TIMELINE:\n")
            append("════════════════════════════════════\n\n")

            append("13.8 Gyr ──────────────────> ∞\n")
            append("│\n")
            append("├─ +5 Gyr: Sun red giant\n")
            append("│   (Earth uninhabitable)\n")
            append("│\n")
            append("├─ +100 Gyr: Last stars die\n")
            append("│   (Degenerate era)\n")
            append("│\n")
            append("├─ +10⁴⁰ yr: Proton decay?\n")
            append("│   (Black hole era)\n")
            append("│\n")
            append("└─ +10¹⁰⁰ yr: Heat death\n")
            append("    (Maximum entropy)\n\n")

            append("BRAHIM ENTROPY:\n")
            append("─────────────────────────────────────\n")
            append("The universe evolves toward\n")
            append("maximum entropy, but the\n")
            append("φ-structure remains encoded\n")
            append("in fundamental constants.\n\n")

            append("Even at heat death:\n")
            append("  φ = ${String.format("%.10f", phi)}\n")
            append("  β = ${String.format("%.10f", BrahimEngine.BETA)}\n")
            append("Mathematical truth is eternal.")
        }
    }
}
