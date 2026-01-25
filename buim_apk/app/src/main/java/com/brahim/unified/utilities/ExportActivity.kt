package com.brahim.unified.utilities

import android.os.Bundle
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.brahim.unified.R
import com.brahim.unified.engine.BrahimEngine

class ExportActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_calculator)

        title = "Export Tools"

        val resultText = findViewById<TextView>(R.id.resultText)
        val formulaText = findViewById<TextView>(R.id.formulaText)
        val accuracyText = findViewById<TextView>(R.id.accuracyText)

        // Generate JSON export
        resultText.text = buildString {
            append("JSON EXPORT FORMAT\n")
            append("════════════════════════════════════\n\n")

            append("{\n")
            append("  \"brahim_sequence\": {\n")
            append("    \"values\": [${BrahimEngine.SEQUENCE.joinToString(", ")}],\n")
            append("    \"sum\": ${BrahimEngine.SUM},\n")
            append("    \"center\": ${BrahimEngine.CENTER},\n")
            append("    \"delta_4\": ${BrahimEngine.DELTA_4},\n")
            append("    \"delta_5\": ${BrahimEngine.DELTA_5}\n")
            append("  },\n")
            append("  \"golden_hierarchy\": {\n")
            append("    \"phi\": ${BrahimEngine.PHI},\n")
            append("    \"alpha\": ${BrahimEngine.ALPHA},\n")
            append("    \"beta\": ${BrahimEngine.BETA},\n")
            append("    \"gamma\": ${BrahimEngine.GAMMA}\n")
            append("  },\n")
            append("  \"resonance\": {\n")
            append("    \"genesis\": ${BrahimEngine.GENESIS}\n")
            append("  }\n")
            append("}\n")
        }

        // Generate CSV export
        formulaText.text = buildString {
            append("CSV EXPORT FORMAT\n")
            append("════════════════════════════════════\n\n")

            append("index,B(n),mirror,pair_sum,delta\n")
            for (i in 1..10) {
                val b = BrahimEngine.B(i)
                val mirror = BrahimEngine.mirror(b)
                val j = 11 - i
                val pairSum = if (i <= 5) b + BrahimEngine.B(j) else 0
                val delta = if (i <= 5) pairSum - 214 else 0
                append("$i,$b,$mirror,$pairSum,$delta\n")
            }
        }

        // Generate LaTeX export
        accuracyText.text = buildString {
            append("LaTeX EXPORT FORMAT\n")
            append("════════════════════════════════════\n\n")

            append("\\section{Brahim Constants}\n\n")
            append("\\begin{align}\n")
            append("\\mathbf{B} &= \\{")
            append(BrahimEngine.SEQUENCE.joinToString(", "))
            append("\\} \\\\\n")
            append("S &= ${BrahimEngine.SUM} \\\\\n")
            append("C &= ${BrahimEngine.CENTER} \\\\\n")
            append("\\varphi &= ${String.format("%.10f", BrahimEngine.PHI)} \\\\\n")
            append("\\beta &= \\sqrt{5} - 2 = ${String.format("%.10f", BrahimEngine.BETA)}\n")
            append("\\end{align}\n\n")

            append("\\section{Physics}\n\n")
            append("\\begin{equation}\n")
            append("\\alpha^{-1} = ${String.format("%.6f", BrahimEngine.Physics.fineStructureInverse())}\n")
            append("\\end{equation}\n")
        }
    }
}
