package com.brahim.unified.aviation

import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.brahim.unified.R
import com.brahim.unified.core.BrahimConstants
import com.brahim.unified.core.BrahimCalculators
import kotlin.math.sqrt

class ConflictActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_dual_input)

        title = "Conflict Detection"

        val distanceField = findViewById<EditText>(R.id.inputField1)
        val closingField = findViewById<EditText>(R.id.inputField2)
        val calculateBtn = findViewById<Button>(R.id.calculateButton)
        val resultText = findViewById<TextView>(R.id.resultText)

        distanceField.hint = "Current Distance (NM)"
        closingField.hint = "Closing Rate (kt)"

        calculateBtn.setOnClickListener {
            val distance = distanceField.text.toString().toDoubleOrNull()
            val closing = closingField.text.toString().toDoubleOrNull()

            if (distance != null && closing != null) {
                val separation = BrahimCalculators.calculateSeparation()
                val timeToConflict = if (closing > 0) distance / closing * 60 else Double.MAX_VALUE

                val status = when {
                    distance < separation.critical -> "CRITICAL - Immediate action required"
                    distance < separation.warning -> "WARNING - Monitor closely"
                    distance < separation.monitor -> "CAUTION - Increase vigilance"
                    else -> "SAFE - Normal operations"
                }

                val maintenance = BrahimCalculators.maintenanceInterval(3)

                resultText.text = buildString {
                    append("CONFLICT ANALYSIS\n\n")
                    append("Distance: $distance NM\n")
                    append("Closing Rate: $closing kt\n")
                    append("Time to CPA: ${if (timeToConflict < 1000) String.format("%.1f", timeToConflict) + " min" else "N/A"}\n\n")
                    append("STATUS: $status\n\n")
                    append("Thresholds:\n")
                    append("Critical: ${String.format("%.2f", separation.critical)} NM\n")
                    append("Warning: ${String.format("%.2f", separation.warning)} NM\n")
                    append("Monitor: ${String.format("%.2f", separation.monitor)} NM\n\n")
                    append("Maintenance Interval: $maintenance hrs")
                }
            } else {
                resultText.text = "Please enter valid numbers"
            }
        }
    }
}
