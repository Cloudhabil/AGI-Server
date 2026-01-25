package com.brahim.unified.traffic

import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.brahim.unified.R
import com.brahim.unified.core.BrahimConstants
import kotlin.math.exp
import kotlin.math.sin

class WavesActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_dual_input)

        title = "Traffic Waves"

        val densityField = findViewById<EditText>(R.id.inputField1)
        val disturbanceField = findViewById<EditText>(R.id.inputField2)
        val calculateBtn = findViewById<Button>(R.id.calculateButton)
        val resultText = findViewById<TextView>(R.id.resultText)

        densityField.hint = "Initial Density (veh/km)"
        disturbanceField.hint = "Disturbance Magnitude"

        calculateBtn.setOnClickListener {
            val density = densityField.text.toString().toDoubleOrNull() ?: 50.0
            val disturbance = disturbanceField.text.toString().toDoubleOrNull() ?: 10.0

            val phi = BrahimConstants.PHI
            val beta = BrahimConstants.BETA_SECURITY
            val genesis = BrahimConstants.GENESIS_CONSTANT

            // Method of Characteristics for traffic waves
            val criticalDensity = BrahimConstants.B(3).toDouble()  // 60 veh/km
            val jamDensity = BrahimConstants.B(10).toDouble()  // 187 veh/km

            // Wave speed (LWR model)
            val freeFlowSpeed = 100.0  // km/h
            val waveSpeed = freeFlowSpeed * (1 - 2 * density / jamDensity)

            // Shock wave formation
            val shockSpeed = if (density > criticalDensity) {
                -freeFlowSpeed * disturbance / jamDensity
            } else {
                0.0
            }

            // Damping with Brahim gamma
            val gamma = BrahimConstants.GAMMA_DAMPING
            val dampingTime = 1.0 / (gamma * genesis)

            // Wave profile at different times
            val times = listOf(0.0, 5.0, 10.0, 20.0, 30.0)
            val profiles = times.map { t ->
                val amplitude = disturbance * exp(-gamma * t)
                val position = waveSpeed * t / 60  // km
                Triple(t, amplitude, position)
            }

            resultText.text = buildString {
                append("TRAFFIC WAVE ANALYSIS\n")
                append("Method of Characteristics\n\n")
                append("Initial Conditions:\n")
                append("  Density: ${String.format("%.0f", density)} veh/km\n")
                append("  Disturbance: ${String.format("%.0f", disturbance)} veh/km\n\n")
                append("WAVE PROPERTIES:\n")
                append("  Wave speed: ${String.format("%.1f", waveSpeed)} km/h\n")
                append("  Direction: ${if (waveSpeed > 0) "Forward" else "Backward"}\n")
                append("  Shock speed: ${String.format("%.1f", shockSpeed)} km/h\n\n")
                append("Thresholds (Brahim):\n")
                append("  Critical: $criticalDensity veh/km (B(3))\n")
                append("  Jam: $jamDensity veh/km (B(10))\n\n")
                append("WAVE EVOLUTION:\n")
                profiles.forEach { (t, amp, pos) ->
                    append("  t=${String.format("%.0f", t)} min: ")
                    append("A=${String.format("%.1f", amp)}, ")
                    append("x=${String.format("%.2f", pos)} km\n")
                }
                append("\nDAMPING:\n")
                append("  γ = ${String.format("%.6f", gamma)}\n")
                append("  Decay time: ${String.format("%.0f", dampingTime)} min\n\n")
                append("PDE: ∂ρ/∂t + c(ρ)∂ρ/∂x = 0\n")
                append("c(ρ) = v_f(1 - 2ρ/ρ_j)")
            }
        }
    }
}
