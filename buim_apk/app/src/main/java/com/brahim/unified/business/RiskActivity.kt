package com.brahim.unified.business

import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.brahim.unified.R
import com.brahim.unified.core.BrahimConstants
import com.brahim.unified.core.BrahimCalculators

class RiskActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_dual_input)

        title = "Risk Assessment"

        val likelihoodField = findViewById<EditText>(R.id.inputField1)
        val impactField = findViewById<EditText>(R.id.inputField2)
        val calculateBtn = findViewById<Button>(R.id.calculateButton)
        val resultText = findViewById<TextView>(R.id.resultText)

        likelihoodField.hint = "Likelihood (1-10)"
        impactField.hint = "Impact (1-10)"

        calculateBtn.setOnClickListener {
            val likelihood = likelihoodField.text.toString().toIntOrNull()?.coerceIn(1, 10) ?: 5
            val impact = impactField.text.toString().toIntOrNull()?.coerceIn(1, 10) ?: 5

            // Traditional risk score
            val traditionalScore = likelihood * impact

            // Brahim risk score with resonance
            val resonance = BrahimConstants.resonance(
                listOf(likelihood.toDouble() / 10),
                listOf(impact.toDouble())
            )

            // ASIOS safety verdict
            val verdict = BrahimCalculators.assessSafety(resonance)

            // Brahim-weighted score
            val brahimLikelihood = BrahimConstants.B(likelihood)
            val brahimImpact = BrahimConstants.B(impact)
            val brahimScore = (brahimLikelihood * brahimImpact).toDouble() / BrahimConstants.SUM_CONSTANT

            // Risk category
            val category = when {
                brahimScore > 100 -> "CRITICAL"
                brahimScore > 50 -> "HIGH"
                brahimScore > 20 -> "MEDIUM"
                brahimScore > 5 -> "LOW"
                else -> "NEGLIGIBLE"
            }

            // Mitigation priority
            val priority = when (verdict) {
                BrahimCalculators.SafetyVerdict.BLOCKED -> "IMMEDIATE ACTION"
                BrahimCalculators.SafetyVerdict.UNSAFE -> "URGENT"
                BrahimCalculators.SafetyVerdict.CAUTION -> "PLANNED"
                BrahimCalculators.SafetyVerdict.NOMINAL -> "MONITOR"
                BrahimCalculators.SafetyVerdict.SAFE -> "ACCEPT"
            }

            resultText.text = buildString {
                append("RISK ASSESSMENT\n")
                append("ASIOS Safety Analysis\n\n")
                append("Input:\n")
                append("  Likelihood: $likelihood/10\n")
                append("  Impact: $impact/10\n\n")
                append("TRADITIONAL SCORE:\n")
                append("  L × I = $traditionalScore/100\n\n")
                append("BRAHIM ANALYSIS:\n")
                append("  B($likelihood) = $brahimLikelihood\n")
                append("  B($impact) = $brahimImpact\n")
                append("  Score: ${String.format("%.1f", brahimScore)}\n\n")
                append("ASSESSMENT:\n")
                append("  Category: $category\n")
                append("  Safety Verdict: $verdict\n")
                append("  Priority: $priority\n\n")
                append("RESONANCE:\n")
                append("  R = ${String.format("%.6f", resonance)}\n")
                append("  Genesis: ${BrahimConstants.GENESIS_CONSTANT}\n")
                append("  Alignment: ${String.format("%.6f", BrahimConstants.axiologicalAlignment(resonance))}\n\n")
                append("Recommendations:\n")
                when (category) {
                    "CRITICAL" -> append("  - Halt activity\n  - Executive escalation\n  - Contingency plan")
                    "HIGH" -> append("  - Active mitigation\n  - Regular monitoring\n  - Risk owner assigned")
                    "MEDIUM" -> append("  - Document controls\n  - Periodic review\n  - Budget contingency")
                    "LOW" -> append("  - Accept with monitoring\n  - Standard procedures")
                    else -> append("  - No action needed\n  - Log and close")
                }
            }
        }
    }
}
