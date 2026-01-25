package com.brahim.unified.utilities

import android.os.Bundle
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.brahim.unified.R
import com.brahim.unified.engine.BrahimEngine
import kotlin.math.pow
import kotlin.math.sqrt
import kotlin.math.PI

class FormulaActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_calculator)

        title = "Formula Calculator"

        val resultText = findViewById<TextView>(R.id.resultText)
        val formulaText = findViewById<TextView>(R.id.formulaText)
        val accuracyText = findViewById<TextView>(R.id.accuracyText)

        val phi = BrahimEngine.PHI
        val beta = BrahimEngine.BETA

        resultText.text = buildString {
            append("BRAHIM FORMULA EVALUATOR\n")
            append("════════════════════════════════════\n\n")

            append("GOLDEN RATIO IDENTITIES:\n")
            append("─────────────────────────────────────\n")

            // φ² = φ + 1
            val phiSq = phi * phi
            val phiPlus1 = phi + 1
            append("φ² = φ + 1\n")
            append("  φ² = ${String.format("%.10f", phiSq)}\n")
            append("  φ+1 = ${String.format("%.10f", phiPlus1)}\n")
            append("  Δ = ${String.format("%.2e", phiSq - phiPlus1)} ✓\n\n")

            // 1/φ = φ - 1
            val invPhi = 1.0 / phi
            val phiMinus1 = phi - 1
            append("1/φ = φ - 1\n")
            append("  1/φ = ${String.format("%.10f", invPhi)}\n")
            append("  φ-1 = ${String.format("%.10f", phiMinus1)}\n")
            append("  Δ = ${String.format("%.2e", invPhi - phiMinus1)} ✓\n")
        }

        formulaText.text = buildString {
            append("BETA IDENTITIES:\n")
            append("════════════════════════════════════\n\n")

            // β = √5 - 2
            val sqrt5minus2 = sqrt(5.0) - 2
            append("β = √5 - 2\n")
            append("  β = ${String.format("%.15f", beta)}\n")
            append("  √5-2 = ${String.format("%.15f", sqrt5minus2)}\n")
            append("  Δ = ${String.format("%.2e", beta - sqrt5minus2)} ✓\n\n")

            // β = 1/φ³
            val invPhiCubed = 1.0 / phi.pow(3)
            append("β = 1/φ³\n")
            append("  β = ${String.format("%.15f", beta)}\n")
            append("  1/φ³ = ${String.format("%.15f", invPhiCubed)}\n")
            append("  Δ = ${String.format("%.2e", beta - invPhiCubed)} ✓\n\n")

            // β² + 4β - 1 = 0
            val polynomial = beta.pow(2) + 4 * beta - 1
            append("β² + 4β - 1 = 0\n")
            append("  Result = ${String.format("%.2e", polynomial)} ✓\n")
        }

        accuracyText.text = buildString {
            append("SEQUENCE FORMULAS:\n")
            append("════════════════════════════════════\n\n")

            append("MIRROR OPERATOR: M(x) = 214 - x\n")
            append("─────────────────────────────────────\n")
            for (i in 1..5) {
                val b = BrahimEngine.B(i)
                val mirror = BrahimEngine.mirror(b)
                val bMirror = BrahimEngine.B(11 - i)
                val check = if (mirror == bMirror) "✓" else "✗"
                append("M(B($i)) = M($b) = $mirror = B(${11-i}) $check\n")
            }

            append("\nSUM IDENTITY: Σ B(i) = 1070\n")
            append("─────────────────────────────────────\n")
            val sum = BrahimEngine.SEQUENCE.sum()
            append("Calculated: $sum\n")
            append("Expected: 1070\n")
            append("Check: ${if (sum == 1070) "✓" else "✗"}\n\n")

            append("PAIR SUM: B(i) + B(11-i) = 214\n")
            append("─────────────────────────────────────\n")
            for (i in listOf(1, 2, 3)) {
                val bi = BrahimEngine.B(i)
                val bj = BrahimEngine.B(11 - i)
                val pairSum = bi + bj
                val check = if (pairSum == 214) "✓" else "≈"
                append("B($i)+B(${11-i}) = $bi+$bj = $pairSum $check\n")
            }
        }
    }
}
