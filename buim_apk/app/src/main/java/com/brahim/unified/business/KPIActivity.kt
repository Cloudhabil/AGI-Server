package com.brahim.unified.business

import android.os.Bundle
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.brahim.unified.R
import com.brahim.unified.core.BrahimConstants

class KPIActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_calculator)

        title = "KPI Dashboard"

        val resultText = findViewById<TextView>(R.id.resultText)
        val formulaText = findViewById<TextView>(R.id.formulaText)
        val accuracyText = findViewById<TextView>(R.id.accuracyText)

        // Brahim-derived KPI benchmarks
        val kpis = listOf(
            KPI("Customer Satisfaction", BrahimConstants.B(10).toDouble() / 2, 95.0, "%"),
            KPI("Employee Engagement", BrahimConstants.B(8).toDouble() / 2, 78.0, "%"),
            KPI("Revenue Growth", BrahimConstants.B(1).toDouble() / 2, 15.0, "%"),
            KPI("Profit Margin", BrahimConstants.B(2).toDouble() / 2, 22.0, "%"),
            KPI("Market Share", BrahimConstants.B(3).toDouble() / 3, 18.0, "%"),
            KPI("Quality Score", BrahimConstants.B(9).toDouble() / 2, 88.0, "%"),
            KPI("On-Time Delivery", BrahimConstants.B(7).toDouble() / 1.5, 92.0, "%"),
            KPI("NPS Score", BrahimConstants.B(4).toDouble() / 1.5, 52.0, "pts")
        )

        val phi = BrahimConstants.PHI

        resultText.text = buildString {
            append("KPI BENCHMARKS\n")
            append("Brahim Sequence Targets\n\n")
            kpis.forEach { kpi ->
                val ratio = kpi.actual / kpi.target * 100
                val status = when {
                    ratio >= 100 -> "●"  // Green
                    ratio >= 80 -> "◐"   // Yellow
                    else -> "○"          // Red
                }
                append("$status ${kpi.name}\n")
                append("  Target: ${String.format("%.1f", kpi.target)}${kpi.unit}\n")
                append("  Actual: ${String.format("%.1f", kpi.actual)}${kpi.unit}\n")
                append("  ${String.format("%.0f", ratio)}% of target\n\n")
            }
        }

        formulaText.text = buildString {
            append("BRAHIM DERIVATIONS:\n\n")
            append("Customer Sat = B(10)/2\n")
            append("  = 187/2 = 93.5%\n\n")
            append("Engagement = B(8)/2\n")
            append("  = 154/2 = 77%\n\n")
            append("Revenue = B(1)/2\n")
            append("  = 27/2 = 13.5%\n\n")
            append("Quality = B(9)/2\n")
            append("  = 172/2 = 86%\n\n")
            append("Golden ratio scaling:\n")
            append("φ = ${String.format("%.4f", phi)}")
        }

        val overallScore = kpis.map { it.actual / it.target }.average() * 100

        accuracyText.text = buildString {
            append("OVERALL PERFORMANCE:\n\n")
            append("Score: ${String.format("%.1f", overallScore)}%\n\n")
            val rating = when {
                overallScore >= 95 -> "EXCEPTIONAL"
                overallScore >= 85 -> "EXCELLENT"
                overallScore >= 75 -> "GOOD"
                overallScore >= 65 -> "FAIR"
                else -> "NEEDS IMPROVEMENT"
            }
            append("Rating: $rating\n\n")
            append("Targets met: ${kpis.count { it.actual >= it.target }}/${kpis.size}\n\n")
            append("Legend:\n")
            append("● >= 100% target\n")
            append("◐ >= 80% target\n")
            append("○ < 80% target")
        }
    }

    data class KPI(val name: String, val target: Double, val actual: Double, val unit: String)
}
