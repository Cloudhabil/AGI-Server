package com.brahim.unified.planetary

import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.brahim.unified.R
import com.brahim.unified.core.BrahimCalculators

class TitanActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_input_calculator)

        title = "Titan Explorer"

        val inputField = findViewById<EditText>(R.id.inputField)
        val calculateBtn = findViewById<Button>(R.id.calculateButton)
        val resultText = findViewById<TextView>(R.id.resultText)

        inputField.hint = "Latitude (degrees)"

        val titan = BrahimCalculators.TitanProperties()

        calculateBtn.setOnClickListener {
            val latitude = inputField.text.toString().toDoubleOrNull()

            if (latitude != null && latitude >= -90 && latitude <= 90) {
                val evapRate = BrahimCalculators.methaneEvaporationRate(latitude)
                val lakeProb = BrahimCalculators.lakeProbability(latitude)

                resultText.text = buildString {
                    append("TITAN EXPLORATION DATA\n")
                    append("Saturn's Largest Moon\n\n")
                    append("Physical Properties:\n")
                    append("  Radius: ${titan.radius} km\n")
                    append("  Mass: ${String.format("%.4e", titan.mass)} kg\n")
                    append("  Surface Gravity: ${titan.gravity} m/s^2\n")
                    append("  Escape Velocity: ${titan.escapeVelocity} km/s\n\n")
                    append("Location Analysis (${latitude} deg):\n")
                    append("  Methane Evaporation: ${String.format("%.4f", evapRate)} kg/m^2/s\n")
                    append("  Lake Probability: ${String.format("%.1f", lakeProb * 100)}%\n\n")
                    append("Model Notes:\n")
                    append("  - Evaporation peaks at equator\n")
                    append("  - Lakes concentrated at poles\n")
                    append("  - Methane cycle analogous to Earth water\n\n")
                    append("Formulas:\n")
                    append("  Evap = 0.1 * cos(lat)\n")
                    append("  Lake = 0.8 * sin^2(lat)")
                }
            } else {
                resultText.text = buildString {
                    append("TITAN BASIC DATA\n\n")
                    append("Radius: ${titan.radius} km\n")
                    append("Mass: ${String.format("%.4e", titan.mass)} kg\n")
                    append("Gravity: ${titan.gravity} m/s^2\n")
                    append("Escape Velocity: ${titan.escapeVelocity} km/s\n\n")
                    append("Enter latitude (-90 to 90) for location analysis")
                }
            }
        }

        // Show basic data initially
        calculateBtn.performClick()
    }
}
