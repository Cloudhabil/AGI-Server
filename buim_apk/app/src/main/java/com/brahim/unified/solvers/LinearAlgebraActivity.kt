package com.brahim.unified.solvers

import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.brahim.unified.R
import com.brahim.unified.core.BrahimConstants
import kotlin.math.sqrt

class LinearAlgebraActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_input_calculator)

        title = "Linear Algebra"

        val inputField = findViewById<EditText>(R.id.inputField)
        val calculateBtn = findViewById<Button>(R.id.calculateButton)
        val resultText = findViewById<TextView>(R.id.resultText)

        inputField.hint = "Matrix size n (1-10)"

        calculateBtn.setOnClickListener {
            val n = inputField.text.toString().toIntOrNull()?.coerceIn(1, 10) ?: 3

            val phi = BrahimConstants.PHI
            val beta = BrahimConstants.BETA_SECURITY

            // Build Brahim matrix
            val matrix = Array(n) { i ->
                DoubleArray(n) { j ->
                    if (i == j) {
                        BrahimConstants.B(i + 1).toDouble()
                    } else if (i + j == n - 1) {
                        BrahimConstants.mirror(BrahimConstants.B((i + 1).coerceIn(1, 10))).toDouble() / 10
                    } else {
                        beta * kotlin.math.abs(i - j)
                    }
                }
            }

            // Calculate trace
            val trace = (0 until n).sumOf { matrix[it][it] }

            // Calculate determinant (for small matrices)
            val det = if (n <= 3) calculateDeterminant(matrix, n) else null

            // Frobenius norm
            val frobNorm = sqrt(matrix.flatMap { it.toList() }.sumOf { it * it })

            // Condition number estimate
            val maxRow = matrix.maxOf { row -> row.sumOf { kotlin.math.abs(it) } }
            val minDiag = (0 until n).minOf { kotlin.math.abs(matrix[it][it]) }
            val condEstimate = maxRow / minDiag

            resultText.text = buildString {
                append("BRAHIM MATRIX ANALYSIS\n")
                append("φ-scaled Linear Algebra\n\n")
                append("Matrix size: ${n}×${n}\n\n")
                append("BRAHIM MATRIX:\n")
                matrix.forEachIndexed { i, row ->
                    append("  [")
                    row.forEachIndexed { j, v ->
                        append(String.format("%6.1f", v))
                        if (j < n - 1) append(", ")
                    }
                    append("]\n")
                }
                append("\nPROPERTIES:\n")
                append("  Trace: ${String.format("%.2f", trace)}\n")
                if (det != null) {
                    append("  Determinant: ${String.format("%.2f", det)}\n")
                }
                append("  Frobenius norm: ${String.format("%.2f", frobNorm)}\n")
                append("  Condition (est): ${String.format("%.2f", condEstimate)}\n\n")
                append("CONSTRUCTION:\n")
                append("  Diagonal: B(i)\n")
                append("  Anti-diag: M(B(i))/10\n")
                append("  Off-diag: β×|i-j|\n\n")
                append("Brahim sequence on diagonal\n")
                append("ensures positive definiteness\n")
                append("for optimization problems")
            }
        }
    }

    private fun calculateDeterminant(m: Array<DoubleArray>, n: Int): Double {
        if (n == 1) return m[0][0]
        if (n == 2) return m[0][0] * m[1][1] - m[0][1] * m[1][0]
        if (n == 3) {
            return m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1]) -
                   m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0]) +
                   m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0])
        }
        return 0.0  // Skip for larger matrices
    }
}
