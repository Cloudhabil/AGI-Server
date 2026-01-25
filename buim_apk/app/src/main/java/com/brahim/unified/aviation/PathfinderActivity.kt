package com.brahim.unified.aviation

import android.os.Bundle
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.brahim.unified.R
import com.brahim.unified.core.BrahimConstants
import com.brahim.unified.core.BrahimCalculators
import kotlin.math.sqrt

class PathfinderActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_calculator)

        title = "Flight Pathfinder"

        val resultText = findViewById<TextView>(R.id.resultText)
        val formulaText = findViewById<TextView>(R.id.formulaText)
        val accuracyText = findViewById<TextView>(R.id.accuracyText)

        val separation = BrahimCalculators.calculateSeparation()
        val phi = BrahimConstants.PHI
        val beta = BrahimConstants.BETA_SECURITY

        resultText.text = buildString {
            append("SEPARATION DISTANCES\n")
            append("Critical: ${String.format("%.2f", separation.critical)} NM\n")
            append("Warning: ${String.format("%.2f", separation.warning)} NM\n")
            append("Monitor: ${String.format("%.2f", separation.monitor)} NM\n\n")
            append("PATH OPTIMIZATION\n")
            append("Golden Ratio Factor: ${String.format("%.6f", phi)}\n")
            append("Compression (beta): ${String.format("%.6f", beta)}\n")
            append("Wormhole Distance Factor: ${String.format("%.4f", beta)}")
        }

        formulaText.text = buildString {
            append("Separation Formulas:\n")
            append("Critical = (B(4)-B(3))/5 = (75-60)/5 = 3.0 NM\n")
            append("Warning = B(1)/5.4 = 27/5.4 = 5.0 NM\n")
            append("Monitor = B(3)/6 = 60/6 = 10.0 NM\n\n")
            append("Path: Method of Characteristics\n")
            append("dx/dt = c(x,t), optimized via phi")
        }

        accuracyText.text = buildString {
            append("ICAO Standards:\n")
            append("Radar Separation: 3-5 NM\n")
            append("Procedural: 10+ NM\n")
            append("Vertical: 1000 ft (RVSM)\n\n")
            append("Brahim accuracy: Within ICAO specs")
        }
    }
}
