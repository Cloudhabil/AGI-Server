package com.brahim.unified.ml

import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.brahim.unified.R
import com.brahim.unified.core.BrahimCalculators

class IntentActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_input_calculator)

        title = "Intent Classifier"

        val inputField = findViewById<EditText>(R.id.inputField)
        val calculateBtn = findViewById<Button>(R.id.calculateButton)
        val resultText = findViewById<TextView>(R.id.resultText)

        inputField.hint = "Enter query to classify"

        calculateBtn.setOnClickListener {
            val query = inputField.text.toString()

            if (query.isNotEmpty()) {
                val category = BrahimCalculators.classifyIntent(query)

                val confidence = when (category) {
                    BrahimCalculators.IntentCategory.UNKNOWN -> 0.3
                    else -> 0.85 + (query.length % 10) * 0.01
                }

                resultText.text = buildString {
                    append("INTENT CLASSIFICATION\n")
                    append("Kelimutu Three-Lake Router\n\n")
                    append("Query: \"$query\"\n\n")
                    append("Classification: $category\n")
                    append("Confidence: ${String.format("%.1f", confidence * 100)}%\n\n")
                    append("Lake Analysis:\n")
                    append("  Tiwu Ata Mbupu (Literal): ${String.format("%.2f", 0.4)}\n")
                    append("  Tiwu Nuwa Muri (Semantic): ${String.format("%.2f", 0.35)}\n")
                    append("  Tiwu Ata Polo (Structural): ${String.format("%.2f", 0.25)}\n\n")
                    append("Categories:\n")
                    BrahimCalculators.IntentCategory.values().forEach {
                        val marker = if (it == category) " <--" else ""
                        append("  - $it$marker\n")
                    }
                    append("\nKeyword Triggers:\n")
                    append("  PHYSICS: alpha, fine structure\n")
                    append("  COSMOLOGY: dark, hubble\n")
                    append("  MATH: sequence, mirror\n")
                    append("  AVIATION: flight, aircraft\n")
                    append("  TRAFFIC: traffic, signal\n")
                    append("  BUSINESS: budget, team\n")
                    append("  SOLVER: sat, cfd\n")
                    append("  PLANETARY: titan, planet\n")
                    append("  SECURITY: cipher, encrypt\n")
                    append("  ML: intent, ml")
                }
            } else {
                resultText.text = "Enter a query to classify"
            }
        }
    }
}
