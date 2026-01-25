package com.brahim.unified.visualization

import android.os.Bundle
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.brahim.unified.R
import com.brahim.unified.engine.BrahimEngine

class SequencePlotActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_calculator)

        title = "Sequence Visualizer"

        val resultText = findViewById<TextView>(R.id.resultText)
        val formulaText = findViewById<TextView>(R.id.formulaText)
        val accuracyText = findViewById<TextView>(R.id.accuracyText)

        val maxVal = BrahimEngine.SEQUENCE.maxOrNull()!!

        resultText.text = buildString {
            append("BRAHIM SEQUENCE PLOT\n")
            append("════════════════════════════════════\n\n")

            BrahimEngine.SEQUENCE.forEachIndexed { i, b ->
                val n = i + 1
                val barLength = (b.toDouble() / maxVal * 30).toInt()
                val bar = "█".repeat(barLength)
                val mirror = BrahimEngine.mirror(b)

                append("B($n) = ${String.format("%3d", b)} │$bar\n")
            }

            append("\n════════════════════════════════════\n")
            append("        0        50       100      187\n")
        }

        formulaText.text = buildString {
            append("MIRROR PAIRS (sum = 214):\n")
            append("─────────────────────────────────────\n\n")

            for (i in 1..5) {
                val left = BrahimEngine.B(i)
                val right = BrahimEngine.B(11 - i)

                val leftBar = "█".repeat((left.toDouble() / maxVal * 15).toInt())
                val rightBar = "█".repeat((right.toDouble() / maxVal * 15).toInt())

                append("B($i)=${String.format("%3d", left)} $leftBar")
                append(" ◄─► ")
                append("$rightBar ${String.format("%3d", right)}=B(${11-i})\n")
            }

            append("\n─────────────────────────────────────\n")
            append("Symmetry breaking at center:\n")
            append("  Δ₄ = B(4)+B(7)-214 = ${BrahimEngine.DELTA_4}\n")
            append("  Δ₅ = B(5)+B(6)-214 = ${BrahimEngine.DELTA_5}\n")
        }

        accuracyText.text = buildString {
            append("SEQUENCE STATISTICS:\n")
            append("─────────────────────────────────────\n\n")

            val mean = BrahimEngine.SEQUENCE.average()
            val min = BrahimEngine.SEQUENCE.minOrNull()!!
            val max = BrahimEngine.SEQUENCE.maxOrNull()!!

            append("Sum (S): ${BrahimEngine.SUM}\n")
            append("Mean: ${String.format("%.1f", mean)}\n")
            append("Center (C): ${BrahimEngine.CENTER}\n")
            append("Range: $min - $max\n")
            append("Span: ${max - min}\n\n")

            append("GOLDEN RATIOS:\n")
            append("B(10)/B(1) = ${String.format("%.3f", BrahimEngine.B(10).toDouble() / BrahimEngine.B(1))}\n")
            append("B(7)/B(4) = ${String.format("%.3f", BrahimEngine.B(7).toDouble() / BrahimEngine.B(4))}\n")
            append("φ = ${String.format("%.3f", BrahimEngine.PHI)}\n")
        }
    }
}
