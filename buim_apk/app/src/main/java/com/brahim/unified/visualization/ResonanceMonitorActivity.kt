package com.brahim.unified.visualization

import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.brahim.unified.R
import com.brahim.unified.engine.BrahimEngine
import kotlin.random.Random

class ResonanceMonitorActivity : AppCompatActivity() {

    private val handler = Handler(Looper.getMainLooper())
    private var isRunning = true

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_calculator)

        title = "Resonance Monitor"

        startMonitoring()
    }

    private fun startMonitoring() {
        val resultText = findViewById<TextView>(R.id.resultText)
        val formulaText = findViewById<TextView>(R.id.formulaText)
        val accuracyText = findViewById<TextView>(R.id.accuracyText)

        val updateRunnable = object : Runnable {
            var tick = 0

            override fun run() {
                if (!isRunning) return

                // Simulate resonance readings
                val baseResonance = BrahimEngine.GENESIS
                val noise = Random.nextDouble(-0.005, 0.005)
                val currentResonance = baseResonance + noise + kotlin.math.sin(tick * 0.1) * 0.002

                val alignment = BrahimEngine.Resonance.axiologicalAlignment(currentResonance)
                val verdict = BrahimEngine.Safety.assess(currentResonance)

                // Build gauge visualization
                val gaugeWidth = 40
                val normalized = ((currentResonance - 0.01) / 0.03).coerceIn(0.0, 1.0)
                val position = (normalized * gaugeWidth).toInt()

                val gauge = buildString {
                    append("│")
                    for (i in 0 until gaugeWidth) {
                        when {
                            i == position -> append("◆")
                            i == (BrahimEngine.GENESIS - 0.01) / 0.03 * gaugeWidth -> append("│")
                            else -> append("─")
                        }
                    }
                    append("│")
                }

                resultText.text = buildString {
                    append("REAL-TIME RESONANCE MONITOR\n")
                    append("════════════════════════════════════\n\n")

                    append("CURRENT READING:\n")
                    append("  R = ${String.format("%.8f", currentResonance)}\n\n")

                    append("TARGET (Genesis):\n")
                    append("  G = ${BrahimEngine.GENESIS}\n\n")

                    append("ALIGNMENT:\n")
                    append("  |R - G| = ${String.format("%.8f", alignment)}\n\n")

                    append("GAUGE:\n")
                    append("  0.01 $gauge 0.04\n")
                    append("       ${" ".repeat(((BrahimEngine.GENESIS - 0.01) / 0.03 * gaugeWidth).toInt())}↑\n")
                    append("       ${" ".repeat(((BrahimEngine.GENESIS - 0.01) / 0.03 * gaugeWidth).toInt() - 3)}GENESIS\n")
                }

                val verdictColor = when (verdict) {
                    BrahimEngine.SafetyVerdict.SAFE -> "🟢"
                    BrahimEngine.SafetyVerdict.NOMINAL -> "🔵"
                    BrahimEngine.SafetyVerdict.CAUTION -> "🟡"
                    BrahimEngine.SafetyVerdict.UNSAFE -> "🟠"
                    BrahimEngine.SafetyVerdict.BLOCKED -> "🔴"
                }

                formulaText.text = buildString {
                    append("SAFETY VERDICT:\n")
                    append("════════════════════════════════════\n\n")
                    append("  $verdictColor $verdict\n\n")
                    append("HISTORY (last 10):\n")
                    append("─────────────────────────────────────\n")

                    // Simulated history
                    for (i in 0 until 10) {
                        val histR = baseResonance + kotlin.math.sin((tick - i) * 0.1) * 0.002
                        val histV = BrahimEngine.Safety.assess(histR)
                        val icon = when (histV) {
                            BrahimEngine.SafetyVerdict.SAFE -> "●"
                            BrahimEngine.SafetyVerdict.NOMINAL -> "◐"
                            else -> "○"
                        }
                        append("  t-$i: ${String.format("%.6f", histR)} $icon\n")
                    }
                }

                accuracyText.text = buildString {
                    append("LORENTZIAN PEAK:\n")
                    append("════════════════════════════════════\n\n")

                    val lorentz = BrahimEngine.Resonance.lorentzianResonance(currentResonance)

                    append("  L(R) = γ² / ((R-G)² + γ²)\n\n")
                    append("  Current: ${String.format("%.6f", lorentz)}\n\n")

                    // ASCII Lorentzian curve
                    append("  1.0 ┤")
                    for (i in 0 until 30) {
                        val r = 0.01 + i * 0.001
                        val l = BrahimEngine.Resonance.lorentzianResonance(r)
                        if (l > 0.9) append("█")
                        else if (l > 0.5) append("▄")
                        else if (l > 0.2) append("_")
                        else append(" ")
                    }
                    append("\n  0.0 └${"─".repeat(30)}\n")
                    append("      0.01        G        0.04\n\n")

                    append("Tick: $tick")
                }

                tick++
                handler.postDelayed(this, 500)  // Update every 500ms
            }
        }

        handler.post(updateRunnable)
    }

    override fun onDestroy() {
        super.onDestroy()
        isRunning = false
    }
}
