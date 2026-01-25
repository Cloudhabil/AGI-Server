package com.brahim.unified.security

import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.brahim.unified.R
import com.brahim.unified.core.BrahimConstants
import kotlin.math.abs

class KeyGenActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_input_calculator)

        title = "Key Generator"

        val inputField = findViewById<EditText>(R.id.inputField)
        val calculateBtn = findViewById<Button>(R.id.calculateButton)
        val resultText = findViewById<TextView>(R.id.resultText)

        inputField.hint = "Seed phrase or number"

        calculateBtn.setOnClickListener {
            val seed = inputField.text.toString()

            if (seed.isNotEmpty()) {
                val phi = BrahimConstants.PHI
                val beta = BrahimConstants.BETA_SECURITY

                // Generate key from seed using Brahim constants
                val seedHash = seed.hashCode().toLong() and 0x7FFFFFFF

                // 256-bit key generation (simplified demonstration)
                val keyParts = mutableListOf<String>()
                var current = seedHash.toDouble()

                for (i in 1..8) {
                    val bi = BrahimConstants.B(i.coerceIn(1, 10))
                    current = (current * phi + bi) % 0xFFFFFFFF
                    val part = String.format("%08X", current.toLong() and 0xFFFFFFFF)
                    keyParts.add(part)
                }

                val fullKey = keyParts.joinToString("")

                // Key strength analysis
                val entropy = seed.length * 4.7  // bits (rough estimate)
                val brahimStrength = (BrahimConstants.SUM_CONSTANT * phi).toInt()

                // Verification checksum
                val checksum = keyParts.sumOf { it.hashCode() } and 0xFFFF

                resultText.text = buildString {
                    append("BRAHIM KEY GENERATION\n")
                    append("φ-based Cryptographic Key\n\n")
                    append("SEED:\n")
                    append("  \"$seed\"\n")
                    append("  Hash: $seedHash\n\n")
                    append("GENERATED KEY (256-bit):\n")
                    keyParts.forEachIndexed { i, part ->
                        append("  ${i + 1}: $part\n")
                    }
                    append("\nFULL KEY:\n")
                    append("  ${fullKey.take(32)}...\n\n")
                    append("KEY PROPERTIES:\n")
                    append("  Length: ${fullKey.length * 4} bits\n")
                    append("  Entropy: ~${String.format("%.0f", entropy)} bits\n")
                    append("  Checksum: ${String.format("%04X", checksum)}\n\n")
                    append("BRAHIM DERIVATION:\n")
                    append("  φ = ${String.format("%.6f", phi)}\n")
                    append("  β = ${String.format("%.6f", beta)}\n")
                    append("  Strength: $brahimStrength bits\n\n")
                    append("Algorithm:\n")
                    append("  K[i] = (K[i-1] × φ + B(i)) mod 2³²\n\n")
                    append("WARNING: Demo only - use\n")
                    append("proper crypto in production")
                }
            } else {
                resultText.text = "Enter a seed phrase to generate a key"
            }
        }
    }
}
