package com.brahim.unified.traffic

import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.brahim.unified.R
import com.brahim.unified.core.BrahimConstants
import com.brahim.unified.core.BrahimCalculators

class IntersectionActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_quad_input)

        title = "Intersection Analysis"

        val northField = findViewById<EditText>(R.id.inputField1)
        val southField = findViewById<EditText>(R.id.inputField2)
        val eastField = findViewById<EditText>(R.id.inputField3)
        val westField = findViewById<EditText>(R.id.inputField4)
        val calculateBtn = findViewById<Button>(R.id.calculateButton)
        val resultText = findViewById<TextView>(R.id.resultText)

        northField.hint = "North Flow (veh/hr)"
        southField.hint = "South Flow (veh/hr)"
        eastField.hint = "East Flow (veh/hr)"
        westField.hint = "West Flow (veh/hr)"

        calculateBtn.setOnClickListener {
            val north = northField.text.toString().toIntOrNull() ?: 400
            val south = southField.text.toString().toIntOrNull() ?: 350
            val east = eastField.text.toString().toIntOrNull() ?: 500
            val west = westField.text.toString().toIntOrNull() ?: 450

            val nsFlow = north + south
            val ewFlow = east + west
            val totalFlow = nsFlow + ewFlow

            // Brahim signal timing
            val baseTiming = BrahimCalculators.calculateSignalTiming()
            val phi = BrahimConstants.PHI

            // Proportional allocation
            val nsRatio = nsFlow.toDouble() / totalFlow
            val ewRatio = ewFlow.toDouble() / totalFlow

            val cycleLength = baseTiming.cycle
            val nsGreen = (cycleLength * nsRatio * 0.85).toInt()  // 85% efficiency
            val ewGreen = (cycleLength * ewRatio * 0.85).toInt()
            val amber = baseTiming.amber
            val allRed = 2  // Safety clearance

            // Level of service
            val saturationFlow = 1800  // veh/hr/lane (standard)
            val nsLanes = 2
            val ewLanes = 2

            val nsCapacity = saturationFlow * nsLanes * nsGreen / cycleLength
            val ewCapacity = saturationFlow * ewLanes * ewGreen / cycleLength

            val nsVC = nsFlow.toDouble() / nsCapacity
            val ewVC = ewFlow.toDouble() / ewCapacity

            fun losFromVC(vc: Double): String = when {
                vc < 0.6 -> "A"
                vc < 0.7 -> "B"
                vc < 0.8 -> "C"
                vc < 0.9 -> "D"
                vc < 1.0 -> "E"
                else -> "F"
            }

            resultText.text = buildString {
                append("INTERSECTION ANALYSIS\n")
                append("Brahim Signal Optimization\n\n")
                append("TRAFFIC VOLUMES:\n")
                append("  North: $north veh/hr\n")
                append("  South: $south veh/hr\n")
                append("  East: $east veh/hr\n")
                append("  West: $west veh/hr\n")
                append("  Total: $totalFlow veh/hr\n\n")
                append("SIGNAL TIMING:\n")
                append("  Cycle: $cycleLength sec (B(3))\n")
                append("  N-S Green: $nsGreen sec\n")
                append("  E-W Green: $ewGreen sec\n")
                append("  Amber: $amber sec (|Δ4|)\n")
                append("  All-Red: $allRed sec\n\n")
                append("CAPACITY ANALYSIS:\n")
                append("  N-S Capacity: ${nsCapacity.toInt()} veh/hr\n")
                append("  E-W Capacity: ${ewCapacity.toInt()} veh/hr\n\n")
                append("LEVEL OF SERVICE:\n")
                append("  N-S: V/C=${String.format("%.2f", nsVC)} → LOS ${losFromVC(nsVC)}\n")
                append("  E-W: V/C=${String.format("%.2f", ewVC)} → LOS ${losFromVC(ewVC)}\n\n")
                append("Brahim Optimization:\n")
                append("  φ-ratio split for balanced delay\n")
                append("  Amber = |B(4)+B(7)-214| = $amber")
            }
        }
    }
}
