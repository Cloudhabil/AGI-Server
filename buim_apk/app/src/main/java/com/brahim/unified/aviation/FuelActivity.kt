package com.brahim.unified.aviation

import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.brahim.unified.R
import com.brahim.unified.core.BrahimConstants
import kotlin.math.pow

class FuelActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_quad_input)

        title = "Fuel Optimizer"

        val distanceField = findViewById<EditText>(R.id.inputField1)
        val payloadField = findViewById<EditText>(R.id.inputField2)
        val altitudeField = findViewById<EditText>(R.id.inputField3)
        val windField = findViewById<EditText>(R.id.inputField4)
        val calculateBtn = findViewById<Button>(R.id.calculateButton)
        val resultText = findViewById<TextView>(R.id.resultText)

        distanceField.hint = "Distance (NM)"
        payloadField.hint = "Payload (kg)"
        altitudeField.hint = "Cruise Alt (ft)"
        windField.hint = "Headwind (kt)"

        calculateBtn.setOnClickListener {
            val distance = distanceField.text.toString().toDoubleOrNull() ?: 500.0
            val payload = payloadField.text.toString().toDoubleOrNull() ?: 20000.0
            val altitude = altitudeField.text.toString().toDoubleOrNull() ?: 35000.0
            val headwind = windField.text.toString().toDoubleOrNull() ?: 0.0

            // Brahim-optimized fuel calculation
            val phi = BrahimConstants.PHI
            val beta = BrahimConstants.BETA_SECURITY

            // Base fuel consumption (kg/NM)
            val baseFuel = 3.5

            // Altitude efficiency (optimal around B(7)*100 = 13600 ft, but jets prefer higher)
            val optimalAlt = BrahimConstants.B(5).toDouble() * 360  // 34920 ft
            val altEfficiency = 1.0 - beta * kotlin.math.abs(altitude - optimalAlt) / optimalAlt

            // Payload factor
            val payloadFactor = 1.0 + (payload / 100000.0) * phi

            // Wind correction
            val groundSpeed = 450.0 - headwind  // Assume 450 kt TAS
            val windFactor = 450.0 / groundSpeed

            // Total fuel
            val fuelRequired = distance * baseFuel * payloadFactor * windFactor / altEfficiency

            // Reserve (Brahim golden ratio)
            val reserve = fuelRequired * (1.0 / phi)  // ~61.8% of trip fuel as reserve

            // Optimal cruise speed
            val optimalSpeed = BrahimConstants.B(6).toDouble() * 3.72  // ~450 kt

            resultText.text = buildString {
                append("FUEL OPTIMIZATION\n")
                append("Brahim Resonance Method\n\n")
                append("Flight Parameters:\n")
                append("  Distance: ${String.format("%.0f", distance)} NM\n")
                append("  Payload: ${String.format("%.0f", payload)} kg\n")
                append("  Cruise Alt: ${String.format("%.0f", altitude)} ft\n")
                append("  Headwind: ${String.format("%.0f", headwind)} kt\n\n")
                append("Efficiency Factors:\n")
                append("  Altitude eff: ${String.format("%.2f", altEfficiency * 100)}%\n")
                append("  Payload factor: ${String.format("%.3f", payloadFactor)}\n")
                append("  Wind factor: ${String.format("%.3f", windFactor)}\n\n")
                append("FUEL REQUIRED:\n")
                append("  Trip fuel: ${String.format("%.0f", fuelRequired)} kg\n")
                append("  Reserve (1/φ): ${String.format("%.0f", reserve)} kg\n")
                append("  TOTAL: ${String.format("%.0f", fuelRequired + reserve)} kg\n\n")
                append("Recommendations:\n")
                append("  Optimal alt: ${String.format("%.0f", optimalAlt)} ft\n")
                append("  Optimal speed: ${String.format("%.0f", optimalSpeed)} kt")
            }
        }
    }
}
