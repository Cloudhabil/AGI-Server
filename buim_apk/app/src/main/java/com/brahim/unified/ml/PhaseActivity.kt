package com.brahim.unified.ml

import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.brahim.unified.R
import com.brahim.unified.core.BrahimConstants
import kotlin.math.sin
import kotlin.math.cos
import kotlin.math.atan2

class PhaseActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_input_calculator)

        title = "Phase Classifier"

        val inputField = findViewById<EditText>(R.id.inputField)
        val calculateBtn = findViewById<Button>(R.id.calculateButton)
        val resultText = findViewById<TextView>(R.id.resultText)

        inputField.hint = "Time series (comma-separated)"

        calculateBtn.setOnClickListener {
            val input = inputField.text.toString()

            try {
                val series = input.split(",").map { it.trim().toDouble() }

                if (series.size < 3) {
                    resultText.text = "Need at least 3 data points"
                    return@setOnClickListener
                }

                val phi = BrahimConstants.PHI
                val beta = BrahimConstants.BETA_SECURITY
                val genesis = BrahimConstants.GENESIS_CONSTANT

                // Calculate phase characteristics
                val mean = series.average()
                val variance = series.map { (it - mean) * (it - mean) }.average()
                val std = kotlin.math.sqrt(variance)

                // Detect trend
                val firstHalf = series.take(series.size / 2).average()
                val secondHalf = series.drop(series.size / 2).average()
                val trend = when {
                    secondHalf > firstHalf * 1.1 -> "INCREASING"
                    secondHalf < firstHalf * 0.9 -> "DECREASING"
                    else -> "STABLE"
                }

                // Phase classification using Brahim
                val normalizedVar = variance / (mean * mean + 0.001)
                val phase = when {
                    normalizedVar < genesis -> "EQUILIBRIUM"
                    normalizedVar < beta -> "TRANSITION"
                    normalizedVar < 1.0 / phi -> "OSCILLATION"
                    else -> "CHAOS"
                }

                // Autocorrelation (lag-1)
                val autoCorr = if (series.size > 1) {
                    val shifted = series.drop(1)
                    val original = series.dropLast(1)
                    val cov = original.zip(shifted).map { (a, b) -> (a - mean) * (b - mean) }.average()
                    cov / variance
                } else 0.0

                resultText.text = buildString {
                    append("PHASE CLASSIFICATION\n")
                    append("Time Series Analysis\n\n")
                    append("INPUT: ${series.size} points\n")
                    append("  ${series.take(5).joinToString(", ") { String.format("%.2f", it) }}")
                    if (series.size > 5) append("...")
                    append("\n\n")
                    append("STATISTICS:\n")
                    append("  Mean: ${String.format("%.4f", mean)}\n")
                    append("  Std Dev: ${String.format("%.4f", std)}\n")
                    append("  Variance: ${String.format("%.4f", variance)}\n")
                    append("  Autocorr: ${String.format("%.4f", autoCorr)}\n\n")
                    append("CLASSIFICATION:\n")
                    append("  Trend: $trend\n")
                    append("  Phase: $phase\n\n")
                    append("BRAHIM THRESHOLDS:\n")
                    append("  Equilibrium: σ²/μ² < $genesis\n")
                    append("  Transition: σ²/μ² < ${String.format("%.4f", beta)}\n")
                    append("  Oscillation: σ²/μ² < ${String.format("%.4f", 1/phi)}\n")
                    append("  Chaos: σ²/μ² >= ${String.format("%.4f", 1/phi)}\n\n")
                    append("Normalized variance:\n")
                    append("  ${String.format("%.6f", normalizedVar)}")
                }
            } catch (e: Exception) {
                resultText.text = "Enter comma-separated numbers\nExample: 1.0, 1.2, 1.1, 1.3, 1.2"
            }
        }
    }
}
