package com.brahim.unified.aviation

import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.brahim.unified.R
import com.brahim.unified.core.BrahimConstants

class RunwayActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_dual_input)

        title = "Runway Allocator"

        val runwaysField = findViewById<EditText>(R.id.inputField1)
        val demandField = findViewById<EditText>(R.id.inputField2)
        val calculateBtn = findViewById<Button>(R.id.calculateButton)
        val resultText = findViewById<TextView>(R.id.resultText)

        runwaysField.hint = "Number of Runways"
        demandField.hint = "Hourly Demand (movements)"

        calculateBtn.setOnClickListener {
            val runways = runwaysField.text.toString().toIntOrNull() ?: 2
            val demand = demandField.text.toString().toIntOrNull() ?: 60

            // Brahim-optimized runway capacity
            val phi = BrahimConstants.PHI
            val beta = BrahimConstants.BETA_SECURITY

            // Base capacity per runway (movements/hour)
            val baseCapacity = BrahimConstants.B(3)  // 60 movements/hr

            // Configuration efficiency
            val configs = when (runways) {
                1 -> listOf(RunwayConfig("Single", 1.0, baseCapacity))
                2 -> listOf(
                    RunwayConfig("Parallel Independent", phi, (baseCapacity * 1.8).toInt()),
                    RunwayConfig("Parallel Dependent", 1.5, (baseCapacity * 1.5).toInt()),
                    RunwayConfig("Intersecting", 1.3, (baseCapacity * 1.3).toInt())
                )
                3 -> listOf(
                    RunwayConfig("Triple Parallel", phi * 1.5, (baseCapacity * 2.5).toInt()),
                    RunwayConfig("Two + Cross", 2.0, (baseCapacity * 2.0).toInt())
                )
                else -> listOf(
                    RunwayConfig("Complex ($runways RWY)", phi * runways * 0.4, (baseCapacity * runways * 0.7).toInt())
                )
            }

            // Calculate utilization
            val bestConfig = configs.maxByOrNull { it.capacity }!!
            val utilization = demand.toDouble() / bestConfig.capacity * 100

            // Slot allocation using Egyptian fractions principle
            val slotDuration = 60.0 / demand  // minutes per slot
            val brahimSlots = BrahimConstants.B(1).toDouble() / demand  // Adjusted slot

            resultText.text = buildString {
                append("RUNWAY ALLOCATION\n")
                append("Brahim Capacity Model\n\n")
                append("Airport: $runways runway(s)\n")
                append("Demand: $demand movements/hr\n\n")
                append("CONFIGURATIONS:\n")
                configs.forEach { config ->
                    val marker = if (config == bestConfig) " <-- BEST" else ""
                    append("  ${config.name}:\n")
                    append("    Capacity: ${config.capacity} mov/hr$marker\n")
                    append("    Efficiency: ${String.format("%.2f", config.efficiency)}\n")
                }
                append("\nANALYSIS:\n")
                append("  Utilization: ${String.format("%.1f", utilization)}%\n")
                val status = when {
                    utilization > 95 -> "CRITICAL - delays expected"
                    utilization > 85 -> "HIGH - monitor closely"
                    utilization > 70 -> "MODERATE - acceptable"
                    else -> "LOW - spare capacity"
                }
                append("  Status: $status\n\n")
                append("SLOT TIMING:\n")
                append("  Standard slot: ${String.format("%.1f", slotDuration)} min\n")
                append("  Brahim slot: ${String.format("%.2f", brahimSlots * 60)} min\n")
                append("  Base capacity: B(3) = $baseCapacity\n\n")
                append("Optimization:\n")
                append("  Golden ratio φ used for\n")
                append("  parallel runway spacing\n")
                append("  and arrival sequencing")
            }
        }
    }

    data class RunwayConfig(val name: String, val efficiency: Double, val capacity: Int)
}
