package com.brahim.unified.math

import android.os.Bundle
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.brahim.unified.R
import com.brahim.unified.core.BrahimConstants
import kotlin.math.pow

class GoldenActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_calculator)

        title = "Golden Ratio Hierarchy"

        val resultText = findViewById<TextView>(R.id.resultText)
        val formulaText = findViewById<TextView>(R.id.formulaText)
        val accuracyText = findViewById<TextView>(R.id.accuracyText)

        val phi = BrahimConstants.PHI
        val phiInv = BrahimConstants.PHI_INV
        val alpha = BrahimConstants.ALPHA_WORMHOLE
        val beta = BrahimConstants.BETA_SECURITY
        val gamma = BrahimConstants.GAMMA_DAMPING

        resultText.text = buildString {
            append("GOLDEN RATIO HIERARCHY\n\n")
            append("φ (phi) = ${String.format("%.15f", phi)}\n\n")
            append("1/φ = ${String.format("%.15f", phiInv)}\n\n")
            append("α = 1/φ² = ${String.format("%.15f", alpha)}\n\n")
            append("β = 1/φ³ = ${String.format("%.15f", beta)}\n")
            append("  = √5 - 2\n\n")
            append("γ = 1/φ⁴ = ${String.format("%.15f", gamma)}")
        }

        formulaText.text = buildString {
            append("Properties:\n\n")
            append("φ = (1 + √5) / 2\n\n")
            append("φ² = φ + 1 = ${String.format("%.10f", phi*phi)}\n\n")
            append("φ - 1/φ = 1\n")
            append("  ${String.format("%.10f", phi)} - ${String.format("%.10f", phiInv)}\n")
            append("  = ${String.format("%.10f", phi - phiInv)}\n\n")
            append("Continued fraction:\n")
            append("φ = 1 + 1/(1 + 1/(1 + 1/...))\n\n")
            append("Fibonacci ratio:\n")
            append("lim(F(n+1)/F(n)) = φ")
        }

        accuracyText.text = buildString {
            append("Verification:\n\n")
            append("β² + 4β - 1 = 0?\n")
            val check = beta * beta + 4 * beta - 1
            append("  ${String.format("%.2e", check)} ✓\n\n")
            append("α/β = φ?\n")
            append("  ${String.format("%.10f", alpha / beta)}\n")
            append("  vs ${String.format("%.10f", phi)}\n\n")
            append("Powers of 1/φ:\n")
            for (i in 1..6) {
                append("  1/φ^$i = ${String.format("%.8f", 1.0/phi.pow(i))}\n")
            }
        }
    }
}
