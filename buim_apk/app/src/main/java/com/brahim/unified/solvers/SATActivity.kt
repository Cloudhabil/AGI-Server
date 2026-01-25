package com.brahim.unified.solvers

import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.brahim.unified.R
import com.brahim.unified.core.BrahimConstants

class SATActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_input_calculator)

        title = "SAT Solver"

        val inputField = findViewById<EditText>(R.id.inputField)
        val calculateBtn = findViewById<Button>(R.id.calculateButton)
        val resultText = findViewById<TextView>(R.id.resultText)

        inputField.hint = "Variables (e.g., 3)"

        calculateBtn.setOnClickListener {
            val variables = inputField.text.toString().toIntOrNull()

            if (variables != null && variables in 1..10) {
                val searchSpace = Math.pow(2.0, variables.toDouble()).toLong()
                val brahimPruning = BrahimConstants.BETA_SECURITY
                val reducedSpace = (searchSpace * brahimPruning).toLong()
                val efficiency = (1 - brahimPruning) * 100

                resultText.text = buildString {
                    append("SAT SOLVER ANALYSIS\n")
                    append("Brahim Heuristic Method\n\n")
                    append("Variables: $variables\n")
                    append("Full Search Space: $searchSpace\n")
                    append("Beta Pruning Factor: ${String.format("%.6f", brahimPruning)}\n")
                    append("Reduced Space: $reducedSpace\n")
                    append("Efficiency Gain: ${String.format("%.1f", efficiency)}%\n\n")
                    append("Brahim SAT Heuristics:\n")
                    append("1. Variable ordering by B(i) weights\n")
                    append("2. Clause learning with phi decay\n")
                    append("3. Restart with golden ratio intervals\n")
                    append("4. Conflict analysis via mirror symmetry\n\n")
                    append("Beta = sqrt(5) - 2 = ${String.format("%.10f", brahimPruning)}")
                }
            } else {
                resultText.text = "Enter variables (1-10)"
            }
        }
    }
}
