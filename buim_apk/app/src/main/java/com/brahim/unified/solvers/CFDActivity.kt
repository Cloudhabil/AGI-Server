package com.brahim.unified.solvers

import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.brahim.unified.R
import com.brahim.unified.core.BrahimCalculators

class CFDActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_quad_input)

        title = "CFD Calculator"

        val densityField = findViewById<EditText>(R.id.inputField1)
        val velocityField = findViewById<EditText>(R.id.inputField2)
        val lengthField = findViewById<EditText>(R.id.inputField3)
        val viscosityField = findViewById<EditText>(R.id.inputField4)
        val calculateBtn = findViewById<Button>(R.id.calculateButton)
        val resultText = findViewById<TextView>(R.id.resultText)

        densityField.hint = "Density (kg/m^3)"
        velocityField.hint = "Velocity (m/s)"
        lengthField.hint = "Char. Length (m)"
        viscosityField.hint = "Viscosity (Pa.s)"

        calculateBtn.setOnClickListener {
            val density = densityField.text.toString().toDoubleOrNull()
            val velocity = velocityField.text.toString().toDoubleOrNull()
            val length = lengthField.text.toString().toDoubleOrNull()
            val viscosity = viscosityField.text.toString().toDoubleOrNull()

            if (density != null && velocity != null && length != null && viscosity != null && viscosity > 0) {
                val re = BrahimCalculators.reynoldsNumber(density, velocity, length, viscosity)
                val regime = BrahimCalculators.flowRegime(re)

                resultText.text = buildString {
                    append("CFD ANALYSIS\n")
                    append("Reynolds Number Calculator\n\n")
                    append("Input Parameters:\n")
                    append("  Density: $density kg/m^3\n")
                    append("  Velocity: $velocity m/s\n")
                    append("  Char. Length: $length m\n")
                    append("  Viscosity: $viscosity Pa.s\n\n")
                    append("Results:\n")
                    append("  Reynolds Number: ${String.format("%.2f", re)}\n")
                    append("  Flow Regime: $regime\n\n")
                    append("Thresholds (Brahim-calibrated):\n")
                    append("  Laminar: Re < 2300\n")
                    append("  Transitional: 2300 <= Re < 4000\n")
                    append("  Turbulent: Re >= 4000\n\n")
                    append("Formula: Re = rho * v * L / mu")
                }
            } else {
                resultText.text = "Enter valid positive numbers\nViscosity must be > 0"
            }
        }
    }
}
