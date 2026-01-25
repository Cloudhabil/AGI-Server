package com.brahim.unified.traffic

import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.brahim.unified.R
import com.brahim.unified.core.BrahimConstants
import kotlin.math.exp
import kotlin.math.ln

class CongestionActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_dual_input)

        title = "Congestion Predictor"

        val densityField = findViewById<EditText>(R.id.inputField1)
        val speedField = findViewById<EditText>(R.id.inputField2)
        val calculateBtn = findViewById<Button>(R.id.calculateButton)
        val resultText = findViewById<TextView>(R.id.resultText)

        densityField.hint = "Density (vehicles/km)"
        speedField.hint = "Average Speed (km/h)"

        calculateBtn.setOnClickListener {
            val density = densityField.text.toString().toDoubleOrNull()
            val speed = speedField.text.toString().toDoubleOrNull()

            if (density != null && speed != null && density > 0) {
                val flow = density * speed
                val criticalDensity = BrahimConstants.B(3).toDouble()
                val jamDensity = BrahimConstants.B(10).toDouble()

                val losRatio = density / criticalDensity
                val los = when {
                    losRatio < 0.35 -> "A - Free Flow"
                    losRatio < 0.55 -> "B - Stable Flow"
                    losRatio < 0.75 -> "C - Stable Flow"
                    losRatio < 0.90 -> "D - High Density"
                    losRatio < 1.00 -> "E - Near Capacity"
                    else -> "F - Congested"
                }

                val resonance = BrahimConstants.resonance(
                    listOf(density / 100),
                    listOf(0.0)
                )
                val waveSpeed = speed - density * (speed / jamDensity)

                resultText.text = buildString {
                    append("CONGESTION ANALYSIS\n\n")
                    append("Input:\n")
                    append("  Density: $density veh/km\n")
                    append("  Speed: $speed km/h\n\n")
                    append("Results:\n")
                    append("  Flow: ${String.format("%.0f", flow)} veh/h\n")
                    append("  Level of Service: $los\n")
                    append("  Wave Speed: ${String.format("%.1f", waveSpeed)} km/h\n\n")
                    append("Brahim Thresholds:\n")
                    append("  Critical Density: $criticalDensity veh/km\n")
                    append("  Jam Density: $jamDensity veh/km\n")
                    append("  Resonance: ${String.format("%.4f", resonance)}")
                }
            } else {
                resultText.text = "Please enter valid positive numbers"
            }
        }
    }
}
