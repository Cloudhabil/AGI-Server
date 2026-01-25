package com.brahim.unified.math

import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.brahim.unified.R
import com.brahim.unified.core.BrahimCalculators

class EgyptianActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_dual_input)

        title = "Egyptian Fractions"

        val numeratorField = findViewById<EditText>(R.id.inputField1)
        val denominatorField = findViewById<EditText>(R.id.inputField2)
        val calculateBtn = findViewById<Button>(R.id.calculateButton)
        val resultText = findViewById<TextView>(R.id.resultText)

        numeratorField.hint = "Numerator"
        denominatorField.hint = "Denominator"

        calculateBtn.setOnClickListener {
            val num = numeratorField.text.toString().toIntOrNull()
            val den = denominatorField.text.toString().toIntOrNull()

            if (num != null && den != null && den > 0 && num > 0) {
                val fractions = BrahimCalculators.egyptianFraction(num, den)

                resultText.text = buildString {
                    append("Egyptian Fraction Decomposition\n\n")
                    append("$num/$den = ")
                    append(fractions.mapIndexed { i, d -> "1/$d" }.joinToString(" + "))
                    append("\n\n")
                    append("Unit Fractions: ${fractions.size}\n")
                    append("Denominators: ${fractions.joinToString(", ")}\n\n")
                    append("Applications:\n")
                    append("- Fair resource division\n")
                    append("- Task scheduling\n")
                    append("- Budget allocation\n")
                    append("- Load balancing")
                }
            } else {
                resultText.text = "Please enter valid positive integers"
            }
        }
    }
}
