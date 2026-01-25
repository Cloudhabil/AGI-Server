package com.brahim.unified.aviation

import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.brahim.unified.R
import com.brahim.unified.core.BrahimConstants
import com.brahim.unified.core.BrahimCalculators

class MaintenanceActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_dual_input)

        title = "Maintenance Scheduler"

        val hoursField = findViewById<EditText>(R.id.inputField1)
        val cyclesField = findViewById<EditText>(R.id.inputField2)
        val calculateBtn = findViewById<Button>(R.id.calculateButton)
        val resultText = findViewById<TextView>(R.id.resultText)

        hoursField.hint = "Current Flight Hours"
        cyclesField.hint = "Current Cycles"

        calculateBtn.setOnClickListener {
            val hours = hoursField.text.toString().toDoubleOrNull() ?: 5000.0
            val cycles = cyclesField.text.toString().toIntOrNull() ?: 3000

            // Brahim maintenance intervals
            val checks = listOf(
                MaintenanceCheck("A-Check", BrahimCalculators.maintenanceInterval(1), "Light maintenance"),
                MaintenanceCheck("B-Check", BrahimCalculators.maintenanceInterval(2), "Moderate inspection"),
                MaintenanceCheck("C-Check", BrahimCalculators.maintenanceInterval(4), "Heavy maintenance"),
                MaintenanceCheck("D-Check", BrahimCalculators.maintenanceInterval(7), "Complete overhaul"),
                MaintenanceCheck("Engine OH", BrahimCalculators.maintenanceInterval(10), "Engine overhaul")
            )

            // Calculate next due
            val upcoming = checks.map { check ->
                val interval = check.intervalHours
                val nextDue = ((hours / interval).toInt() + 1) * interval
                val remaining = nextDue - hours
                check to remaining
            }.sortedBy { it.second }

            // Component life limits (Brahim-derived)
            val components = listOf(
                Component("Landing Gear", BrahimConstants.B(10) * 100, cycles),
                Component("APU", BrahimConstants.B(8) * 100, (hours / 1.5).toInt()),
                Component("Engine 1", BrahimConstants.B(9) * 150, (hours / 1.2).toInt()),
                Component("Engine 2", BrahimConstants.B(9) * 150, (hours / 1.2).toInt())
            )

            resultText.text = buildString {
                append("MAINTENANCE SCHEDULE\n")
                append("Brahim Interval System\n\n")
                append("Current Status:\n")
                append("  Flight Hours: ${String.format("%.0f", hours)}\n")
                append("  Cycles: $cycles\n\n")
                append("UPCOMING CHECKS:\n")
                upcoming.take(3).forEach { (check, remaining) ->
                    val status = when {
                        remaining < 100 -> "[SOON]"
                        remaining < 500 -> "[PLAN]"
                        else -> ""
                    }
                    append("  ${check.name}: ${String.format("%.0f", remaining)} hrs $status\n")
                    append("    (every ${check.intervalHours} hrs - ${check.description})\n")
                }
                append("\nBRAHIM INTERVALS:\n")
                for (i in 1..10 step 3) {
                    val interval = BrahimCalculators.maintenanceInterval(i)
                    append("  B($i) × 100 = $interval hrs\n")
                }
                append("\nCOMPONENT LIFE:\n")
                components.forEach { comp ->
                    val remaining = comp.limit - comp.current
                    val pct = (comp.current.toDouble() / comp.limit * 100)
                    append("  ${comp.name}:\n")
                    append("    ${comp.current}/${comp.limit} (${String.format("%.1f", pct)}%)\n")
                }
            }
        }
    }

    data class MaintenanceCheck(val name: String, val intervalHours: Int, val description: String)
    data class Component(val name: String, val limit: Int, val current: Int)
}
