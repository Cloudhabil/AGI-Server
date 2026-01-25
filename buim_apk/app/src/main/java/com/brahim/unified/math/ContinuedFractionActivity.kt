package com.brahim.unified.math

import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.brahim.unified.R
import com.brahim.unified.core.BrahimConstants
import kotlin.math.floor

class ContinuedFractionActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_input_calculator)

        title = "Continued Fractions"

        val inputField = findViewById<EditText>(R.id.inputField)
        val calculateBtn = findViewById<Button>(R.id.calculateButton)
        val resultText = findViewById<TextView>(R.id.resultText)

        inputField.hint = "Number (or phi, beta, alpha)"

        calculateBtn.setOnClickListener {
            val input = inputField.text.toString().trim().lowercase()

            val number = when (input) {
                "phi", "φ" -> BrahimConstants.PHI
                "beta", "β" -> BrahimConstants.BETA_SECURITY
                "alpha", "α" -> BrahimConstants.ALPHA_WORMHOLE
                "gamma", "γ" -> BrahimConstants.GAMMA_DAMPING
                "genesis" -> BrahimConstants.GENESIS_CONSTANT
                else -> input.toDoubleOrNull()
            }

            if (number != null && number > 0) {
                val cf = continuedFraction(number, 15)
                val convergents = calculateConvergents(cf)

                resultText.text = buildString {
                    append("CONTINUED FRACTION\n\n")
                    append("Number: ${String.format("%.10f", number)}\n\n")
                    append("CF: [${cf.joinToString("; ")}]\n\n")
                    append("Notation: ${cf[0]} + 1/(${cf.getOrNull(1) ?: "..."} + 1/(...))\n\n")
                    append("Convergents:\n")
                    convergents.take(8).forEachIndexed { i, (p, q) ->
                        val approx = p.toDouble() / q
                        val error = kotlin.math.abs(approx - number)
                        append("  $p/$q = ${String.format("%.8f", approx)}")
                        append(" (err: ${String.format("%.2e", error)})\n")
                    }
                    append("\nSpecial constants:\n")
                    append("  φ: [1; 1, 1, 1, ...] (all 1s)\n")
                    append("  β: [0; 4, 4, 4, ...] (all 4s)\n")
                    append("  e: [2; 1, 2, 1, 1, 4, 1, ...]\n")
                    append("  π: [3; 7, 15, 1, 292, ...]")
                }
            } else {
                resultText.text = buildString {
                    append("Enter a positive number\n\n")
                    append("Special keywords:\n")
                    append("  phi (φ) - Golden ratio\n")
                    append("  beta (β) - Security constant\n")
                    append("  alpha (α) - Wormhole constant\n")
                    append("  gamma (γ) - Damping constant\n")
                    append("  genesis - 0.0219")
                }
            }
        }
    }

    private fun continuedFraction(x: Double, maxTerms: Int): List<Int> {
        val result = mutableListOf<Int>()
        var current = x
        repeat(maxTerms) {
            val a = floor(current).toInt()
            result.add(a)
            val frac = current - a
            if (frac < 1e-10) return result
            current = 1.0 / frac
            if (current > 1e10) return result
        }
        return result
    }

    private fun calculateConvergents(cf: List<Int>): List<Pair<Long, Long>> {
        val convergents = mutableListOf<Pair<Long, Long>>()
        var pPrev = 0L
        var pCurr = 1L
        var qPrev = 1L
        var qCurr = 0L

        for (a in cf) {
            val pNew = a * pCurr + pPrev
            val qNew = a * qCurr + qPrev
            convergents.add(pNew to qNew)
            pPrev = pCurr
            pCurr = pNew
            qPrev = qCurr
            qCurr = qNew
        }
        return convergents
    }
}
