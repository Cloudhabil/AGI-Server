package com.brahim.unified.planetary

import android.os.Bundle
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.brahim.unified.R
import com.brahim.unified.core.BrahimConstants
import kotlin.math.sqrt

class MarsActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_calculator)

        title = "Mars Habitat"

        val resultText = findViewById<TextView>(R.id.resultText)
        val formulaText = findViewById<TextView>(R.id.formulaText)
        val accuracyText = findViewById<TextView>(R.id.accuracyText)

        val phi = BrahimConstants.PHI
        val beta = BrahimConstants.BETA_SECURITY

        // Mars parameters
        val marsRadius = 3389.5  // km
        val marsGravity = 3.71  // m/s²
        val marsDayLength = 24.6  // hours
        val marsYear = 687  // Earth days

        // Brahim habitat design
        val domeRadius = BrahimConstants.B(3).toDouble()  // 60 meters
        val domeHeight = domeRadius / phi  // Golden ratio proportion
        val livingArea = kotlin.math.PI * domeRadius * domeRadius  // m²
        val volume = (2.0 / 3.0) * kotlin.math.PI * domeRadius * domeRadius * domeHeight

        // Life support using Brahim ratios
        val crewSize = BrahimConstants.B(1) / 3  // 9 people
        val o2PerPerson = BrahimConstants.B(2).toDouble() / 100  // 0.42 kg/day
        val waterPerPerson = BrahimConstants.B(3).toDouble() / 20  // 3 L/day
        val foodPerPerson = BrahimConstants.B(1).toDouble() / 15  // 1.8 kg/day

        resultText.text = buildString {
            append("MARS HABITAT DESIGN\n")
            append("Brahim Proportions\n\n")
            append("MARS PARAMETERS:\n")
            append("  Radius: $marsRadius km\n")
            append("  Gravity: $marsGravity m/s²\n")
            append("  Sol: $marsDayLength hours\n")
            append("  Year: $marsYear Earth days\n\n")
            append("DOME SPECIFICATIONS:\n")
            append("  Radius: ${String.format("%.1f", domeRadius)} m (B(3))\n")
            append("  Height: ${String.format("%.1f", domeHeight)} m (r/φ)\n")
            append("  Floor Area: ${String.format("%.0f", livingArea)} m²\n")
            append("  Volume: ${String.format("%.0f", volume)} m³\n\n")
            append("CREW: $crewSize people\n")
        }

        formulaText.text = buildString {
            append("LIFE SUPPORT (per person/day):\n\n")
            append("  Oxygen: ${String.format("%.2f", o2PerPerson)} kg\n")
            append("    (B(2)/100 = 42/100)\n\n")
            append("  Water: ${String.format("%.1f", waterPerPerson)} L\n")
            append("    (B(3)/20 = 60/20)\n\n")
            append("  Food: ${String.format("%.1f", foodPerPerson)} kg\n")
            append("    (B(1)/15 = 27/15)\n\n")
            append("DAILY TOTALS (crew of $crewSize):\n")
            append("  O2: ${String.format("%.1f", o2PerPerson * crewSize)} kg\n")
            append("  H2O: ${String.format("%.0f", waterPerPerson * crewSize)} L\n")
            append("  Food: ${String.format("%.1f", foodPerPerson * crewSize)} kg")
        }

        val missionDuration = BrahimConstants.B(10) * 3  // 561 days
        val totalO2 = o2PerPerson * crewSize * missionDuration
        val totalWater = waterPerPerson * crewSize * missionDuration
        val totalFood = foodPerPerson * crewSize * missionDuration

        accuracyText.text = buildString {
            append("MISSION: ${missionDuration} days\n")
            append("(B(10) × 3 = 187 × 3)\n\n")
            append("TOTAL SUPPLIES:\n")
            append("  Oxygen: ${String.format("%.0f", totalO2)} kg\n")
            append("  Water: ${String.format("%.0f", totalWater)} L\n")
            append("  Food: ${String.format("%.0f", totalFood)} kg\n\n")
            append("RECYCLING TARGETS:\n")
            append("  Water: ${String.format("%.0f", beta * 100)}% recovery\n")
            append("  O2: ${String.format("%.0f", (1/phi) * 100)}% from ISRU\n\n")
            append("Golden proportion (φ) ensures\n")
            append("optimal space utilization")
        }
    }
}
