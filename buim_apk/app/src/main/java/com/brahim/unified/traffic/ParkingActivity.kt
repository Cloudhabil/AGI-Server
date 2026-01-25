package com.brahim.unified.traffic

import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.brahim.unified.R
import com.brahim.unified.core.BrahimConstants
import com.brahim.unified.core.BrahimCalculators

class ParkingActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_dual_input)

        title = "Parking Allocator"

        val spotsField = findViewById<EditText>(R.id.inputField1)
        val demandField = findViewById<EditText>(R.id.inputField2)
        val calculateBtn = findViewById<Button>(R.id.calculateButton)
        val resultText = findViewById<TextView>(R.id.resultText)

        spotsField.hint = "Total Parking Spots"
        demandField.hint = "Expected Vehicles"

        calculateBtn.setOnClickListener {
            val totalSpots = spotsField.text.toString().toIntOrNull() ?: 100
            val demand = demandField.text.toString().toIntOrNull() ?: 80

            // Egyptian fraction allocation
            val zones = listOf("Premium", "Standard", "Economy", "Accessible")
            val fractions = BrahimCalculators.egyptianFraction(totalSpots, zones.size + 1)

            // Brahim-weighted allocation
            val allocation = mutableMapOf<String, Int>()
            val phi = BrahimConstants.PHI

            // Premium: B(1)/S of total
            allocation["Premium"] = (totalSpots * BrahimConstants.B(1) / BrahimConstants.SUM_CONSTANT.toDouble()).toInt()
            // Standard: B(3)/S of total
            allocation["Standard"] = (totalSpots * BrahimConstants.B(3) / BrahimConstants.SUM_CONSTANT.toDouble()).toInt()
            // Economy: B(5)/S of total
            allocation["Economy"] = (totalSpots * BrahimConstants.B(5) / BrahimConstants.SUM_CONSTANT.toDouble()).toInt()
            // Accessible: minimum 5% or B(1)
            allocation["Accessible"] = maxOf((totalSpots * 0.05).toInt(), BrahimConstants.B(1) / 5)

            // Remaining to standard
            val allocated = allocation.values.sum()
            allocation["Standard"] = allocation["Standard"]!! + (totalSpots - allocated)

            // Occupancy prediction
            val occupancy = demand.toDouble() / totalSpots * 100
            val turnover = BrahimConstants.PHI  // Average turnover rate

            resultText.text = buildString {
                append("PARKING ALLOCATION\n")
                append("Egyptian Fraction Method\n\n")
                append("Facility:\n")
                append("  Total spots: $totalSpots\n")
                append("  Expected demand: $demand vehicles\n")
                append("  Occupancy: ${String.format("%.1f", occupancy)}%\n\n")
                append("BRAHIM ALLOCATION:\n")
                allocation.forEach { (zone, spots) ->
                    val pct = spots.toDouble() / totalSpots * 100
                    append("  $zone: $spots spots (${String.format("%.1f", pct)}%)\n")
                }
                append("\nEGYPTIAN FRACTIONS:\n")
                append("  $totalSpots/${zones.size + 1} = ")
                append(fractions.joinToString(" + ") { "1/$it" })
                append("\n\nPRICING (Brahim ratios):\n")
                val basePrice = 5.0
                append("  Premium: $${String.format("%.2f", basePrice * phi)}/hr\n")
                append("  Standard: $${String.format("%.2f", basePrice)}/hr\n")
                append("  Economy: $${String.format("%.2f", basePrice / phi)}/hr\n")
                append("  Accessible: $${String.format("%.2f", basePrice * 0.5)}/hr\n\n")
                append("Turnover rate: ${String.format("%.2f", turnover)} vehicles/spot/day")
            }
        }
    }
}
