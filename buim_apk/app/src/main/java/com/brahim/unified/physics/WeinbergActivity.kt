package com.brahim.unified.physics

import android.os.Bundle
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.brahim.unified.R
import com.brahim.unified.core.BrahimConstants

class WeinbergActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_calculator)

        title = "Weinberg Angle"

        val resultText = findViewById<TextView>(R.id.resultText)
        val formulaText = findViewById<TextView>(R.id.formulaText)
        val accuracyText = findViewById<TextView>(R.id.accuracyText)

        val sinSqTheta = BrahimConstants.weinbergAngle()
        val experimental = 0.23122
        val (dev, unit) = BrahimConstants.accuracy(sinSqTheta, experimental)

        resultText.text = "sin^2(theta_W) = ${BrahimConstants.formatScientific(sinSqTheta)}"
        formulaText.text = "Formula: B(1) / (B(7) - 19)\n= 27 / (136 - 19)\n= 27 / 117"
        accuracyText.text = "CODATA: $experimental\nDeviation: ${String.format("%.2f", dev)} $unit"
    }
}
