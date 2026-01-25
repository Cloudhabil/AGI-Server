package com.brahim.unified.business

import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.brahim.unified.R
import com.brahim.unified.core.BrahimConstants
import com.brahim.unified.core.BrahimCalculators

class ComplianceActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_input_calculator)

        title = "Compliance Checker"

        val inputField = findViewById<EditText>(R.id.inputField)
        val calculateBtn = findViewById<Button>(R.id.calculateButton)
        val resultText = findViewById<TextView>(R.id.resultText)

        inputField.hint = "Compliance scores (comma-sep, 0-100)"

        calculateBtn.setOnClickListener {
            try {
                val scores = inputField.text.toString()
                    .split(",")
                    .map { it.trim().toDouble().coerceIn(0.0, 100.0) }

                if (scores.isEmpty()) {
                    resultText.text = "Enter at least one score"
                    return@setOnClickListener
                }

                val average = scores.average()
                val min = scores.minOrNull()!!
                val max = scores.maxOrNull()!!

                // Axiological alignment
                val normalizedScores = scores.map { it / 100.0 }
                val resonance = BrahimConstants.resonance(
                    normalizedScores,
                    normalizedScores.indices.map { it.toDouble() }
                )
                val alignment = BrahimConstants.axiologicalAlignment(resonance)
                val verdict = BrahimCalculators.assessSafety(resonance)

                // Compliance status
                val status = when {
                    min >= 90 -> "EXCELLENT"
                    min >= 80 -> "COMPLIANT"
                    min >= 70 -> "MARGINAL"
                    min >= 60 -> "NON-COMPLIANT"
                    else -> "CRITICAL"
                }

                // Brahim thresholds
                val thresholds = mapOf(
                    "Excellence" to (BrahimConstants.B(10).toDouble() / 2),  // 93.5
                    "Compliance" to (BrahimConstants.B(8).toDouble() / 2),   // 77
                    "Minimum" to (BrahimConstants.B(3).toDouble()),          // 60
                    "Critical" to (BrahimConstants.B(1).toDouble())          // 27
                )

                resultText.text = buildString {
                    append("COMPLIANCE ANALYSIS\n")
                    append("Axiological Alignment Check\n\n")
                    append("Scores: ${scores.joinToString(", ") { String.format("%.0f", it) }}\n\n")
                    append("SUMMARY:\n")
                    append("  Count: ${scores.size} areas\n")
                    append("  Average: ${String.format("%.1f", average)}%\n")
                    append("  Range: ${String.format("%.0f", min)} - ${String.format("%.0f", max)}%\n\n")
                    append("STATUS: $status\n\n")
                    append("AXIOLOGICAL ANALYSIS:\n")
                    append("  Resonance: ${String.format("%.6f", resonance)}\n")
                    append("  Alignment: ${String.format("%.6f", alignment)}\n")
                    append("  Verdict: $verdict\n\n")
                    append("BRAHIM THRESHOLDS:\n")
                    thresholds.forEach { (name, value) ->
                        val check = if (min >= value) "✓" else "✗"
                        append("  $check $name: ${String.format("%.1f", value)}%\n")
                    }
                    append("\nAREAS NEEDING ATTENTION:\n")
                    scores.forEachIndexed { i, score ->
                        if (score < 80) {
                            append("  Area ${i + 1}: ${String.format("%.0f", score)}% ")
                            append("(need +${String.format("%.0f", 80 - score)})\n")
                        }
                    }
                    if (scores.all { it >= 80 }) {
                        append("  All areas compliant!")
                    }
                }
            } catch (e: Exception) {
                resultText.text = "Enter comma-separated numbers (0-100)\nExample: 85, 92, 78, 95"
            }
        }
    }
}
