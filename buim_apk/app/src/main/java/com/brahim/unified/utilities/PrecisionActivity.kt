package com.brahim.unified.utilities

import android.os.Bundle
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.brahim.unified.R
import com.brahim.unified.engine.BrahimEngine
import kotlin.math.abs
import kotlin.math.log10

class PrecisionActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_calculator)

        title = "Precision Analyzer"

        val resultText = findViewById<TextView>(R.id.resultText)
        val formulaText = findViewById<TextView>(R.id.formulaText)
        val accuracyText = findViewById<TextView>(R.id.accuracyText)

        resultText.text = buildString {
            append("NUMERICAL PRECISION ANALYSIS\n")
            append("════════════════════════════════════\n\n")

            append("PHYSICS CONSTANTS ACCURACY:\n")
            append("─────────────────────────────────────\n\n")

            val comparisons = listOf(
                Triple("α⁻¹ (Fine Structure)", BrahimEngine.Physics.fineStructureInverse(), 137.035999084),
                Triple("sin²θ_W (Weinberg)", BrahimEngine.Physics.weinbergAngle(), 0.23122),
                Triple("m_μ/m_e (Mass Ratio)", BrahimEngine.Physics.muonElectronRatio(), 206.7682830),
                Triple("m_p/m_e (Proton/e)", BrahimEngine.Physics.protonElectronRatio(), 1836.15267343)
            )

            comparisons.forEach { (name, calc, codata) ->
                val relError = abs(calc - codata) / codata
                val ppm = relError * 1e6
                val sigFigs = if (relError > 0) -log10(relError).toInt() else 15

                append("$name:\n")
                append("  Calculated: ${String.format("%.8f", calc)}\n")
                append("  CODATA:     ${String.format("%.8f", codata)}\n")
                append("  Error:      ${String.format("%.2f", ppm)} ppm\n")
                append("  Sig. Figs:  $sigFigs digits\n\n")
            }
        }

        formulaText.text = buildString {
            append("MATHEMATICAL IDENTITY CHECKS:\n")
            append("════════════════════════════════════\n\n")

            val phi = BrahimEngine.PHI
            val beta = BrahimEngine.BETA
            val alpha = BrahimEngine.ALPHA

            val checks = listOf(
                Triple("φ² - φ - 1", kotlin.math.pow(phi, 2.0) - phi - 1, 0.0),
                Triple("β² + 4β - 1", kotlin.math.pow(beta, 2.0) + 4*beta - 1, 0.0),
                Triple("α/β - φ", alpha/beta - phi, 0.0),
                Triple("β - 1/φ³", beta - 1/kotlin.math.pow(phi, 3.0), 0.0),
                Triple("φ + 1/φ - √5", phi + 1/phi - kotlin.math.sqrt(5.0), 0.0)
            )

            append("Identity          |  Result    | Status\n")
            append("─────────────────────────────────────────\n")

            checks.forEach { (name, result, expected) ->
                val error = abs(result - expected)
                val status = when {
                    error < 1e-14 -> "✓ Perfect"
                    error < 1e-10 -> "○ Good"
                    else -> "✗ Error"
                }
                append("${name.padEnd(17)}| ${String.format("%+.2e", result)} | $status\n")
            }
        }

        accuracyText.text = buildString {
            append("SEQUENCE INTEGRITY:\n")
            append("════════════════════════════════════\n\n")

            append("CHECKSUM VERIFICATION:\n")
            append("─────────────────────────────────────\n")
            val sum = BrahimEngine.SEQUENCE.sum()
            val expectedSum = 1070
            append("Σ B(i) = $sum (expected: $expectedSum)\n")
            append("Status: ${if (sum == expectedSum) "✓ PASS" else "✗ FAIL"}\n\n")

            append("MIRROR SYMMETRY:\n")
            append("─────────────────────────────────────\n")
            var mirrorPassed = 0
            for (i in 1..5) {
                val bi = BrahimEngine.B(i)
                val bj = BrahimEngine.B(11 - i)
                val pairSum = bi + bj
                if (i in listOf(1, 2, 3, 8, 9, 10) && pairSum == 214) mirrorPassed++
                if (i == 4 && pairSum == 211) mirrorPassed++  // Δ₄ = -3
                if (i == 5 && pairSum == 218) mirrorPassed++  // Δ₅ = +4
            }
            append("Mirror pairs: $mirrorPassed/5 verified\n\n")

            append("RESONANCE GATE:\n")
            append("─────────────────────────────────────\n")
            val verifications = BrahimEngine.Verify.runAllVerifications()
            val passed = verifications.count { it.second }
            val total = verifications.size
            append("Verifications: $passed/$total passed\n")
            append("Gate Status: ${if (passed == total) "✓ OPEN" else "○ PARTIAL"}\n")
        }
    }
}
