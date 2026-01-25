package com.brahim.unified.aviation

import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.brahim.unified.R
import com.brahim.unified.core.BrahimConstants
import kotlin.math.exp

class AltitudeActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_dual_input)

        title = "Altitude Optimizer"

        val distanceField = findViewById<EditText>(R.id.inputField1)
        val weightField = findViewById<EditText>(R.id.inputField2)
        val calculateBtn = findViewById<Button>(R.id.calculateButton)
        val resultText = findViewById<TextView>(R.id.resultText)

        distanceField.hint = "Distance (NM)"
        weightField.hint = "Takeoff Weight (kg)"

        calculateBtn.setOnClickListener {
            val distance = distanceField.text.toString().toDoubleOrNull() ?: 1000.0
            val weight = weightField.text.toString().toDoubleOrNull() ?: 75000.0

            // Brahim-derived altitude bands
            val altitudeBands = listOf(
                AltitudeBand("FL270", 27000, BrahimConstants.B(1) * 1000),
                AltitudeBand("FL330", 33000, (BrahimConstants.B(2) - 9) * 1000),
                AltitudeBand("FL350", 35000, (BrahimConstants.B(3) - 25) * 1000),
                AltitudeBand("FL370", 37000, (BrahimConstants.B(4) - 38) * 1000),
                AltitudeBand("FL390", 39000, (BrahimConstants.B(5) - 58) * 1000),
                AltitudeBand("FL410", 41000, (BrahimConstants.B(6) - 80) * 1000)
            )

            // Calculate optimal altitude based on weight and distance
            val phi = BrahimConstants.PHI
            val beta = BrahimConstants.BETA_SECURITY

            // Weight factor (heavier = lower optimal altitude)
            val maxWeight = 150000.0
            val weightFactor = 1.0 - (weight / maxWeight) * beta

            // Distance factor (longer = higher optimal)
            val distanceFactor = kotlin.math.min(1.0, distance / 2000.0)

            // Optimal altitude
            val baseOptimal = 35000.0
            val optimalAlt = baseOptimal + 4000 * distanceFactor * weightFactor

            // Find recommended band
            val recommended = altitudeBands.minByOrNull {
                kotlin.math.abs(it.altitude - optimalAlt)
            }

            // Step climb profile
            val stepClimb = calculateStepClimb(distance, weight, optimalAlt)

            resultText.text = buildString {
                append("ALTITUDE OPTIMIZATION\n")
                append("Brahim Band Selection\n\n")
                append("Input:\n")
                append("  Distance: ${String.format("%.0f", distance)} NM\n")
                append("  TOW: ${String.format("%.0f", weight)} kg\n\n")
                append("Optimal Altitude:\n")
                append("  Calculated: ${String.format("%.0f", optimalAlt)} ft\n")
                append("  Recommended: ${recommended?.name ?: "N/A"}\n\n")
                append("Brahim Altitude Bands:\n")
                altitudeBands.forEach { band ->
                    val marker = if (band == recommended) " <-- OPTIMAL" else ""
                    append("  ${band.name}: ${band.altitude} ft$marker\n")
                }
                append("\nStep Climb Profile:\n")
                stepClimb.forEachIndexed { i, (dist, alt) ->
                    append("  ${String.format("%.0f", dist)} NM: FL${alt/100}\n")
                }
                append("\nFactors:\n")
                append("  Weight factor: ${String.format("%.3f", weightFactor)}\n")
                append("  Distance factor: ${String.format("%.3f", distanceFactor)}")
            }
        }
    }

    private fun calculateStepClimb(distance: Double, weight: Double, targetAlt: Double): List<Pair<Double, Int>> {
        val steps = mutableListOf<Pair<Double, Int>>()
        val phi = BrahimConstants.PHI

        // Initial altitude (lower due to weight)
        var currentAlt = (targetAlt - 4000).toInt()
        currentAlt = (currentAlt / 1000) * 1000  // Round to 1000

        steps.add(0.0 to currentAlt)

        // Step climb at golden ratio intervals
        var nextStep = distance / phi
        while (nextStep < distance && currentAlt < targetAlt) {
            currentAlt += 2000
            steps.add(nextStep to currentAlt)
            nextStep += (distance - nextStep) / phi
        }

        return steps
    }

    data class AltitudeBand(val name: String, val altitude: Int, val brahimMapping: Int)
}
