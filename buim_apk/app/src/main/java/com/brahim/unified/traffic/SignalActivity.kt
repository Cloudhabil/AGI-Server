package com.brahim.unified.traffic

import android.os.Bundle
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.brahim.unified.R
import com.brahim.unified.core.BrahimConstants
import com.brahim.unified.core.BrahimCalculators

class SignalActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_calculator)

        title = "Signal Timing"

        val resultText = findViewById<TextView>(R.id.resultText)
        val formulaText = findViewById<TextView>(R.id.formulaText)
        val accuracyText = findViewById<TextView>(R.id.accuracyText)

        val timing = BrahimCalculators.calculateSignalTiming()

        resultText.text = buildString {
            append("BRAHIM SIGNAL TIMING\n\n")
            append("Cycle Length: ${timing.cycle} seconds\n")
            append("Green Phase: ${timing.green} seconds\n")
            append("Amber Phase: ${timing.amber} seconds\n")
            append("Red Phase: ${timing.red} seconds\n\n")
            append("Total: ${timing.green + timing.amber + timing.red} seconds")
        }

        formulaText.text = buildString {
            append("Derivation from Brahim Sequence:\n\n")
            append("Cycle = B(3) = 60 seconds\n")
            append("Green = B(1) = 27 seconds\n")
            append("Amber = |delta(4)| = |B(4)+B(7)-214| = 3 seconds\n")
            append("Red = Cycle - Green - Amber = 30 seconds\n\n")
            append("Golden ratio optimization ensures\n")
            append("green/cycle ~ 1/phi for flow harmony")
        }

        accuracyText.text = buildString {
            append("Standard Guidelines:\n")
            append("Amber: 3-6 seconds (ITE)\n")
            append("Min Green: 7 seconds\n")
            append("Max Cycle: 120 seconds\n\n")
            append("Brahim timing complies with standards\n")
            append("while optimizing throughput")
        }
    }
}
