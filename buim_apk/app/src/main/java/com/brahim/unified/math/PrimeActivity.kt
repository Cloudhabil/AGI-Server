package com.brahim.unified.math

import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.brahim.unified.R
import com.brahim.unified.core.BrahimConstants

class PrimeActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_input_calculator)

        title = "Prime Factorization"

        val inputField = findViewById<EditText>(R.id.inputField)
        val calculateBtn = findViewById<Button>(R.id.calculateButton)
        val resultText = findViewById<TextView>(R.id.resultText)

        inputField.hint = "Number to factorize (or 'B' for sequence)"

        calculateBtn.setOnClickListener {
            val input = inputField.text.toString().trim()

            if (input.equals("B", ignoreCase = true) || input.equals("sequence", ignoreCase = true)) {
                // Factorize entire Brahim sequence
                resultText.text = buildString {
                    append("BRAHIM SEQUENCE FACTORIZATION\n\n")
                    for (i in 1..10) {
                        val bn = BrahimConstants.B(i)
                        val factors = factorize(bn)
                        val isPrime = factors.size == 1 && factors[0] == bn
                        append("B($i) = $bn")
                        if (isPrime) {
                            append(" [PRIME]\n")
                        } else {
                            append(" = ${factors.joinToString(" × ")}\n")
                        }
                    }
                    append("\nPrime elements: ")
                    val primes = (1..10).filter { isPrime(BrahimConstants.B(it)) }
                        .map { "B($it)=${BrahimConstants.B(it)}" }
                    append(primes.joinToString(", "))
                    append("\n\nSum S = 214 = ${factorize(214).joinToString(" × ")}")
                    append("\nCenter C = 107 [PRIME]")
                }
            } else {
                val n = input.toIntOrNull()
                if (n != null && n > 1) {
                    val factors = factorize(n)
                    val isPrime = factors.size == 1 && factors[0] == n

                    resultText.text = buildString {
                        append("PRIME FACTORIZATION\n\n")
                        append("Number: $n\n\n")
                        if (isPrime) {
                            append("$n is PRIME\n\n")
                        } else {
                            append("$n = ${factors.joinToString(" × ")}\n\n")
                        }
                        append("Factor count: ${factors.size}\n")
                        append("Unique factors: ${factors.toSet().size}\n\n")

                        // Check if related to Brahim
                        val brahimMatch = (1..10).find { BrahimConstants.B(it) == n }
                        if (brahimMatch != null) {
                            append("This is B($brahimMatch) in Brahim sequence!\n")
                            append("Mirror: ${BrahimConstants.mirror(n)}")
                        } else {
                            append("Not in Brahim sequence\n")
                            append("Closest B(i): ${findClosest(n)}")
                        }
                    }
                } else {
                    resultText.text = "Enter a number > 1\nor 'B' for sequence analysis"
                }
            }
        }
    }

    private fun factorize(n: Int): List<Int> {
        val factors = mutableListOf<Int>()
        var num = n
        var d = 2
        while (d * d <= num) {
            while (num % d == 0) {
                factors.add(d)
                num /= d
            }
            d++
        }
        if (num > 1) factors.add(num)
        return factors
    }

    private fun isPrime(n: Int): Boolean {
        if (n < 2) return false
        if (n == 2) return true
        if (n % 2 == 0) return false
        var i = 3
        while (i * i <= n) {
            if (n % i == 0) return false
            i += 2
        }
        return true
    }

    private fun findClosest(n: Int): String {
        var minDiff = Int.MAX_VALUE
        var closest = 1
        for (i in 1..10) {
            val diff = kotlin.math.abs(BrahimConstants.B(i) - n)
            if (diff < minDiff) {
                minDiff = diff
                closest = i
            }
        }
        return "B($closest) = ${BrahimConstants.B(closest)} (diff: $minDiff)"
    }
}
