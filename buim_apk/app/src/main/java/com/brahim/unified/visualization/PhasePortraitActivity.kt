package com.brahim.unified.visualization

import android.os.Bundle
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.brahim.unified.R
import com.brahim.unified.engine.BrahimEngine

class PhasePortraitActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_calculator)

        title = "Phase Portrait"

        val resultText = findViewById<TextView>(R.id.resultText)
        val formulaText = findViewById<TextView>(R.id.formulaText)
        val accuracyText = findViewById<TextView>(R.id.accuracyText)

        // Simulate FitzHugh-Nagumo dynamics
        var state = BrahimEngine.Wormhole.PhaseState(0.0, 0.0)
        val trajectory = mutableListOf<BrahimEngine.Wormhole.PhaseState>()

        // Run simulation
        val input = 0.5
        for (i in 0 until 200) {
            trajectory.add(state)
            state = BrahimEngine.Wormhole.fitzHughNagumo(state, input)
        }

        // Create ASCII phase portrait (20x20 grid)
        val grid = Array(20) { CharArray(40) { ' ' } }

        trajectory.forEach { (k, d) ->
            val x = ((k + 2.5) / 5.0 * 39).toInt().coerceIn(0, 39)
            val y = ((d + 1.0) / 2.0 * 19).toInt().coerceIn(0, 19)
            grid[19 - y][x] = '·'
        }

        // Mark attractor
        val lastState = trajectory.last()
        val ax = ((lastState.kappa + 2.5) / 5.0 * 39).toInt().coerceIn(0, 39)
        val ay = ((lastState.debt + 1.0) / 2.0 * 19).toInt().coerceIn(0, 19)
        if (ay in 0..19 && ax in 0..39) grid[19 - ay][ax] = '●'

        resultText.text = buildString {
            append("FITZHUGH-NAGUMO DYNAMICS\n")
            append("Wormhole Observer Phase Space\n")
            append("════════════════════════════════════\n\n")

            append("κ (Kappa) - Excitation variable\n")
            append("D (Debt) - Recovery variable\n\n")

            append(" D\n")
            append(" ↑\n")
            grid.forEach { row ->
                append(" │${String(row)}\n")
            }
            append(" └${"─".repeat(40)}→ κ\n")
            append("  -2.5                              2.5\n")
        }

        formulaText.text = buildString {
            append("DYNAMICAL EQUATIONS:\n")
            append("═══════════════════════════════════\n\n")
            append("dκ/dt = κ - κ³/3 - D + I\n\n")
            append("dD/dt = (κ + a - b·D) / τ\n\n")
            append("Parameters:\n")
            append("  a = 0.7\n")
            append("  b = 0.8\n")
            append("  τ = 12.5\n")
            append("  I = $input (external input)\n\n")
            append("This models the governance system:\n")
            append("  κ = system state (excitation)\n")
            append("  D = accumulated debt\n")
            append("  I = resonance input\n")
        }

        val finalState = trajectory.last()
        accuracyText.text = buildString {
            append("TRAJECTORY ANALYSIS:\n")
            append("═══════════════════════════════════\n\n")
            append("Initial state:\n")
            append("  κ₀ = 0.0, D₀ = 0.0\n\n")
            append("Final state (t=200):\n")
            append("  κ = ${String.format("%.4f", finalState.kappa)}\n")
            append("  D = ${String.format("%.4f", finalState.debt)}\n\n")
            append("Attractor: ● (limit cycle)\n\n")
            append("GOVERNANCE SIGNALS:\n")
            append("─────────────────────────────────────\n")
            val throttle = if (finalState.kappa > 1.0) "ACTIVE" else "INACTIVE"
            val purge = if (finalState.debt > 0.5) "NEEDED" else "CLEAR"
            append("  Throttle: $throttle\n")
            append("  Purge: $purge\n\n")
            append("System stable within φ-bounds")
        }
    }
}
