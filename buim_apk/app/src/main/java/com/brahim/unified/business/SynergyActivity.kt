package com.brahim.unified.business

import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.brahim.unified.R
import com.brahim.unified.core.BrahimConstants
import com.brahim.unified.core.BrahimCalculators

class SynergyActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_dual_input)

        title = "Team Synergy Analyzer"

        val skillsField = findViewById<EditText>(R.id.inputField1)
        val tenureField = findViewById<EditText>(R.id.inputField2)
        val calculateBtn = findViewById<Button>(R.id.calculateButton)
        val resultText = findViewById<TextView>(R.id.resultText)

        skillsField.hint = "Skill Gaps (comma-separated)"
        tenureField.hint = "Tenure Diffs (comma-separated)"

        calculateBtn.setOnClickListener {
            val skillsText = skillsField.text.toString()
            val tenureText = tenureField.text.toString()

            try {
                val skills = skillsText.split(",").map { it.trim().toDouble() }
                val tenures = tenureText.split(",").map { it.trim().toDouble() }

                if (skills.size != tenures.size) {
                    resultText.text = "Skill gaps and tenure diffs must have same count"
                    return@setOnClickListener
                }

                val synergy = BrahimCalculators.teamSynergy(skills, tenures)
                val isOptimal = BrahimCalculators.isOptimalTeam(synergy)
                val verdict = BrahimCalculators.assessSafety(synergy)

                resultText.text = buildString {
                    append("TEAM SYNERGY ANALYSIS\n")
                    append("Resonance-Based Evaluation\n\n")
                    append("Input:\n")
                    append("  Skill Gaps: ${skills.joinToString(", ")}\n")
                    append("  Tenure Diffs: ${tenures.joinToString(", ")}\n\n")
                    append("Results:\n")
                    append("  Synergy Score: ${String.format("%.6f", synergy)}\n")
                    append("  Optimal Team: ${if (isOptimal) "YES" else "NO"}\n")
                    append("  Safety Verdict: $verdict\n\n")
                    append("Thresholds:\n")
                    append("  Genesis Constant: ${BrahimConstants.GENESIS_CONSTANT}\n")
                    append("  Alignment: ${String.format("%.6f", BrahimConstants.axiologicalAlignment(synergy))}\n\n")
                    append("Formula: R = sum(1/(d^2+eps)) * e^(-lambda*t)")
                }
            } catch (e: Exception) {
                resultText.text = "Enter numbers separated by commas\nExample: 0.1, 0.2, 0.3"
            }
        }
    }
}
