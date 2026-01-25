package com.brahim.unified.business

import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.brahim.unified.R
import com.brahim.unified.core.BrahimConstants
import com.brahim.unified.core.BrahimCalculators

class SalaryActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_dual_input)

        title = "Salary Hierarchy"

        val baseField = findViewById<EditText>(R.id.inputField1)
        val levelsField = findViewById<EditText>(R.id.inputField2)
        val calculateBtn = findViewById<Button>(R.id.calculateButton)
        val resultText = findViewById<TextView>(R.id.resultText)

        baseField.hint = "Base Salary"
        levelsField.hint = "Number of Levels (1-10)"

        calculateBtn.setOnClickListener {
            val baseSalary = baseField.text.toString().toDoubleOrNull() ?: 50000.0
            val levels = levelsField.text.toString().toIntOrNull()?.coerceIn(1, 10) ?: 5

            // Calculate salaries using Brahim multipliers
            val salaries = (1..levels).map { level ->
                val multiplier = BrahimCalculators.salaryMultiplier(level)
                val salary = baseSalary * multiplier
                Triple(level, multiplier, salary)
            }

            val healthyRatio = BrahimCalculators.healthySalaryRatio()
            val actualRatio = salaries.last().third / salaries.first().third

            resultText.text = buildString {
                append("SALARY HIERARCHY\n")
                append("Brahim Fair Compensation\n\n")
                append("Base Salary: $${String.format("%,.0f", baseSalary)}\n")
                append("Levels: $levels\n\n")
                append("SALARY STRUCTURE:\n")
                salaries.forEach { (level, mult, salary) ->
                    append("  Level $level: $${String.format("%,.0f", salary)}")
                    append(" (${String.format("%.2f", mult)}x)\n")
                }
                append("\nRANGE ANALYSIS:\n")
                append("  Lowest: $${String.format("%,.0f", salaries.first().third)}\n")
                append("  Highest: $${String.format("%,.0f", salaries.last().third)}\n")
                append("  Actual ratio: ${String.format("%.2f", actualRatio)}x\n\n")
                append("BRAHIM BENCHMARK:\n")
                append("  Healthy ratio: ${String.format("%.2f", healthyRatio)}x\n")
                append("  (B(10)/B(1) = 187/27)\n\n")
                val status = when {
                    actualRatio <= healthyRatio -> "FAIR - Within healthy range"
                    actualRatio <= healthyRatio * 1.5 -> "MODERATE - Acceptable"
                    else -> "WARNING - May cause issues"
                }
                append("  Status: $status\n\n")
                append("Brahim Multipliers:\n")
                append("  B(n)/B(1) ensures natural\n")
                append("  progression based on sequence")
            }
        }
    }
}
