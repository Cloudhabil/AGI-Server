package com.brahim.unified.math

import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.brahim.unified.R
import com.brahim.unified.core.BrahimConstants

class MirrorActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_input_calculator)

        title = "Mirror Operator"

        val inputField = findViewById<EditText>(R.id.inputField)
        val calculateBtn = findViewById<Button>(R.id.calculateButton)
        val resultText = findViewById<TextView>(R.id.resultText)

        inputField.hint = "Enter a number"

        calculateBtn.setOnClickListener {
            val input = inputField.text.toString().toDoubleOrNull()
            if (input != null) {
                val mirror = BrahimConstants.mirror(input)
                val isPair = (input + mirror) == BrahimConstants.SUM_CONSTANT.toDouble()

                resultText.text = buildString {
                    append("Input: $input\n")
                    append("Mirror M($input) = ${BrahimConstants.SUM_CONSTANT} - $input = $mirror\n\n")
                    append("Sum: $input + $mirror = ${input + mirror}\n")
                    append("Is Mirror Pair: ${if (isPair) "YES" else "NO"}\n\n")
                    append("Brahim Sequence Mirror Pairs:\n")
                    for (i in 1..5) {
                        val b = BrahimConstants.B(i)
                        val m = BrahimConstants.B(11 - i)
                        append("B($i) + B(${11-i}) = $b + $m = ${b + m}\n")
                    }
                }
            } else {
                resultText.text = "Please enter a valid number"
            }
        }
    }
}
