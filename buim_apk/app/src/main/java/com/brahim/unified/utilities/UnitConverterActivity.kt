package com.brahim.unified.utilities

import android.os.Bundle
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.brahim.unified.R
import com.brahim.unified.engine.BrahimEngine
import kotlin.math.pow

class UnitConverterActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_calculator)

        title = "Unit Converter"

        val resultText = findViewById<TextView>(R.id.resultText)
        val formulaText = findViewById<TextView>(R.id.formulaText)
        val accuracyText = findViewById<TextView>(R.id.accuracyText)

        // φ-based unit scales
        val phi = BrahimEngine.PHI
        val scales = listOf(
            "φ⁻⁴" to phi.pow(-4),
            "φ⁻³" to phi.pow(-3),
            "φ⁻²" to phi.pow(-2),
            "φ⁻¹" to phi.pow(-1),
            "φ⁰" to 1.0,
            "φ¹" to phi,
            "φ²" to phi.pow(2),
            "φ³" to phi.pow(3),
            "φ⁴" to phi.pow(4)
        )

        resultText.text = buildString {
            append("GOLDEN RATIO UNIT SCALES\n")
            append("════════════════════════════════════\n\n")

            append("BASE REFERENCE: 1 meter\n")
            append("─────────────────────────────────────\n\n")

            scales.forEach { (name, value) ->
                val formatted = String.format("%.6f", value)
                append("  $name = $formatted m\n")
            }

            append("\n════════════════════════════════════\n")
            append("φ = ${String.format("%.10f", phi)}\n")
        }

        formulaText.text = buildString {
            append("BRAHIM SEQUENCE UNITS\n")
            append("─────────────────────────────────────\n\n")

            append("Sequence: B = {27, 42, 60, 75, 97,\n")
            append("              121, 136, 154, 172, 187}\n\n")

            append("B-SCALE CONVERSIONS:\n\n")

            for (i in 1..10) {
                val b = BrahimEngine.B(i)
                val meters = b / 100.0
                val feet = meters * 3.28084
                append("B($i) = $b → ${String.format("%.2f", meters)}m = ${String.format("%.2f", feet)}ft\n")
            }
        }

        accuracyText.text = buildString {
            append("SPECIAL CONVERSIONS\n")
            append("─────────────────────────────────────\n\n")

            val beta = BrahimEngine.BETA
            val alpha = BrahimEngine.ALPHA

            append("SECURITY CONSTANT UNITS:\n")
            append("  β = ${String.format("%.10f", beta)}\n")
            append("  1/β = ${String.format("%.6f", 1/beta)}\n")
            append("  β² = ${String.format("%.10f", beta * beta)}\n\n")

            append("WORMHOLE CONSTANT UNITS:\n")
            append("  α = ${String.format("%.10f", alpha)}\n")
            append("  α/β = φ = ${String.format("%.6f", alpha/beta)}\n\n")

            append("CENTER UNIT:\n")
            append("  C = ${BrahimEngine.CENTER} (central axis)\n")
            append("  S/2 = ${BrahimEngine.SUM / 2.0} (sum midpoint)\n")
        }
    }
}
