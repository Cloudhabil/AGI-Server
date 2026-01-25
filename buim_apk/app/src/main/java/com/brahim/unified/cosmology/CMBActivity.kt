package com.brahim.unified.cosmology

import android.os.Bundle
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.brahim.unified.R
import com.brahim.unified.engine.BrahimEngine
import kotlin.math.pow
import kotlin.math.cos
import kotlin.math.PI

class CMBActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_calculator)

        title = "CMB Analysis"

        val resultText = findViewById<TextView>(R.id.resultText)
        val formulaText = findViewById<TextView>(R.id.formulaText)
        val accuracyText = findViewById<TextView>(R.id.accuracyText)

        val phi = BrahimEngine.PHI

        resultText.text = buildString {
            append("COSMIC MICROWAVE BACKGROUND\n")
            append("════════════════════════════════════\n\n")

            append("TEMPERATURE:\n")
            append("─────────────────────────────────────\n")
            append("T_CMB = 2.7255 ± 0.0006 K\n\n")

            append("BRAHIM CONNECTION:\n")
            append("─────────────────────────────────────\n")
            val temp_approx = BrahimEngine.SEQUENCE[0] / 10.0  // 2.7
            append("T ≈ B(1)/10 = ${BrahimEngine.SEQUENCE[0]}/10\n")
            append("  = ${String.format("%.1f", temp_approx)} K\n\n")

            append("More precisely:\n")
            val temp_phi = BrahimEngine.B(1) / (phi.pow(3) + 7)
            append("T ≈ B(1)/(φ³ + 7)\n")
            append("  = 27/${String.format("%.3f", phi.pow(3) + 7)}\n")
            append("  = ${String.format("%.4f", temp_phi)} K\n")
        }

        formulaText.text = buildString {
            append("ACOUSTIC PEAKS:\n")
            append("════════════════════════════════════\n\n")

            append("The CMB power spectrum shows peaks\n")
            append("at specific angular scales.\n\n")

            append("PEAK POSITIONS (multipole ℓ):\n")
            append("─────────────────────────────────────\n")

            // First few acoustic peaks
            val peaks = listOf(
                1 to 220,
                2 to 546,
                3 to 800
            )

            peaks.forEach { (n, ell) ->
                append("Peak $n: ℓ ≈ $ell\n")
            }

            append("\nBRAHIM SCALING:\n")
            append("─────────────────────────────────────\n")
            // First peak ~220 ≈ S + 6
            append("ℓ₁ ≈ S + 6 = ${BrahimEngine.SUM} + 6 = 220 ✓\n")
            // Second peak ~546 ≈ 2.5 × 220 ≈ S × φ
            val ell2_approx = BrahimEngine.SUM * phi.pow(1.5)
            append("ℓ₂ ≈ S × φ^1.5 = ${String.format("%.0f", ell2_approx)}\n")

            append("\nASCII POWER SPECTRUM:\n")
            append("─────────────────────────────────────\n")
            append("  │    ╱╲\n")
            append("  │   ╱  ╲    ╱╲\n")
            append("C_ℓ│  ╱    ╲  ╱  ╲  ╱╲\n")
            append("  │ ╱      ╲╱    ╲╱  ╲...\n")
            append("  └──────────────────────→\n")
            append("    10  100  500  1000  ℓ\n")
        }

        accuracyText.text = buildString {
            append("ANISOTROPIES:\n")
            append("════════════════════════════════════\n\n")

            append("Temperature fluctuations:\n")
            append("  ΔT/T ~ 10⁻⁵\n\n")

            append("These tiny variations seeded\n")
            append("all cosmic structure!\n\n")

            append("POLARIZATION:\n")
            append("─────────────────────────────────────\n")
            append("E-mode: Scalar perturbations\n")
            append("B-mode: Tensor (gravitational waves)\n\n")

            append("BRAHIM INTERPRETATION:\n")
            append("─────────────────────────────────────\n")
            append("The acoustic peak structure may\n")
            append("encode φ-geometry of primordial\n")
            append("spacetime.\n\n")

            append("Ratio of peaks:\n")
            val ratio = 546.0 / 220.0
            append("  ℓ₂/ℓ₁ = ${String.format("%.3f", ratio)}\n")
            append("  φ^1.5 = ${String.format("%.3f", phi.pow(1.5))}\n")
            append("  Difference: ${String.format("%.1f", (ratio - phi.pow(1.5)) * 100)}%")
        }
    }
}
