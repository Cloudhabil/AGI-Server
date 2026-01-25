package com.brahim.unified.traffic

import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.brahim.unified.R
import com.brahim.unified.core.BrahimConstants
import com.brahim.unified.core.BrahimCalculators

class EmergencyActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_dual_input)

        title = "Emergency Router"

        val distanceField = findViewById<EditText>(R.id.inputField1)
        val urgencyField = findViewById<EditText>(R.id.inputField2)
        val calculateBtn = findViewById<Button>(R.id.calculateButton)
        val resultText = findViewById<TextView>(R.id.resultText)

        distanceField.hint = "Distance to Hospital (km)"
        urgencyField.hint = "Urgency (1-10)"

        calculateBtn.setOnClickListener {
            val distance = distanceField.text.toString().toDoubleOrNull() ?: 5.0
            val urgency = urgencyField.text.toString().toIntOrNull() ?: 5

            val phi = BrahimConstants.PHI
            val beta = BrahimConstants.BETA_SECURITY

            // Priority calculation using Brahim
            val priority = when {
                urgency >= 9 -> "CODE RED - Life threatening"
                urgency >= 7 -> "CODE ORANGE - Urgent"
                urgency >= 5 -> "CODE YELLOW - Semi-urgent"
                urgency >= 3 -> "CODE GREEN - Non-urgent"
                else -> "CODE WHITE - Minor"
            }

            // Signal preemption timing
            val preemptionRadius = BrahimConstants.B(urgency.coerceIn(1, 10)).toDouble() * 10  // meters

            // ETA calculations
            val normalSpeed = 40.0  // km/h in traffic
            val emergencySpeed = 80.0  // km/h with preemption
            val wormholeSpeed = emergencySpeed / beta  // Brahim-optimized

            val normalETA = distance / normalSpeed * 60
            val emergencyETA = distance / emergencySpeed * 60
            val wormholeETA = distance / wormholeSpeed * 60 * phi  // Adjusted for real-world

            // Safety verdict
            val resonance = BrahimConstants.resonance(listOf(distance), listOf(urgency.toDouble()))
            val verdict = BrahimCalculators.assessSafety(resonance)

            resultText.text = buildString {
                append("EMERGENCY ROUTING\n")
                append("Brahim Priority System\n\n")
                append("Incident:\n")
                append("  Distance: ${String.format("%.1f", distance)} km\n")
                append("  Urgency: $urgency/10\n")
                append("  Priority: $priority\n\n")
                append("RESPONSE TIMES:\n")
                append("  Normal traffic: ${String.format("%.1f", normalETA)} min\n")
                append("  With preemption: ${String.format("%.1f", emergencyETA)} min\n")
                append("  Brahim-optimized: ${String.format("%.1f", wormholeETA)} min\n\n")
                append("SIGNAL PREEMPTION:\n")
                append("  Radius: ${String.format("%.0f", preemptionRadius)} m\n")
                append("  Based on B($urgency) = ${BrahimConstants.B(urgency.coerceIn(1, 10))}\n\n")
                append("Corridor clearance:\n")
                val clearTime = BrahimCalculators.calculateSignalTiming()
                append("  Green extension: +${clearTime.green / 3} sec\n")
                append("  Cross traffic hold: ${clearTime.cycle / 2} sec\n\n")
                append("Safety Analysis:\n")
                append("  Resonance: ${String.format("%.6f", resonance)}\n")
                append("  Verdict: $verdict")
            }
        }
    }
}
