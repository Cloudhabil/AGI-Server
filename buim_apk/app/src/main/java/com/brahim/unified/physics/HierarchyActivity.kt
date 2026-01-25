package com.brahim.unified.physics

import android.os.Bundle
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.brahim.unified.R
import com.brahim.unified.core.BrahimConstants
import kotlin.math.pow

class HierarchyActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_calculator)

        title = "Mass & Coupling Hierarchy"

        val resultText = findViewById<TextView>(R.id.resultText)
        val formulaText = findViewById<TextView>(R.id.formulaText)
        val accuracyText = findViewById<TextView>(R.id.accuracyText)

        val couplingHierarchy = BrahimConstants.couplingHierarchy()
        val massHierarchy = BrahimConstants.massHierarchy()

        // Calculate intermediate values
        val b1 = BrahimConstants.B(1)
        val b7 = BrahimConstants.B(7)
        val b10 = BrahimConstants.B(10)
        val mirrorB7 = BrahimConstants.mirror(b7)

        resultText.text = buildString {
            append("HIERARCHY PROBLEM\n\n")
            append("Coupling Hierarchy:\n")
            append("  ${BrahimConstants.formatScientific(couplingHierarchy)}\n\n")
            append("Mass Hierarchy:\n")
            append("  ${BrahimConstants.formatScientific(massHierarchy)}\n\n")
            append("Ratio (Coupling/Mass):\n")
            append("  ${BrahimConstants.formatScientific(couplingHierarchy / massHierarchy)}")
        }

        formulaText.text = buildString {
            append("Coupling Hierarchy:\n")
            append("  (B(7) * M(B(7)))^9\n")
            append("  = ($b7 * $mirrorB7)^9\n")
            append("  = ${b7 * mirrorB7}^9\n\n")
            append("Mass Hierarchy:\n")
            append("  (B(1) * B(10))^6\n")
            append("  = ($b1 * $b10)^6\n")
            append("  = ${b1 * b10}^6")
        }

        accuracyText.text = buildString {
            append("The Hierarchy Problem:\n\n")
            append("Why is gravity so weak?\n")
            append("Planck mass / proton mass ~ 10^19\n\n")
            append("Brahim explanation:\n")
            append("Mirror symmetry breaking in\n")
            append("the B(4),B(5),B(6),B(7) region\n")
            append("creates the mass gap.\n\n")
            append("Delta(4) + Delta(5) = ${BrahimConstants.netAsymmetry()}")
        }
    }
}
