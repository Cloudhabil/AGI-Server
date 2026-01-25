package com.brahim.unified.solvers

import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.brahim.unified.R
import com.brahim.unified.core.BrahimConstants

class ConstraintActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_dual_input)

        title = "Constraint Solver"

        val constraintsField = findViewById<EditText>(R.id.inputField1)
        val variablesField = findViewById<EditText>(R.id.inputField2)
        val calculateBtn = findViewById<Button>(R.id.calculateButton)
        val resultText = findViewById<TextView>(R.id.resultText)

        constraintsField.hint = "Number of constraints"
        variablesField.hint = "Number of variables"

        calculateBtn.setOnClickListener {
            val constraints = constraintsField.text.toString().toIntOrNull()?.coerceIn(1, 20) ?: 5
            val variables = variablesField.text.toString().toIntOrNull()?.coerceIn(1, 20) ?: 3

            val phi = BrahimConstants.PHI
            val beta = BrahimConstants.BETA_SECURITY
            val genesis = BrahimConstants.GENESIS_CONSTANT

            // Problem characteristics
            val ratio = constraints.toDouble() / variables
            val density = if (constraints > variables) constraints / variables else variables / constraints

            // Difficulty estimation using Brahim
            val difficulty = when {
                ratio < 1.0 -> "UNDER-CONSTRAINED (multiple solutions)"
                ratio == 1.0 -> "WELL-CONSTRAINED (unique solution likely)"
                ratio < phi -> "SLIGHTLY OVER-CONSTRAINED"
                else -> "HEAVILY OVER-CONSTRAINED (may be infeasible)"
            }

            // Search space
            val searchSpace = Math.pow(2.0, variables.toDouble()).toLong()
            val prunedSpace = (searchSpace * beta).toLong()

            // Resonance-based constraint ordering
            val ordering = (1..constraints).map { c ->
                val tightness = BrahimConstants.B(c.coerceIn(1, 10)).toDouble() / BrahimConstants.SUM_CONSTANT
                c to tightness
            }.sortedByDescending { it.second }

            resultText.text = buildString {
                append("CONSTRAINT SOLVER\n")
                append("Resonance-Based Ordering\n\n")
                append("Problem:\n")
                append("  Constraints: $constraints\n")
                append("  Variables: $variables\n")
                append("  Ratio: ${String.format("%.2f", ratio)}\n\n")
                append("Classification:\n")
                append("  $difficulty\n\n")
                append("SEARCH SPACE:\n")
                append("  Full: $searchSpace states\n")
                append("  β-pruned: $prunedSpace states\n")
                append("  Reduction: ${String.format("%.1f", (1 - beta) * 100)}%\n\n")
                append("CONSTRAINT ORDERING:\n")
                append("(by Brahim tightness)\n")
                ordering.take(5).forEach { (c, t) ->
                    append("  C$c: tightness=${String.format("%.3f", t)}\n")
                }
                if (ordering.size > 5) append("  ...(${ordering.size - 5} more)\n")
                append("\nSOLVER STRATEGY:\n")
                append("  1. Order by tightness (B(i)/S)\n")
                append("  2. Propagate constraints\n")
                append("  3. Backtrack with φ-restart\n")
                append("  4. Check resonance gate\n\n")
                append("Resonance threshold: $genesis")
            }
        }
    }
}
