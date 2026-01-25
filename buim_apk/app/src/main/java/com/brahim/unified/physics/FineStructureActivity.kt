package com.brahim.unified.physics

import android.os.Bundle
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.brahim.unified.R
import com.brahim.unified.core.BrahimConstants

class FineStructureActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_calculator)

        title = "Fine Structure Constant"

        val resultText = findViewById<TextView>(R.id.resultText)
        val formulaText = findViewById<TextView>(R.id.formulaText)
        val accuracyText = findViewById<TextView>(R.id.accuracyText)

        val alphaInv = BrahimConstants.fineStructureInverse()
        val experimental = 137.035999084
        val (dev, unit) = BrahimConstants.accuracy(alphaInv, experimental)

        resultText.text = "alpha^-1 = ${BrahimConstants.formatScientific(alphaInv)}"
        formulaText.text = "Formula: B(7) + 1 + 1/(B(1) + 1)\n= 136 + 1 + 1/28\n= 137.0357..."
        accuracyText.text = "CODATA: $experimental\nDeviation: ${String.format("%.2f", dev)} $unit"
    }
}
