package com.brahim.unified.physics

import android.os.Bundle
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.brahim.unified.R
import com.brahim.unified.core.BrahimConstants

class CouplingActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_calculator)

        title = "Coupling Constants"

        val resultText = findViewById<TextView>(R.id.resultText)
        val formulaText = findViewById<TextView>(R.id.formulaText)
        val accuracyText = findViewById<TextView>(R.id.accuracyText)

        val strongInv = BrahimConstants.strongCouplingInverse()
        val weakInv = BrahimConstants.weakCouplingInverse()
        val hierarchy = BrahimConstants.couplingHierarchy()

        resultText.text = buildString {
            append("COUPLING CONSTANTS\n\n")
            append("Strong Coupling (1/alpha_s):\n")
            append("  ${String.format("%.4f", strongInv)}\n\n")
            append("Weak Coupling (1/alpha_w):\n")
            append("  ${String.format("%.4f", weakInv)}\n\n")
            append("Coupling Hierarchy:\n")
            append("  ${BrahimConstants.formatScientific(hierarchy)}")
        }

        formulaText.text = buildString {
            append("Derivations:\n\n")
            append("Strong: (B(2)-B(1))/2 + 1\n")
            append("  = (42-27)/2 + 1 = 8.5\n\n")
            append("Weak: (B(1)+B(2))/2 - 3\n")
            append("  = (27+42)/2 - 3 = 31.5\n\n")
            append("Hierarchy: (B(7)*M(B(7)))^9\n")
            append("  = (136 * 78)^9")
        }

        accuracyText.text = buildString {
            append("Physical Significance:\n\n")
            append("Strong force: binds quarks\n")
            append("Weak force: radioactive decay\n")
            append("EM force: alpha = 1/137\n\n")
            append("Hierarchy explains why gravity\n")
            append("is 10^36 times weaker than EM")
        }
    }
}
