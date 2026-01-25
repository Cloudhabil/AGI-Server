package com.brahim.unified.security

import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.brahim.unified.R
import com.brahim.unified.core.BrahimConstants
import com.brahim.unified.core.BrahimCalculators

class ASIOSActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_input_calculator)

        title = "ASIOS Guard"

        val inputField = findViewById<EditText>(R.id.inputField)
        val calculateBtn = findViewById<Button>(R.id.calculateButton)
        val resultText = findViewById<TextView>(R.id.resultText)

        inputField.hint = "Input resonance value"

        calculateBtn.setOnClickListener {
            val resonance = inputField.text.toString().toDoubleOrNull()

            if (resonance != null) {
                val verdict = BrahimCalculators.assessSafety(resonance)
                val alignment = BrahimConstants.axiologicalAlignment(resonance)
                val genesis = BrahimConstants.GENESIS_CONSTANT

                val (status, description, action) = when (verdict) {
                    BrahimCalculators.SafetyVerdict.SAFE -> Triple(
                        "SAFE", "Fully aligned with axiological values",
                        "PROCEED - No restrictions"
                    )
                    BrahimCalculators.SafetyVerdict.NOMINAL -> Triple(
                        "NOMINAL", "Minor deviation within tolerance",
                        "PROCEED - Standard monitoring"
                    )
                    BrahimCalculators.SafetyVerdict.CAUTION -> Triple(
                        "CAUTION", "Moderate deviation detected",
                        "PROCEED WITH CARE - Enhanced logging"
                    )
                    BrahimCalculators.SafetyVerdict.UNSAFE -> Triple(
                        "UNSAFE", "Significant deviation from safe values",
                        "RESTRICT - Manual review required"
                    )
                    BrahimCalculators.SafetyVerdict.BLOCKED -> Triple(
                        "BLOCKED", "Critical deviation - potential harm",
                        "DENY - Action blocked"
                    )
                }

                resultText.text = buildString {
                    append("ASIOS SAFETY ANALYSIS\n")
                    append("Axiological Safety Intelligence OS\n\n")
                    append("INPUT:\n")
                    append("  Resonance: ${String.format("%.8f", resonance)}\n")
                    append("  Genesis target: $genesis\n")
                    append("  Alignment: ${String.format("%.8f", alignment)}\n\n")
                    append("╔════════════════════════════╗\n")
                    append("║  VERDICT: $status\n")
                    append("╚════════════════════════════╝\n\n")
                    append("ASSESSMENT:\n")
                    append("  $description\n\n")
                    append("ACTION:\n")
                    append("  $action\n\n")
                    append("THRESHOLDS:\n")
                    append("  SAFE:    alignment < 0.001\n")
                    append("  NOMINAL: alignment < 0.01\n")
                    append("  CAUTION: alignment < 0.05\n")
                    append("  UNSAFE:  alignment < 0.1\n")
                    append("  BLOCKED: alignment >= 0.1\n\n")
                    append("Berry-Keating Energy:\n")
                    val density = resonance / (1 + resonance)
                    val energy = (density - 0.00221888) * (density - 0.00221888)
                    append("  E[ψ] = ${String.format("%.6e", energy)}")
                }
            } else {
                resultText.text = buildString {
                    append("ASIOS GUARD SYSTEM\n\n")
                    append("Enter a resonance value to analyze.\n\n")
                    append("Example values:\n")
                    append("  0.0219 - Genesis (optimal)\n")
                    append("  0.022 - Near optimal\n")
                    append("  0.03 - Moderate deviation\n")
                    append("  0.1 - High deviation\n")
                    append("  0.5 - Critical deviation\n\n")
                    append("The ASIOS system evaluates\n")
                    append("axiological alignment based on\n")
                    append("distance from the Genesis constant.")
                }
            }
        }
    }
}
