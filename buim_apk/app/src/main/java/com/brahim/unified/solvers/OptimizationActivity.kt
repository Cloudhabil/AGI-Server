package com.brahim.unified.solvers

import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.brahim.unified.R
import com.brahim.unified.core.BrahimConstants
import kotlin.math.pow
import kotlin.math.abs

class OptimizationActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_dual_input)

        title = "Golden Optimization"

        val startField = findViewById<EditText>(R.id.inputField1)
        val targetField = findViewById<EditText>(R.id.inputField2)
        val calculateBtn = findViewById<Button>(R.id.calculateButton)
        val resultText = findViewById<TextView>(R.id.resultText)

        startField.hint = "Start point x₀"
        targetField.hint = "Target minimum (for demo)"

        calculateBtn.setOnClickListener {
            val x0 = startField.text.toString().toDoubleOrNull() ?: 5.0
            val target = targetField.text.toString().toDoubleOrNull() ?: 0.0

            val phi = BrahimConstants.PHI
            val beta = BrahimConstants.BETA_SECURITY

            // Golden Section Search demonstration
            // Find minimum of f(x) = (x - target)² in interval [a, b]
            var a = x0 - 10
            var b = x0 + 10
            val tolerance = 0.0001
            val maxIter = 50

            val history = mutableListOf<Triple<Double, Double, Double>>()

            // Golden section points
            var c = b - (b - a) / phi
            var d = a + (b - a) / phi

            fun f(x: Double) = (x - target).pow(2) + beta * kotlin.math.sin(x)

            var iterations = 0
            while (abs(b - a) > tolerance && iterations < maxIter) {
                iterations++
                history.add(Triple(a, b, (a + b) / 2))

                if (f(c) < f(d)) {
                    b = d
                } else {
                    a = c
                }

                c = b - (b - a) / phi
                d = a + (b - a) / phi
            }

            val minimum = (a + b) / 2
            val fMin = f(minimum)

            // Gradient descent comparison
            var xGD = x0
            val alpha = 0.1  // Learning rate
            var gdIter = 0
            while (abs(xGD - target) > tolerance && gdIter < maxIter) {
                val grad = 2 * (xGD - target) + beta * kotlin.math.cos(xGD)
                xGD -= alpha * grad
                gdIter++
            }

            resultText.text = buildString {
                append("GOLDEN SECTION SEARCH\n")
                append("φ-based Optimization\n\n")
                append("Function: f(x) = (x-$target)² + β·sin(x)\n")
                append("Start: x₀ = $x0\n\n")
                append("GOLDEN SECTION RESULT:\n")
                append("  Minimum at x = ${String.format("%.6f", minimum)}\n")
                append("  f(x*) = ${String.format("%.6f", fMin)}\n")
                append("  Iterations: $iterations\n\n")
                append("GRADIENT DESCENT COMPARISON:\n")
                append("  Result: x = ${String.format("%.6f", xGD)}\n")
                append("  f(x) = ${String.format("%.6f", f(xGD))}\n")
                append("  Iterations: $gdIter\n\n")
                append("CONVERGENCE HISTORY:\n")
                history.take(5).forEachIndexed { i, (lo, hi, mid) ->
                    append("  ${i + 1}: [${String.format("%.3f", lo)}, ${String.format("%.3f", hi)}]\n")
                }
                if (history.size > 5) append("  ...(${history.size - 5} more)\n")
                append("\nGOLDEN RATIO ADVANTAGE:\n")
                append("  φ = ${String.format("%.6f", phi)}\n")
                append("  Optimal interval reduction\n")
                append("  No gradient needed\n")
                append("  Guaranteed convergence")
            }
        }
    }
}
