package com.brahim.unified.security

import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.brahim.unified.R
import com.brahim.unified.core.BrahimConstants
import com.brahim.unified.core.BrahimCalculators
import kotlin.math.roundToInt

class CipherActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_input_calculator)

        title = "Wormhole Cipher"

        val inputField = findViewById<EditText>(R.id.inputField)
        val calculateBtn = findViewById<Button>(R.id.calculateButton)
        val resultText = findViewById<TextView>(R.id.resultText)

        inputField.hint = "Text to encrypt"

        calculateBtn.setOnClickListener {
            val plaintext = inputField.text.toString()

            if (plaintext.isNotEmpty()) {
                val beta = BrahimConstants.BETA_SECURITY
                val encrypted = encrypt(plaintext, beta)
                val decrypted = decrypt(encrypted, beta)
                val compression = BrahimCalculators.compressionRatio()

                val resonance = BrahimConstants.resonance(
                    plaintext.map { it.code.toDouble() / 256 },
                    plaintext.indices.map { it.toDouble() }
                )
                val verdict = BrahimCalculators.assessSafety(resonance)

                resultText.text = buildString {
                    append("WORMHOLE CIPHER\n")
                    append("Beta-Based Encryption\n\n")
                    append("Plaintext: $plaintext\n")
                    append("Encrypted: $encrypted\n")
                    append("Decrypted: $decrypted\n\n")
                    append("Security Parameters:\n")
                    append("  Beta: ${String.format("%.10f", beta)}\n")
                    append("  Compression: ${String.format("%.2f", compression * 100)}%\n")
                    append("  Resonance: ${String.format("%.6f", resonance)}\n")
                    append("  Safety Verdict: $verdict\n\n")
                    append("Properties:\n")
                    append("  beta^2 + 4*beta - 1 = 0\n")
                    append("  alpha/beta = phi\n")
                    append("  Wormhole distance = d * beta")
                }
            } else {
                resultText.text = "Enter text to encrypt"
            }
        }
    }

    private fun encrypt(text: String, beta: Double): String {
        return text.map { c ->
            val shifted = ((c.code * (1 + beta)).roundToInt() % 128)
            if (shifted in 32..126) shifted.toChar() else ((shifted % 95) + 32).toChar()
        }.joinToString("")
    }

    private fun decrypt(text: String, beta: Double): String {
        return text.map { c ->
            val shifted = ((c.code / (1 + beta)).roundToInt())
            if (shifted in 32..126) shifted.toChar() else ((shifted % 95) + 32).toChar()
        }.joinToString("")
    }
}
