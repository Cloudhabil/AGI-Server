package com.brahim.unified.math

import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.brahim.unified.R
import com.brahim.unified.core.BrahimConstants

class ResonanceActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_dual_input)

        title = "Resonance Calculator"

        val distancesField = findViewById<EditText>(R.id.inputField1)
        val timesField = findViewById<EditText>(R.id.inputField2)
        val calculateBtn = findViewById<Button>(R.id.calculateButton)
        val resultText = findViewById<TextView>(R.id.resultText)

        distancesField.hint = "Distances (comma-sep)"
        timesField.hint = "Time diffs (comma-sep)"

        calculateBtn.setOnClickListener {
            try {
                val distances = distancesField.text.toString()
                    .split(",").map { it.trim().toDouble() }
                val times = timesField.text.toString()
                    .split(",").map { it.trim().toDouble() }

                if (distances.size != times.size) {
                    resultText.text = "Lists must have same length"
                    return@setOnClickListener
                }

                val resonance = BrahimConstants.resonance(distances, times)
                val alignment = BrahimConstants.axiologicalAlignment(resonance)
                val genesis = BrahimConstants.GENESIS_CONSTANT

                resultText.text = buildString {
                    append("RESONANCE ANALYSIS\n\n")
                    append("Input:\n")
                    append("  Distances: ${distances.joinToString(", ")}\n")
                    append("  Time diffs: ${times.joinToString(", ")}\n\n")
                    append("Results:\n")
                    append("  Resonance R: ${String.format("%.8f", resonance)}\n")
                    append("  Genesis target: $genesis\n")
                    append("  Alignment |R-G|: ${String.format("%.8f", alignment)}\n\n")
                    append("Interpretation:\n")
                    when {
                        alignment < 0.001 -> append("  PERFECT RESONANCE\n  System in harmony")
                        alignment < 0.01 -> append("  STRONG RESONANCE\n  Good alignment")
                        alignment < 0.05 -> append("  MODERATE RESONANCE\n  Acceptable")
                        alignment < 0.1 -> append("  WEAK RESONANCE\n  Needs adjustment")
                        else -> append("  NO RESONANCE\n  System unstable")
                    }
                    append("\n\nFormula:\n")
                    append("R = Σ(1/(d²+ε)) × e^(-λt)\n")
                    append("λ = $genesis (Genesis constant)")
                }
            } catch (e: Exception) {
                resultText.text = "Enter comma-separated numbers\nExample: 0.1, 0.2, 0.3"
            }
        }
    }
}
