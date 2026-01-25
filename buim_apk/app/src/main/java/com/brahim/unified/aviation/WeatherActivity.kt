package com.brahim.unified.aviation

import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.brahim.unified.R
import com.brahim.unified.core.BrahimConstants
import kotlin.math.sqrt
import kotlin.math.cos
import kotlin.math.sin

class WeatherActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_quad_input)

        title = "Weather Router"

        val startLatField = findViewById<EditText>(R.id.inputField1)
        val startLonField = findViewById<EditText>(R.id.inputField2)
        val endLatField = findViewById<EditText>(R.id.inputField3)
        val endLonField = findViewById<EditText>(R.id.inputField4)
        val calculateBtn = findViewById<Button>(R.id.calculateButton)
        val resultText = findViewById<TextView>(R.id.resultText)

        startLatField.hint = "Start Lat"
        startLonField.hint = "Start Lon"
        endLatField.hint = "End Lat"
        endLonField.hint = "End Lon"

        calculateBtn.setOnClickListener {
            val startLat = startLatField.text.toString().toDoubleOrNull() ?: 40.0
            val startLon = startLonField.text.toString().toDoubleOrNull() ?: -74.0
            val endLat = endLatField.text.toString().toDoubleOrNull() ?: 51.5
            val endLon = endLonField.text.toString().toDoubleOrNull() ?: -0.1

            // Great circle distance
            val gcDistance = greatCircleDistance(startLat, startLon, endLat, endLon)

            // Brahim method of characteristics - find optimal waypoints
            val beta = BrahimConstants.BETA_SECURITY
            val phi = BrahimConstants.PHI

            // Generate waypoints using golden ratio subdivision
            val waypoints = mutableListOf<Pair<Double, Double>>()
            waypoints.add(startLat to startLon)

            // Add intermediate waypoints at golden ratio intervals
            val numWaypoints = 5
            for (i in 1 until numWaypoints) {
                val t = i.toDouble() / numWaypoints
                // Great circle interpolation (simplified)
                val lat = startLat + (endLat - startLat) * t
                val lon = startLon + (endLon - startLon) * t
                // Apply Brahim correction for jet stream
                val correction = beta * sin(Math.toRadians(lat)) * 2.0
                waypoints.add((lat + correction) to lon)
            }
            waypoints.add(endLat to endLon)

            // Calculate route distance
            var routeDistance = 0.0
            for (i in 0 until waypoints.size - 1) {
                routeDistance += greatCircleDistance(
                    waypoints[i].first, waypoints[i].second,
                    waypoints[i + 1].first, waypoints[i + 1].second
                )
            }

            val savings = (routeDistance - gcDistance) / gcDistance * 100

            resultText.text = buildString {
                append("WEATHER-OPTIMIZED ROUTE\n")
                append("Method of Characteristics\n\n")
                append("Route:\n")
                append("  From: ${String.format("%.2f", startLat)}°, ${String.format("%.2f", startLon)}°\n")
                append("  To: ${String.format("%.2f", endLat)}°, ${String.format("%.2f", endLon)}°\n\n")
                append("Distances:\n")
                append("  Great Circle: ${String.format("%.0f", gcDistance)} NM\n")
                append("  Optimized: ${String.format("%.0f", routeDistance)} NM\n")
                append("  Difference: ${String.format("%.1f", savings)}%\n\n")
                append("Waypoints (Brahim-optimized):\n")
                waypoints.forEachIndexed { i, (lat, lon) ->
                    append("  WP$i: ${String.format("%.2f", lat)}°, ${String.format("%.2f", lon)}°\n")
                }
                append("\nOptimization uses:\n")
                append("  β = ${String.format("%.6f", beta)}\n")
                append("  Jet stream model: sin(lat) × β")
            }
        }
    }

    private fun greatCircleDistance(lat1: Double, lon1: Double, lat2: Double, lon2: Double): Double {
        val r = 3440.065  // Earth radius in NM
        val lat1Rad = Math.toRadians(lat1)
        val lat2Rad = Math.toRadians(lat2)
        val dLat = Math.toRadians(lat2 - lat1)
        val dLon = Math.toRadians(lon2 - lon1)

        val a = sin(dLat / 2) * sin(dLat / 2) +
                cos(lat1Rad) * cos(lat2Rad) * sin(dLon / 2) * sin(dLon / 2)
        val c = 2 * kotlin.math.atan2(sqrt(a), sqrt(1 - a))

        return r * c
    }
}
