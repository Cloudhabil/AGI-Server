package com.brahim.unified.business

import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.brahim.unified.R
import com.brahim.unified.core.BrahimConstants
import com.brahim.unified.core.BrahimCalculators

class AllocatorActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_dual_input)

        title = "Resource Allocator"

        val budgetField = findViewById<EditText>(R.id.inputField1)
        val departmentsField = findViewById<EditText>(R.id.inputField2)
        val calculateBtn = findViewById<Button>(R.id.calculateButton)
        val resultText = findViewById<TextView>(R.id.resultText)

        budgetField.hint = "Total Budget"
        departmentsField.hint = "Number of Departments"

        calculateBtn.setOnClickListener {
            val budget = budgetField.text.toString().toDoubleOrNull()
            val departments = departmentsField.text.toString().toIntOrNull()

            if (budget != null && departments != null && departments > 0 && departments <= 10) {
                val allocations = mutableListOf<Pair<String, Double>>()
                var remaining = budget

                for (i in 1..departments) {
                    val ratio = BrahimCalculators.salaryMultiplier(departments - i + 1)
                    val totalRatio = (1..departments).sumOf { BrahimCalculators.salaryMultiplier(it) }
                    val allocation = budget * ratio / totalRatio
                    allocations.add("Dept $i" to allocation)
                }

                val healthyRatio = BrahimCalculators.healthySalaryRatio()

                resultText.text = buildString {
                    append("BUDGET ALLOCATION\n")
                    append("Egyptian Fraction Method\n\n")
                    append("Total Budget: ${String.format("%.2f", budget)}\n")
                    append("Departments: $departments\n\n")
                    append("Allocations:\n")
                    allocations.forEachIndexed { i, (name, amount) ->
                        val pct = amount / budget * 100
                        append("$name: ${String.format("%.2f", amount)} (${String.format("%.1f", pct)}%)\n")
                    }
                    append("\nTotal: ${String.format("%.2f", allocations.sumOf { it.second })}\n\n")
                    append("Healthy Ratio (B10/B1): ${String.format("%.2f", healthyRatio)}x")
                }
            } else {
                resultText.text = "Enter valid budget and departments (1-10)"
            }
        }
    }
}
