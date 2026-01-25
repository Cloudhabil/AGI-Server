package com.brahim.unified.traffic

import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.brahim.unified.R
import com.brahim.unified.core.BrahimConstants

class RouteActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_dual_input)

        title = "Route Optimizer"

        val distanceField = findViewById<EditText>(R.id.inputField1)
        val trafficField = findViewById<EditText>(R.id.inputField2)
        val calculateBtn = findViewById<Button>(R.id.calculateButton)
        val resultText = findViewById<TextView>(R.id.resultText)

        distanceField.hint = "Direct Distance (km)"
        trafficField.hint = "Congestion Level (0-10)"

        calculateBtn.setOnClickListener {
            val distance = distanceField.text.toString().toDoubleOrNull() ?: 10.0
            val congestion = trafficField.text.toString().toDoubleOrNull() ?: 5.0

            val phi = BrahimConstants.PHI
            val beta = BrahimConstants.BETA_SECURITY

            // Route options with Brahim optimization
            val routes = listOf(
                RouteOption("Direct", distance, congestion, 1.0),
                RouteOption("Highway", distance * 1.2, congestion * 0.5, 1.3),
                RouteOption("Local Streets", distance * 0.9, congestion * 1.5, 0.6),
                RouteOption("Brahim Optimal", distance * phi * beta * 2, congestion * beta, phi * 0.8)
            )

            // Calculate travel times
            val results = routes.map { route ->
                val baseSpeed = 50.0  // km/h base speed
                val congestionFactor = 1.0 / (1.0 + route.congestion * 0.1)
                val effectiveSpeed = baseSpeed * route.speedFactor * congestionFactor
                val time = route.distance / effectiveSpeed * 60  // minutes
                route to time
            }.sortedBy { it.second }

            val best = results.first()
            val direct = results.find { it.first.name == "Direct" }!!

            resultText.text = buildString {
                append("ROUTE OPTIMIZATION\n")
                append("Golden Ratio Pathfinding\n\n")
                append("Input:\n")
                append("  Direct distance: ${String.format("%.1f", distance)} km\n")
                append("  Congestion: ${String.format("%.1f", congestion)}/10\n\n")
                append("ROUTE OPTIONS:\n\n")
                results.forEach { (route, time) ->
                    val marker = if (route == best.first) " <-- BEST" else ""
                    val saving = ((direct.second - time) / direct.second * 100)
                    append("${route.name}$marker\n")
                    append("  Distance: ${String.format("%.1f", route.distance)} km\n")
                    append("  Time: ${String.format("%.0f", time)} min\n")
                    if (route != direct.first) {
                        append("  vs Direct: ${String.format("%+.0f", -saving)}%\n")
                    }
                    append("\n")
                }
                append("BRAHIM FACTORS:\n")
                append("  φ = ${String.format("%.4f", phi)}\n")
                append("  β = ${String.format("%.4f", beta)}\n")
                append("  Wormhole compression: ${String.format("%.1f", beta * 100)}%")
            }
        }
    }

    data class RouteOption(val name: String, val distance: Double, val congestion: Double, val speedFactor: Double)
}
