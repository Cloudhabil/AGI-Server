package com.brahim.unified.solvers

import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.brahim.unified.R
import com.brahim.unified.core.BrahimConstants

class PDEActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_dual_input)

        title = "PDE Characteristics"

        val waveSpeedField = findViewById<EditText>(R.id.inputField1)
        val initialField = findViewById<EditText>(R.id.inputField2)
        val calculateBtn = findViewById<Button>(R.id.calculateButton)
        val resultText = findViewById<TextView>(R.id.resultText)

        waveSpeedField.hint = "Wave Speed c"
        initialField.hint = "Initial amplitude A"

        calculateBtn.setOnClickListener {
            val c = waveSpeedField.text.toString().toDoubleOrNull() ?: 1.0
            val A = initialField.text.toString().toDoubleOrNull() ?: 1.0

            val beta = BrahimConstants.BETA_SECURITY
            val gamma = BrahimConstants.GAMMA_DAMPING

            // Method of Characteristics for wave equation
            // u_t + c*u_x = 0 -> characteristics: x = x0 + c*t

            // Generate characteristic curves
            val times = listOf(0.0, 0.5, 1.0, 2.0, 5.0)
            val x0Values = listOf(-2.0, -1.0, 0.0, 1.0, 2.0)

            // Characteristics with Brahim damping
            val characteristics = x0Values.map { x0 ->
                times.map { t ->
                    val x = x0 + c * t
                    val u = A * kotlin.math.exp(-gamma * t) * kotlin.math.cos(beta * x)
                    Triple(t, x, u)
                }
            }

            resultText.text = buildString {
                append("METHOD OF CHARACTERISTICS\n")
                append("Wave Equation with Damping\n\n")
                append("PDE: ∂u/∂t + c·∂u/∂x = -γu\n\n")
                append("Parameters:\n")
                append("  Wave speed c = $c\n")
                append("  Amplitude A = $A\n")
                append("  Damping γ = ${String.format("%.6f", gamma)}\n")
                append("  Wavenumber β = ${String.format("%.6f", beta)}\n\n")
                append("CHARACTERISTICS:\n")
                append("  dx/dt = c  →  x = x₀ + ct\n\n")
                append("SOLUTION along characteristics:\n")
                append("  u(x,t) = A·e^(-γt)·cos(βx)\n\n")
                append("SAMPLE VALUES:\n")
                characteristics.forEachIndexed { i, curve ->
                    val x0 = x0Values[i]
                    append("x₀ = ${String.format("%+.1f", x0)}:\n")
                    curve.take(3).forEach { (t, x, u) ->
                        append("  t=${String.format("%.1f", t)}: ")
                        append("x=${String.format("%+.2f", x)}, ")
                        append("u=${String.format("%+.4f", u)}\n")
                    }
                }
                append("\nBRAHIM INSIGHT:\n")
                append("  γ = 1/φ⁴ provides natural damping\n")
                append("  β = √5-2 sets oscillation scale")
            }
        }
    }
}
