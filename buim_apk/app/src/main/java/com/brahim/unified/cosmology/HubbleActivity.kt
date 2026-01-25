package com.brahim.unified.cosmology

import android.os.Bundle
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.brahim.unified.R
import com.brahim.unified.engine.BrahimEngine
import kotlin.math.pow
import kotlin.math.sqrt

class HubbleActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_calculator)

        title = "Hubble Flow"

        val resultText = findViewById<TextView>(R.id.resultText)
        val formulaText = findViewById<TextView>(R.id.formulaText)
        val accuracyText = findViewById<TextView>(R.id.accuracyText)

        val hubble = BrahimEngine.Cosmology.hubbleConstant()
        val phi = BrahimEngine.PHI

        resultText.text = buildString {
            append("HUBBLE CONSTANT FROM BRAHIM\n")
            append("════════════════════════════════════\n\n")

            append("EXPANSION RATE:\n")
            append("─────────────────────────────────────\n\n")

            append("H₀ = S/φ⁴ × correction\n\n")

            val phi4 = phi.pow(4)
            append("Where:\n")
            append("  S = ${BrahimEngine.SUM} (sequence pair sum)\n")
            append("  φ⁴ = ${String.format("%.6f", phi4)}\n")
            append("  S/φ⁴ = ${String.format("%.2f", BrahimEngine.SUM / phi4)}\n\n")

            append("CALCULATED:\n")
            append("  H₀ = ${String.format("%.1f", hubble)} km/s/Mpc\n\n")

            append("OBSERVATIONS:\n")
            append("─────────────────────────────────────\n")
            append("Planck CMB:  67.4 ± 0.5 km/s/Mpc\n")
            append("Local (SH0ES): 73.0 ± 1.0 km/s/Mpc\n\n")

            append("HUBBLE TENSION: ~5σ discrepancy!")
        }

        formulaText.text = buildString {
            append("HUBBLE TENSION & BRAHIM:\n")
            append("════════════════════════════════════\n\n")

            append("The \"Hubble tension\" represents one\n")
            append("of the biggest mysteries in modern\n")
            append("cosmology.\n\n")

            append("BRAHIM INTERPRETATION:\n")
            append("─────────────────────────────────────\n\n")

            // The two measurements might correspond to different φ-scalings
            val h_planck = BrahimEngine.SUM / phi.pow(4) * 10 // ~31.4 * scaling
            val h_local = BrahimEngine.SUM / phi.pow(3.5) * 10

            append("Early Universe (CMB era):\n")
            append("  H₀ ~ S/φ⁴ scaled\n")
            append("  → Lower value\n\n")

            append("Late Universe (local):\n")
            append("  H₀ ~ S/φ³·⁵ scaled\n")
            append("  → Higher value\n\n")

            append("The tension may reflect\n")
            append("φ-evolution of spacetime!")
        }

        accuracyText.text = buildString {
            append("UNIVERSE AGE:\n")
            append("════════════════════════════════════\n\n")

            // Hubble time = 1/H₀
            val hubbleTime = 978.0 / hubble  // in Gyr

            append("HUBBLE TIME:\n")
            append("─────────────────────────────────────\n")
            append("t_H = 1/H₀\n")
            append("    = ${String.format("%.2f", hubbleTime)} Gyr\n\n")

            append("UNIVERSE AGE (corrected):\n")
            append("  t₀ ≈ 0.96 × t_H\n")
            append("     ≈ ${String.format("%.2f", hubbleTime * 0.96)} Gyr\n\n")

            append("Planck measurement: 13.8 Gyr\n\n")

            append("DISTANCE SCALE:\n")
            append("─────────────────────────────────────\n")
            val hubbleRadius = 3000.0 / hubble * 100  // c/H₀ in Mpc
            append("Hubble radius: c/H₀\n")
            append("  = ${String.format("%.0f", hubbleRadius)} Mpc\n")
            append("  = ${String.format("%.1f", hubbleRadius * 3.26)} Gly\n\n")

            append("Observable universe radius:\n")
            append("  ~ 46 billion light-years")
        }
    }
}
