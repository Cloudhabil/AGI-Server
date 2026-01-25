package com.brahim.unified.physics

import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.brahim.unified.R
import com.brahim.unified.core.BrahimConstants

class QuantumActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_input_calculator)

        title = "Quantum Numbers"

        val inputField = findViewById<EditText>(R.id.inputField)
        val calculateBtn = findViewById<Button>(R.id.calculateButton)
        val resultText = findViewById<TextView>(R.id.resultText)

        inputField.hint = "Principal quantum number n (1-10)"

        calculateBtn.setOnClickListener {
            val n = inputField.text.toString().toIntOrNull()

            if (n != null && n in 1..10) {
                val bn = BrahimConstants.B(n)
                val mirror = BrahimConstants.mirror(bn)

                // Derive quantum properties from Brahim
                val orbitalMax = n - 1  // l = 0 to n-1
                val magneticRange = 2 * orbitalMax + 1  // m = -l to +l
                val spinStates = 2  // s = +1/2 or -1/2
                val maxElectrons = 2 * n * n  // Pauli exclusion

                // Brahim interpretation
                val brahimEnergy = -bn.toDouble() / (n * n)  // Scaled energy level
                val brahimRadius = bn.toDouble() * n * n / BrahimConstants.CENTER  // Scaled radius

                resultText.text = buildString {
                    append("QUANTUM NUMBERS for n=$n\n\n")
                    append("Standard QM:\n")
                    append("  Principal (n): $n\n")
                    append("  Angular (l): 0 to $orbitalMax\n")
                    append("  Magnetic (m): ${-orbitalMax} to $orbitalMax\n")
                    append("  Spin (s): +1/2, -1/2\n")
                    append("  Max electrons: $maxElectrons\n\n")
                    append("Brahim Mapping:\n")
                    append("  B($n) = $bn\n")
                    append("  Mirror M(B($n)) = $mirror\n")
                    append("  Sum check: ${bn + mirror}\n\n")
                    append("Brahim-derived:\n")
                    append("  Energy scale: ${String.format("%.4f", brahimEnergy)}\n")
                    append("  Radius scale: ${String.format("%.4f", brahimRadius)} a₀\n\n")
                    append("Shell: ${getShellName(n)}")
                }
            } else {
                resultText.text = "Enter n from 1 to 10\n\nBrahim sequence has 10 elements,\nmapping to quantum shells K through N+..."
            }
        }
    }

    private fun getShellName(n: Int): String = when(n) {
        1 -> "K (innermost)"
        2 -> "L"
        3 -> "M"
        4 -> "N"
        5 -> "O"
        6 -> "P"
        7 -> "Q"
        else -> "Extended shell $n"
    }
}
