package com.brahim.unified.math

import android.os.Bundle
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.brahim.unified.R
import com.brahim.unified.core.BrahimConstants

class SequenceActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_calculator)

        title = "Brahim Sequence"

        val resultText = findViewById<TextView>(R.id.resultText)
        val formulaText = findViewById<TextView>(R.id.formulaText)
        val accuracyText = findViewById<TextView>(R.id.accuracyText)

        val sequence = BrahimConstants.SEQUENCE.joinToString(", ")
        val sum = BrahimConstants.SEQUENCE.sum()
        val center = BrahimConstants.CENTER

        resultText.text = buildString {
            append("B = {$sequence}\n\n")
            append("Sum S = $sum\n")
            append("Center C = $center\n")
            append("phi = ${String.format("%.10f", BrahimConstants.PHI)}")
        }

        formulaText.text = buildString {
            append("Properties:\n")
            append("B(1) + B(10) = ${BrahimConstants.B(1)} + ${BrahimConstants.B(10)} = ${BrahimConstants.B(1) + BrahimConstants.B(10)}\n")
            append("B(2) + B(9) = ${BrahimConstants.B(2)} + ${BrahimConstants.B(9)} = ${BrahimConstants.B(2) + BrahimConstants.B(9)}\n")
            append("B(3) + B(8) = ${BrahimConstants.B(3)} + ${BrahimConstants.B(8)} = ${BrahimConstants.B(3) + BrahimConstants.B(8)}\n")
            append("All pairs sum to S = 214")
        }

        val mirrorOk = BrahimConstants.verifyMirrorSymmetry()
        val alphaOmega = BrahimConstants.verifyAlphaOmega()
        val bekenstein = BrahimConstants.verifyBekensteinHawking()

        accuracyText.text = buildString {
            append("Verification:\n")
            append("Mirror Symmetry: ${if (mirrorOk) "PASS" else "FAIL"}\n")
            append("Alpha-Omega (B10=7*B1-2): ${if (alphaOmega) "PASS" else "FAIL"}\n")
            append("Bekenstein-Hawking (C=4*B1-1): ${if (bekenstein) "PASS" else "FAIL"}")
        }
    }
}
