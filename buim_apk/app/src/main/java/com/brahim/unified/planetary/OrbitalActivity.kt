package com.brahim.unified.planetary

import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.brahim.unified.R
import com.brahim.unified.core.BrahimConstants
import kotlin.math.sqrt
import kotlin.math.pow
import kotlin.math.PI

class OrbitalActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_dual_input)

        title = "Orbital Mechanics"

        val altitudeField = findViewById<EditText>(R.id.inputField1)
        val massField = findViewById<EditText>(R.id.inputField2)
        val calculateBtn = findViewById<Button>(R.id.calculateButton)
        val resultText = findViewById<TextView>(R.id.resultText)

        altitudeField.hint = "Orbital altitude (km)"
        massField.hint = "Central body (1=Earth, 2=Mars)"

        calculateBtn.setOnClickListener {
            val altitude = altitudeField.text.toString().toDoubleOrNull() ?: 400.0
            val bodyType = massField.text.toString().toIntOrNull() ?: 1

            val phi = BrahimConstants.PHI
            val beta = BrahimConstants.BETA_SECURITY

            // Planetary parameters
            val (bodyName, radius, mu) = when (bodyType) {
                1 -> Triple("Earth", 6371.0, 398600.4)  // km, km³/s²
                2 -> Triple("Mars", 3389.5, 42828.0)
                else -> Triple("Earth", 6371.0, 398600.4)
            }

            val r = radius + altitude  // orbital radius

            // Orbital velocity
            val velocity = sqrt(mu / r)  // km/s

            // Orbital period
            val period = 2 * PI * sqrt(r.pow(3) / mu)  // seconds
            val periodMin = period / 60

            // Escape velocity
            val escapeVel = sqrt(2 * mu / r)

            // Hohmann transfer to higher orbit
            val targetAlt = altitude * phi  // Golden ratio higher
            val r2 = radius + targetAlt
            val deltaV1 = sqrt(mu / r) * (sqrt(2 * r2 / (r + r2)) - 1)
            val deltaV2 = sqrt(mu / r2) * (1 - sqrt(2 * r / (r + r2)))
            val totalDeltaV = deltaV1 + deltaV2

            // Brahim orbit classifications
            val orbitType = when {
                altitude < BrahimConstants.B(3) -> "Very Low (below B(3))"
                altitude < BrahimConstants.B(5) * 4 -> "Low (LEO range)"
                altitude < BrahimConstants.B(7) * 100 -> "Medium (MEO range)"
                altitude < BrahimConstants.B(10) * 200 -> "High"
                else -> "Geosynchronous+"
            }

            resultText.text = buildString {
                append("ORBITAL MECHANICS\n")
                append("$bodyName Orbit Analysis\n\n")
                append("ORBIT PARAMETERS:\n")
                append("  Altitude: ${String.format("%.0f", altitude)} km\n")
                append("  Radius: ${String.format("%.0f", r)} km\n")
                append("  Type: $orbitType\n\n")
                append("DYNAMICS:\n")
                append("  Velocity: ${String.format("%.3f", velocity)} km/s\n")
                append("  Period: ${String.format("%.1f", periodMin)} min\n")
                append("  Escape: ${String.format("%.3f", escapeVel)} km/s\n\n")
                append("HOHMANN TRANSFER:\n")
                append("  Target: ${String.format("%.0f", targetAlt)} km (×φ)\n")
                append("  ΔV₁: ${String.format("%.4f", deltaV1)} km/s\n")
                append("  ΔV₂: ${String.format("%.4f", deltaV2)} km/s\n")
                append("  Total: ${String.format("%.4f", totalDeltaV)} km/s\n\n")
                append("BRAHIM ORBITS:\n")
                append("  B(3)×1 = ${BrahimConstants.B(3)} km (VL)\n")
                append("  B(5)×4 = ${BrahimConstants.B(5) * 4} km (LEO)\n")
                append("  B(7)×100 = ${BrahimConstants.B(7) * 100} km (MEO)\n")
                append("  B(10)×200 = ${BrahimConstants.B(10) * 200} km (GEO)")
            }
        }
    }
}
